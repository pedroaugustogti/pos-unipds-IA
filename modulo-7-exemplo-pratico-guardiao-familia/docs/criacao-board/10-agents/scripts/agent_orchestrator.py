#!/usr/bin/env python3
"""Orquestrador legado: seleciona task, claim no board, gera instruções de execução."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.board_client import claim_task, comment_issue, add_labels  # noqa: E402
from lib.task_router import AGENT_DEFAULT_REPO, pick_task, slugify  # noqa: E402

PR_TEMPLATE = ROOT / "templates" / "PR_TEMPLATE.md"
SKILLS = ROOT / "skills"
REPOS_BASE = Path(r"C:\Users\pedro\Documents\guardiao-familia")


def render_pr_body(task: dict, agent: str) -> str:
    tpl = PR_TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "{task_id}": task["id"],
        "{task_title}": task["title"],
        "{agent_role}": agent,
        "{epic_id}": task["epic_id"],
        "{epic_name}": task.get("epic_name", ""),
        "{repo}": task["repo"],
        "{effort_sp}": task["effort_sp"],
        "{rice}": task["rice"],
        "{wsjf}": task["wsjf"],
        "{priority_rank}": task["priority_rank"],
        "{files_changed_count}": "0",
        "{insertions}": "0",
        "{deletions}": "0",
    }
    for k, v in replacements.items():
        tpl = tpl.replace(k, str(v))
    return tpl


def build_agent_instructions(task: dict, agent: str) -> str:
    folder_map = {
        "backend": "backend",
        "frontend-mobile": "frontend-mobile",
        "frontend-web": "frontend-web",
        "cloud-infra": "cloud-infra",
        "database": "database",
        "devops-cicd": "devops-cicd",
        "qa": "qa",
        "stores-release": "stores-release",
    }
    skill_path = SKILLS / folder_map.get(agent, agent) / "SKILL.md"
    branch = f"feat/{task['id']}-{slugify(task['title'])}"
    repo_path = REPOS_BASE / task["repo"]

    return f"""# Instruções de execução — {agent}

## Task selecionada
- **ID:** {task['id']}
- **Título:** {task['title']}
- **Repo:** {task['repo']} @ {repo_path}
- **Priority rank:** #{task['priority_rank']}
- **Sprint:** {task['sprint']}

## Skill
Leia e siga: `{skill_path}`

## Passos
1. `cd {repo_path}` && checkout main/master && pull
2. `git checkout -b {branch}`
3. Implementar escopo da task {task['id']}
4. Commit: `feat({task['id']}): <descrição>`
5. Push e abrir PR com body abaixo
6. Comentar issue e mover card para In Review

## PR body
---
{render_pr_body(task, agent)}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Orquestrador de agentes Guardião Família")
    parser.add_argument("--agent", required=True, choices=list(AGENT_DEFAULT_REPO.keys()))
    parser.add_argument("--sprint", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--claim", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    task = pick_task(args.agent, args.sprint)
    if not task:
        print(f"Nenhuma task elegível para agent={args.agent}", file=sys.stderr)
        sys.exit(1)

    branch = f"feat/{task['id']}-{slugify(task['title'])}"
    result = {
        "agent": args.agent,
        "task": task,
        "branch": branch,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(build_agent_instructions(task, args.agent))

    if args.claim:
        claim_result = claim_task(task, args.agent, branch, dry_run=args.dry_run)
        if not args.json:
            print("\n--- Claim ---")
            print(json.dumps(claim_result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
