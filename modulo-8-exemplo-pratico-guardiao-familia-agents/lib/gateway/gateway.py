"""Gateway único: emit_status_event — contrato + HITL + handoff + board."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lib.gateway.event_contract import EventPayload
from lib.orchestrator.event_orchestrator import (
    emit_board_event as _emit_board_event_legacy,
    list_idle_agents,
    load_runtime,
    resolve_agent_for_event,
    save_runtime,
)
from lib.gateway.handoff import write_handoff
from lib.gateway.hitl_gates import evaluate_hitl
from lib.paths import AUDIT_TRAIL
from board_automation.board.task_router import load_tasks


def _task_by_id(task_id: str) -> dict | None:
    return next((t for t in load_tasks() if t["id"] == task_id), None)


def _append_audit(row: dict[str, Any]) -> None:
    AUDIT_TRAIL.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_TRAIL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _seen_idempotency(key: str) -> bool:
    rt = load_runtime()
    seen = rt.setdefault("idempotency", {})
    if key in seen:
        return True
    return False


def _mark_idempotency(key: str, result: dict[str, Any]) -> None:
    rt = load_runtime()
    seen = rt.setdefault("idempotency", {})
    seen[key] = {"at": result.get("at") or result.get("notification", {}).get("at"), "ok": result.get("ok")}
    # keep last 200
    if len(seen) > 200:
        for k in list(seen.keys())[: len(seen) - 200]:
            seen.pop(k, None)
    save_runtime(rt)


def emit_status_event(
    task_id: str,
    event: str,
    *,
    from_agent: str | None = None,
    summary: str = "",
    repo: str | None = None,
    branch: str | None = None,
    pr_url: str | None = None,
    doubts: list[str] | None = None,
    findings: list[str] | None = None,
    metrics: dict[str, Any] | None = None,
    bug_kind: str | None = None,
    react_trace: list[dict[str, Any]] | None = None,
    dry_run: bool = False,
    apply_board: bool = True,
    force_hitl_approved: bool = False,
) -> dict[str, Any]:
    """
    Porta única de eventos do board.

    - Monta EventPayload
    - Idempotência
    - HITL (merge / blocker / review alto risco)
    - Aplica board + despacho idle
    - Grava handoff + audit trail
    """
    task = _task_by_id(task_id)
    if not task:
        return {"ok": False, "error": f"Task {task_id} nao encontrada"}

    # Normalizar release_blocker do CSV (yes/true)
    rb = task.get("release_blocker")
    if isinstance(rb, str) and rb.lower() in ("yes", "true", "1"):
        task = {**task, "release_blocker": True}

    if event == "claim" and not force_hitl_approved:
        from lib.orchestrator.claim_lock import check_claim_allowed
        from lib.core.dependencies import dependencies_satisfied
        from board_automation.board.reviewer_pairs import normalize_creator_role
        role = normalize_creator_role(from_agent or task.get("agent_role") or "backend")
        lock = check_claim_allowed(task_id, role)
        if not lock.get("ok") and lock.get("code") != "already_owned":
            return {"ok": False, "code": lock.get("code"), "lock": lock, "error": lock.get("reason")}
        by_id = {t["id"]: t for t in load_tasks()}
        dep_ok, missing = dependencies_satisfied(task, by_id)
        if not dep_ok:
            return {
                "ok": False,
                "code": "depends_on",
                "error": f"Dependencias nao Done: {missing}",
                "missing": missing,
            }

    from lib.gateway.event_schema import validate_event_payload
    schema = validate_event_payload(
        task_id=task_id,
        event=event,
        pr_url=pr_url,
        react_trace=react_trace or (metrics or {}).get("react_trace"),
        bug_kind=bug_kind,
    )
    if not schema["ok"]:
        return {"ok": False, "code": "schema", "errors": schema["errors"]}

    if event == "open_pr" and not (react_trace or (metrics or {}).get("react_trace")):
        return {
            "ok": False,
            "code": "react_trace_required",
            "error": "open_pr exige react_trace no handoff (politica ReAct).",
        }

    if event == "approve_review" and not force_hitl_approved:
        from lib.gateway.handoff import load_handoff
        ho = load_handoff(task_id) or {}
        eg = (ho.get("metrics") or {}).get("eval_gate")
        if eg is not None and eg.get("ok") is False:
            return {
                "ok": False,
                "code": "eval_gate_failed",
                "error": "Eval gate deterministico falhou — corrija antes do approve",
                "eval_gate": eg,
            }

    payload = EventPayload(
        task_id=task_id,
        event=event,
        agent_role=task.get("agent_role"),
        repo=repo or task.get("repo"),
        branch=branch,
        pr_url=pr_url,
        summary=summary,
        doubts=doubts or [],
        metrics=metrics or {},
        bug_kind=bug_kind,
        dry_run=dry_run,
    )

    key = payload.key()
    if not dry_run and _seen_idempotency(key):
        return {"ok": True, "duplicate": True, "idempotency_key": key, "payload": payload.to_dict()}

    rt = load_runtime()
    bug_count = int((rt.get("bug_counts") or {}).get(task_id, {}).get("count") or 0)
    if event == "test_failed_bug":
        bug_count += 1

    hitl = evaluate_hitl(task, event, bug_count=bug_count)
    if force_hitl_approved:
        hitl = {**hitl, "required": False, "mode": "auto", "reason": "hitl_approved override"}

    if hitl["mode"] == "block_until_human" and not force_hitl_approved:
        pending = {
            "ok": True,
            "hitl": hitl,
            "status": "awaiting_human",
            "payload": payload.to_dict(),
            "idle_agents": list_idle_agents(),
            "message": (
                f"HITL obrigatório para `{event}` em `{task_id}`. "
                f"{hitl['human_action']}"
            ),
        }
        # fila HITL no runtime
        if not dry_run:
            q = rt.setdefault("hitl_queue", [])
            q[:] = [x for x in q if x.get("task_id") != task_id or x.get("event") != event]
            q.append({
                "task_id": task_id,
                "event": event,
                "hitl": hitl,
                "payload": payload.to_dict(),
            })
            save_runtime(rt)
            _append_audit({"type": "hitl_block", **pending["payload"], "hitl": hitl})
        return pending

    # propose_only: aplica board com evento propose_review se approve_review
    board_event = event
    if hitl["mode"] == "propose_only" and event == "approve_review" and not force_hitl_approved:
        board_event = "approve_review"  # status Ready for Test, mas marca proposta
        # não avança QA automaticamente: enfileira HITL confirm
        result = _emit_board_event_legacy(
            task_id,
            board_event,
            summary=summary or "Veredito proposto por reviewer LLM — aguardando humano",
            dry_run=dry_run,
            apply_board=apply_board,
        )
        result["hitl"] = hitl
        result["status"] = "propose_only"
        result["payload"] = payload.to_dict()
        if not dry_run:
            rt = load_runtime()
            q = rt.setdefault("hitl_queue", [])
            q.append({
                "task_id": task_id,
                "event": "confirm_approve_review",
                "hitl": hitl,
                "payload": payload.to_dict(),
            })
            save_runtime(rt)
            next_agent = (result.get("notification") or {}).get("next_agent") or "qa-gate"
            write_handoff(
                task_id,
                from_agent=from_agent or "reviewer",
                to_agent="human",
                event=event,
                status="Ready for Test",
                repo=payload.repo,
                branch=branch,
                pr_url=pr_url,
                summary=summary,
                doubts=doubts,
                findings=findings,
                metrics=metrics,
                react_trace=react_trace,
            )
            _append_audit({"type": "propose_only", "task_id": task_id, "event": event, "hitl": hitl})
            # não despachar qa-gate até hitl_approved
            note = result.get("notification") or {}
            if note.get("dispatch"):
                note["dispatch"] = {
                    "action": "await_human",
                    "call_agent": "human",
                    "message": hitl["human_action"],
                    "deferred_agent": next_agent,
                }
        if not dry_run:
            _mark_idempotency(key, result)
        return result

    # Classificação de bug → skill impactada
    if event == "test_failed_bug" and bug_kind:
        summary = f"[{bug_kind}] {summary}".strip()

    result = _emit_board_event_legacy(
        task_id,
        board_event,
        summary=summary,
        dry_run=dry_run,
        apply_board=apply_board,
    )
    note = result.get("notification") or {}
    next_agent = note.get("next_agent") or "orchestrator"
    src = from_agent or note.get("previous_agent") or "orchestrator"

    if not dry_run and result.get("ok"):
        write_handoff(
            task_id,
            from_agent=src,
            to_agent=next_agent,
            event=event,
            status=str(note.get("to") or ""),
            repo=payload.repo,
            branch=branch,
            pr_url=pr_url,
            summary=summary,
            doubts=doubts,
            findings=findings,
            metrics=metrics,
            react_trace=react_trace,
        )
        _append_audit({
            "type": "event",
            "task_id": task_id,
            "event": event,
            "from": note.get("from"),
            "to": note.get("to"),
            "next_agent": next_agent,
            "dispatch": (note.get("dispatch") or {}).get("action"),
            "hitl": hitl,
            "correlation_id": payload.correlation_id,
        })
        _mark_idempotency(key, result)

    result["hitl"] = hitl
    result["payload"] = payload.to_dict()
    result["status"] = "applied"
    return result


def approve_hitl(task_id: str, event: str, *, dry_run: bool = False) -> dict[str, Any]:
    """Humano libera evento bloqueado (merge, blocker, review alto risco)."""
    return emit_status_event(
        task_id,
        event,
        dry_run=dry_run,
        force_hitl_approved=True,
        summary="HITL aprovado por humano",
    )


def list_hitl_queue() -> list[dict[str, Any]]:
    return list(load_runtime().get("hitl_queue") or [])
