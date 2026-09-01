#!/usr/bin/env python3
"""Sinal de CI: enfileira qa-gate (green) ou retrocesso QA (red)."""

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
from lib.ci.ci_signals import handle_ci_green, handle_ci_red  # noqa: E402


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
