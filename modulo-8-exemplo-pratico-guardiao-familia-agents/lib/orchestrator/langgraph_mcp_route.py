"""Roteamento LangGraph → parâmetros de on_status_event / execute MCP."""

from __future__ import annotations

from typing import Any

from board_automation.board.reviewer_pairs import QA_GATE_ROLE, normalize_creator_role, reviewer_for
from board_automation.board.task_status_workflow import merge_owner_for_task

# Status em que o grafo executa atuação MCP (on_status → guard → execute)
MCP_ACTUATION_STATUSES = frozenset({
    "Todo",
    "In Progress",
    "Ready for Code Review",
    "In Code Review",
    "Ready for Test",
    "In Test",
    "In Pull Request",
})


def actuation_params_for_status(task: dict[str, Any], board_status: str) -> dict[str, Any]:
    """Monta kwargs para prepare_actuation_for_event a partir do status atual."""
    status = (board_status or "Todo").strip()
    creator = normalize_creator_role(str(task.get("agent_role") or "backend"))
    track = str(task.get("track") or "produto")

    if status == "Todo":
        return {"event": "orchestrator_enter_in_progress"}
    if status == "In Progress":
        return {"agent_role": creator, "board_status": "In Progress"}
    if status == "Ready for Code Review":
        return {"agent_role": creator, "board_status": "Ready for Code Review"}
    if status == "In Code Review":
        return {"agent_role": reviewer_for(creator), "board_status": "In Code Review"}
    if status == "Ready for Test":
        return {"agent_role": reviewer_for(creator), "board_status": "Ready for Test"}
    if status == "In Test":
        return {"agent_role": QA_GATE_ROLE, "board_status": "In Test"}
    if status == "In Pull Request":
        owner = merge_owner_for_task(track)
        return {"agent_role": owner, "board_status": "Done"}
    return {"event": "noop"}


def should_run_mcp_actuation(state: dict[str, Any]) -> bool:
    status = str(state.get("board_status") or "")
    if status not in MCP_ACTUATION_STATUSES:
        return False
    if status == "Ready for Test" and not state.get("test_ci_ready"):
        return False
    if status == "In Pull Request" and not state.get("merge_checks_ok"):
        return False
    return True
