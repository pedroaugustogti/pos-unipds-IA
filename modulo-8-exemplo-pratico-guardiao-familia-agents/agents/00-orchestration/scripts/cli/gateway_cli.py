#!/usr/bin/env python3
"""CLI da porta unica de eventos (gateway)."""

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
from lib.gateway import approve_hitl, emit_status_event, list_hitl_queue  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Gateway de eventos do board Guardião Família")
    p.add_argument("--task", required=False, help="task_id")
    p.add_argument("--event", required=False, help="claim|open_pr|merge_pr|...")
    p.add_argument("--summary", default="")
    p.add_argument("--pr-url", default=None)
    p.add_argument("--branch", default=None)
    p.add_argument("--bug-kind", choices=("regression", "flaky"), default=None)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--approve-hitl", action="store_true", help="Libera evento HITL")
    p.add_argument("--list-hitl", action="store_true")
    args = p.parse_args()

    if args.list_hitl:
        print(json.dumps({"hitl_queue": list_hitl_queue()}, ensure_ascii=False, indent=2))
        return 0

    if not args.task or not args.event:
        p.error("--task e --event sao obrigatorios (exceto --list-hitl)")

    if args.approve_hitl:
        out = approve_hitl(args.task, args.event, dry_run=args.dry_run)
    else:
        out = emit_status_event(
            args.task,
            args.event,
            summary=args.summary,
            pr_url=args.pr_url,
            branch=args.branch,
            bug_kind=args.bug_kind,
            dry_run=args.dry_run,
        )
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
