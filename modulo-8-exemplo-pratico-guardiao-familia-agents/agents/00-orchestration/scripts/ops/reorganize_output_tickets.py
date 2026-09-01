#!/usr/bin/env python3
"""Migra output legado para layout por ticket: `{task_id}/{agent_role}-({cycle})/`."""

from __future__ import annotations

import importlib.util
import json
import shutil
from collections import defaultdict
from pathlib import Path

_bs = Path(__file__).resolve().parents[2] / "bootstrap.py"
_spec = importlib.util.spec_from_file_location("orch_bootstrap", _bs)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
_mod.setup()

from lib.paths import (  # noqa: E402
    EVIDENCE_DIR,
    HANDOFF_DIR,
    LANGGRAPH_DIR,
    OBSERVABILITY_DIR,
    QA_EVIDENCE_DIR,
    QA_SEED_CACHE_DIR,
)
from lib.ticket_output import (  # noqa: E402
    agent_cycle_dir,
    is_ticket_id,
    qa_evidence_dir,
    resolve_agent_cycle,
    ticket_dir,
    ticket_handoff_path,
    ticket_seed_cache_path,
    write_ticket_handoff,
)


def _read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _move_handoff(task_id: str, moved: list[str]) -> None:
    legacy = HANDOFF_DIR / f"{task_id}.json"
    dest = ticket_handoff_path(task_id)
    if legacy.is_file() and not dest.is_file():
        payload = _read_json(legacy)
        if payload:
            write_ticket_handoff(task_id, payload)
            moved.append(f"handoffs/{task_id}.json -> {task_id}/handoff.json")
    elif legacy.is_file() and dest.is_file():
        moved.append(f"handoffs/{task_id}.json (mantido espelho legado)")


def _move_qa_evidence(task_id: str, moved: list[str]) -> None:
    handoff = _read_json(ticket_handoff_path(task_id)) or _read_json(HANDOFF_DIR / f"{task_id}.json")
    cycle = resolve_agent_cycle(handoff, "qa-gate")
    dest = qa_evidence_dir(task_id, cycle=cycle)

    for src_root in (EVIDENCE_DIR / task_id, QA_EVIDENCE_DIR / task_id):
        if not src_root.is_dir():
            continue
        for item in src_root.rglob("*"):
            if item.is_file():
                rel = item.relative_to(src_root)
                target = dest / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    shutil.copy2(item, target)
        moved.append(f"{src_root.name}/{task_id}/ -> {task_id}/{dest.parent.name}/evidence/")


def _distribute_task_history(task_id: str, moved: list[str]) -> None:
    tasks_json = OBSERVABILITY_DIR / "tasks" / f"{task_id}.json"
    data = _read_json(tasks_json)
    if not data:
        return
    handoff = _read_json(ticket_handoff_path(task_id)) or _read_json(HANDOFF_DIR / f"{task_id}.json")
    buckets: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for step in data.get("steps") or []:
        agent = str(step.get("agent") or "unknown")
        event = str(step.get("event") or "")
        cycle = resolve_agent_cycle(handoff, agent, event=event)
        buckets[(agent, cycle)].append(step)

    for (agent, cycle), steps in buckets.items():
        cycle_dir = agent_cycle_dir(task_id, agent, cycle=cycle)
        actions_path = cycle_dir / "actions.json"
        actions_path.write_text(
            json.dumps(
                {
                    "task_id": task_id,
                    "agent": agent,
                    "cycle": cycle,
                    "cycle_dir": cycle_dir.name,
                    "steps": steps,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        from board_automation.board.task_action_history import render_task_history_page

        payload = {
            "task_id": task_id,
            "title": data.get("title") or task_id,
            "final_status": data.get("final_status"),
            "steps": steps,
        }
        render_task_history_page(payload, html_path=cycle_dir / "action-history.html")
        moved.append(f"observability/tasks/{task_id}.json -> {cycle_dir.name}/actions.json")


def _move_seed_cache(task_id: str, moved: list[str]) -> None:
    legacy = QA_SEED_CACHE_DIR / f"{task_id}.json"
    dest = ticket_seed_cache_path(task_id)
    if legacy.is_file() and not dest.is_file():
        shutil.copy2(legacy, dest)
        moved.append(f"mobile/qa_seed_cache/{task_id}.json -> {task_id}/seed-cache.json")


def _move_langgraph(task_id: str, moved: list[str]) -> None:
    legacy = LANGGRAPH_DIR / f"{task_id}.json"
    if not legacy.is_file():
        return
    from lib.ticket_output import langgraph_run_path

    dest = langgraph_run_path(task_id, "orchestrator", cycle=1)
    if not dest.is_file():
        shutil.copy2(legacy, dest)
        moved.append(f"langgraph/{task_id}.json -> {task_id}/orchestrator-(1)/langgraph-run.json")


def _discover_ticket_ids() -> list[str]:
    ids: set[str] = set()
    if HANDOFF_DIR.is_dir():
        ids.update(p.stem.upper() for p in HANDOFF_DIR.glob("T-P*.json"))
    for root in (EVIDENCE_DIR, QA_EVIDENCE_DIR, LANGGRAPH_DIR):
        if root.is_dir():
            ids.update(p.name.upper() for p in root.iterdir() if p.is_dir() and is_ticket_id(p.name))
    obs = OBSERVABILITY_DIR / "tasks"
    if obs.is_dir():
        ids.update(p.stem.upper() for p in obs.glob("T-P*.json"))
    return sorted(ids)


def main() -> int:
    moved: list[str] = []
    for task_id in _discover_ticket_ids():
        ticket_dir(task_id)
        _move_handoff(task_id, moved)
        _move_qa_evidence(task_id, moved)
        _move_seed_cache(task_id, moved)
        _distribute_task_history(task_id, moved)
        _move_langgraph(task_id, moved)

    print(f"Migração ticket layout: {len(moved)} operações")
    for line in moved:
        print(f"  - {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
