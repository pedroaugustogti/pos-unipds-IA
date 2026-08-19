#!/usr/bin/env python3
"""CLI para transições de status no GitHub Project #2."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.board_client import update_project_status  # noqa: E402
from lib.task_router import load_tasks  # noqa: E402
from lib.task_status_workflow import (  # noqa: E402
    EVENT_TARGET,
    STATUSES,
    apply_event,
    can_transition,
    resolve_status,
    transition,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Transicao de status — workflow v2")
    parser.add_argument("--task", required=True, help="Task ID ex: T-P04-005")
    parser.add_argument("--event", choices=sorted(EVENT_TARGET.keys()), help="Evento de automacao")
    parser.add_argument("--status", help="Status destino explicito")
    parser.add_argument("--current", default="Todo", help="Status atual (para validar transicao)")
    parser.add_argument("--kind", choices=["feature", "bug"], default="feature")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == args.task), None)
    if not task:
        raise SystemExit(f"Task {args.task} nao encontrada no mapa")

    if args.event:
        target = apply_event(args.current, args.event, args.kind)
    elif args.status:
        target = transition(args.current, args.status, args.kind)
    else:
        parser.error("Informe --event ou --status")

    result = {
        "task_id": args.task,
        "kind": args.kind,
        "from": resolve_status(args.current),
        "to": target,
        "event": args.event,
        "allowed": sorted(can_transition(resolve_status(args.current), target, args.kind)),
    }

    if not args.dry_run:
        board = update_project_status(args.task, task["title"], target, dry_run=False)
        result["board"] = board
    else:
        result["board"] = {"dry_run": True, "status": target}

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{result['from']} -> {result['to']}" + (f" (event: {args.event})" if args.event else ""))


if __name__ == "__main__":
    main()
