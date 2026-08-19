#!/usr/bin/env python3
"""Entry point CrewAI — orquestrador de agentes + board GitHub."""

from __future__ import annotations

import argparse
import json
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


def run_crewai(sprint: int, dry_run: bool, mode: str) -> str:
    from crew import build_crew, build_hierarchical_crew, build_review_crew  # noqa: E402

    set_dry_run(dry_run)
    if mode == "review":
        crew = build_review_crew(dry_run)
    elif mode == "hierarchical":
        crew = build_hierarchical_crew(sprint, dry_run)
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
        choices=["deterministic", "crew", "hierarchical", "review"],
        default="deterministic",
        help="deterministic=sem LLM; crew/hierarchical=CrewAI; review=crew de revisores",
    )
    parser.add_argument("--phase", choices=["sprint", "review"], default="sprint")
    args = parser.parse_args()

    if args.dry_run:
        set_dry_run(True)

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
