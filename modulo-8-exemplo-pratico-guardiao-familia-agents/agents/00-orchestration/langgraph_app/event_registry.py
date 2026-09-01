"""Catálogo de eventos role-based → pipeline MCP (v2 LangGraph)."""

from __future__ import annotations

from typing import Any

from board_automation.board.task_status_workflow import (
    build_event,
    role_event_catalog,
)

# Ordem fixa das MCP tools no pipeline
MCP_TOOL_NAMES = (
    "orchestrator_enter_in_progress",
    "emit_status_event",
    "on_status_event",
    "hitl_guard_actuation",
    "developer_implement",
    "developer_review",
    "qa_validate",
    "execute_agent_actuation_tool",
)


def event_node_id(event: str) -> str:
    """ID de nó LangGraph (sem caracteres inválidos)."""
    return "evt_" + event.replace("-", "_")


def node_id_to_event(node_id: str) -> str | None:
    if not node_id.startswith("evt_"):
        return None
    slug = node_id[4:]
    for row in role_event_catalog():
        if event_node_id(row["event"]) == node_id:
            return row["event"]
    return None


def build_pipeline(row: dict[str, str]) -> tuple[str, ...]:
    """Define quais MCP tools o nó deste evento executa (em ordem)."""
    event = row["event"]
    if event == "orchestrator_enter_in_progress":
        return ("orchestrator_enter_in_progress",)

    cls = row["classification"]
    target = row["board_status"]
    kind = row["kind"]

    tools: list[str] = []

    if event == "orchestrator_todo":
        tools.append("emit_status_event")

    tools.extend(["on_status_event", "hitl_guard_actuation"])

    if cls == "creator" and target == "In Progress" and kind == "advance":
        tools.append("developer_implement")
    elif cls == "reviewer" and target == "Ready for Test":
        tools.append("developer_review")
    elif cls == "qa-gate" and target == "In Test":
        tools.append("qa_validate")
    elif kind == "return" and target == "In Progress":
        tools.append("developer_implement")

    tools.append("execute_agent_actuation_tool")
    return tuple(tools)


def build_event_registry() -> dict[str, dict[str, Any]]:
    """Mapa event → spec (metadados + pipeline MCP)."""
    registry: dict[str, dict[str, Any]] = {}
    for row in role_event_catalog():
        event = row["event"]
        registry[event] = {
            **row,
            "node_id": event_node_id(event),
            "pipeline": build_pipeline(row),
        }
    return registry


EVENT_REGISTRY: dict[str, dict[str, Any]] = build_event_registry()


def effective_pipeline(spec: dict[str, Any], board_status: str) -> tuple[str, ...]:
    """Ajusta pipeline conforme status atual (ex.: já em ICR → review completo)."""
    pipeline = list(spec["pipeline"])
    cls = spec.get("classification")
    target = spec.get("board_status")
    status = (board_status or "").strip()

    if cls == "reviewer" and target == "In Code Review":
        if status == "In Code Review" and "developer_review" not in pipeline:
            pipeline.insert(pipeline.index("execute_agent_actuation_tool"), "developer_review")
        elif status == "Ready for Code Review" and "developer_review" in pipeline:
            pipeline.remove("developer_review")

    return tuple(pipeline)


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
