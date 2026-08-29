#!/usr/bin/env python3
"""CLI do dispatch adapter (Fase 2)."""

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

from lib.orchestrator.dispatch_adapter import (  # noqa: E402
    cursor_sdk_status,
    drain_queued,
    resolve_backend,
)
from lib.env_load import ensure_env  # noqa: E402
from lib.orchestrator.worker_jobs import load_jobs  # noqa: E402

ensure_env()


def main() -> int:
    p = argparse.ArgumentParser(description="Dispatch de jobs queued")
    p.add_argument("--status", action="store_true", help="Mostra backend resolvido + SDK")
    p.add_argument("--drain", action="store_true", help="Lease+dispatch ate --limit jobs")
    p.add_argument("--limit", type=int, default=1)
    p.add_argument("--backend", default=None, help="auto|manual_fallback|cursor_automation")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--job", default=None, help="job_id especifico")
    args = p.parse_args()

    if args.status:
        print(json.dumps({
            "backend_resolved": resolve_backend(args.backend),
            "cursor_sdk": cursor_sdk_status(),
            "queued": sum(1 for j in (load_jobs().get("jobs") or []) if j.get("status") == "queued"),
            "leased": sum(1 for j in (load_jobs().get("jobs") or []) if j.get("status") == "leased"),
        }, ensure_ascii=False, indent=2))
        return 0

    if args.job:
        from lib.orchestrator.dispatch_adapter import dispatch_job

        data = load_jobs()
        job = next((j for j in (data.get("jobs") or []) if j.get("job_id") == args.job), None)
        if not job:
            print(json.dumps({"ok": False, "error": "job not found"}, ensure_ascii=False))
            return 1
        out = dispatch_job(job, dry_run=args.dry_run, backend=args.backend)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0 if out.get("ok") else 1

    if args.drain:
        results = drain_queued(dry_run=args.dry_run, limit=args.limit, backend=args.backend)
        print(json.dumps({"ok": True, "count": len(results), "results": results}, ensure_ascii=False, indent=2))
        return 0

    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
