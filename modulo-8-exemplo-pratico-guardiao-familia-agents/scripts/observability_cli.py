#!/usr/bin/env python3
"""CLI de observabilidade do fluxo dos agentes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.observability import (  # noqa: E402
    DASHBOARD_PATH,
    LOG_PATH,
    SNAPSHOT_PATH,
    build_snapshot,
    read_events,
    write_dashboard,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Observabilidade — fluxo agentes Guardião Família")
    parser.add_argument("--tail", type=int, default=0, help="Ultimos N eventos do JSONL")
    parser.add_argument("--summary", action="store_true", help="Imprime snapshot resumido")
    parser.add_argument("--dashboard", action="store_true", help="Regenera dashboard.html")
    parser.add_argument("--json", action="store_true", help="Saida JSON")
    parser.add_argument("--open", action="store_true", help="Abre dashboard no browser (Windows)")
    args = parser.parse_args()

    if not any([args.tail, args.summary, args.dashboard, args.open]):
        args.summary = True
        args.dashboard = True

    snap = build_snapshot()
    if args.dashboard:
        path = write_dashboard(snap)
        print(f"Dashboard: {path}")

    if args.tail:
        events = read_events(limit=args.tail)
        if args.json:
            print(json.dumps(events, ensure_ascii=False, indent=2))
        else:
            for e in events:
                print(
                    f"{e.get('ts')} | {e.get('kind')} | {e.get('event')} | "
                    f"{e.get('task_id')} | {e.get('agent')} | {e.get('from_status')}->{e.get('to_status')} | "
                    f"{e.get('dispatch_action')}"
                )

    if args.summary:
        totals = snap.get("totals") or {}
        if args.json:
            print(json.dumps({
                "totals": totals,
                "busy": snap.get("busy_agents"),
                "idle": snap.get("idle_agents"),
                "blockers": snap.get("blockers"),
                "paths": snap.get("paths"),
            }, ensure_ascii=False, indent=2))
        else:
            print("=== Observabilidade ===")
            print(f"Eventos: {totals.get('events')}")
            print(f"Idle: {totals.get('idle_agents')} | Busy: {totals.get('busy_agents')} | Fila: {totals.get('queue_len')} | Blockers: {totals.get('blockers')}")
            print(f"Por evento: {totals.get('by_event')}")
            print(f"Log: {LOG_PATH}")
            print(f"Snapshot: {SNAPSHOT_PATH}")
            print(f"Dashboard: {DASHBOARD_PATH}")

    if args.open:
        import os
        os.startfile(str(DASHBOARD_PATH))  # type: ignore[attr-defined]

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
