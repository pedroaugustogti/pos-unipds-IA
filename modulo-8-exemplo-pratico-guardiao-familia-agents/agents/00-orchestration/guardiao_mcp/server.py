"""Fase B — MCP server Guardião Família (fachada sobre lib/*)."""

from __future__ import annotations

import sys
from pathlib import Path

# Pacote local + lib do módulo
_MODULE_ROOT = Path(__file__).resolve().parents[3]
if str(_MODULE_ROOT) not in sys.path:
    sys.path.insert(0, str(_MODULE_ROOT))

from lib.env_load import ensure_env  # noqa: E402

ensure_env()

from mcp.server.fastmcp import FastMCP  # noqa: E402

from guardiao_mcp.instructions import SERVER_INSTRUCTIONS  # noqa: E402
from guardiao_mcp.tools import (  # noqa: E402
    developer_implement,
    developer_review,
    emit_status_event,
    execute_agent_actuation_tool,
    hitl_guard_actuation,
    list_mcp_tools,
    list_status_events,
    on_status_event,
    orchestrator_enter_in_progress,
    qa_appium_suite_child,
    qa_appium_suite_parent,
    qa_db_cleanup,
    qa_db_seed,
    qa_validate,
    register_all,
)

mcp = FastMCP(
    "guardiao-familia-agents",
    instructions=SERVER_INSTRUCTIONS,
)

register_all(mcp)

__all__ = [
    "mcp",
    "main",
    "emit_status_event",
    "list_status_events",
    "on_status_event",
    "hitl_guard_actuation",
    "execute_agent_actuation_tool",
    "orchestrator_enter_in_progress",
    "developer_implement",
    "developer_review",
    "qa_validate",
    "qa_db_seed",
    "qa_db_cleanup",
    "qa_appium_suite_parent",
    "qa_appium_suite_child",
    "list_mcp_tools",
]


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
