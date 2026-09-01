"""Roteamento orchestrator: status do board → evento role-based."""

from __future__ import annotations

from typing import Any

from board_automation.board.task_status_workflow import build_event


def resolve_event_for_board(task: dict[str, Any], board_status: str) -> str:
    """Orchestrator: evento role-based para o status atual da task."""
    from lib.orchestrator.langgraph_mcp_route import actuation_params_for_status

    status = (board_status or "Todo").strip()
    params = actuation_params_for_status(task, status)
    if params.get("event"):
        return str(params["event"])
    role = params.get("agent_role")
    bst = params.get("board_status")
    if role and bst:
        return build_event(str(role), str(bst))
    return "noop"
