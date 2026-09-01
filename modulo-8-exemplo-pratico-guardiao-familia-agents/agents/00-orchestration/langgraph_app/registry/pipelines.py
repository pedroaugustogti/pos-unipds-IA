"""Regras de pipeline MCP por evento role-based."""

from __future__ import annotations

from typing import Any

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
