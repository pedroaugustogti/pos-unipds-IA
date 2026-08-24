"""Roteamento de tasks por agent_role — scoring e seleção via Status do board JSON."""

from __future__ import annotations

import csv
from pathlib import Path

from lib.local_board import status_map
from lib.task_status_workflow import resolve_status

ROOT = Path(__file__).resolve().parents[1]
MAP_CSV = ROOT / "TASK_AGENT_MAP.csv"

from lib.reviewer_pairs import normalize_creator_role

AGENT_ROLES = (
    "backend",
    "frontend-mobile",
    "frontend-web",
    "cloud-infra",
    "database",
    "devops-cicd",
    "qa-author",
    "qa-gate",
    "stores-release",
)

AGENT_DEFAULT_REPO = {
    "backend": "guardiao-familia-api",
    "frontend-mobile": "guardiao-familia-parent",
    "frontend-web": "guardiao-familia-backoffice",
    "cloud-infra": "guardiao-familia-api",
    "database": "guardiao-familia-api",
    "devops-cicd": "guardiao-familia-api",
    "qa-author": "guardiao-familia-api",
    "qa-gate": "guardiao-familia-api",
    "qa": "guardiao-familia-api",  # legado CSV
    "stores-release": "guardiao-familia-parent",
}

# Criadores só claimem cards em Todo (fonte: github-project-2-import.json → fields.Status)
CREATOR_CLAIMABLE_STATUSES = frozenset({"Todo"})

# Filas por papel (pipeline — não confundir com criação de harness)
ROLE_QUEUE_STATUSES: dict[str, frozenset[str]] = {
    "qa-gate": frozenset({"Ready for Test", "In Test"}),
    "devops-cicd": frozenset({"In Pull Request"}),
    "stores-release": frozenset({"Todo", "In Pull Request"}),
}


def load_tasks(*, refresh_board_status: bool = True) -> list[dict]:
    if not MAP_CSV.exists():
        raise FileNotFoundError(f"Execute classify_tasks.py. Falta {MAP_CSV}")
    rows = list(csv.DictReader(MAP_CSV.open(encoding="utf-8")))
    if not refresh_board_status:
        for row in rows:
            row.setdefault("board_status", "Todo")
        return rows

    statuses = status_map()
    for row in rows:
        raw = statuses.get(row["id"], row.get("status_baseline") or "Todo")
        try:
            row["board_status"] = resolve_status(str(raw))
        except ValueError:
            # Baseline legado (todo/partial/done) ou valor desconhecido
            baseline = str(row.get("status_baseline") or "todo").lower()
            row["board_status"] = "Done" if baseline == "done" else "Todo"
    return rows


def _map_role(agent: str) -> str:
    return normalize_creator_role(agent)


def _csv_roles_for_agent(agent: str) -> set[str]:
    """Roles no CSV que este agente pode claimar como criador."""
    a = _map_role(agent)
    if a == "qa-author":
        return {"qa", "qa-author"}
    return {a}


def _claimable_statuses(agent: str) -> frozenset[str]:
    """Status do board a partir dos quais o agent pode selecionar/claim."""
    a = _map_role(agent)
    if a == "qa-gate":
        return ROLE_QUEUE_STATUSES["qa-gate"]
    if a == "stores-release":
        return ROLE_QUEUE_STATUSES["stores-release"]
    if a == "devops-cicd":
        return CREATOR_CLAIMABLE_STATUSES | ROLE_QUEUE_STATUSES["devops-cicd"]
    return CREATOR_CLAIMABLE_STATUSES


def _in_stage_queue(row: dict, agent: str, board_status: str) -> bool:
    """Filas de workflow (QA-gate / merge) independentes do agent_role do CSV."""
    a = _map_role(agent)
    if a == "qa-gate" and board_status in ROLE_QUEUE_STATUSES["qa-gate"]:
        return True
    if board_status != "In Pull Request":
        return False
    track = row.get("track") or ""
    if a == "stores-release" and track == "stores":
        return True
    if a == "devops-cicd" and track != "stores":
        return True
    return False


def score_task(row: dict, agent: str, sprint_atual: int = 1) -> float:
    agent = _map_role(agent)
    board_status = row.get("board_status") or "Todo"
    if board_status == "Done":
        return -1.0

    csv_roles = _csv_roles_for_agent(agent)
    role_match = (
        row["agent_role"] in csv_roles
        or row.get("agent_role_secondary") in csv_roles
        or row["agent_role"] == agent
        or row.get("agent_role_secondary") == agent
    )
    # qa-gate nunca claima Todo de harness — só fila de teste
    if agent == "qa-gate":
        role_match = False
    if role_match:
        if board_status not in _claimable_statuses(agent):
            return -1.0
    elif not _in_stage_queue(row, agent, board_status):
        return -1.0

    s = 1000 - int(row["priority_rank"])
    if row["repo"] == AGENT_DEFAULT_REPO.get(agent, ""):
        s += 50
    if int(row["sprint"]) == sprint_atual:
        s += 30
    if board_status == "Todo":
        s += 20
    if board_status == "Ready for Test" and agent == "qa-gate":
        s += 40
    if board_status == "In Pull Request" and agent in ("devops-cicd", "stores-release"):
        s += 40
    if row.get("agent_role_secondary") == agent and row["agent_role"] != agent:
        s -= 100
    return s


def pick_task(
    agent: str,
    sprint_atual: int = 1,
    exclude_ids: set[str] | None = None,
    sprint_only: bool = False,
) -> dict | None:
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


def pick_tasks_for_sprint(
    sprint: int, limit_per_agent: int = 1, sprint_only: bool = True
) -> list[dict]:
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
    repl = {
        "á": "a",
        "à": "a",
        "â": "a",
        "ã": "a",
        "é": "e",
        "ê": "e",
        "í": "i",
        "ó": "o",
        "ô": "o",
        "õ": "o",
        "ú": "u",
        "ç": "c",
    }
    for ch, r in repl.items():
        s = s.replace(ch, r)
    s = "".join(c if c.isalnum() else "-" for c in s)
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-")[:max_len]
