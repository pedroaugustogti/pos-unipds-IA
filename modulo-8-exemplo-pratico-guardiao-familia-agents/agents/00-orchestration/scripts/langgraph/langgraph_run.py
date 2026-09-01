#!/usr/bin/env python3
"""Fase C — pipeline LangGraph (OpenRouter + Kanban)."""

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
import os
import sys
from pathlib import Path

from lib.env_load import ensure_env  # noqa: E402

ensure_env()


def main() -> int:
    p = argparse.ArgumentParser(description="LangGraph Guardião — pipeline Fase C")
    p.add_argument("--task", default="")
    p.add_argument("--smoke", action="store_true", help="Escolhe task piloto sem hint high")
    p.add_argument("--mode", default=None, help="dry_run | demo | live")
    p.add_argument("--title", default="")
    p.add_argument("--role", default="")
    p.add_argument("--from-zero", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    task_id = args.task
    if args.smoke:
        from lib.orchestrator.smoke_tasks import pick_smoke_task

        task_id = pick_smoke_task(prefer_id=task_id or None)["id"]
    elif not task_id:
        print(json.dumps({"ok": False, "error": "Informe --task ou --smoke"}, ensure_ascii=False))
        return 2

    orch = (os.environ.get("GUARDIAO_ORCHESTRATOR") or "langgraph").strip()
    if orch not in ("langgraph", "auto"):
        print(
            json.dumps(
                {"ok": False, "error": f"GUARDIAO_ORCHESTRATOR={orch}"},
                ensure_ascii=False,
            )
        )
        return 2

    from langgraph_app import run_once  # noqa: E402

    try:
        out = run_once(
            task_id,
            mode=args.mode,
            title=args.title,
            agent_role=args.role,
            from_zero=args.from_zero,
        )
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False, indent=2))
        return 1

    slim = {
        "ok": not out.get("error") and (out.get("done") or out.get("hitl_pending") or out.get("board_status") == "Done"),
        "task_id": out.get("task_id"),
        "mode": out.get("mode"),
        "board_status": out.get("board_status"),
        "done": out.get("done"),
        "hitl_pending": out.get("hitl_pending"),
        "steps": out.get("steps"),
        "decision": out.get("decision"),
        "review": out.get("review"),
        "model_tier": {
            "tier": (out.get("model_tier") or {}).get("tier"),
            "model": (out.get("model_tier") or {}).get("model"),
            "purpose": (out.get("model_tier") or {}).get("purpose"),
        },
        "messages": out.get("messages"),
        "token_usage": out.get("token_usage"),
        "langsmith": out.get("langsmith"),
        "persist_path": out.get("persist_path"),
        "error": out.get("error"),
        "react_trace_len": len(out.get("react_trace") or []),
    }
    # partial success if progressed without fatal error
    if not slim["ok"] and not out.get("error") and (out.get("messages") or out.get("react_trace")):
        slim["ok"] = True
        slim["partial"] = True

    print(json.dumps(slim, ensure_ascii=True, indent=2, default=str))
    return 0 if slim["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
