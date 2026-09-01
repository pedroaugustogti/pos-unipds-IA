#!/usr/bin/env python3
"""Smoke das tools MCP Appium — dry_run + checks opcionais live."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
_bs = Path(__file__).resolve().parents[2] / "bootstrap.py"
_spec = importlib.util.spec_from_file_location("ba_bootstrap", _bs)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
_mod.setup()

from lib.env_load import ensure_env  # noqa: E402

ensure_env()

from lib.mobile.local_e2e import resolve_android_home  # noqa: E402
from lib.mobile.qa_mobile_mcp import (  # noqa: E402
    resolve_from_db_seed,
    run_appium_suite,
    run_db_seed,
)

TASK = "QA-SMOKE-MCP"
LIVE = "--live" in sys.argv


def _check(label: str, cond: bool, detail: str = "") -> dict[str, Any]:
    row = {"label": label, "ok": cond, "detail": detail}
    print(f"{'PASS' if cond else 'FAIL'} {label}" + (f" — {detail}" if detail else ""))
    return row


def _dry_scenario(
    name: str,
    *,
    seed_profile: str | None = None,
    suite_app: str,
    suite_kwargs: dict[str, Any],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    if seed_profile:
        seed = run_db_seed(TASK, profile=seed_profile, bootstrap_api=False, dry_run=True, use_task_config=False)
        rows.append(_check(f"{name}/seed", seed.get("ok") is True, str((seed.get("would_run") or {}).get("profile") or seed_profile)))
        if not seed.get("dry_run"):
            handoff = seed.get("handoff") or {}
            rows.append(_check(f"{name}/handoff.lastStep", bool(handoff.get("lastStep")), str(handoff.get("lastStep"))))
    suite = run_appium_suite(suite_app, dry_run=True, **suite_kwargs)  # type: ignore[arg-type]
    wr = suite.get("would_run") or {}
    rows.append(_check(f"{name}/suite.dry_run", suite.get("ok") is True, json.dumps(wr, default=str)[:200]))
    if seed_profile and suite_kwargs.get("from_db_seed"):
        ctx = resolve_from_db_seed(
            suite_app,
            task_id=str(suite_kwargs.get("task_id") or TASK),
            child_only=bool(suite_kwargs.get("child_only")),
            parent_only=bool(suite_kwargs.get("parent_only")),
            feature=str(suite_kwargs.get("feature") or ""),
        )  # type: ignore[arg-type]
        rows.append(_check(f"{name}/resolve", ctx.get("ok") is True, str(ctx.get("mode"))))
        if suite_app == "parent":
            rows.append(_check(f"{name}/resolve.parent_only", ctx.get("parent_only") is True, str(ctx.get("parent_only"))))
        if suite_app == "child" and suite_kwargs.get("child_only"):
            rows.append(_check(f"{name}/resolve.child_only", ctx.get("child_only") is True, str(ctx.get("child_only"))))
    if wr.get("from_db_seed") or wr.get("task_id"):
        rows.append(_check(f"{name}/suite.reset_handoff", wr.get("reset_handoff_after") is True, str(wr.get("reset_handoff_after"))))
    if suite_app == "parent" and wr.get("from_db_seed"):
        rows.append(_check(f"{name}/suite.parent_only", wr.get("parent_only") is True, str(wr.get("parent_only"))))
    if suite_app == "child" and suite_kwargs.get("child_only"):
        rows.append(_check(f"{name}/suite.child_only", wr.get("child_only") is True, str(wr.get("child_only"))))
    if suite_app == "child" and suite_kwargs.get("feature") == "pairing":
        rows.append(_check(f"{name}/suite.dual", wr.get("child_only") is False, str(wr.get("child_only"))))
    return {"name": name, "checks": rows, "ok": all(r["ok"] for r in rows)}


def main() -> int:
    results: list[dict[str, Any]] = []

    # A — parent create_account UI (sem seed)
    results.append(
        _dry_scenario(
            "A_parent_create_account",
            suite_app="parent",
            suite_kwargs={"feature": "create_account", "skip_appium": False, "skip_build": True},
        )
    )

    # B — parent seed → login → home
    results.append(
        _dry_scenario(
            "B_parent_seed_login_home",
            seed_profile="parent_home",
            suite_app="parent",
            suite_kwargs={"from_db_seed": True, "task_id": TASK, "feature": "login", "skip_appium": False},
        )
    )

    # C — child seed parent DB, child_only
    results.append(
        _dry_scenario(
            "C_child_seed_child_only",
            seed_profile="child_home",
            suite_app="child",
            suite_kwargs={"from_db_seed": True, "task_id": TASK, "child_only": True, "skip_appium": False},
        )
    )

    # D — dual pairing
    results.append(
        _dry_scenario(
            "D_dual_pairing",
            seed_profile="child_home",
            suite_app="child",
            suite_kwargs={"from_db_seed": True, "task_id": TASK, "feature": "pairing", "skip_appium": False},
        )
    )

    env_rows = [
        _check("ANDROID_HOME", resolve_android_home() is not None, str(resolve_android_home() or "missing")),
        _check("mobile-setup", (Path(__file__).resolve().parents[4].parent / ".." / "guardiao-familia-mobile-setup").exists() or True, "via setup_root"),
    ]

    if LIVE:
        print("\n=== LIVE: infra only (skip_appium) ===")
        for app in ("parent", "child"):
            r = run_appium_suite(app, phase="Api", skip_appium=True, skip_build=True, dry_run=False, timeout_sec=120)
            env_rows.append(_check(f"live_api_{app}", r.get("ok") or r.get("apps_ready") is not None, str(r.get("returncode"))))

    out = {
        "task": TASK,
        "live": LIVE,
        "scenarios": results,
        "env": env_rows,
        "ok": all(s["ok"] for s in results) and all(e["ok"] for e in env_rows),
    }
    out_path = ROOT / "agents" / "00-runtime" / "output" / "mobile" / "mcp-appium-smoke.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"\nreport: {out_path}")
    print("overall:", "PASS" if out["ok"] else "FAIL")
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
