"""Executa a fase do agente a partir do contexto de on_status_event e emite o próximo evento."""

from __future__ import annotations

import json
import os
import sys
from typing import Any

from board_automation.board.reviewer_pairs import QA_GATE_ROLE, normalize_creator_role, reviewer_for
from board_automation.board.task_status_workflow import build_event, merge_owner_for_task
from lib.orchestrator.event_orchestrator import set_agent_state
from lib.paths import ORCHESTRATION_DIR

if str(ORCHESTRATION_DIR) not in sys.path:
    sys.path.insert(0, str(ORCHESTRATION_DIR))

PHASE_BY_TARGET_STATUS: dict[str, str] = {
    "In Progress": "implement",
    "Ready for Code Review": "start_review",
    "In Code Review": "review",
    "Ready for Test": "start_test",
    "In Test": "qa",
    "In Pull Request": "merge",
}


def normalize_actuation_context(raw: dict[str, Any] | str) -> dict[str, Any]:
    """Aceita retorno direto de on_status_event ou envelope MCP {ok, result}."""
    if isinstance(raw, str):
        raw = json.loads(raw)
    if not isinstance(raw, dict):
        raise ValueError("actuation_context deve ser dict ou JSON")

    if raw.get("ok") is True:
        inner = raw.get("result")
        if isinstance(inner, dict) and inner.get("task_id"):
            if inner.get("ok") is False:
                raise ValueError(inner.get("error") or "contexto com erro")
            return inner
        if raw.get("task_id"):
            return raw

    if raw.get("task_id") and raw.get("assigned_agent"):
        return raw

    raise ValueError(
        "contexto invalido — passe o JSON retornado por on_status_event (campo result ou objeto plano)"
    )


def _build_state(ctx: dict[str, Any], *, mode: str) -> dict[str, Any]:
    board = ctx.get("board_task") or {}
    tid = str(ctx.get("task_id") or board.get("id") or "")
    return {
        "task_id": tid,
        "title": ctx.get("title") or board.get("title") or tid,
        "agent_role": ctx.get("creator_role") or board.get("agent_role") or "backend",
        "board_status": ctx.get("target_status") or board.get("board_status") or "Todo",
        "mode": mode,
        "handoff": ctx.get("handoff") or {},
        "model_tier": ctx.get("model_tier") or {},
        "ci_status": (ctx.get("ci") or {}).get("ci_status") or "pending",
        "test_ci_ready": (ctx.get("ci") or {}).get("ci_status") == "green",
        "messages": [],
        "last_tool_results": [],
        "react_trace": list(ctx.get("react_trace") or []),
        "hitl_pending": False,
        "done": False,
        "steps": 0,
        "max_steps": 4,
        "token_usage": {},
        "last_llm_usage": None,
        "error": None,
        "track": board.get("track") or ctx.get("ticket", {}).get("track") or "produto",
        "pr_url": (ctx.get("handoff") or {}).get("pr_url") or (ctx.get("ci") or {}).get("pr_url"),
    }


def _run_light_phase(phase: str, state: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    """Transições sem nó pesado (start_review, start_test, merge)."""
    assigned = str(ctx.get("assigned_agent") or "")
    tid = state["task_id"]
    creator = normalize_creator_role(str(ctx.get("creator_role") or state.get("agent_role") or "backend"))
    track = str(state.get("track") or "produto")
    if phase == "start_review":
        next_event = build_event(reviewer_for(creator), "In Code Review")
    elif phase == "start_test":
        next_event = build_event(QA_GATE_ROLE, "In Test")
    elif phase == "merge":
        next_event = build_event(merge_owner_for_task(track), "Done")
    else:
        next_event = "noop"
    summaries = {
        "start_review": f"{assigned} assume code review em {tid}",
        "start_test": f"QA gate inicia testes em {tid}",
        "merge": f"{assigned} prepara merge de {tid}",
    }
    return {
        "decision": {
            "next_event": next_event,
            "summary": summaries.get(phase, phase),
            "rationale": f"Fase `{phase}` após on_status_event",
            "confidence": 1.0,
            "needs_human": phase == "merge" and state.get("mode") == "live",
        },
        "messages": [f"{phase}: {summaries.get(phase, '')}"],
        "steps": int(state.get("steps") or 0) + 1,
        "react_trace": [
            {
                "thought": summaries.get(phase, phase),
                "action": phase,
                "observation": f"assigned={assigned}",
                "agent": assigned,
            }
        ],
    }


def _run_work_phase(phase: str, state: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    mode = str(state.get("mode") or "dry_run")
    if phase == "implement":
        from lib.orchestrator.phase_developer_implement import run_developer_implement

        return run_developer_implement(ctx, mode=mode)
    if phase == "review":
        from lib.orchestrator.phase_developer_review import run_developer_review

        return run_developer_review(ctx, mode=mode)
    if phase == "qa":
        from lib.orchestrator.phase_qa_validate import run_qa_validate

        return run_qa_validate(ctx, mode=mode)
    raise ValueError(f"Fase de trabalho desconhecida: {phase}")


def execute_agent_actuation(
    actuation_context: dict[str, Any] | str,
    *,
    guard_pass_id: str | None = None,
    mode: str | None = None,
    use_role_events: bool = True,
    phase_work: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Pipeline: contexto on_status_event → fase (ou phase_work pré-calculado) → emit_status_event.
    """
    from lib.gateway.actuation_guardrail import consume_guard_pass, validate_guard_pass

    ctx = normalize_actuation_context(actuation_context)
    if not guard_pass_id:
        return {
            "ok": False,
            "error": "Chame hitl_guard_actuation antes e passe guard_pass_id",
            "required_tool": "hitl_guard_actuation",
            "task_id": ctx.get("task_id"),
        }
    guard_check = validate_guard_pass(guard_pass_id, ctx)
    if not guard_check.get("valid"):
        return {
            "ok": False,
            "error": guard_check.get("reason") or "guard_pass_id inválido",
            "required_tool": "hitl_guard_actuation",
            "task_id": ctx.get("task_id"),
        }
    consume_guard_pass(guard_pass_id)
    tid = str(ctx.get("task_id") or "")
    assigned = str(ctx.get("assigned_agent") or "")
    target_status = str(ctx.get("target_status") or "")

    phase = PHASE_BY_TARGET_STATUS.get(target_status)
    if not phase:
        return {
            "ok": False,
            "error": f"Sem fase mapeada para target_status={target_status!r}",
            "task_id": tid,
            "assigned_agent": assigned,
        }

    run_mode = (mode or os.environ.get("GUARDIAO_LANGGRAPH_MODE") or "dry_run").strip()
    state = _build_state(ctx, mode=run_mode)

    set_agent_state(assigned, "busy", tid, persist=True)
    work_out: dict[str, Any]
    try:
        if phase_work is not None:
            work_out = phase_work
        elif phase in ("start_review", "start_test", "merge"):
            work_out = _run_light_phase(phase, state, ctx)
        else:
            work_out = _run_work_phase(phase, state, ctx)
    except Exception as exc:  # noqa: BLE001
        set_agent_state(assigned, "idle", None, persist=True)
        return {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "task_id": tid,
            "phase": phase,
            "assigned_agent": assigned,
        }

    merged = {**state, **work_out}
    decision = dict(merged.get("decision") or {})
    emit_event = str(decision.get("next_event") or "noop")

    if emit_event == "scope_redirect":
        set_agent_state(assigned, "idle", None, persist=True)
        return {
            "ok": True,
            "task_id": tid,
            "phase": phase,
            "assigned_agent": assigned,
            "scope_redirect": merged.get("scope_redirect"),
            "decision": decision,
            "emit": None,
            "message": "Implementacao bloqueada — redirecionar escopo",
        }

    if not use_role_events and emit_event not in ("noop",):
        pass  # mantém evento retornado pela fase (sempre role-based)

    from lib.orchestrator.apply_board import apply_decision

    apply_out = apply_decision(merged)
    set_agent_state(assigned, "idle", None, persist=True)

    emit_result = None
    for item in reversed(apply_out.get("last_tool_results") or []):
        if isinstance(item, dict) and ("result" in item or "ok" in item):
            emit_result = item
            break

    status_changed = apply_out.get("board_status") != state.get("board_status")
    gateway_ok = bool((emit_result or {}).get("ok")) if emit_result else status_changed

    return {
        "ok": gateway_ok and not apply_out.get("error"),
        "task_id": tid,
        "phase": phase,
        "assigned_agent": assigned,
        "target_status_in": target_status,
        "board_status_out": apply_out.get("board_status"),
        "mode": run_mode,
        "decision": decision,
        "emit_event": emit_event,
        "hitl_pending": bool(apply_out.get("hitl_pending")),
        "done": bool(apply_out.get("done")),
        "work": {
            "messages": work_out.get("messages"),
            "react_trace": work_out.get("react_trace"),
            "review": work_out.get("review"),
            "implement_path": work_out.get("implement_path"),
            "execution_plan": work_out.get("execution_plan"),
            "changed_files": work_out.get("changed_files"),
            "unit_tests": work_out.get("unit_tests"),
            "ac_validation": work_out.get("ac_validation"),
            "evidence_paths": work_out.get("evidence_paths"),
            "mcp_steps": work_out.get("mcp_steps"),
            "phase_tool": {
                "implement": "developer_implement",
                "review": "developer_review",
                "qa": "qa_validate",
            }.get(phase),
        },
        "apply": {
            "messages": apply_out.get("messages"),
            "react_trace": apply_out.get("react_trace"),
            "gateway": emit_result,
        },
    }
