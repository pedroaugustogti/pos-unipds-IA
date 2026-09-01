"""Próximo evento sugerido por status (role-based)."""

from __future__ import annotations

from board_automation.board.reviewer_pairs import QA_GATE_ROLE, normalize_creator_role, reviewer_for
from board_automation.board.task_status_workflow import EVENT_TARGET, build_event, is_known_event, merge_owner_for_task

STATUS_NEXT_TARGET: dict[str, str] = {
    "Todo": "In Progress",
    "In Progress": "Ready for Code Review",
    "Ready for Code Review": "In Code Review",
    "In Code Review": "Ready for Test",
    "Ready for Test": "In Test",
    "In Test": "In Pull Request",
    "In Pull Request": "Done",
    "Done": "noop",
}


def suggested_event(
    board_status: str | None,
    *,
    creator_role: str = "backend",
    track: str = "produto",
) -> str:
    status = (board_status or "Todo").strip()
    target = STATUS_NEXT_TARGET.get(status, "noop")
    if target == "noop":
        return "noop"
    creator = normalize_creator_role(creator_role)
    if status == "Todo":
        return "orchestrator_enter_in_progress"
    if status == "In Progress":
        return build_event(creator, "Ready for Code Review")
    if status == "Ready for Code Review":
        return build_event(reviewer_for(creator), "In Code Review")
    if status == "In Code Review":
        return build_event(reviewer_for(creator), "Ready for Test")
    if status == "Ready for Test":
        return build_event(QA_GATE_ROLE, "In Test")
    if status == "In Test":
        return build_event(QA_GATE_ROLE, "In Pull Request")
    if status == "In Pull Request":
        return build_event(merge_owner_for_task(track), "Done")
    event = build_event(creator, target)
    if event not in EVENT_TARGET:
        return "noop"
    return event


def status_after_event(event: str, current: str | None = None) -> str:
    if is_known_event(event):
        return EVENT_TARGET[event]
    return current or "Todo"
