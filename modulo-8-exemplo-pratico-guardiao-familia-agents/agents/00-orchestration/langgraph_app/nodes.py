"""Nós do grafo Fase C — policy + LLM OpenRouter + implement/qa/hitl."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from lib.orchestrator.event_orchestrator import acting_agent_for_event
from lib.core.model_tier import select_model
from lib.paths import LANGGRAPH_DIR
from board_automation.board.reviewer_pairs import normalize_creator_role
from board_automation.board.task_router import load_tasks
from board_automation.board.task_status_workflow import EVENT_TARGET
from langgraph_app.llm import (
    format_usage_line,
    get_llm,
    invoke_structured,
    invoke_text,
    merge_usage_totals,
)
from langgraph_app.policy import status_after_event, suggested_event
from langgraph_app.schemas import OrchestratorDecision, ReviewVerdict
from langgraph_app.tracing import pipeline_span
from langgraph_app import tools_bridge as tools
from board_automation.board.task_action_history import build_agent_observation
from lib.ci.ci_state import ci_fields_for_state, patch_ci_state


def _acc_usage(state: dict[str, Any], usage: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "token_usage": merge_usage_totals(state.get("token_usage"), usage),
        "last_llm_usage": usage,
    }


def _task(state: dict[str, Any]) -> dict[str, Any]:
    tid = state.get("task_id") or ""
    found = next((t for t in load_tasks() if t.get("id") == tid), None)
    if found:
        # Prefer board_status already tracked in pipeline (dry_run simulation)
        row = dict(found)
        if state.get("board_status") and state.get("mode") == "dry_run":
            row["board_status"] = state["board_status"]
        # creator vem do CSV; state.agent_role soh se CSV ausente
        if not row.get("agent_role") and state.get("agent_role"):
            row["agent_role"] = state["agent_role"]
        return row
    return {
        "id": tid,
        "title": state.get("title") or tid,
        "agent_role": state.get("agent_role") or "backend",
        "board_status": state.get("board_status") or "Todo",
        "track": state.get("track") or "produto",
    }


def _mode(state: dict[str, Any]) -> str:
    return (state.get("mode") or os.environ.get("GUARDIAO_LANGGRAPH_MODE") or "dry_run").strip()


def _dry(state: dict[str, Any]) -> bool:
    return _mode(state) == "dry_run"


def _creator_role(state: dict[str, Any]) -> str:
    task = _task(state)
    return normalize_creator_role(
        str(task.get("agent_role") or state.get("agent_role") or "backend")
    )


def _acting_agent(state: dict[str, Any], event: str) -> str:
    """Agente que assina o passo (from_agent / histórico)."""
    task = {**_task(state), "agent_role": _creator_role(state)}
    try:
        return acting_agent_for_event(task, event)
    except ValueError:
        return _creator_role(state)


def route_task(state: dict[str, Any]) -> dict[str, Any]:
    task = _task(state)
    status = state.get("board_status") or task.get("board_status") or "Todo"
    if _mode(state) != "dry_run":
        fresh = next((t for t in load_tasks() if t.get("id") == task.get("id")), None)
        if fresh:
            status = fresh.get("board_status") or status
            task = fresh

    from lib.core.agent_registry import redirect_comment, resolve_agent_for_task

    resolved = resolve_agent_for_task(task)
    creator = normalize_creator_role(str(resolved.get("agent_role") or "backend"))
    tier = select_model({**task, "agent_role": creator}, purpose="route", role=creator)

    out: dict[str, Any] = {
        "title": task.get("title") or state.get("title") or "",
        "board_status": status,
        "agent_role": creator,
        "agent_role_secondary": str(resolved.get("agent_role_secondary") or ""),
        "model_tier": tier,
        "steps": int(state.get("steps") or 0) + 1,
    }

    if resolved.get("redirected"):
        msg = (
            f"route: redirect {resolved.get('from_role')} -> {creator} "
            f"({resolved.get('match_reason')})"
        )
        out["scope_redirect"] = resolved
        out["messages"] = list(state.get("messages") or []) + [msg]
        out["react_trace"] = [
            {
                "thought": "Roteamento com redirecionamento de escopo",
                "action": "route_task",
                "observation": resolved.get("reason") or msg,
                "redirect": {"from": resolved.get("from_role"), "to": creator},
            }
        ]
        if not _dry(state):
            try:
                from board_automation.board.board_client import comment_issue

                body = redirect_comment(resolved, str(task.get("id") or state.get("task_id")))
                if body:
                    comment_issue(
                        str(task.get("repo") or "guardiao-familia-api"),
                        str(task.get("id") or state.get("task_id")),
                        body,
                        dry_run=False,
                    )
            except Exception:  # noqa: BLE001
                pass
    else:
        out["messages"] = list(state.get("messages") or []) + [
            f"route: status={status} creator={creator} repo={resolved.get('repo')}"
        ]
        out["react_trace"] = [
            {
                "thought": "Roteamento",
                "action": "route_task",
                "observation": status,
                "repo_path": resolved.get("repo_path"),
            }
        ]
    return out


def load_context(state: dict[str, Any]) -> dict[str, Any]:
    tid = state["task_id"]
    ho = tools.get_handoff(tid)
    handoff = (ho.get("result") if ho.get("ok") else {}) or {}
    purpose = "review" if "Review" in str(state.get("board_status") or "") else "implement_low"
    tier = tools.select_model_tier(
        purpose,
        title=state.get("title") or "",
        agent_role=state.get("agent_role") or "",
    )
    ci = ci_fields_for_state(tid, mode=_mode(state))
    return {
        "handoff": handoff,
        "model_tier": (tier.get("result") if tier.get("ok") else state.get("model_tier")) or {},
        **ci,
        "messages": list(state.get("messages") or []) + [f"context: ci={ci.get('ci_status')}"],
        "steps": int(state.get("steps") or 0) + 1,
        "react_trace": [
            {
                "thought": "Contexto",
                "action": "load_context",
                "observation": f"ci={ci.get('ci_status')}",
            }
        ],
    }


def implement_node(state: dict[str, Any]) -> dict[str, Any]:
    """Demo/local: grava artefato de implementação antes do open_pr."""
    with pipeline_span(
        "implement",
        metadata={"task_id": state.get("task_id"), "board_status": state.get("board_status")},
    ):
        return _implement_node(state)


def _implement_node(state: dict[str, Any]) -> dict[str, Any]:
    task = _task(state)
    tid = task["id"]
    dry = _dry(state)
    mode = _mode(state)

    from lib.core.agent_registry import profile_for_role, resolve_agent_for_task

    resolved = resolve_agent_for_task(task)
    creator = _creator_role(state)
    if resolved.get("redirected") and normalize_creator_role(creator) != normalize_creator_role(
        str(resolved.get("agent_role") or "")
    ):
        reason = str(resolved.get("reason") or "fora de escopo")
        summary = f"Implementacao bloqueada: redirecionar para `{resolved.get('agent_role')}`"
        return {
            "decision": {
                "next_event": "scope_redirect",
                "summary": summary,
                "rationale": reason,
                "confidence": 0.95,
                "needs_human": False,
            },
            "scope_redirect": resolved,
            "messages": list(state.get("messages") or []) + [f"implement: {summary}"],
            "steps": int(state.get("steps") or 0) + 1,
            "react_trace": [
                {
                    "thought": summary,
                    "action": "implement_node",
                    "observation": reason,
                    "suggested_agent": resolved.get("agent_role"),
                    "repo_path": resolved.get("repo_path"),
                }
            ],
        }

    profile = profile_for_role(creator)
    ws = LANGGRAPH_DIR / "workspace" / tid
    deliverables: list[dict[str, Any]] = []
    executed = ["workspace_prepare"]
    impl_meta: dict[str, Any] = {}

    # Trabalho real no site quando a task e do tipo hero (fluxo padrao board)
    site_ok = False
    infra_scope: dict[str, Any] | None = None
    if not dry:
        try:
            from board_automation.board.infra_policy import infra_implement_scope, is_infra_okr_task

            if is_infra_okr_task(task):
                infra_scope = infra_implement_scope(tid, str(task.get("title") or ""))
                executed.extend(
                    [
                        "infra_policy:terraform_only",
                        "scope:infra/terraform",
                        "no_aws_apply",
                    ]
                )
                deliverables.append(
                    {
                        "path": "infra/terraform/",
                        "what": "estrutura HCL (OKR O2 — sem apply AWS)",
                    }
                )
        except Exception as exc:  # noqa: BLE001
            infra_scope = {"ok": False, "error": str(exc)[:300]}

    if not dry and not infra_scope:
        try:
            from lib.site.site_hero_work import apply_hero_commit, is_site_hero_task

            if is_site_hero_task(task):
                impl_meta = apply_hero_commit(tid)
                site_ok = bool(impl_meta.get("ok"))
                executed.extend(
                    [
                        "checkout_main",
                        f"branch:{impl_meta.get('branch')}",
                        "edit_index.html",
                        f"commit:{(impl_meta.get('sha') or '')[:12]}",
                    ]
                )
                deliverables.append(
                    {
                        "path": "index.html",
                        "what": f"H1+title -> {impl_meta.get('expected')}",
                    }
                )
        except Exception as exc:  # noqa: BLE001
            impl_meta = {"ok": False, "error": str(exc)[:300]}

    from board_automation.board.infra_policy import POLICY_SUMMARY

    content = (
        f"# Implementacao LangGraph — {tid}\n\n"
        f"Titulo: {task.get('title')}\n"
        f"Role: {task.get('agent_role')}\n"
        f"Repo: {resolved.get('repo') or task.get('repo') or 'n/a'}\n"
        f"Repo path: {resolved.get('repo_path') or profile.get('path_hint') or 'n/a'}\n"
        f"Track: {task.get('track') or 'n/a'}\n"
        f"Mode: {mode}\n"
    )
    if infra_scope:
        content += (
            f"\n## OKR infra — Terraform only\n\n"
            f"{POLICY_SUMMARY}\n\n"
            f"Escopo: {infra_scope.get('allowed')}\n"
            f"Proibido: {infra_scope.get('forbidden')}\n"
        )
    else:
        content += f"Site hero: {impl_meta or 'n/a'}\n"
    content += "\nGerado pelo no implement (orquestracao padrao).\n"
    path = None
    if not dry:
        ws.mkdir(parents=True, exist_ok=True)
        path = ws / "IMPLEMENTACAO.md"
        path.write_text(content, encoding="utf-8")
        executed.append("write_IMPLEMENTACAO.md")
        deliverables.append({"path": str(path), "what": "plano/artefato LangGraph"})

    summary = f"Implementacao preparada para {tid}"
    sel = state.get("model_tier") or {}
    usage: dict[str, Any] | None = None
    try:
        prompt = (
            f"Em 2-3 frases (PT-BR), descreva o que voce implementou na task "
            f"{tid}: {task.get('title')} (role {task.get('agent_role')}). "
        )
        if infra_scope:
            prompt += (
                "Task OKR infra: apenas alteracoes Terraform (HCL/modulos), "
                "sem terraform apply nem mutacao AWS."
            )
        else:
            prompt += f"Detalhe site={impl_meta.get('sha') if impl_meta else 'artefato local'}."
        summary, sel, usage = invoke_text(task, prompt, purpose="implement_low")
        summary = summary[:500]
    except Exception as exc:  # noqa: BLE001
        summary = f"{summary} (llm_skip: {type(exc).__name__})"

    usage_line = format_usage_line(usage)
    hist_extra = _history_extra({**state, "last_llm_usage": usage, "model_tier": sel}, "implement")
    hist_extra["focus"] = (
        "OKR infra: estrutura Terraform (sem apply AWS)"
        if infra_scope
        else (
            f"implementacao hero/site sha={(impl_meta or {}).get('sha', 'n/a')}"
            if impl_meta
            else "artefato IMPLEMENTACAO.md"
        )
    )
    if not dry:
        tools.append_task_action(
            tid,
            agent=_creator_role(state),
            event="implement",
            thought=summary,
            action=(
                f"Editar infra/terraform (branch `{infra_scope.get('branch_prefix')}`)"
                if infra_scope
                else (
                    f"Aplicar mudanca + commit `{(impl_meta or {}).get('branch', 'workspace')}`"
                    if impl_meta
                    else f"Gravar artefato em {path}"
                )
            ),
            observation=build_agent_observation(
                str(hist_extra["focus"]),
                extra=hist_extra,
                detail=(
                    f"infra_terraform_only={bool(infra_scope)}; site_ok={site_ok}; {usage_line}"
                ),
                ok=bool(infra_scope or site_ok or path),
            ),
            dry_run=False,
            record_history=True,
            from_status=state.get("board_status") or "In Progress",
            to_status=state.get("board_status") or "In Progress",
            extra=hist_extra,
            executed=executed,
            deliverables=deliverables or None,
            ok=bool(infra_scope or site_ok or path),
        )

    return {
        "model_tier": sel,
        "implement_path": str(path) if path else None,
        "decision": {
            "next_event": "open_pr",
            "summary": summary,
            "rationale": (
                f"Implementacao pronta (sha={(impl_meta or {}).get('sha', 'local')}); abrir PR"
            ),
            "confidence": 0.9 if (site_ok or path) else 0.5,
            "needs_human": False,
        },
        "messages": list(state.get("messages") or [])
        + [f"implement: {summary[:80]} | {usage_line}"],
        "steps": int(state.get("steps") or 0) + 1,
        "react_trace": [
            {
                "thought": summary,
                "action": "implement_node",
                "observation": f"{impl_meta or path} | {usage_line}",
                "llm_usage": usage,
            }
        ],
        **_acc_usage(state, usage),
    }


def decide_next(state: dict[str, Any]) -> dict[str, Any]:
    """Policy + LLM (summary/rationale). Em demo/dry_run a policy manda no evento."""
    with pipeline_span(
        "decide",
        metadata={"task_id": state.get("task_id"), "board_status": state.get("board_status")},
    ):
        return _decide_next(state)


def _decide_next(state: dict[str, Any]) -> dict[str, Any]:
    task = _task(state)
    status = state.get("board_status") or task.get("board_status") or "Todo"
    policy_event = suggested_event(status)

    if policy_event == "start_test" and not state.get("test_ci_ready"):
        return {
            "decision": {
                "next_event": "noop",
                "summary": f"Aguardando ci_green antes de start_test ({status})",
                "rationale": "gate CI no grafo (wait_ci)",
                "confidence": 1.0,
                "needs_human": False,
            },
            "messages": list(state.get("messages") or []) + [f"decide: blocked start_test (ci={state.get('ci_status')})"],
            "steps": int(state.get("steps") or 0) + 1,
            "react_trace": [
                {
                    "thought": "CI pendente",
                    "action": "decide:block_start_test",
                    "observation": str(state.get("ci_status")),
                }
            ],
        }

    if policy_event == "noop":
        return {
            "decision": {
                "next_event": "noop",
                "summary": f"Status terminal ou sem acao: {status}",
                "rationale": "policy",
                "confidence": 1.0,
                "needs_human": False,
            },
            "messages": list(state.get("messages") or []) + [f"decide: noop ({status})"],
            "steps": int(state.get("steps") or 0) + 1,
            "done": status == "Done",
            "react_trace": [
                {"thought": "Sem proximo evento", "action": "decide:noop", "observation": status}
            ],
        }

    purpose = "review" if "Review" in status else "implement_low"
    if "SOS" in str(task.get("title") or "") or any(
        h in str(task.get("title") or "").lower()
        for h in ("pagamento", "lgpd", "auth", "sos")
    ):
        purpose = "implement_high" if purpose.startswith("implement") else purpose

    data = {
        "next_event": policy_event,
        "summary": f"Avancar {status} -> {policy_event}",
        "rationale": "Evento sugerido pela policy do Kanban",
        "confidence": 0.85,
        "needs_human": False,
    }
    sel = state.get("model_tier") or {}
    usage: dict[str, Any] | None = None
    try:
        decision, sel, usage = invoke_structured(
            task,
            (
                "Voce confirma o proximo evento do board Guardiao Familia.\n"
                f"task_id={task.get('id')} title={task.get('title')}\n"
                f"board_status={status} agent_role={task.get('agent_role')}\n"
                f"Evento sugerido pela policy: {policy_event}\n"
                f"Eventos permitidos: {sorted(EVENT_TARGET)}\n"
                f"Prefira next_event={policy_event}. "
                "Pode usar noop so se houver bloqueio claro. "
                "Preencha summary e rationale."
            ),
            OrchestratorDecision,
            purpose=purpose,
        )
        llm_data = decision.model_dump()
        if _mode(state) == "live" and llm_data["next_event"] in set(EVENT_TARGET) | {"noop"}:
            if llm_data.get("confidence", 0) >= 0.8:
                data = llm_data
            else:
                data["summary"] = llm_data.get("summary") or data["summary"]
                data["rationale"] = llm_data.get("rationale") or data["rationale"]
        else:
            data["summary"] = llm_data.get("summary") or data["summary"]
            data["rationale"] = llm_data.get("rationale") or data["rationale"]
            data["confidence"] = float(llm_data.get("confidence") or data["confidence"])
            data["next_event"] = policy_event
    except Exception as exc:  # noqa: BLE001
        data["rationale"] += f" | llm_fallback: {type(exc).__name__}"

    if data["next_event"] != "noop" and data["next_event"] not in EVENT_TARGET:
        data["next_event"] = policy_event

    usage_line = format_usage_line(usage)
    return {
        "decision": data,
        "model_tier": sel,
        "messages": list(state.get("messages") or [])
        + [f"decide: {data['next_event']} conf={data.get('confidence', 0):.2f} | {usage_line}"],
        "steps": int(state.get("steps") or 0) + 1,
        "react_trace": [
            {
                "thought": data.get("rationale", ""),
                "action": f"decide:{data['next_event']}",
                "observation": f"{data.get('summary', '')} | {usage_line}",
                "llm_usage": usage,
            }
        ],
        **_acc_usage(state, usage),
    }


def review_node(state: dict[str, Any]) -> dict[str, Any]:
    with pipeline_span(
        "review",
        metadata={"task_id": state.get("task_id"), "board_status": state.get("board_status")},
    ):
        return _review_node(state)


def _review_node(state: dict[str, Any]) -> dict[str, Any]:
    task = _task(state)
    usage: dict[str, Any] | None = None
    sel = state.get("model_tier") or {}
    try:
        verdict, sel, usage = invoke_structured(
            task,
            (
                "Voce e reviewer do Guardiao Familia.\n"
                f"task={task.get('id')} title={task.get('title')} status={task.get('board_status')}\n"
                f"handoff_keys={list((state.get('handoff') or {}).keys())}\n"
                "Em modo demo/academico prefira approve se nao houver risco critico documentado. "
                "Decida approve ou request_changes."
            ),
            ReviewVerdict,
            purpose="review",
        )
        data = verdict.model_dump()
    except Exception as exc:  # noqa: BLE001
        data = {
            "verdict": "approve",
            "findings": [f"llm_fallback:{type(exc).__name__}"],
            "summary": "approve (fallback)",
            "confidence": 0.6,
            "needs_human": False,
        }
    next_event = "approve_review" if data["verdict"] == "approve" else "request_changes"
    usage_line = format_usage_line(usage)
    acting = _acting_agent(state, next_event)
    return {
        "review": data,
        "decision": {
            "next_event": next_event,
            "summary": data.get("summary") or data["verdict"],
            "rationale": "; ".join(data.get("findings") or [data["verdict"]]),
            "confidence": data.get("confidence", 0.7),
            "needs_human": bool(data.get("needs_human")),
        },
        "model_tier": sel,
        "messages": list(state.get("messages") or [])
        + [f"review: {data['verdict']} agent={acting} | {usage_line}"],
        "steps": int(state.get("steps") or 0) + 1,
        "react_trace": [
            {
                "thought": data.get("summary") or "",
                "action": f"review:{data['verdict']}",
                "observation": f"{data.get('findings')} | {usage_line}",
                "llm_usage": usage,
                "agent": acting,
            }
        ],
        **_acc_usage(state, usage),
    }


def qa_node(state: dict[str, Any]) -> dict[str, Any]:
    """QA: Playwright no site hero quando aplicavel; senao test_passed tipado."""
    with pipeline_span(
        "qa",
        metadata={"task_id": state.get("task_id"), "board_status": state.get("board_status")},
    ):
        return _qa_node(state)


def _qa_node(state: dict[str, Any]) -> dict[str, Any]:
    task = _task(state)
    tid = str(task.get("id") or state.get("task_id") or "")
    dry = _dry(state)
    mode = _mode(state)
    qa_result: dict[str, Any] = {"ok": True, "skipped": True}
    usage: dict[str, Any] | None = None
    sel = state.get("model_tier") or {}
    next_event = "test_passed"
    summary = "Suite tipada OK"
    rationale = "qa_gate tipado (orquestracao)"

    try:
        from board_automation.board.infra_policy import (
            POLICY_SUMMARY,
            is_infra_okr_task,
            validate_infra_executed,
        )

        if is_infra_okr_task(task):
            ho = state.get("handoff") or {}
            metrics = ho.get("metrics") or {}
            executed = list(metrics.get("executed") or [])
            ok_policy, reason = validate_infra_executed(executed)
            qa_result = {
                "ok": ok_policy,
                "infra": True,
                "policy": POLICY_SUMMARY,
                "reason": reason,
            }
            if ok_policy:
                next_event = "test_passed"
                summary = "OKR infra: Terraform only — sem apply AWS"
                rationale = POLICY_SUMMARY
            else:
                next_event = "test_failed_bug"
                summary = f"Violacao politica infra: {reason}"
                rationale = reason
    except Exception as exc:  # noqa: BLE001
        qa_result = {"ok": False, "error": str(exc)[:200]}

    if not dry and not qa_result.get("infra"):
        try:
            from board_automation.board.board_client import comment_issue_with_image
            from lib.mobile.qa_playwright import format_qa_issue_comment
            from lib.site.site_hero_work import is_site_hero_task, run_hero_qa

            from lib.mobile.mobile_work import (
                is_mobile_e2e_task,
                is_mobile_pairing_task,
                wants_mobile_setup_evidence,
            )
            from lib.mobile.qa_mobile import format_qa_mobile_comment, run_mobile_pairing_qa
            from lib.mobile.qa_mobile_setup_evidence import (
                format_evidence_comment,
                run_mobile_setup_qa_for_task,
            )

            if is_site_hero_task(task):
                qa_result = run_hero_qa(tid)
                png = qa_result.get("png_bytes")
                comment_issue_with_image(
                    str(task.get("repo") or "guardiao-familia-site"),
                    tid,
                    format_qa_issue_comment(qa_result),
                    png if isinstance(png, (bytes, bytearray)) else None,
                    filename=str(qa_result.get("filename") or f"{tid}_home_hero.png"),
                    dry_run=False,
                )
                if qa_result.get("ok"):
                    next_event = "test_passed"
                    summary = "Playwright PASS — hero validado"
                    rationale = str((qa_result.get("case") or {}).get("notes") or "PASS")
                else:
                    next_event = "test_failed_bug"
                    summary = "Playwright FAIL"
                    rationale = str(
                        (qa_result.get("case") or {}).get("notes")
                        or qa_result.get("error")
                        or "FAIL"
                    )
            elif wants_mobile_setup_evidence(task):
                qa_result = run_mobile_setup_qa_for_task(task)
                repo = str(task.get("repo") or "guardiao-familia-child")
                png = qa_result.get("png_bytes")
                comment_issue_with_image(
                    repo,
                    tid,
                    qa_result.get("comment") or format_evidence_comment(qa_result),
                    png if isinstance(png, (bytes, bytearray)) else None,
                    filename=str(qa_result.get("filename") or f"{tid}_mobile_evidence.png"),
                    dry_run=False,
                )
                if qa_result.get("ok"):
                    next_event = "test_passed"
                    mode = "mobile-setup"
                    summary = "Mobile-setup PASS — fast-stack + evidências empacotadas"
                    rationale = str((qa_result.get("case") or {}).get("notes") or "PASS")
                else:
                    next_event = "test_failed_bug"
                    summary = "Mobile-setup FAIL"
                    rationale = str(
                        (qa_result.get("case") or {}).get("notes")
                        or (qa_result.get("run") or {}).get("stdout_tail")
                        or qa_result.get("error")
                        or "FAIL"
                    )[:500]
            elif is_mobile_e2e_task(task) or is_mobile_pairing_task(task):
                full_ui = is_mobile_pairing_task(task)
                qa_result = run_mobile_pairing_qa(tid, full_ui=full_ui)
                repo = str(task.get("repo") or "guardiao-familia-api")
                comment_issue_with_image(
                    repo,
                    tid,
                    format_qa_mobile_comment(qa_result),
                    None,
                    dry_run=False,
                )
                if qa_result.get("ok"):
                    next_event = "test_passed"
                    mode = qa_result.get("mode") or "mobile"
                    summary = f"Mobile E2E PASS ({mode})"
                    rationale = str((qa_result.get("case") or {}).get("notes") or "PASS")
                else:
                    next_event = "test_failed_bug"
                    summary = "Mobile E2E FAIL"
                    rationale = str(
                        (qa_result.get("case") or {}).get("notes")
                        or qa_result.get("error")
                        or "FAIL"
                    )
        except Exception as exc:  # noqa: BLE001
            qa_result = {"ok": False, "error": str(exc)[:300]}
            next_event = "test_failed_bug"
            summary = f"QA erro: {type(exc).__name__}"
            rationale = str(exc)[:200]

    try:
        text, sel, usage = invoke_text(
            task,
            (
                f"Voce e qa-gate. Task {tid}: {task.get('title')}. "
                f"Resultado QA={summary}. Em 2 frases (PT-BR) registre o thought do gate."
            ),
            purpose="summarize",
        )
        summary = f"{summary} | {text[:240]}"
    except Exception:  # noqa: BLE001
        pass

    usage_line = format_usage_line(usage)
    hist_extra = _history_extra({**state, "last_llm_usage": usage, "model_tier": sel}, "qa")
    hist_extra["focus"] = f"QA {next_event} (modo={mode})"
    if not dry:
        tools.append_task_action(
            tid,
            agent="qa-gate",
            event="qa_gate",
            thought=summary,
            action=f"Decidir `{next_event}` apos evidencias QA",
            observation=build_agent_observation(
                str(hist_extra["focus"]),
                extra=hist_extra,
                detail=str((qa_result.get("case") or {}).get("notes") or qa_result.get("error") or ""),
                ok=bool(qa_result.get("ok")),
            ),
            dry_run=False,
            record_history=True,
            from_status=state.get("board_status") or "In Test",
            to_status=state.get("board_status") or "In Test",
            extra=hist_extra,
            executed=["qa_node", f"next:{next_event}"],
            test_scenarios=[qa_result.get("case")] if qa_result.get("case") else None,
            ok=bool(qa_result.get("ok")),
        )

    return {
        "decision": {
            "next_event": next_event,
            "summary": summary,
            "rationale": rationale,
            "confidence": 0.95 if next_event == "test_passed" else 0.7,
            "needs_human": False,
        },
        "model_tier": sel,
        "messages": list(state.get("messages") or []) + [f"qa: {next_event} | {usage_line}"],
        "steps": int(state.get("steps") or 0) + 1,
        "react_trace": [
            {
                "thought": summary,
                "action": "qa_node",
                "observation": f"{next_event} | {usage_line}",
                "llm_usage": usage,
            }
        ],
        **_acc_usage(state, usage),
    }


def _history_extra(state: dict[str, Any], event: str) -> dict[str, Any]:
    usage = state.get("last_llm_usage")
    extra: dict[str, Any] = {
        "stage": event,
        "focus": f"transicao `{event}` no board (modo={_mode(state)})",
    }
    if usage and (
        usage.get("total_tokens")
        or usage.get("input_tokens")
        or usage.get("output_tokens")
        or usage.get("model")
    ):
        extra["model"] = usage.get("model") or "n/a"
        extra["purpose"] = usage.get("purpose")
        extra["llm_usage"] = usage
        extra["tokens"] = {
            "input": usage.get("input_tokens", 0),
            "output": usage.get("output_tokens", 0),
            "total": usage.get("total_tokens", 0),
        }
    totals = state.get("token_usage")
    if totals:
        extra["token_usage_total"] = totals
    # fallback: tier selecionado no state
    tier = state.get("model_tier") or {}
    if not extra.get("model") or extra.get("model") == "n/a":
        if tier.get("model"):
            extra["model"] = tier.get("model")
            extra["purpose"] = extra.get("purpose") or tier.get("purpose") or "implement_low"
    return extra


def apply_decision(state: dict[str, Any]) -> dict[str, Any]:
    dec = state.get("decision") or {}
    event = dec.get("next_event") or "noop"
    # D2: nomes de pipeline (merge_pr → merge)
    span_name = "merge" if event == "merge_pr" else event
    with pipeline_span(
        span_name,
        run_type="tool",
        metadata={
            "task_id": state.get("task_id"),
            "event": event,
            "mode": _mode(state),
            "from_status": state.get("board_status"),
            "dry_run": _dry(state),
        },
    ):
        return _apply_decision(state)


def _apply_decision(state: dict[str, Any]) -> dict[str, Any]:
    dec = state.get("decision") or {}
    event = dec.get("next_event") or "noop"
    dry = _dry(state)
    mode = _mode(state)
    msgs = list(state.get("messages") or [])
    results = list(state.get("last_tool_results") or [])
    status = state.get("board_status") or "Todo"
    usage = state.get("last_llm_usage")
    usage_line = format_usage_line(usage)
    hist_extra = _history_extra(state, event)
    acting = "orchestrator" if event == "noop" else _acting_agent(state, event)
    hist_extra["acting_agent"] = acting
    hist_extra["creator_role"] = _creator_role(state)

    if event == "noop":
        msgs.append(f"apply: noop | {usage_line}")
        return {
            "messages": msgs,
            "steps": int(state.get("steps") or 0) + 1,
            "done": status == "Done",
            "react_trace": [
                {
                    "thought": "noop",
                    "action": "apply_skip",
                    "observation": f"{status} | {usage_line}",
                    "llm_usage": usage,
                }
            ],
            "last_llm_usage": None,
        }

    react = [
        {
            "thought": dec.get("rationale") or event,
            "action": event,
            "observation": f"{dec.get('summary') or ''} | agent={acting} | {usage_line}",
            "llm_usage": usage,
            "agent": acting,
        }
    ]

    # dry_run: simula Status sem chamar gateway (evita validar board real)
    if dry:
        new_status = status_after_event(event, status)
        out = {
            "ok": True,
            "dry_run": True,
            "result": {"ok": True, "simulated": True, "event": event, "to": new_status},
            "error": None,
        }
        results.append(out)
        tools.append_task_action(
            state["task_id"],
            agent=acting,
            event=event,
            thought=(
                dec.get("rationale")
                or f"Como `{acting}`, decidi emitir `{event}` a partir de `{status}` "
                f"(summary={dec.get('summary') or '—'}; conf={dec.get('confidence')})."
            ),
            action=(
                f"Simular gateway `emit_status_event({event})` em dry_run "
                f"(from_agent={acting}; sem gravar Project remoto)."
            ),
            observation=build_agent_observation(
                f"dry_run: `{acting}` valida `{status}` -> `{new_status}` via `{event}`",
                extra=hist_extra,
                detail=f"decision.next_event={event}; usage={usage_line}",
                ok=True,
            ),
            dry_run=True,
            record_history=True,
            from_status=status,
            to_status=new_status,
            extra=hist_extra,
            executed=[
                f"acting_agent={acting}",
                f"policy/suggested -> {event}",
                f"status_after_event -> {new_status}",
            ],
        )
        msgs.append(f"apply: {event} -> {new_status} agent={acting} dry=True | {usage_line}")
        ci_updates: dict[str, Any] = {}
        if event == "open_pr":
            patch_ci_state(
                state["task_id"],
                status="pending",
                last_signal="open_pr",
                pr_url=f"https://example.com/langgraph/{state['task_id']}",
                summary="PR simulado — CI pending (dry_run)",
                event="open_pr",
                board_status=new_status,
                from_agent=acting,
                to_agent="devops-cicd",
            )
            ci_updates = ci_fields_for_state(state["task_id"], mode=mode)
        return {
            "board_status": new_status,
            "last_tool_results": results,
            "hitl_pending": False,
            **ci_updates,
            "messages": msgs,
            "steps": int(state.get("steps") or 0) + 1,
            "done": new_status == "Done",
            "react_trace": [
                {
                    "thought": dec.get("rationale") or "",
                    "action": f"simulate:{event}",
                    "observation": f"-> {new_status} | agent={acting} | {usage_line}",
                    "llm_usage": usage,
                    "agent": acting,
                }
            ],
            "last_llm_usage": None,
        }

    kwargs: dict[str, Any] = {
        "dry_run": False,
        "from_agent": acting,
        "react_trace": react,
    }
    if event == "open_pr":
        ho = state.get("handoff") or {}
        pr = ho.get("pr_url") or state.get("pr_url")
        if not pr:
            pr = f"https://example.com/langgraph/{state['task_id']}"
        kwargs["pr_url"] = pr
        branch = ho.get("branch")
        if branch:
            kwargs["branch"] = branch

    if event == "merge_pr" and mode == "demo":
        kwargs["force_hitl_approved"] = True

    out = tools.emit_status_event(
        state["task_id"],
        event,
        summary=dec.get("summary") or "",
        **kwargs,
    )
    results.append(out)

    awaiting = (out.get("result") or {}).get("status") == "awaiting_human"
    new_status = status
    board = (out.get("result") or {}).get("board") or out.get("board") or {}
    local_ok = bool((board.get("local") or {}).get("ok")) if isinstance(board, dict) else False
    # Local board is source of truth for LangGraph; GitHub Project may collapse Status.
    if (out.get("ok") or local_ok) and not awaiting:
        fresh = next((t for t in load_tasks() if t.get("id") == state["task_id"]), None)
        new_status = (fresh or {}).get("board_status") or status_after_event(event, status)
    elif awaiting:
        new_status = status

    tools.append_task_action(
        state["task_id"],
        agent=acting,
        event=event,
        thought=(
            dec.get("rationale")
            or f"Como `{acting}`, decidi emitir `{event}` a partir de `{status}` "
            f"(summary={dec.get('summary') or '—'}; conf={dec.get('confidence')}; "
            f"needs_human={dec.get('needs_human')})."
        ),
        action=(
            f"Chamar gateway `emit_status_event(task={state['task_id']}, event={event})` "
            f"from_agent={acting}; modo={mode}; apply_board=true."
        ),
        observation=build_agent_observation(
            f"`{acting}` aplica `{event}` (`{status}` -> `{new_status}`)",
            extra=hist_extra,
            detail=(
                f"gateway_ok={out.get('ok')}; awaiting_human={awaiting}; "
                f"local_ok={local_ok}; usage={usage_line}"
            ),
            ok=bool(out.get("ok") or local_ok),
        ),
        dry_run=False,
        record_history=True,
        from_status=status,
        to_status=new_status,
        extra=hist_extra,
        executed=[
            f"acting_agent={acting}",
            f"emit_status_event:{event}",
            f"board_status->{new_status}",
            f"hitl_pending={awaiting}",
        ],
        ok=bool(out.get("ok") or local_ok),
    )

    msgs.append(
        f"apply: {event} -> {new_status} agent={acting} dry=False ok={out.get('ok')} | {usage_line}"
    )
    ci_updates: dict[str, Any] = {}
    if event == "open_pr" and (out.get("ok") or local_ok):
        patch_ci_state(
            state["task_id"],
            status="pending",
            last_signal="open_pr",
            pr_url=kwargs.get("pr_url"),
            branch=kwargs.get("branch"),
            summary=dec.get("summary") or "PR aberto — aguardando checks",
            event="open_pr",
            board_status=new_status,
            from_agent=acting,
            to_agent="devops-cicd",
        )
        ci_updates = ci_fields_for_state(state["task_id"], mode=mode)
    return {
        "board_status": new_status,
        "last_tool_results": results,
        "hitl_pending": bool(awaiting) and mode == "live",
        **ci_updates,
        "messages": msgs,
        "steps": int(state.get("steps") or 0) + 1,
        "done": new_status == "Done",
        "react_trace": [
            {
                "thought": dec.get("rationale") or "",
                "action": f"emit:{event}",
                "observation": f"-> {new_status} | agent={acting} | {usage_line}",
                "llm_usage": usage,
                "agent": acting,
            }
        ],
        "last_llm_usage": None,
    }


def hitl_node(state: dict[str, Any]) -> dict[str, Any]:
    """Live: pausa. Demo: já force no apply. Dry: simula Done."""
    mode = _mode(state)
    dry = _dry(state)
    if mode == "live":
        return {
            "hitl_pending": True,
            "messages": list(state.get("messages") or [])
            + ["hitl: awaiting human approve_hitl(merge_pr)"],
            "steps": int(state.get("steps") or 0) + 1,
            "react_trace": [
                {"thought": "HITL", "action": "interrupt", "observation": "awaiting_human"}
            ],
        }
    if dry:
        return {
            "board_status": "Done",
            "done": True,
            "hitl_pending": False,
            "messages": list(state.get("messages") or []) + ["hitl: dry_run simulate Done"],
            "steps": int(state.get("steps") or 0) + 1,
            "react_trace": [
                {"thought": "HITL dry", "action": "simulate_done", "observation": "Done"}
            ],
        }
    # demo already force-approved in apply
    return {
        "messages": list(state.get("messages") or []) + ["hitl: demo passthrough"],
        "steps": int(state.get("steps") or 0) + 1,
        "react_trace": [{"thought": "HITL demo", "action": "passthrough", "observation": "ok"}],
    }
