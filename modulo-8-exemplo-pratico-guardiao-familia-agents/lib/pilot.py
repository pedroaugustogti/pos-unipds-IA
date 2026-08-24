"""IDs do piloto de autonomia (Fase 0) — consumido pelo autonomy_loop."""

from __future__ import annotations

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
