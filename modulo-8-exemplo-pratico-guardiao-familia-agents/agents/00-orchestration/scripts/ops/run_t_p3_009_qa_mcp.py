#!/usr/bin/env python3
"""Executa sequência MCP qa-gate para T-P3-009: seed → Appium → evidências → cleanup."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
_bs = Path(__file__).resolve().parents[2] / "bootstrap.py"
_spec = importlib.util.spec_from_file_location("ba_bootstrap", _bs)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
_mod.setup()

from lib.env_load import ensure_env  # noqa: E402

ensure_env()

from lib.mobile.qa_mobile_mcp import run_appium_suite, run_db_cleanup, run_db_seed  # noqa: E402

TASK_ID = "T-P3-009"


def main() -> int:
    dry = "--dry-run" in sys.argv
    results: dict[str, object] = {}

    print("=== 1/3 qa_db_seed ===")
    seed = run_db_seed(
        TASK_ID,
        profile="basic_parent",
        bootstrap_api=False,
        use_task_config=True,
        dry_run=dry,
    )
    results["seed"] = seed
    print(json.dumps({k: v for k, v in seed.items() if k != "steps"}, ensure_ascii=False, indent=2, default=str))
    if not seed.get("ok"):
        return 1

    print("\n=== 2/3 qa_appium_suite_child ===")
    suite = run_appium_suite(
        "child",
        from_db_seed=True,
        task_id=TASK_ID,
        feature="go_to_home_child",
        phase="All",
        skip_build=True,
        skip_appium=False,
        child_only=True,
        dry_run=dry,
        timeout_sec=3600,
    )
    results["suite"] = {k: v for k, v in suite.items() if k not in ("stdout_tail",)}
    if suite.get("stdout_tail"):
        results["suite_stdout_tail"] = str(suite["stdout_tail"])[-1500:]
    print(json.dumps(results["suite"], ensure_ascii=False, indent=2, default=str))
    if not suite.get("ok"):
        out_path = ROOT / "agents" / "00-runtime" / "output" / "mobile" / f"{TASK_ID}-qa-run.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        return 1

    print("\n=== 3/3 qa_db_cleanup ===")
    cleanup = run_db_cleanup(task_id=TASK_ID, dry_run=dry)
    results["cleanup"] = cleanup
    print(json.dumps(cleanup, ensure_ascii=False, indent=2, default=str))

    out_path = ROOT / "agents" / "00-runtime" / "output" / "mobile" / f"{TASK_ID}-qa-run.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"\nreport: {out_path}")
    return 0 if cleanup.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
