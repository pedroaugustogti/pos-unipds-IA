"""Layout de output por ticket: `{task_id}/{agent_role}-({cycle})/`."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

from lib.paths import HANDOFF_DIR, RUNTIME_OUTPUT_DIR
from board_automation.board.task_status_workflow import parse_event

TICKET_ID_RE = re.compile(r"^T-P\d+-\d+$", re.IGNORECASE)

# Retrocesso para In Progress (role-based return ou nomes legados em histórico)
_LEGACY_REWORK = frozenset({"request_changes", "test_failed_bug"})
IMPLEMENTER_ROLES = frozenset(
    {
        "backend",
        "frontend-mobile",
        "frontend-web",
        "cloud-infra",
        "database",
        "devops-cicd",
        "qa-author",
        "stores-release",
    }
)


def is_ticket_id(value: str) -> bool:
    return bool(TICKET_ID_RE.match(str(value or "").strip()))


def normalize_agent_role(role: str) -> str:
    return str(role or "").strip().lower()


def agent_cycle_slug(agent_role: str, cycle: int) -> str:
    role = normalize_agent_role(agent_role)
    n = max(1, int(cycle))
    return f"{role}-({n})"


def ticket_dir(task_id: str) -> Path:
    tid = str(task_id).strip()
    if not is_ticket_id(tid):
        raise ValueError(f"task_id inválido para layout por ticket: {task_id!r}")
    path = RUNTIME_OUTPUT_DIR / tid
    path.mkdir(parents=True, exist_ok=True)
    return path


def ticket_seed_cache_path(task_id: str) -> Path:
    return ticket_dir(task_id) / "seed-cache.json"


def ticket_handoff_path(task_id: str) -> Path:
    return ticket_dir(task_id) / "handoff.json"


def resolve_handoff_path(task_id: str) -> Path:
    """Caminho canônico do handoff (`{ticket}/handoff.json`)."""
    return ticket_handoff_path(task_id)


def _is_rework_event(event: str) -> bool:
    if event in _LEGACY_REWORK:
        return True
    parsed = parse_event(event)
    return bool(parsed and parsed.get("return") and parsed.get("status") == "In Progress")


def _is_qa_start_test(event: str) -> bool:
    if event == "start_test":
        return True
    parsed = parse_event(event)
    return bool(
        parsed
        and parsed.get("agent_role") == "qa-gate"
        and parsed.get("status") == "In Test"
        and not parsed.get("return")
    )


def _is_reviewer_start_review(event: str, role: str, *, from_agent: str = "") -> bool:
    if event == "start_review":
        return not from_agent or normalize_agent_role(from_agent) == role
    parsed = parse_event(event)
    return bool(
        parsed
        and normalize_agent_role(str(parsed.get("agent_role") or "")) == role
        and parsed.get("status") == "In Code Review"
        and not parsed.get("return")
    )


def resolve_agent_cycle(handoff: dict[str, Any] | None, agent_role: str, *, event: str = "") -> int:
    """Ciclo de trabalho do agente (1 = primeira rodada no ticket)."""
    role = normalize_agent_role(agent_role)
    history = list((handoff or {}).get("history") or [])

    if role == "qa-gate":
        n = sum(1 for h in history if _is_qa_start_test(str(h.get("event") or "")))
        if _is_qa_start_test(event):
            n += 1
        return max(1, n)

    if role.endswith("-reviewer"):
        n = sum(
            1
            for h in history
            if _is_reviewer_start_review(
                str(h.get("event") or ""),
                role,
                from_agent=str(h.get("from_agent") or ""),
            )
        )
        if _is_reviewer_start_review(event, role):
            n += 1
        return max(1, n if n else 1)

    rework = sum(1 for h in history if _is_rework_event(str(h.get("event") or "")))
    if _is_rework_event(event):
        pass
    return max(1, 1 + rework)


def agent_cycle_dir(
    task_id: str,
    agent_role: str,
    *,
    cycle: int | None = None,
    handoff: dict[str, Any] | None = None,
    event: str = "",
) -> Path:
    if cycle is None:
        if handoff is None:
            handoff = _read_json(resolve_handoff_path(task_id))
        cycle = resolve_agent_cycle(handoff, agent_role, event=event)
    path = ticket_dir(task_id) / agent_cycle_slug(agent_role, cycle)
    path.mkdir(parents=True, exist_ok=True)
    return path


def agent_evidence_dir(
    task_id: str,
    agent_role: str,
    *,
    cycle: int | None = None,
    handoff: dict[str, Any] | None = None,
    event: str = "",
) -> Path:
    path = agent_cycle_dir(
        task_id, agent_role, cycle=cycle, handoff=handoff, event=event
    ) / "evidence"
    path.mkdir(parents=True, exist_ok=True)
    return path


def qa_evidence_dir(
    task_id: str,
    *,
    cycle: int | None = None,
    handoff: dict[str, Any] | None = None,
    event: str = "",
) -> Path:
    return agent_evidence_dir(
        task_id, "qa-gate", cycle=cycle, handoff=handoff, event=event
    )


def agent_actions_path(
    task_id: str,
    agent_role: str,
    *,
    cycle: int | None = None,
    handoff: dict[str, Any] | None = None,
    event: str = "",
) -> Path:
    return agent_cycle_dir(
        task_id, agent_role, cycle=cycle, handoff=handoff, event=event
    ) / "actions.json"


def langgraph_run_path(task_id: str, agent_role: str = "orchestrator", *, cycle: int = 1) -> Path:
    return agent_cycle_dir(task_id, agent_role, cycle=cycle) / "langgraph-run.json"


def write_ticket_handoff(task_id: str, payload: dict[str, Any]) -> Path:
    """Grava handoff canônico em `{ticket}/handoff.json`."""
    path = ticket_handoff_path(task_id)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def snapshot_handoff_for_agent(
    task_id: str,
    payload: dict[str, Any],
    *,
    agent_role: str,
    event: str = "",
) -> Path:
    """Cópia do handoff no ciclo do agente que está entregando trabalho."""
    cycle = resolve_agent_cycle(payload, agent_role, event=event)
    dest = agent_cycle_dir(task_id, agent_role, cycle=cycle) / "handoff-snapshot.json"
    dest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return dest


def append_agent_action(
    task_id: str,
    agent_role: str,
    step: dict[str, Any],
    *,
    cycle: int | None = None,
    handoff: dict[str, Any] | None = None,
    event: str = "",
) -> Path:
    """Acumula passos ReAct no ciclo do agente (`actions.json`)."""
    if handoff is None:
        handoff = _read_json(resolve_handoff_path(task_id))
    path = agent_actions_path(
        task_id, agent_role, cycle=cycle, handoff=handoff, event=event
    )
    data: dict[str, Any]
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        resolved = cycle or resolve_agent_cycle(handoff, agent_role, event=event)
        data = {
            "task_id": task_id,
            "agent": normalize_agent_role(agent_role),
            "cycle": resolved,
            "cycle_dir": agent_cycle_slug(agent_role, resolved),
            "steps": [],
        }
    steps = list(data.get("steps") or [])
    steps.append(step)
    data["steps"] = steps
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def list_ticket_ids() -> list[str]:
    ids: set[str] = set()
    if HANDOFF_DIR.is_dir():
        for p in HANDOFF_DIR.glob("T-P*.json"):
            ids.add(p.stem.upper())
    if RUNTIME_OUTPUT_DIR.is_dir():
        for p in RUNTIME_OUTPUT_DIR.iterdir():
            if p.is_dir() and is_ticket_id(p.name):
                ids.add(p.name.upper())
    return sorted(ids)


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def migrate_legacy_qa_evidence(task_id: str, src: Path, *, cycle: int = 1) -> Path | None:
    """Move pasta legada de evidências QA para `{ticket}/qa-gate-({cycle})/evidence/`."""
    if not src.is_dir():
        return None
    dest = qa_evidence_dir(task_id, cycle=cycle)
    if dest.exists() and any(dest.iterdir()):
        return dest
    if src.resolve() == dest.resolve():
        return dest
    shutil.copytree(src, dest, dirs_exist_ok=True)
    return dest
