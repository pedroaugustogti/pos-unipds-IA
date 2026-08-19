"""Roteamento de tasks por agent_role — scoring e seleção."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_CSV = ROOT / "TASK_AGENT_MAP.csv"

AGENT_ROLES = (
    "backend",
    "frontend-mobile",
    "frontend-web",
    "cloud-infra",
    "database",
    "devops-cicd",
    "qa",
    "stores-release",
)

AGENT_DEFAULT_REPO = {
    "backend": "guardiao-familia-api",
    "frontend-mobile": "guardiao-familia-parent",
    "frontend-web": "guardiao-familia-backoffice",
    "cloud-infra": "guardiao-familia-api",
    "database": "guardiao-familia-api",
    "devops-cicd": "guardiao-familia-api",
    "qa": "guardiao-familia-api",
    "stores-release": "guardiao-familia-parent",
}


def load_tasks() -> list[dict]:
    if not MAP_CSV.exists():
        raise FileNotFoundError(f"Execute classify_tasks.py. Falta {MAP_CSV}")
    return list(csv.DictReader(MAP_CSV.open(encoding="utf-8")))


def score_task(row: dict, agent: str, sprint_atual: int = 1) -> float:
    if row["agent_role"] != agent and row.get("agent_role_secondary") != agent:
        return -1.0
    if row["status_baseline"] == "done":
        return -1.0

    s = 1000 - int(row["priority_rank"])
    if row["repo"] == AGENT_DEFAULT_REPO.get(agent, ""):
        s += 50
    if int(row["sprint"]) == sprint_atual:
        s += 30
    if row["status_baseline"] == "todo":
        s += 20
    if row.get("agent_role_secondary") == agent and row["agent_role"] != agent:
        s -= 100
    return s


def pick_task(agent: str, sprint_atual: int = 1, exclude_ids: set[str] | None = None, sprint_only: bool = False) -> dict | None:
    exclude = exclude_ids or set()
    tasks = load_tasks()
    scored = []
    for t in tasks:
        if t["id"] in exclude:
            continue
        if sprint_only and int(t["sprint"]) != sprint_atual:
            continue
        s = score_task(t, agent, sprint_atual)
        if s > 0:
            scored.append((s, t))
    if not scored:
        return None
    scored.sort(key=lambda x: (-x[0], int(x[1]["priority_rank"])))
    return scored[0][1]


def pick_tasks_for_sprint(sprint: int, limit_per_agent: int = 1, sprint_only: bool = True) -> list[dict]:
    """Retorna até `limit_per_agent` tasks por agent_role para o sprint."""
    assigned: list[dict] = []
    used_ids: set[str] = set()

    for role in AGENT_ROLES:
        for _ in range(limit_per_agent):
            task = pick_task(role, sprint, exclude_ids=used_ids, sprint_only=sprint_only)
            if not task:
                break
            task = dict(task)
            task["assigned_agent"] = role
            assigned.append(task)
            used_ids.add(task["id"])

    assigned.sort(key=lambda t: int(t["priority_rank"]))
    return assigned


def slugify(title: str, max_len: int = 40) -> str:
    s = title.lower()
    repl = {"á": "a", "à": "a", "â": "a", "ã": "a", "é": "e", "ê": "e",
            "í": "i", "ó": "o", "ô": "o", "õ": "o", "ú": "u", "ç": "c"}
    for ch, r in repl.items():
        s = s.replace(ch, r)
    s = "".join(c if c.isalnum() else "-" for c in s)
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-")[:max_len]
