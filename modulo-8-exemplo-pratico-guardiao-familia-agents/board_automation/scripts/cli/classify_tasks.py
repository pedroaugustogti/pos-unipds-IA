#!/usr/bin/env python3
"""Classifica tasks do backlog por agent_role para roteamento autônomo."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_bs = Path(__file__).resolve().parents[2] / "bootstrap.py"
_spec = importlib.util.spec_from_file_location("orch_bootstrap", _bs)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
_mod.setup()

import csv
from pathlib import Path

from lib.core.agent_registry import classify_task as classify

from lib.paths import MODULE_ROOT, REPO_ROOT

BACKLOG = REPO_ROOT / "07-planilhas" / "BACKLOG_PRIORIZADO_FINAL.csv"
from lib.paths import BOARD_MAPS_DIR

OUTPUT = BOARD_MAPS_DIR / "TASK_AGENT_MAP.csv"


def main() -> None:
    rows = list(csv.DictReader(BACKLOG.open(encoding="utf-8")))
    out_fields = [
        "id", "title", "agent_role", "agent_role_secondary",
        "track", "repo", "epic_id", "sprint", "priority_rank",
        "effort_sp", "rice", "wsjf", "status_baseline", "release_blocker",
        "match_reason",
    ]

    classified = []
    counts: dict[str, int] = {}

    for row in rows:
        role, secondary, _reason = classify(row)
        counts[role] = counts.get(role, 0) + 1
        reason = f"track={row['track']},repo={row['repo']},epic={row['epic_id']}"
        classified.append({
            "id": row["id"],
            "title": row["title"],
            "agent_role": role,
            "agent_role_secondary": secondary,
            "track": row["track"],
            "repo": row["repo"],
            "epic_id": row["epic_id"],
            "sprint": row["sprint"],
            "priority_rank": row["priority_rank"],
            "effort_sp": row["effort_sp"],
            "rice": row["rice"],
            "wsjf": row["wsjf"],
            "status_baseline": row["status_baseline"],
            "release_blocker": row["release_blocker"],
            "match_reason": reason,
        })

    with OUTPUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out_fields)
        w.writeheader()
        w.writerows(classified)

    print(f"Classificadas {len(classified)} tasks -> {OUTPUT}")
    for role, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {role}: {n}")


if __name__ == "__main__":
    main()
