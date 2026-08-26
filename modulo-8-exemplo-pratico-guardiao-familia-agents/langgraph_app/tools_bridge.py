"""Ponte gateway/MCP para o grafo (Fase C)."""

from __future__ import annotations

import json
from typing import Any

from lib.gateway import (
    approve_hitl as gateway_approve_hitl,
    emit_status_event as gateway_emit,
    list_hitl_queue as gateway_list_hitl,
)
from lib.model_tier import select_model
from lib.handoff import load_handoff
from lib.task_action_history import append_task_action as history_append
from guardiao_mcp import server as mcp_tools


def _parse(raw: str) -> dict[str, Any]:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"ok": False, "error": "invalid_json", "raw": raw[:500]}


def emit_status_event(
    task_id: str,
    event: str,
    summary: str = "",
    *,
    dry_run: bool = True,
    pr_url: str | None = None,
    from_agent: str | None = None,
    react_trace: list[dict[str, Any]] | None = None,
    force_hitl_approved: bool = False,
) -> dict[str, Any]:
    result = gateway_emit(
        task_id,
        event,
        summary=summary,
        dry_run=dry_run,
        apply_board=True,
        pr_url=pr_url,
        from_agent=from_agent,
        react_trace=react_trace,
        force_hitl_approved=force_hitl_approved,
    )
    return {
        "ok": bool(result.get("ok")),
        "dry_run": dry_run,
        "result": result,
        "error": result.get("error"),
    }


def approve_hitl(task_id: str, event: str, *, dry_run: bool = False) -> dict[str, Any]:
    result = gateway_approve_hitl(task_id, event, dry_run=dry_run)
    return {"ok": bool(result.get("ok")), "dry_run": dry_run, "result": result, "error": result.get("error")}


def select_model_tier(purpose: str, title: str = "", agent_role: str = "") -> dict[str, Any]:
    task = {"title": title, "agent_role": agent_role}
    return {"ok": True, "result": select_model(task, purpose=purpose, role=agent_role or None)}


def get_handoff(task_id: str) -> dict[str, Any]:
    data = load_handoff(task_id)
    if data is None:
        return {"ok": False, "error": f"Handoff ausente: {task_id}", "result": {}}
    return {"ok": True, "result": data}


def list_hitl_queue() -> dict[str, Any]:
    return {"ok": True, "result": {"hitl_queue": gateway_list_hitl()}}


def append_task_action(
    task_id: str,
    *,
    agent: str,
    event: str,
    thought: str,
    action: str,
    observation: str = "",
    dry_run: bool = True,
    from_status: str | None = None,
    to_status: str | None = None,
    extra: dict[str, Any] | None = None,
    record_history: bool = False,
    executed: list[str] | None = None,
    ok: bool = True,
    deliverables: list[dict[str, Any]] | None = None,
    test_scenarios: list[dict[str, Any]] | None = None,
    findings: list[dict[str, Any]] | None = None,
    title: str | None = None,
) -> dict[str, Any]:
    """Grava historico se nao for dry_run, ou se record_history (tokens/modelo)."""
    if dry_run and not record_history:
        return {
            "ok": True,
            "dry_run": True,
            "result": {"would_append": {"task_id": task_id, "event": event, "extra": extra}},
        }
    row = history_append(
        task_id,
        agent=agent,
        event=event,
        thought=thought,
        action=action,
        observation=observation,
        from_status=from_status,
        to_status=to_status,
        extra=extra,
        dry_run=dry_run,
        executed=executed,
        ok=ok,
        deliverables=deliverables,
        test_scenarios=test_scenarios,
        findings=findings,
        title=title,
    )
    return {"ok": True, "dry_run": dry_run, "result": row}


def list_mcp_catalog() -> dict[str, Any]:
    return _parse(mcp_tools.list_mcp_tools())
