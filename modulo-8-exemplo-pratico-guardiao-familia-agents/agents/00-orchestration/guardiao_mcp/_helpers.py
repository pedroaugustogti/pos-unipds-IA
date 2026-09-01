"""Helpers compartilhados entre tools MCP."""

from __future__ import annotations

from typing import Any

from board_automation.board.task_router import load_tasks


def task_by_id(task_id: str) -> dict[str, Any] | None:
    return next((t for t in load_tasks() if t.get("id") == task_id), None)
