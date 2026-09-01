#!/usr/bin/env python3
"""Validação live isolada das tools MCP Appium + seed (cenários A–D)."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
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
from lib.mobile.qa_mobile_mcp import run_appium_suite, run_db_cleanup, run_db_seed  # noqa: E402
from lib.mobile.qa_mobile_setup_evidence import _package, collect_artifacts, setup_root  # noqa: E402
from lib.paths import QA_EVIDENCE_DIR  # noqa: E402

TIMEOUT = 2400

SCENARIOS: list[dict[str, Any]] = [
    {
        "key": "A",
        "name": "A_parent_create_account",
        "task_id": "QA-LIVE-A",
        "seed_profile": None,
        "app": "parent",
        "suite_kw": {"feature": "create_account", "skip_appium": False},
        "optional": True,
    },
    {
        "key": "B",
        "name": "B_parent_seed_login",
        "task_id": "QA-LIVE-B",
        "seed_profile": "parent_home",
        "app": "parent",
        "suite_kw": {"from_db_seed": True, "feature": "login", "skip_appium": False},
    },
    {
        "key": "C",
        "name": "C_child_seed_child_only",
        "task_id": "QA-LIVE-C",
        "seed_profile": "child_home",
        "app": "child",
        "suite_kw": {"from_db_seed": True, "child_only": True, "skip_appium": False},
    },
    {
        "key": "D",
        "name": "D_dual_pairing",
        "task_id": "QA-LIVE-D",
        "seed_profile": "child_home",
        "app": "child",
        "suite_kw": {"from_db_seed": True, "feature": "pairing", "child_only": False, "skip_appium": False},
    },
]


def _adb_devices() -> list[str]:
    home = resolve_android_home()
    if not home:
        return []
    adb = home / "platform-tools" / ("adb.exe" if sys.platform == "win32" else "adb")
    r = subprocess.run([str(adb), "devices"], capture_output=True, text=True, timeout=15)
    return [ln.split()[0] for ln in (r.stdout or "").splitlines() if "\tdevice" in ln]


def _row(name: str, ok: bool, detail: str = "") -> dict[str, Any]:
    print(f"{'PASS' if ok else 'FAIL'} {name}" + (f" — {detail}" if detail else ""), flush=True)
    return {"name": name, "ok": ok, "detail": detail}


def _count_evidence(task_id: str, artifacts: dict[str, Any]) -> dict[str, int]:
    png = mp4 = 0
    for d in artifacts.get("evidence_dirs") or []:
        dp = Path(d)
        if dp.is_dir():
            png += len(list(dp.glob("*.png")))
            mp4 += len(list(dp.glob("*.mp4")))
    qa_dir = QA_EVIDENCE_DIR / task_id
    if qa_dir.is_dir():
        png += len(list(qa_dir.glob("*.png")))
        mp4 += len(list(qa_dir.glob("*.mp4")))
    return {"png": png, "mp4": mp4}


def _run_scenario(spec: dict[str, Any]) -> dict[str, Any]:
    name = str(spec["name"])
    task_id = str(spec["task_id"])
    app = str(spec["app"])
    seed_profile = spec.get("seed_profile")
    suite_kw = dict(spec.get("suite_kw") or {})
    suite_kw["task_id"] = task_id

    rows: list[dict[str, Any]] = []
    t0 = time.time()

    # cleanup prévio — evita interferência de run anterior com mesmo ticket
    pre = run_db_cleanup(task_id=task_id, dry_run=False)
    rows.append(_row(f"{name}/pre_cleanup", bool(pre.get("ok")), str(pre.get("purged") or "ok")))

    if seed_profile:
        seed = run_db_seed(
            task_id,
            profile=str(seed_profile),
            bootstrap_api=True,
            use_task_config=False,
            dry_run=False,
        )
        rows.append(
            _row(
                f"{name}/seed",
                bool(seed.get("ok")),
                str((seed.get("handoff") or {}).get("lastStep")),
            )
        )
        if not seed.get("ok"):
            return {"name": name, "task_id": task_id, "ok": False, "checks": rows, "seconds": round(time.time() - t0, 1)}

    suite = run_appium_suite(app, dry_run=False, skip_build=True, timeout_sec=TIMEOUT, **suite_kw)  # type: ignore[arg-type]
    ok = bool(suite.get("ok"))
    markers = suite.get("markers") or []
    tail = " | ".join(markers[-4:])
    if suite.get("partial_success"):
        ok = True
        tail += " | partial_success"
    rows.append(_row(f"{name}/suite", ok, tail or str(suite.get("returncode"))))

    evidence: dict[str, Any] = {}
    if ok:
        try:
            pkg = _package(task_id, setup_root())
            arts = collect_artifacts(setup_root())
            counts = _count_evidence(task_id, arts)
            evidence = {"package_dir": str(pkg), "counts": counts}
            rows.append(
                _row(
                    f"{name}/evidence",
                    counts["png"] > 0,
                    f"png={counts['png']} mp4={counts['mp4']} → {pkg}",
                )
            )
        except Exception as exc:  # noqa: BLE001
            rows.append(_row(f"{name}/evidence", False, str(exc)))

    cleanup = run_db_cleanup(task_id=task_id, dry_run=False)
    rows.append(_row(f"{name}/cleanup", bool(cleanup.get("ok")), "purged"))

    return {
        "name": name,
        "task_id": task_id,
        "ok": all(r["ok"] for r in rows if not r["name"].endswith("/pre_cleanup")),
        "checks": rows,
        "seconds": round(time.time() - t0, 1),
        "evidence": evidence,
        "suite": {
            k: suite[k]
            for k in ("ok", "partial_success", "returncode", "markers", "handoff_after")
            if k in suite
        },
    }


def _selected_scenarios() -> list[dict[str, Any]]:
    keys: set[str] | None = None
    for i, a in enumerate(sys.argv):
        if a in ("--scenario", "-s") and i + 1 < len(sys.argv):
            keys = {k.strip().upper() for k in sys.argv[i + 1].split(",")}
            break
        if a.startswith("--scenario="):
            keys = {k.strip().upper() for k in a.split("=", 1)[1].split(",")}
            break
    if keys:
        return [s for s in SCENARIOS if s["key"] in keys]
    out = [s for s in SCENARIOS if not s.get("optional")]
    if "--full" in sys.argv:
        out = [s for s in SCENARIOS if s["key"] == "A"] + out
    return out


def main() -> int:
    devices = _adb_devices()
    print("adb devices:", devices or "(nenhum)", flush=True)
    if not devices:
        print("AVISO: nenhum emulador online — boot via start-emulators.ps1", flush=True)

    results = [_run_scenario(s) for s in _selected_scenarios()]

    out = {
        "at": datetime.now(timezone.utc).isoformat(),
        "devices": devices,
        "scenarios": results,
        "ok": all(s["ok"] for s in results),
    }
    path = ROOT / "agents" / "00-runtime" / "output" / "mobile" / "mcp-appium-live.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"\nreport: {path}", flush=True)
    print("overall:", "PASS" if out["ok"] else "FAIL", flush=True)
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
