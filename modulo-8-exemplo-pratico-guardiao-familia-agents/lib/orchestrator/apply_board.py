"""apply_decision — emite status no board (usado por execute_agent_actuation)."""

from __future__ import annotations

import os
from typing import Any

from board_automation.board.task_router import load_tasks
from board_automation.board.task_action_history import append_task_action as history_append, build_agent_observation
from board_automation.board.reviewer_pairs import normalize_creator_role
from board_automation.board.task_status_workflow import is_merge_event, is_open_pr_event
from lib.ci.ci_state import ci_fields_for_state, patch_ci_state
from lib.mcp_invoke import emit_status_event as mcp_emit_status_event
from lib.orchestrator.event_orchestrator import acting_agent_for_event

from langgraph_app.llm import format_usage_line
from langgraph_app.policy import status_after_event


def _mode(state: dict[str, Any]) -> str:
    return (state.get("mode") or os.environ.get("GUARDIAO_LANGGRAPH_MODE") or "dry_run").strip()


def _dry(state: dict[str, Any]) -> bool:
    return _mode(state) == "dry_run"


def _task(state: dict[str, Any]) -> dict[str, Any]:
    tid = state.get("task_id") or ""
    found = next((t for t in load_tasks() if t.get("id") == tid), None)
    if found:
        row = dict(found)
        if state.get("board_status"):
            row["board_status"] = state["board_status"]
        return row
    return {
        "id": tid,
        "title": state.get("title") or tid,
        "agent_role": state.get("agent_role") or "backend",
        "board_status": state.get("board_status") or "Todo",
        "track": state.get("track") or "produto",
    }


def _creator_role(state: dict[str, Any]) -> str:
    return normalize_creator_role(str(_task(state).get("agent_role") or state.get("agent_role") or "backend"))


def _acting_agent(state: dict[str, Any], event: str) -> str:
    task = {**_task(state), "agent_role": _creator_role(state)}
    try:
        return acting_agent_for_event(task, event)
    except ValueError:
        return _creator_role(state)


def apply_decision(state: dict[str, Any]) -> dict[str, Any]:
    dec = state.get("decision") or {}
    event = dec.get("next_event") or "noop"
    dry = _dry(state)
    mode = _mode(state)
    msgs = list(state.get("messages") or [])
    results = list(state.get("last_tool_results") or [])
    status = state.get("board_status") or "Todo"
    usage = state.get("last_llm_usage")
    usage_line = format_usage_line(usage)
    acting = "orchestrator" if event == "noop" else _acting_agent(state, event)

    if event == "noop":
        return {
            "messages": msgs + [f"apply: noop | {usage_line}"],
            "steps": int(state.get("steps") or 0) + 1,
            "done": status == "Done",
            "react_trace": [{"thought": "noop", "action": "apply_decision:noop", "observation": status}],
        }

    if dry:
        new_status = status_after_event(event, status)
        out = {"ok": True, "dry_run": True, "result": {"ok": True, "simulated": True, "event": event, "to": new_status}}
        results.append(out)
        history_append(
            state["task_id"],
            agent=acting,
            event=event,
            thought=dec.get("rationale") or f"emit {event}",
            action=f"MCP emit_status_event({event}) dry_run",
            observation=build_agent_observation(f"{status} -> {new_status}", ok=True),
            dry_run=True,
            from_status=status,
            to_status=new_status,
        )
        ci_updates: dict[str, Any] = {}
        if is_open_pr_event(event):
            patch_ci_state(
                state["task_id"],
                status="pending",
                last_signal=event,
                pr_url=f"https://example.com/langgraph/{state['task_id']}",
                summary="PR simulado",
                event=event,
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
            "messages": msgs + [f"apply: {event} -> {new_status} dry"],
            "steps": int(state.get("steps") or 0) + 1,
            "done": new_status == "Done",
            "react_trace": [{"thought": dec.get("rationale") or "", "action": f"apply_decision:{event}", "observation": new_status}],
        }

    kwargs: dict[str, Any] = {"dry_run": False, "from_agent": acting}
    if is_open_pr_event(event):
        ho = state.get("handoff") or {}
        kwargs["pr_url"] = ho.get("pr_url") or state.get("pr_url") or f"https://example.com/langgraph/{state['task_id']}"
        if ho.get("branch"):
            kwargs["branch"] = ho["branch"]
    if is_merge_event(event) and mode == "demo":
        kwargs["force_hitl_approved"] = True

    out = mcp_emit_status_event(state["task_id"], event, summary=dec.get("summary") or "", **kwargs)
    results.append(out)
    awaiting = (out.get("result") or {}).get("status") == "awaiting_human"
    board = (out.get("result") or {}).get("board") or out.get("board") or {}
    local_ok = bool((board.get("local") or {}).get("ok")) if isinstance(board, dict) else False
    new_status = status
    if out.get("duplicate"):
        from board_automation.board.local_board import get_local_status

        new_status = get_local_status(state["task_id"]) or status_after_event(event, status)
    elif (out.get("ok") or local_ok) and not awaiting:
        fresh = next((t for t in load_tasks() if t.get("id") == state["task_id"]), None)
        new_status = (fresh or {}).get("board_status") or status_after_event(event, status)

    history_append(
        state["task_id"],
        agent=acting,
        event=event,
        thought=dec.get("rationale") or f"emit {event}",
        action=f"MCP emit_status_event({event})",
        observation=build_agent_observation(f"{status} -> {new_status}", ok=bool(out.get("ok") or local_ok)),
        dry_run=False,
        from_status=status,
        to_status=new_status,
        ok=bool(out.get("ok") or local_ok),
    )
    ci_updates: dict[str, Any] = {}
    if is_open_pr_event(event) and (out.get("ok") or local_ok):
        patch_ci_state(
            state["task_id"],
            status="pending",
            last_signal=event,
            pr_url=kwargs.get("pr_url"),
            summary=dec.get("summary") or "PR aberto",
            event=event,
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
        "messages": msgs + [f"apply: {event} -> {new_status}"],
        "steps": int(state.get("steps") or 0) + 1,
        "done": new_status == "Done",
        "react_trace": [{"thought": dec.get("rationale") or "", "action": f"apply_decision:{event}", "observation": new_status}],
    }
