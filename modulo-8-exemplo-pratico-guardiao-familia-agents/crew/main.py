#!/usr/bin/env python3
"""Entry point CrewAI — orquestrador de agentes + board GitHub."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

CREW_DIR = Path(__file__).resolve().parent
ROOT = CREW_DIR.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(CREW_DIR))

from lib.board_client import claim_task  # noqa: E402
from lib.task_router import pick_tasks_for_sprint, slugify  # noqa: E402
from tools.board_tools import set_dry_run  # noqa: E402


def run_deterministic(sprint: int, limit: int, dry_run: bool) -> dict:
    """Modo sem LLM: planeja + claim direto (util para CI/dry-run)."""
    assignments = pick_tasks_for_sprint(sprint, limit)
    claims = []
    for task in assignments:
        agent = task["assigned_agent"]
        branch = f"feat/{task['id']}-{slugify(task['title'])}"
        claims.append(claim_task(task, agent, branch, dry_run=dry_run))

    report = {
        "mode": "deterministic",
        "sprint": sprint,
        "assignments_count": len(assignments),
        "claims": claims,
    }

    out_dir = CREW_DIR / "output"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "sprint_claims.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    return report


def run_events_deterministic(dry_run: bool = True, limit: int = 8) -> dict:
    """Orquestra eventos: idle → claim/dispatch; demo blocker apos 3 bugs."""
    from lib.event_orchestrator import (  # noqa: E402
        list_idle_agents,
        load_runtime,
        notify_status_change,
        process_dispatch_queue,
        record_bug,
        release_agent,
        save_runtime,
    )

    assignments = pick_tasks_for_sprint(1, limit_per_agent=1, sprint_only=False)[:limit]
    events = []
    for task in assignments:
        release_agent(task["assigned_agent"])
        note = notify_status_change(
            task["id"],
            "claim",
            from_status="Todo",
            to_status="In Progress",
            dry_run=dry_run,
        )
        events.append({
            "task_id": task["id"],
            "assigned_agent": task["assigned_agent"],
            "notification": note,
        })

    demo_task = assignments[0]["id"] if assignments else "T-P05-001"
    rt = load_runtime()
    rt.setdefault("bug_counts", {})[demo_task] = {
        "count": 0, "history": [], "skill": None, "blocker": False,
    }
    rt["blockers"] = [b for b in rt.get("blockers", []) if b.get("task_id") != demo_task]
    save_runtime(rt)

    bugs = [
        record_bug(demo_task, f"Bug recorrente #{i + 1} (demo orchestrator)", dry_run=dry_run)
        for i in range(3)
    ]

    drained = process_dispatch_queue(limit=5)
    runtime = load_runtime()
    report = {
        "mode": "events",
        "dry_run": dry_run,
        "idle_after": list_idle_agents(),
        "events": events,
        "bugs_demo": bugs,
        "dispatched_queue": drained,
        "blockers": runtime.get("blockers") or [],
        "event_log_tail": (runtime.get("event_log") or [])[-10:],
    }
    out = CREW_DIR / "output" / "events_orchestration.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def run_crewai(sprint: int, dry_run: bool, mode: str) -> str:
    from crew import (  # noqa: E402
        build_crew,
        build_events_crew,
        build_hierarchical_crew,
        build_review_crew,
    )

    set_dry_run(dry_run)
    if mode == "review":
        crew = build_review_crew(dry_run)
    elif mode == "hierarchical":
        crew = build_hierarchical_crew(sprint, dry_run)
    elif mode == "events":
        crew = build_events_crew(dry_run)
    else:
        crew = build_crew(sprint, dry_run)
    result = crew.kickoff(inputs={"sprint": sprint})
    return str(result)


def main() -> int:
    parser = argparse.ArgumentParser(description="CrewAI Orchestrator — Guardiao Familia Board")
    parser.add_argument("--sprint", type=int, default=1)
    parser.add_argument("--limit", type=int, default=1, help="Tasks por agente (modo deterministic)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--mode",
        choices=["deterministic", "crew", "hierarchical", "review", "events"],
        default="deterministic",
        help="deterministic|crew|hierarchical|review|events",
    )
    parser.add_argument("--phase", choices=["sprint", "review"], default="sprint")
    parser.add_argument(
        "--events-llm",
        action="store_true",
        help="Com --mode events: usa CrewAI LLM em vez do orquestrador deterministico",
    )
    args = parser.parse_args()

    if args.dry_run:
        set_dry_run(True)

    if args.mode == "events" and not args.events_llm and os.environ.get("CREWAI_EVENTS_LLM") != "1":
        report = run_events_deterministic(dry_run=True)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if args.mode == "deterministic" and args.phase == "review":
        from lib.board_client import finalize_pr_review  # noqa: E402
        from lib.reviewer_pairs import CREATOR_ROLES, reviewer_for  # noqa: E402
        from lib.task_router import load_tasks  # noqa: E402

        results = []
        for role in CREATOR_ROLES:
            tasks = [t for t in load_tasks() if t["agent_role"] == role][:1]
            for task in tasks:
                results.append(finalize_pr_review(
                    task, role, reviewer_for(role), "approved",
                    "Review deterministico dry-run.", dry_run=args.dry_run,
                ))
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0

    if args.mode == "deterministic":
        report = run_deterministic(args.sprint, args.limit, args.dry_run)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    try:
        result = run_crewai(args.sprint, args.dry_run, args.mode)
        print(result)
        return 0
    except ImportError as e:
        print(f"CrewAI nao instalado: {e}", file=sys.stderr)
        print("pip install -r crew/requirements.txt", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
