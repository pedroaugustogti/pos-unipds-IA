#!/usr/bin/env python3
"""Refresh seed + Appium suite + greeting evidence + cleanup (T-P3-009)."""

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

from lib.mobile.mobile_e2e_seed import default_db_seed_config, provision_handoff  # noqa: E402
from lib.mobile.qa_mobile_mcp import (  # noqa: E402
    _save_seed_cache,
    run_appium_suite,
    run_db_cleanup,
)

TASK_ID = "T-P3-009"


def main() -> int:
    cfg = default_db_seed_config(TASK_ID)
    cfg["reuse_handoff"] = False
    cfg["bootstrap_api"] = False
    seed = provision_handoff(TASK_ID, config=cfg)
    if not seed.get("ok"):
        print(json.dumps(seed, indent=2, default=str))
        return 1
    _save_seed_cache(TASK_ID, seed)
    print("pairing_code", (seed.get("handoff") or {}).get("pairing_code"))

    suite = run_appium_suite(
        "child",
        from_db_seed=True,
        task_id=TASK_ID,
        feature="go_to_home_child",
        skip_build=True,
        skip_appium=False,
        child_only=True,
        dry_run=False,
        timeout_sec=3600,
    )
    out_path = ROOT / "agents" / "00-runtime" / "output" / "mobile" / f"{TASK_ID}-qa-run.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"seed": {"ok": True, "pairing_code": (seed.get("handoff") or {}).get("pairing_code")}, "suite": suite}
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("suite_ok", suite.get("ok"))
    if not suite.get("ok"):
        return 1

    cleanup = run_db_cleanup(task_id=TASK_ID, dry_run=False)
    payload["cleanup"] = cleanup
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("cleanup_ok", cleanup.get("ok"))
    return 0 if cleanup.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
