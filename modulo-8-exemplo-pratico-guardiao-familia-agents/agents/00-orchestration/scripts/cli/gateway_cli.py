#!/usr/bin/env python3
"""CLI da porta unica de eventos (gateway) — eventos role-based v2."""

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

from lib.env_load import ensure_env  # noqa: E402

ensure_env()
from board_automation.board.task_status_workflow import build_event
from lib.gateway.v2_events import is_valid_gateway_event, legacy_event_error  # noqa: E402
from lib.gateway import approve_hitl, emit_status_event, list_hitl_queue  # noqa: E402


def _resolve_event(args: argparse.Namespace) -> str:
    if args.event:
        return args.event.strip()
    if args.agent_role and args.board_status:
        return build_event(args.agent_role, args.board_status, return_=args.return_event)
    return ""


def main() -> int:
    p = argparse.ArgumentParser(
        description="Gateway de eventos do board Guardião Família (role-based v2)",
    )
    p.add_argument("--task", required=False, help="task_id (ex: T-P3-009)")
    p.add_argument(
        "--event",
        required=False,
        help="Evento role-based (ex: frontend-mobile_ready_for_code_review)",
    )
    p.add_argument("--agent-role", default="", help="Monta evento com --board-status")
    p.add_argument("--board-status", default="", help='Status alvo (ex: "In Progress")')
    p.add_argument(
        "--return-event",
        action="store_true",
        help="Retrocesso ({agent_role}_return_{status_slug})",
    )
    p.add_argument("--from-agent", default="", help="Papel emissor (deve bater com prefixo do evento)")
    p.add_argument("--summary", default="")
    p.add_argument("--pr-url", default=None)
    p.add_argument("--branch", default=None)
    p.add_argument("--bug-kind", choices=("regression", "flaky"), default=None)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--approve-hitl", action="store_true", help="Libera evento HITL")
    p.add_argument("--list-hitl", action="store_true")
    p.add_argument(
        "--react-trace-json",
        default="",
        help="JSON array — obrigatório para evento creator → Ready for Code Review",
    )
    args = p.parse_args()

    if args.list_hitl:
        print(json.dumps({"hitl_queue": list_hitl_queue()}, ensure_ascii=False, indent=2))
        return 0

    event = _resolve_event(args)
    if not args.task or not event:
        p.error("--task e (--event OU --agent-role + --board-status) sao obrigatorios")

    legacy = legacy_event_error(event)
    if legacy:
        print(json.dumps({"ok": False, "error": legacy}, ensure_ascii=False, indent=2))
        return 1

    if not is_valid_gateway_event(event):
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": f"evento invalido (v2): {event}",
                    "hint": "Use list_status_events (MCP) ou scripts/langgraph/list_nodes.py",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    react_trace = None
    if args.react_trace_json:
        react_trace = json.loads(Path(args.react_trace_json).read_text(encoding="utf-8"))

    if args.approve_hitl:
        out = approve_hitl(args.task, event, dry_run=args.dry_run)
    else:
        out = emit_status_event(
            args.task,
            event,
            summary=args.summary,
            pr_url=args.pr_url,
            branch=args.branch,
            bug_kind=args.bug_kind,
            dry_run=args.dry_run,
            react_trace=react_trace,
            from_agent=args.from_agent or None,
        )
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
