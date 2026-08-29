"""IDs do piloto de autonomia (Fase 0) — consumido pelo autonomy_loop."""

from __future__ import annotations

from typing import Any

# Ver docs/autonomia/CONFIGURACAO_E_TECNOLOGIA.md (piloto em lib/pilot.py)
PILOT_TASK_IDS: frozenset[str] = frozenset({
    "T-P05-005",
    "T-P05-006",
    "T-P05-008",
    "T-P05-010",
    "T-I03-001",
    "T-I03-002",
    "T-I03-003",
    "T-P05-001",
})

PILOT_SPRINT = 3
PILOT_ROLES: tuple[str, ...] = (
    "frontend-mobile",
    "devops-cicd",
    "qa-gate",
)

# Subconjunto Fase 5 — intercalação supervisionada (3 tasks, 2 creators)
PHASE5_TASK_IDS: tuple[str, ...] = (
    "T-P05-005",  # frontend-mobile
    "T-I03-001",  # devops-cicd
    "T-P05-006",  # frontend-mobile (2ª — após liberar WIP da 1ª)
)

# Smoke: preferir tasks sem HIGH_HINTS (lib.model_tier) para economizar tokens
SMOKE_TASK_PRIORITY: tuple[str, ...] = (
    "T-P05-005",
    "T-P05-001",
    "T-I03-001",
    "T-P05-008",
    "T-P05-010",
    "T-I03-003",
)


def pick_smoke_task(*, prefer_id: str | None = None) -> dict[str, Any]:
    """Escolhe task piloto sem hint high (nao usa modelo caro no smoke)."""
    from lib.core.model_tier import is_high_risk
    from board_automation.board.task_router import load_tasks

    by_id = {t["id"]: t for t in load_tasks(refresh_board_status=False)}

    if prefer_id:
        task = by_id.get(prefer_id)
        if not task:
            raise ValueError(f"Task {prefer_id} nao encontrada no board")
        if is_high_risk(task):
            raise ValueError(
                f"Task {prefer_id} tem hint high — smoke usa apenas tasks low "
                f"(HIGH_HINTS em lib.model_tier)"
            )
        return task

    for tid in SMOKE_TASK_PRIORITY:
        if tid not in PILOT_TASK_IDS:
            continue
        task = by_id.get(tid)
        if task and not is_high_risk(task):
            return task

    for tid in sorted(PILOT_TASK_IDS):
        task = by_id.get(tid)
        if task and not is_high_risk(task):
            return task

    raise ValueError("Nenhuma task piloto sem hint high disponivel para smoke")
