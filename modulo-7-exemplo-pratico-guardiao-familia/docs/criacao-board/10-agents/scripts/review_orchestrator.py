#!/usr/bin/env python3
"""Orquestrador de revisores: finaliza PR e atualiza board."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.board_client import finalize_pr_review, find_pr_for_task  # noqa: E402
from lib.reviewer_pairs import CREATOR_ROLES, CREATOR_TO_REVIEWER, reviewer_for  # noqa: E402
from lib.task_router import load_tasks, pick_task  # noqa: E402

REVIEW_TEMPLATE = ROOT / "templates" / "REVIEW_TEMPLATE.md"
SKILLS = ROOT / "skills"


def render_review_body(task_id: str, creator: str, verdict: str) -> str:
    tpl = REVIEW_TEMPLATE.read_text(encoding="utf-8")
    reviewer = CREATOR_TO_REVIEWER[creator]
    board = "Done" if verdict == "approved" else "In Progress"
    for k, v in {
        "{task_id}": task_id,
        "{creator_role}": creator,
        "{reviewer_role}": reviewer,
        "{verdict}": verdict,
        "{review_date}": datetime.now(timezone.utc).isoformat(),
        "{board_status}": board,
    }.items():
        tpl = tpl.replace(k, v)
    return tpl


def build_review_instructions(task: dict, creator: str, verdict: str = "approved") -> str:
    reviewer = reviewer_for(creator)
    skill = SKILLS / reviewer / "SKILL.md"
    pr = find_pr_for_task(task["repo"], task["id"], dry_run=True)

    return f"""# Instrucoes de review — {reviewer}

## Task
- **ID:** {task['id']}
- **Titulo:** {task['title']}
- **Criador:** {creator}
- **Repo:** {task['repo']}

## Skill revisor
Leia: `{skill}`

## Passos
1. Revisar diff do PR (buscar por `{task['id']}`)
2. Aplicar checklist da skill revisor
3. Preencher review abaixo
4. Executar finalize:
   `python scripts/review_orchestrator.py --creator {creator} --task {task['id']} --verdict {verdict} --finalize`

## Review body
---
{render_review_body(task['id'], creator, verdict)}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Review orchestrator Guardiao Familia")
    parser.add_argument("--creator", required=True, choices=list(CREATOR_ROLES))
    parser.add_argument("--task", help="Task ID especifica (ex: T-P04-005)")
    parser.add_argument("--verdict", default="approved", choices=["approved", "changes_requested"])
    parser.add_argument("--summary", default="Review automatico — ver checklist no PR.")
    parser.add_argument("--pr-url", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--finalize", action="store_true", help="Executa finalize no board")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.task:
        tasks = load_tasks()
        task = next((t for t in tasks if t["id"] == args.task), None)
        if not task:
            print(f"Task {args.task} nao encontrada", file=sys.stderr)
            sys.exit(1)
    else:
        task = pick_task(args.creator, sprint_atual=1, sprint_only=False)
        if not task:
            print(f"Nenhuma task para {args.creator}", file=sys.stderr)
            sys.exit(1)

    reviewer = reviewer_for(args.creator)
    result = {
        "creator": args.creator,
        "reviewer": reviewer,
        "task": task,
        "verdict": args.verdict,
    }

    if args.json and not args.finalize:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif not args.finalize:
        print(build_review_instructions(task, args.creator, args.verdict))

    if args.finalize:
        fin = finalize_pr_review(
            task, args.creator, reviewer, args.verdict,
            args.summary, pr_url=args.pr_url, dry_run=args.dry_run,
        )
        result["finalize"] = fin
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
