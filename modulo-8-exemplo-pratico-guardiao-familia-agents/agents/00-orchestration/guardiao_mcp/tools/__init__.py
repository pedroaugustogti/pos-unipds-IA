"""Registro e reexportação das 14 tools MCP."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP

_TOOL_MODULES = (
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
)


def register_all(mcp: FastMCP) -> None:
    import importlib

    for name in _TOOL_MODULES:
        mod = importlib.import_module(f"guardiao_mcp.tools.{name}")
        mod.register(mcp)


from .developer_implement import developer_implement  # noqa: E402
from .developer_review import developer_review  # noqa: E402
from .emit_status_event import emit_status_event  # noqa: E402
from .execute_agent_actuation_tool import execute_agent_actuation_tool  # noqa: E402
from .hitl_guard_actuation import hitl_guard_actuation  # noqa: E402
from .list_mcp_tools import list_mcp_tools  # noqa: E402
from .list_status_events import list_status_events  # noqa: E402
from .on_status_event import on_status_event  # noqa: E402
from .orchestrator_enter_in_progress import orchestrator_enter_in_progress  # noqa: E402
from .qa_appium_suite_child import qa_appium_suite_child  # noqa: E402
from .qa_appium_suite_parent import qa_appium_suite_parent  # noqa: E402
from .qa_db_cleanup import qa_db_cleanup  # noqa: E402
from .qa_db_seed import qa_db_seed  # noqa: E402
from .qa_validate import qa_validate  # noqa: E402

__all__ = [
    "register_all",
    *list(_TOOL_MODULES),
]
