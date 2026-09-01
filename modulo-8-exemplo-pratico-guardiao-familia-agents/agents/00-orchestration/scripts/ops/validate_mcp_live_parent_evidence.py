#!/usr/bin/env python3
"""Validação live MCP — parent seed+login e cadastro UI (evidências vídeo/PNG)."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

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
from lib.mobile.qa_mobile_setup_evidence import setup_root  # noqa: E402

PARENT_SERIAL = os.environ.get("GF_PARENT_EMULATOR_SERIAL", "emulator-5554")
TIMEOUT = 2400
TMP_BASE = ROOT / "agents" / "00-runtime" / "output" / "mobile" / "tmp_evidence"


def _adb() -> str:
    home = resolve_android_home()
    if not home:
        raise RuntimeError("ANDROID_HOME não configurado")
    return str(home / "platform-tools" / ("adb.exe" if sys.platform == "win32" else "adb"))


def _adb_run(args: list[str], *, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [_adb(), "-s", PARENT_SERIAL, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def _screenshot(dest: Path) -> bool:
    remote = "/sdcard/qa_evidence_cap.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    cap = _adb_run(["shell", "screencap", "-p", remote], timeout=30)
    if cap.returncode != 0:
        return False
    pull = _adb_run(["pull", remote, str(dest)], timeout=60)
    _adb_run(["shell", "rm", "-f", remote], timeout=15)
    return pull.returncode == 0 and dest.is_file() and dest.stat().st_size > 0


def _stop_screenrecord() -> None:
    """Encerra screenrecord no device (terminate() no host não para o processo no emulador)."""
    _adb_run(["shell", "pkill", "-l", "INT", "screenrecord"], timeout=10)
    _adb_run(["shell", "killall", "screenrecord"], timeout=10)


@contextmanager
def screen_record(local_path: Path) -> Iterator[None]:
    remote = "/sdcard/qa_live_record.mp4"
    proc: subprocess.Popen[Any] | None = None
    _adb_run(["shell", "rm", "-f", remote], timeout=15)
    try:
        proc = subprocess.Popen(
            [_adb(), "-s", PARENT_SERIAL, "shell", "screenrecord", "--time-limit", "120", remote],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(1)
        yield
    finally:
        _stop_screenrecord()
        if proc:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        time.sleep(1)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        pull = _adb_run(["pull", remote, str(local_path)], timeout=30)
        if pull.returncode != 0 or not local_path.is_file():
            # pull pode falhar se gravação não finalizou — não bloquear o pipeline
            pass
        _adb_run(["shell", "rm", "-f", remote], timeout=15)


def _copy_appium_evidence(dest: Path, prefix: str) -> list[str]:
    setup = setup_root()
    ev_root = setup / "docs" / "appium-evidence"
    copied: list[str] = []
    if not ev_root.is_dir():
        return copied
    for d in sorted(ev_root.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)[:6]:
        if not d.is_dir():
            continue
        target = dest / f"{prefix}_{d.name}"
        if target.exists():
            continue
        shutil.copytree(d, target)
        copied.append(str(target))
    return copied


def _make_out_dir(name: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = TMP_BASE / f"{name}_{stamp}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def scenario_1_parent_seed_login() -> dict[str, Any]:
    task_id = "QA-LIVE-EV-01"
    out = _make_out_dir("01_parent_seed_login")
    t0 = time.time()
    rows: list[dict[str, Any]] = []

    pre = run_db_cleanup(task_id=task_id, dry_run=False)
    rows.append({"step": "pre_cleanup", "ok": bool(pre.get("ok"))})

    seed = run_db_seed(
        task_id,
        profile="parent_home",
        bootstrap_api=True,
        use_task_config=False,
        dry_run=False,
    )
    rows.append({"step": "qa_db_seed", "ok": bool(seed.get("ok")), "detail": (seed.get("handoff") or {}).get("lastStep")})
    if not seed.get("ok"):
        return {"name": "01_parent_seed_login", "ok": False, "out_dir": str(out), "rows": rows}

    os.environ["GF_APPIUM_EVIDENCE_DIR"] = str(out / "appium-evidence")
    video_path = out / "login_to_home.mp4"
    screenshot_path = out / "parent_home.png"

    with screen_record(video_path):
        suite = run_appium_suite(
            "parent",
            dry_run=False,
            skip_build=True,
            from_db_seed=True,
            task_id=task_id,
            feature="login",
            skip_appium=False,
            reset_handoff_after=True,
            timeout_sec=TIMEOUT,
        )

    rows.append({
        "step": "qa_appium_suite_parent",
        "ok": bool(suite.get("ok")),
        "markers": (suite.get("markers") or [])[-5:],
        "handoff_after": (suite.get("handoff_after") or {}).get("lastStep"),
    })
    _screenshot(screenshot_path)
    evidence_dirs = _copy_appium_evidence(out, "step")

    cleanup = run_db_cleanup(task_id=task_id, dry_run=False)
    rows.append({"step": "cleanup", "ok": bool(cleanup.get("ok"))})

    media = {
        "video": str(video_path) if video_path.is_file() else None,
        "screenshot_home": str(screenshot_path) if screenshot_path.is_file() else None,
        "evidence_dirs": evidence_dirs,
        "package_dir": str(out),
    }
    ok = bool(suite.get("ok")) and bool(media["screenshot_home"])
    report = {
        "scenario": "01_parent_seed_login",
        "task_id": task_id,
        "ok": ok,
        "seconds": round(time.time() - t0, 1),
        "media": media,
        "rows": rows,
        "suite": {k: suite.get(k) for k in ("ok", "returncode", "partial_success", "markers") if k in suite},
    }
    _write_report(out / "report.json", report)
    return report


def _run_parent_phase(
    *,
    task_id: str,
    feature: str,
    out: Path,
    video_name: str,
    png_name: str,
    from_db_seed: bool = False,
    resume: bool = False,
) -> dict[str, Any]:
    os.environ["GF_APPIUM_EVIDENCE_DIR"] = str(out / "appium-evidence" / feature)
    os.environ["GF_RESUME_FROM_HANDOFF"] = "1" if resume else "0"
    os.environ["GF_SKIP_DB_CLEANUP"] = "1"
    video_path = out / video_name
    png_path = out / png_name

    with screen_record(video_path):
        suite = run_appium_suite(
            "parent",
            dry_run=False,
            skip_build=True,
            feature=feature,
            from_db_seed=from_db_seed,
            task_id=task_id if from_db_seed else "",
            resume_from_handoff=resume,
            skip_appium=False,
            reset_handoff_after=False,
            timeout_sec=TIMEOUT,
        )

    _screenshot(png_path)
    evidence = _copy_appium_evidence(out, feature)
    return {
        "feature": feature,
        "ok": bool(suite.get("ok")),
        "video": str(video_path) if video_path.is_file() else None,
        "screenshot": str(png_path) if png_path.is_file() else None,
        "evidence_dirs": evidence,
        "markers": (suite.get("markers") or [])[-5:],
        "handoff_after": (suite.get("handoff_after") or {}).get("lastStep"),
        "suite_ok": suite.get("ok"),
    }


def scenario_2_parent_ui_full() -> dict[str, Any]:
    task_id = "QA-LIVE-EV-02"
    out = _make_out_dir("02_parent_ui_cadastro")
    t0 = time.time()
    phases: list[dict[str, Any]] = []

    pre = run_db_cleanup(task_id=task_id, dry_run=False)
    phases.append({"step": "pre_cleanup", "ok": bool(pre.get("ok"))})

    # Reset handoff para fluxo UI limpo
    handoff_path = setup_root() / "docs" / "stage-handoff.json"
    if handoff_path.is_file():
        handoff_path.write_text("{}\n", encoding="utf-8")

    for feature, video, png in (
        ("create_account", "01_create_account.mp4", "01_create_account_end.png"),
        ("config_family", "02_config_family.mp4", "02_config_family_end.png"),
        ("login", "03_login.mp4", "03_login_end.png"),
    ):
        phase = _run_parent_phase(
            task_id=task_id,
            feature=feature,
            out=out,
            video_name=video,
            png_name=png,
            resume=feature != "create_account",
        )
        phases.append(phase)
        if not phase.get("ok"):
            break

    cleanup = run_db_cleanup(task_id=task_id, dry_run=False)
    phases.append({"step": "cleanup", "ok": bool(cleanup.get("ok"))})

    ok = all(p.get("ok") for p in phases if p.get("feature"))
    report = {
        "scenario": "02_parent_ui_cadastro",
        "task_id": task_id,
        "ok": ok,
        "seconds": round(time.time() - t0, 1),
        "package_dir": str(out),
        "phases": phases,
    }
    _write_report(out / "report.json", report)
    return report


def main() -> int:
    TMP_BASE.mkdir(parents=True, exist_ok=True)
    home = resolve_android_home()
    if home:
        os.environ["ANDROID_HOME"] = str(home)
        os.environ["PATH"] = str(home / "platform-tools") + os.pathsep + os.environ.get("PATH", "")
    os.environ.setdefault("GF_PARENT_EMULATOR_SERIAL", PARENT_SERIAL)

    results = [scenario_1_parent_seed_login(), scenario_2_parent_ui_full()]
    summary = {
        "at": datetime.now(timezone.utc).isoformat(),
        "scenarios": results,
        "ok": all(r.get("ok") for r in results),
    }
    summary_path = TMP_BASE / "mcp-live-parent-evidence-summary.json"
    _write_report(summary_path, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
    print(f"\nsummary: {summary_path}")
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
