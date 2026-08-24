#!/usr/bin/env python3
"""C — Sinal de CI: enfileira qa-gate (green) ou test_failed_bug (red)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.ci_signals import handle_ci_green, handle_ci_red  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--task", required=True)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--green", action="store_true")
    g.add_argument("--red", action="store_true")
    p.add_argument("--bug-kind", choices=("regression", "flaky"), default="regression")
    p.add_argument("--summary", default="CI failed")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if args.green:
        out = handle_ci_green(task_id=args.task, dry_run=args.dry_run)
    else:
        out = handle_ci_red(
            task_id=args.task,
            bug_kind=args.bug_kind,
            summary=args.summary,
            dry_run=args.dry_run,
        )
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
