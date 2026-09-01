"""Seleção de tasks para smoke tests (sem fila worker)."""

from __future__ import annotations

from typing import Any

SMOKE_TASK_PRIORITY: tuple[str, ...] = (
    "T-P3-009",
    "T-P05-005",
    "T-P05-001",
    "T-I03-001",
)


def pick_smoke_task(*, prefer_id: str | None = None) -> dict[str, Any]:
    from lib.core.model_tier import is_high_risk
    from board_automation.board.task_router import load_tasks

    by_id = {t["id"]: t for t in load_tasks(refresh_board_status=False)}

    if prefer_id:
        task = by_id.get(prefer_id)
        if not task:
            raise ValueError(f"Task {prefer_id} nao encontrada no board")
        if is_high_risk(task):
            raise ValueError(f"Task {prefer_id} tem hint high — smoke usa apenas tasks low")
        return task

    for tid in SMOKE_TASK_PRIORITY:
        task = by_id.get(tid)
        if task and not is_high_risk(task):
            return task

    for task in by_id.values():
        if task.get("board_status") == "Todo" and not is_high_risk(task):
            return task

    raise ValueError("Nenhuma task low-hint disponivel para smoke")
