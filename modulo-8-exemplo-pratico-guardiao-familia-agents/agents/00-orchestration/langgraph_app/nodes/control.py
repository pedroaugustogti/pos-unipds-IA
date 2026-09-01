"""Nós de controle: sync_board e orchestrator_decide."""

from __future__ import annotations

from typing import Any

from board_automation.board.board_task_loader import get_board_task

from langgraph_app.nodes._helpers import dry_run, step
from langgraph_app.registry import EVENT_REGISTRY, resolve_event_for_board
from lib.orchestrator.langgraph_mcp_route import should_run_mcp_actuation


def sync_board_node(state: dict[str, Any]) -> dict[str, Any]:
    tid = str(state.get("task_id") or "")
    row = get_board_task(tid) or {}
    status = str(row.get("board_status") or state.get("board_status") or "Todo")
    patch: dict[str, Any] = {
        "board_status": status,
        "agent_role": row.get("agent_role") or state.get("agent_role"),
        "title": row.get("title") or state.get("title"),
        "messages": [f"sync_board: {status}"],
        "react_trace": [{"thought": "Board", "action": "sync_board", "observation": status}],
    }
    if dry_run(state):
        if status == "Ready for Test":
            patch["test_ci_ready"] = True
        if status == "In Pull Request":
            patch["merge_checks_ok"] = True
    return step(state, patch)


def orchestrator_decide_node(state: dict[str, Any]) -> dict[str, Any]:
    """Escolhe qual nó evt_* executar com base no status atual."""
    tid = str(state.get("task_id") or "")
    task = get_board_task(tid) or {"id": tid, "agent_role": state.get("agent_role")}
    status = str(state.get("board_status") or "Todo")

    if status == "Done":
        return step(state, {"done": True, "selected_event": "", "messages": ["decide: Done"]})

    if not should_run_mcp_actuation({**state, "board_status": status}):
        return step(state, {
            "selected_event": "",
            "messages": [f"decide: aguardando pre-requisito em {status}"],
        })

    event = resolve_event_for_board(task, status)
    if event == "noop" or event not in EVENT_REGISTRY:
        return step(state, {"done": True, "selected_event": "", "messages": [f"decide: noop ({status})"]})

    spec = EVENT_REGISTRY[event]
    return step(state, {
        "selected_event": event,
        "selected_node_id": spec["node_id"],
        "messages": [f"decide: {event} [{spec['classification']}]"],
        "react_trace": [{
            "thought": "Orchestrator roteia por status",
            "action": "orchestrator_decide",
            "observation": event,
        }],
    })
