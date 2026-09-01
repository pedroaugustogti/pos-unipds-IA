"""Factory de nós evt_* — um nó LangGraph por evento do catálogo."""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

from board_automation.board.task_status_workflow import build_event

from langgraph_app.nodes._helpers import dry_run, mode, step
from langgraph_app.registry import EVENT_REGISTRY, effective_pipeline
from lib import mcp_invoke as mcp


def _run_mcp_tool(
    tool: str,
    state: dict[str, Any],
    spec: dict[str, Any],
    *,
    ctx: dict[str, Any] | None,
    guard_id: str | None,
    phase_work: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any] | None, str | None, dict[str, Any] | None, str | None]:
    """Executa uma MCP tool; retorna (raw, ctx, guard_id, phase_work, error)."""
    tid = str(state.get("task_id") or "")
    event = str(spec["event"])
    agent_role = str(spec.get("agent_role") or "")
    clearance = bool(state.get("human_clearance") or mode(state) in ("demo", "dry_run"))

    if tool == "orchestrator_enter_in_progress":
        raw = mcp.orchestrator_enter_in_progress(
            task_id=tid,
            sprint=1,
            dry_run=dry_run(state),
            summary=f"LangGraph {event} {tid}",
        )
        if not raw.get("ok"):
            return raw, ctx, guard_id, phase_work, str(raw.get("error") or "orchestrator_enter_in_progress falhou")
        return raw, ctx, guard_id, phase_work, None

    if tool == "emit_status_event":
        raw = mcp.emit_status_event(
            task_id=tid,
            event=event,
            summary=str(state.get("pending_emit_summary") or f"langgraph {event}"),
            dry_run=dry_run(state),
            from_agent=agent_role,
        )
        if not raw.get("ok"):
            return raw, ctx, guard_id, phase_work, str(raw.get("error") or "emit_status_event falhou")
        return raw, ctx, guard_id, phase_work, None

    if tool == "on_status_event":
        raw = mcp.on_status_event(task_id=tid, event=event)
        if not raw.get("ok"):
            return raw, None, guard_id, phase_work, str(raw.get("error") or "on_status_event falhou")
        return raw, mcp.unwrap_result(raw), guard_id, phase_work, None

    if tool == "hitl_guard_actuation":
        if not ctx:
            return {"ok": False}, ctx, guard_id, phase_work, "hitl_guard_actuation sem actuation_context"
        raw = mcp.hitl_guard_actuation(
            ctx,
            mode=mode(state),
            human_clearance=clearance,
            clearance_note="langgraph-v2",
            dry_run=dry_run(state),
        )
        if not raw.get("ok"):
            inner = raw.get("result") if isinstance(raw.get("result"), dict) else raw
            return raw, ctx, None, phase_work, str(raw.get("error") or inner.get("reason") or "hitl blocked")
        guard = mcp.unwrap_result(raw)
        return raw, ctx, str(guard.get("guard_pass_id") or ""), phase_work, None

    if tool == "developer_implement":
        if not ctx:
            return {"ok": False}, ctx, guard_id, phase_work, "developer_implement sem contexto"
        raw = mcp.developer_implement(ctx, mode=mode(state))
        if not raw.get("ok"):
            return raw, ctx, guard_id, phase_work, str(raw.get("error") or "developer_implement falhou")
        return raw, ctx, guard_id, mcp.unwrap_result(raw), None

    if tool == "developer_review":
        if not ctx:
            return {"ok": False}, ctx, guard_id, phase_work, "developer_review sem contexto"
        raw = mcp.developer_review(ctx, mode=mode(state))
        if not raw.get("ok"):
            return raw, ctx, guard_id, phase_work, str(raw.get("error") or "developer_review falhou")
        return raw, ctx, guard_id, mcp.unwrap_result(raw), None

    if tool == "qa_validate":
        if not ctx:
            return {"ok": False}, ctx, guard_id, phase_work, "qa_validate sem contexto"
        raw = mcp.qa_validate(ctx, mode=mode(state))
        inner = mcp.unwrap_result(raw)
        fail_event = build_event("qa-gate", "In Progress", return_=True)
        if not raw.get("ok") and (inner.get("decision") or {}).get("next_event") != fail_event:
            return raw, ctx, guard_id, phase_work, str(raw.get("error") or "qa_validate falhou")
        return raw, ctx, guard_id, inner, None

    if tool == "execute_agent_actuation_tool":
        if not ctx or not guard_id:
            return {"ok": False}, ctx, guard_id, phase_work, "execute sem contexto ou guard_pass_id"
        pw = phase_work if phase_work else None
        raw = mcp.execute_agent_actuation_tool(
            ctx,
            guard_pass_id=guard_id,
            mode=mode(state),
            phase_work=pw,
        )
        if not raw.get("ok"):
            return raw, ctx, guard_id, phase_work, str(raw.get("error") or "execute falhou")
        return raw, ctx, None, {}, None

    return {"ok": False}, ctx, guard_id, phase_work, f"tool desconhecida: {tool}"


def make_event_node(spec: dict[str, Any]) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """Factory: um nó LangGraph por evento do catálogo."""
    event = str(spec["event"])
    pipeline: tuple[str, ...] = tuple(spec["pipeline"])
    node_id = str(spec["node_id"])

    def node(state: dict[str, Any]) -> dict[str, Any]:
        ctx: dict[str, Any] | None = state.get("actuation_context") or None
        guard_id: str | None = state.get("guard_pass_id")
        phase_work: dict[str, Any] | None = state.get("phase_work") or None
        trace: list[dict[str, Any]] = []
        active_pipeline = effective_pipeline(spec, str(state.get("board_status") or ""))
        msgs: list[str] = [f"{node_id}: pipeline={list(active_pipeline)}"]

        for tool in active_pipeline:
            raw, ctx, guard_id, phase_work, err = _run_mcp_tool(
                tool,
                state,
                spec,
                ctx=ctx,
                guard_id=guard_id,
                phase_work=phase_work,
            )
            trace.append({
                "thought": event,
                "action": tool,
                "observation": str(raw.get("ok")),
                "agent": spec.get("agent_role"),
            })
            if err:
                patch: dict[str, Any] = {
                    "error": err,
                    "actuation_context": ctx,
                    "guard_pass_id": guard_id,
                    "phase_work": phase_work or {},
                    "messages": msgs + [f"{node_id}: {tool} FAIL — {err}"],
                    "react_trace": trace,
                }
                if tool == "hitl_guard_actuation":
                    patch["hitl_pending"] = True
                return step(state, patch)

        patch = {
            "actuation_context": ctx,
            "guard_pass_id": None,
            "phase_work": {},
            "selected_event": "",
            "messages": msgs + [f"{node_id}: ok"],
            "react_trace": trace,
        }
        if active_pipeline[-1] == "execute_agent_actuation_tool":
            ex = mcp.unwrap_result(raw)
            patch["board_status"] = ex.get("board_status_out") or state.get("board_status")
            patch["done"] = bool(ex.get("done")) or patch.get("board_status") == "Done"
            patch["hitl_pending"] = bool(ex.get("hitl_pending"))
            patch["messages"] = msgs + [f"{node_id}: emit={ex.get('emit_event')} -> {ex.get('board_status_out')}"]
        elif active_pipeline == ("orchestrator_enter_in_progress",):
            inner = mcp.unwrap_result(raw)
            patch["board_status"] = str(inner.get("target_status") or "In Progress")
            patch["task_id"] = str(inner.get("task", {}).get("id") or state.get("task_id") or "")

        return step(state, patch)

    node.__name__ = node_id
    node.__doc__ = f"Evento `{event}` — MCP: {', '.join(pipeline)}"
    return node


def build_all_event_nodes() -> dict[str, Callable[[dict[str, Any]], dict[str, Any]]]:
    """55 nós (um por evento role-based)."""
    return {spec["node_id"]: make_event_node(spec) for spec in EVENT_REGISTRY.values()}


ALL_EVENT_NODES: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = build_all_event_nodes()
