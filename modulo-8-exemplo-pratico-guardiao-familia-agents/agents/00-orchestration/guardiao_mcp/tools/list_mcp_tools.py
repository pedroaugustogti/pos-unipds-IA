"""Tool: list_mcp_tools — catálogo meta do servidor."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from guardiao_mcp.contract import ok

DESCRIPTION = """\
**Quando:** início de sessão ou dúvida sobre catálogo.

**Faz:** lista as 14 tools (gateway, phase, orchestrator, qa_mobile, meta) e flag writes.

**Grupos v2:** gateway (5) · phase (3) · orchestrator (1) · qa_mobile (4) · meta (1).
"""

TOOL_CATALOG = [
    {"name": "emit_status_event", "group": "gateway", "writes": True},
    {"name": "list_status_events", "group": "gateway", "writes": False},
    {"name": "on_status_event", "group": "gateway", "writes": False},
    {"name": "hitl_guard_actuation", "group": "gateway", "writes": True},
    {"name": "developer_implement", "group": "phase", "writes": True},
    {"name": "developer_review", "group": "phase", "writes": True},
    {"name": "qa_validate", "group": "phase", "writes": True},
    {"name": "execute_agent_actuation_tool", "group": "gateway", "writes": True},
    {"name": "orchestrator_enter_in_progress", "group": "orchestrator", "writes": True},
    {"name": "qa_db_seed", "group": "qa_mobile", "writes": True},
    {"name": "qa_db_cleanup", "group": "qa_mobile", "writes": True},
    {"name": "qa_appium_suite_parent", "group": "qa_mobile", "writes": True},
    {"name": "qa_appium_suite_child", "group": "qa_mobile", "writes": True},
    {"name": "list_mcp_tools", "group": "meta", "writes": False},
]


def list_mcp_tools() -> str:
    """Catálogo de tools deste servidor MCP."""
    return ok({"count": len(TOOL_CATALOG), "tools": TOOL_CATALOG})


def register(mcp: FastMCP) -> None:
    mcp.tool(description=DESCRIPTION)(list_mcp_tools)
