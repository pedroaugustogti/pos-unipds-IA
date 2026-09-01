"""Captura de evidências por cenário declarado em `task.qa.scenarios` (ex.: greeting-*)."""

from __future__ import annotations

import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lib.mobile.local_e2e import resolve_android_home
from lib.mobile.mobile_runtime_config import stack
from lib.ticket_output import qa_evidence_dir, resolve_agent_cycle, resolve_handoff_path

_GREETING_RE = re.compile(r"^greeting-.+-(\d{1,2})h$", re.IGNORECASE)


def scenarios_need_capture(scenarios: list[Any]) -> bool:
    return bool(_greeting_targets(scenarios))


def _greeting_targets(scenarios: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for raw in scenarios:
        sid = str(raw).strip()
        m = _GREETING_RE.match(sid)
        if not m:
            continue
        hour = int(m.group(1))
        if hour < 0 or hour > 23:
            continue
        label = "Bom dia" if hour < 12 else ("Boa tarde" if hour < 18 else "Boa noite")
        out.append(
            {
                "id": sid,
                "label": label,
                "hour": hour,
                "adb_date": f"0808{hour:02d}002026.00",
            }
        )
    return out


def _adb_bin() -> str:
    home = resolve_android_home()
    if not home:
        raise FileNotFoundError("ANDROID_HOME não configurado — instale Android SDK")
    name = "adb.exe" if __import__("os").name == "nt" else "adb"
    adb = home / "platform-tools" / name
    if not adb.is_file():
        raise FileNotFoundError(f"adb não encontrado: {adb}")
    return str(adb)


def _run(adb: str, serial: str, *args: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    import os

    env = dict(os.environ)
    home = resolve_android_home()
    if home:
        env["ANDROID_HOME"] = str(home)
        sep = ";" if os.name == "nt" else ":"
        env["PATH"] = str(home / "platform-tools") + sep + env.get("PATH", "")
    return subprocess.run(
        [adb, "-s", serial, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env=env,
    )


def _prepare_time_override(adb: str, serial: str) -> None:
    import os

    if os.environ.get("GF_SKIP_ADB_ROOT", "").strip() in ("1", "true", "yes"):
        return
    _run(adb, serial, "root", timeout=30)
    _run(adb, serial, "wait-for-device", timeout=60)
    _run(adb, serial, "shell", "settings", "put", "global", "auto_time", "0", timeout=15)
    _run(adb, serial, "shell", "settings", "put", "global", "auto_time_zone", "0", timeout=15)


def _set_device_time(adb: str, serial: str, adb_date: str) -> subprocess.CompletedProcess[str]:
    _prepare_time_override(adb, serial)
    return _run(adb, serial, "shell", "date", adb_date, timeout=20)


def _relaunch_child(adb: str, serial: str) -> None:
    child = stack("child")
    pkg = child["bundle_id"]
    activity = child["activity"]
    _run(adb, serial, "shell", "am", "force-stop", pkg, timeout=30)
    time.sleep(1)
    _run(adb, serial, "shell", "am", "start", "-n", activity, timeout=30)
    time.sleep(4)


def capture_scenario_evidence(
    task_id: str,
    scenarios: list[Any],
    *,
    emulator_serial: str = "",
    record_video: bool = True,
    video_sec: int = 8,
) -> dict[str, Any]:
    """PNG (+ MP4) por slug `greeting-*-NNh` em `task.qa.scenarios`."""
    targets = _greeting_targets(scenarios)
    if not targets:
        return {"ok": True, "skipped": True, "reason": "nenhum cenário greeting-* na task"}

    adb = _adb_bin()
    serial = emulator_serial or stack("child")["emulator"]
    handoff = None
    try:
        hp = resolve_handoff_path(task_id)
        if hp.is_file():
            handoff = json.loads(hp.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        handoff = None
    cycle = resolve_agent_cycle(handoff, "qa-gate")
    out_dir = qa_evidence_dir(task_id, cycle=cycle)

    artifacts: list[dict[str, Any]] = []
    errors: list[str] = []

    devices = _run(adb, serial, "devices", timeout=15)
    if serial not in (devices.stdout or ""):
        return {
            "ok": False,
            "error": f"emulador {serial} offline — suba stack Appium antes",
            "adb_devices": devices.stdout,
        }

    for scenario in targets:
        sid = scenario["id"]
        png_path = out_dir / f"{sid}.png"
        mp4_path = out_dir / f"{sid}.mp4"
        try:
            date_r = _set_device_time(adb, serial, scenario["adb_date"])
            if date_r.returncode != 0:
                errors.append(f"{sid}: date failed: {(date_r.stderr or date_r.stdout)[:200]}")
                continue
            _relaunch_child(adb, serial)
            cap = subprocess.run(
                [adb, "-s", serial, "exec-out", "screencap", "-p"],
                capture_output=True,
                timeout=30,
            )
            if cap.returncode != 0 or not cap.stdout:
                errors.append(f"{sid}: screencap failed")
                continue
            png_path.write_bytes(cap.stdout)
            entry: dict[str, Any] = {
                "scenario": sid,
                "label": scenario["label"],
                "png": str(png_path),
                "hour": scenario["hour"],
            }
            if record_video:
                remote = f"/sdcard/{sid}.mp4"
                _run(adb, serial, "shell", "rm", "-f", remote, timeout=10)
                rec = subprocess.Popen(
                    [adb, "-s", serial, "shell", "screenrecord", "--time-limit", str(video_sec), remote],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                time.sleep(video_sec + 1)
                rec.terminate()
                try:
                    rec.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    rec.kill()
                pull = _run(adb, serial, "pull", remote, str(mp4_path), timeout=120)
                if pull.returncode == 0 and mp4_path.is_file() and mp4_path.stat().st_size > 0:
                    entry["mp4"] = str(mp4_path)
                else:
                    errors.append(f"{sid}: mp4 pull failed")
            artifacts.append(entry)
        except (OSError, subprocess.TimeoutExpired) as exc:
            errors.append(f"{sid}: {exc}")

    expected = len(targets)
    manifest = {
        "task_id": task_id,
        "type": "scenario_evidence",
        "emulator": serial,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "artifacts": artifacts,
        "errors": errors,
        "ok": len(artifacts) >= expected and not errors,
    }
    (out_dir / "scenario-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest
