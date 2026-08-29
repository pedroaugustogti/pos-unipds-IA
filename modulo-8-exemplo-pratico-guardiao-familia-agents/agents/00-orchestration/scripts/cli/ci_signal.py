#!/usr/bin/env python3
"""CLI Fase 3 — sinais PR/CI → gateway / qa-gate."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_bs = Path(__file__).resolve().parents[2] / "bootstrap.py"
_spec = importlib.util.spec_from_file_location("orch_bootstrap", _bs)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
_mod.setup()

import argparse
import json
import sys
from pathlib import Path

from lib.paths import MODULE_ROOT  # noqa: E402
from lib.env_load import ensure_env  # noqa: E402

ensure_env()
from lib.ci.ci_signals import (  # noqa: E402
    dispatch_signal,
    handle_ci_green,
    handle_ci_red,
    handle_pr_signal,
    parse_task_id,
)


def main() -> int:
    p = argparse.ArgumentParser(description="Sinais GitHub → board agents")
    p.add_argument("--payload", help="JSON file (repository_dispatch client_payload)")
    p.add_argument("--stdin", action="store_true")
    p.add_argument("--signal", choices=("pr_opened", "pr_synchronize", "ci_green", "ci_red"))
    p.add_argument("--task", default=None)
    p.add_argument("--pr-url", default=None)
    p.add_argument("--pr-title", default=None)
    p.add_argument("--branch", default=None)
    p.add_argument("--summary", default="")
    p.add_argument("--bug-kind", choices=("regression", "flaky"), default="regression")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--parse-title", default=None, help="So extrai task_id do titulo")
    args = p.parse_args()

    if args.parse_title is not None:
        tid = parse_task_id(args.parse_title)
        print(json.dumps({"task_id": tid}, ensure_ascii=False))
        return 0 if tid else 1

    if args.payload or args.stdin:
        raw = sys.stdin.read() if args.stdin else Path(args.payload).read_text(encoding="utf-8")
        payload = json.loads(raw)
        out = dispatch_signal(payload, dry_run=args.dry_run)
    elif args.signal:
        task = args.task or parse_task_id(args.pr_title, args.branch)
        if not task:
            p.error("--task ou titulo/branch com [T-XXX]")
        if args.signal in ("pr_opened", "pr_synchronize"):
            out = handle_pr_signal(
                task_id=task,
                pr_url=args.pr_url,
                branch=args.branch,
                summary=args.summary,
                dry_run=args.dry_run,
            )
        elif args.signal == "ci_green":
            out = handle_ci_green(task_id=task, dry_run=args.dry_run)
        else:
            out = handle_ci_red(
                task_id=task,
                bug_kind=args.bug_kind,
                summary=args.summary or "CI failed",
                dry_run=args.dry_run,
            )
    else:
        p.print_help()
        return 0

    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
