"""Tool: list_status_events — catálogo de eventos role-based."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP

from board_automation.board.task_status_workflow import role_event_catalog
from guardiao_mcp.contract import ok

DESCRIPTION = """\
**Quando:** consultar os 55 eventos role-based antes de `emit_status_event`.

**Faz:** retorna catálogo com event, agent_role, board_status, kind (advance|return), classification.

**Filtros:** agent_role, classification (creator|reviewer|qa-gate|ops|orchestrator).
"""


def list_status_events(
    agent_role: Annotated[str, "Filtrar por papel (ex: frontend-mobile). Vazio = todos."] = "",
    classification: Annotated[
        str,
        "Filtrar por classificação: creator, reviewer, qa-gate, ops, orchestrator",
    ] = "",
) -> str:
    """Catálogo de eventos role-based alinhados a agent_role e board status."""
    rows = role_event_catalog()
    if agent_role:
        rows = [r for r in rows if r["agent_role"] == agent_role]
    if classification:
        rows = [r for r in rows if r["classification"] == classification]
    return ok({
        "pattern_advance": "{agent_role}_{status_slug}",
        "pattern_return": "{agent_role}_return_{status_slug}",
        "events": rows,
        "count": len(rows),
    })


def register(mcp: FastMCP) -> None:
    mcp.tool(description=DESCRIPTION)(list_status_events)
