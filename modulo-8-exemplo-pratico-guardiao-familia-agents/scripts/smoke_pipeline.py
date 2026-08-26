#!/usr/bin/env python3
"""Smoke da pipeline LangGraph — somente tasks sem hint high (economia de tokens)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.env_load import ensure_env  # noqa: E402
from lib.model_tier import is_high_risk, select_model  # noqa: E402
from lib.pilot import pick_smoke_task  # noqa: E402

ensure_env()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--task", default="", help="Task piloto (deve ser low-hint; senao erro)")
    p.add_argument("--mode", default="dry_run", choices=("dry_run", "demo", "live"))
    p.add_argument("--from-zero", action="store_true", default=True)
    p.add_argument("--no-from-zero", action="store_false", dest="from_zero")
    args = p.parse_args()

    try:
        task = pick_smoke_task(prefer_id=args.task or None)
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    tier = select_model(task, purpose="implement_low", role=task.get("agent_role"))
    if tier.get("tier") == "high":
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": f"Smoke abortado: {task['id']} roteou tier high",
                    "model_tier": tier,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    from langgraph_app import run_once  # noqa: E402

    try:
        out = run_once(
            task["id"],
            mode=args.mode,
            title=task.get("title") or "",
            agent_role=task.get("agent_role") or "",
            from_zero=args.from_zero,
        )
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False, indent=2))
        return 1

    slim = {
        "ok": not out.get("error") and (out.get("board_status") == "Done" or out.get("done")),
        "smoke": True,
        "high_hint": is_high_risk(task),
        "task_id": task["id"],
        "title": task.get("title"),
        "mode": out.get("mode"),
        "board_status": out.get("board_status"),
        "steps": out.get("steps"),
        "token_usage": out.get("token_usage"),
        "model_tier": tier,
        "error": out.get("error"),
    }
    if not slim["ok"] and not out.get("error"):
        slim["ok"] = True
        slim["partial"] = True

    print(json.dumps(slim, ensure_ascii=True, indent=2, default=str))
    return 0 if slim["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
