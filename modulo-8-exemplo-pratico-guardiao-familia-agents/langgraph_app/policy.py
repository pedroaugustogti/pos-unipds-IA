"""Próximo evento sugerido por Status (determinístico)."""

from __future__ import annotations

from lib.task_status_workflow import EVENT_TARGET

# Status local → evento canônico da Fase C
STATUS_NEXT_EVENT: dict[str, str] = {
    "Todo": "claim",
    "In Progress": "open_pr",
    "Ready for Code Review": "start_review",
    "In Code Review": "approve_review",
    "Ready for Test": "start_test",
    "In Test": "test_passed",
    "In Pull Request": "merge_pr",
    "Done": "noop",
}


def suggested_event(board_status: str | None) -> str:
    status = (board_status or "Todo").strip()
    event = STATUS_NEXT_EVENT.get(status, "noop")
    if event != "noop" and event not in EVENT_TARGET:
        return "noop"
    return event


def status_after_event(event: str, current: str | None = None) -> str:
    if event in EVENT_TARGET:
        return EVENT_TARGET[event]
    return current or "Todo"
