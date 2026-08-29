#!/usr/bin/env python3
"""Agente QA: scan estático + Appium → mobile_user_flows.db (seed de fluxos 0→N)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib.env_load import ensure_env  # noqa: E402

ensure_env()

from lib.mobile.mobile_flow_discovery import (  # noqa: E402
    get_flow,
    resolve_user_flow_for_task,
    run_discovery,
)
from lib.mobile.mobile_user_flow_db import db_path, find_flows_for_task, stats  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", choices=["parent", "child", "both"], default="both")
    parser.add_argument("--appium", action="store_true", help="Dump UIAutomator no emulador")
    parser.add_argument("--appium-p0", action="store_true", help="Fase 2: reconcile P0 runtime (launch+dump+shot)")
    parser.add_argument("--lookup", default="", help="Buscar fluxo: screen ou label")
    parser.add_argument("--flow-id", default="", help="Mostrar fluxo por ID")
    parser.add_argument("--task-id", default="", help="Simular lookup para task (ex. T-P3-002)")
    args = parser.parse_args()

    if args.flow_id:
        flow = get_flow(args.flow_id)
        print(json.dumps(flow, indent=2, ensure_ascii=False))
        return 0 if flow else 1

    if args.lookup:
        flows = find_flows_for_task(label_hint=args.lookup, screen_hint=args.lookup)
        print(json.dumps(flows[:3], indent=2, ensure_ascii=False))
        return 0

    if args.task_id:
        import json as _json
        from pathlib import Path as _Path

        backlog = _json.loads((ROOT / "board_automation/data/imports/BACKLOG_PROJECT3.json").read_text(encoding="utf-8"))
        extra_path = ROOT / "board_automation/data/imports/PROJECT3_REFINEMENT_EXTRA.json"
        extra_all = _json.loads(extra_path.read_text(encoding="utf-8")) if extra_path.is_file() else {}
        task = None
        for t in backlog.get("tasks") or []:
            if t["id"] == args.task_id:
                task = {**t, "refinement": {**(t.get("refinement") or {}), **(extra_all.get(args.task_id, {}).get("refinement") or {})}}
                break
        if not task:
            print(f"task {args.task_id} not in backlog")
            return 1
        uf = resolve_user_flow_for_task(task)
        print(json.dumps(uf, indent=2, ensure_ascii=False))
        return 0 if uf else 1

    apps = ["parent", "child"] if args.app == "both" else [args.app]
    result = run_discovery(apps, appium=args.appium, appium_p0=args.appium_p0)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nDB: {db_path()}")
    print(f"Stats: {stats()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
