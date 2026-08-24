#!/usr/bin/env python3
"""Classifica tasks do backlog por agent_role para roteamento autônomo."""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT.parent / "07-planilhas" / "BACKLOG_PRIORIZADO_FINAL.csv"
OUTPUT = ROOT / "TASK_AGENT_MAP.csv"

QA_PATTERN = re.compile(r"\b(teste|test|e2e|spec|qa|coverage)\b", re.I)
DB_PATTERN = re.compile(r"\b(migration|postgres|redis|schema|rds|elasticache)\b", re.I)
DEVOPS_PATTERN = re.compile(
    r"\b(ci/?cd|pipeline|github actions|sentry|observabilidade|workflow|alertas)\b", re.I
)

DEVOPS_EPICS = {"E-I02", "E-I03"}
DB_EPIC = "E-I04"
INFRA_EPICS = {"E-I01", "E-I05", "E-I06"}

MOBILE_REPOS = {"guardiao-familia-parent", "guardiao-familia-child"}
WEB_REPOS = {"guardiao-familia-backoffice", "guardiao-familia-site"}


def classify(row: dict) -> tuple[str, str]:
    track = row["track"]
    epic = row["epic_id"]
    repo = row["repo"]
    title = row["title"]

    if track == "stores":
        sec = "frontend-mobile" if repo in MOBILE_REPOS else ""
        return "stores-release", sec

    if QA_PATTERN.search(title):
        if repo in MOBILE_REPOS:
            return "qa", "frontend-mobile"
        if repo == "guardiao-familia-api":
            return "qa", "backend"
        return "qa", ""

    if epic == DB_EPIC or DB_PATTERN.search(title):
        sec = "cloud-infra" if track == "infraestrutura" else "backend"
        return "database", sec

    if epic in DEVOPS_EPICS or DEVOPS_PATTERN.search(title):
        return "devops-cicd", ""

    if track == "infraestrutura" or epic in INFRA_EPICS:
        sec = "database" if DB_PATTERN.search(title) else ""
        return "cloud-infra", sec

    if repo in MOBILE_REPOS:
        sec = "qa" if QA_PATTERN.search(title) else ""
        return "frontend-mobile", sec

    if repo in WEB_REPOS:
        return "frontend-web", ""

    if repo == "guardiao-familia-api" and track == "produto":
        sec = "qa" if "integração" in title.lower() else ""
        return "backend", sec

    return "backend", ""


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
        role, secondary = classify(row)
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
