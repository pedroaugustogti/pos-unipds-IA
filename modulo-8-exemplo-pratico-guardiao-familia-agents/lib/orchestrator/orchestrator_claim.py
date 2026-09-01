"""Orchestrator: seleciona task Todo prioritária e emite orchestrator_enter_in_progress."""

from __future__ import annotations

from typing import Any

from board_automation.board.reviewer_pairs import normalize_creator_role
from board_automation.board.task_router import load_tasks, pick_priority_todo_task
from board_automation.board.task_status_workflow import build_event, resolve_status
from lib.gateway.gateway import emit_status_event


def orchestrator_enter_priority_todo(
    *,
    task_id: str = "",
    sprint: int = 1,
    sprint_only: bool = False,
    summary: str = "",
    dry_run: bool = True,
) -> dict[str, Any]:
    """
    Seleciona a task Todo de maior prioridade e emite orchestrator_enter_in_progress.

    Equivalente semântico ao claim, com from_agent=orchestrator.
    """
    task: dict[str, Any] | None
    if task_id:
        task = next((t for t in load_tasks() if t.get("id") == task_id), None)
        if not task:
            return {"ok": False, "error": f"Task {task_id} nao encontrada"}
        try:
            if resolve_status(str(task.get("board_status") or "Todo")) != "Todo":
                return {
                    "ok": False,
                    "error": f"Task {task_id} nao esta em Todo (status={task.get('board_status')})",
                }
        except ValueError:
            return {"ok": False, "error": f"Status invalido para {task_id}"}
    else:
        task = pick_priority_todo_task(sprint, sprint_only=sprint_only)
        if not task:
            return {
                "ok": False,
                "error": "Nenhuma task em Todo elegivel no board",
                "sprint": sprint,
                "sprint_only": sprint_only,
            }

    tid = str(task["id"])
    creator = normalize_creator_role(str(task.get("agent_role") or "backend"))
    emit_summary = summary or (
        f"Orchestrator claim prioritario: {tid} ({task.get('title', '')[:80]}) -> {creator}"
    )

    emit = emit_status_event(
        tid,
        "orchestrator_enter_in_progress",
        from_agent="orchestrator",
        summary=emit_summary,
        dry_run=dry_run,
        apply_board=True,
    )

    return {
        "ok": bool(emit.get("ok")),
        "task": {
            "id": tid,
            "title": task.get("title"),
            "agent_role": creator,
            "board_status": task.get("board_status"),
            "priority_rank": task.get("priority_rank"),
            "sprint": task.get("sprint"),
            "repo": task.get("repo"),
            "track": task.get("track"),
        },
        "event": "orchestrator_enter_in_progress",
        "target_status": "In Progress",
        "assigned_creator": creator,
        "creator_event_hint": build_event(creator, "In Progress"),
        "emit": emit,
        "dry_run": dry_run,
        "error": emit.get("error"),
    }
