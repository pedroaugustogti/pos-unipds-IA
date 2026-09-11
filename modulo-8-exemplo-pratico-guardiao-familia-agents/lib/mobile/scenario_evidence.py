"""Captura contínua de evidências greeting-* (após suite Appium OK nesta execução).

Pipeline canônico (um fluxo, sem passos soltos):
  1. prepare  — device online, auto_time off (1×), adb reverse Metro
  2. capture  — para cada período (08h → 15h → 21h): date → relaunch → wait greeting → PNG
  3. finalize — restaura auto_time, grava scenario-manifest + timeline

O MP4 do fluxo pairing→home continua vindo do Appium (`video_scope=appium_flow`).
Não usa estado salvo de handoff.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lib.mobile.local_e2e import resolve_android_home
from lib.mobile.mobile_runtime_config import stack
from lib.ticket_output import qa_evidence_dir, resolve_agent_cycle

_GREETING_RE = re.compile(r"^greeting-.+-(\d{1,2})h$", re.IGNORECASE)
_CHILD_DEV_URL = (
    os.environ.get("GF_CHILD_DEV_CLIENT_URL")
    or "guardiao-filho://expo-development-client/?url=http://10.0.2.2:9090"
)
_GREETING_WAIT_SEC = float(os.environ.get("GF_GREETING_WAIT_SEC") or "18")
_POLL_SEC = 0.6


def wants_appium_flow_video(evidence: dict[str, Any] | None) -> bool:
    """Ticket pede 1 MP4 do fluxo Appium (pairing→home), não por saudação."""
    if not isinstance(evidence, dict):
        return False
    scope = str(evidence.get("video_scope") or "").lower()
    if "appium_flow" in scope or "pairing_to_home" in scope:
        return True
    if evidence.get("greeting_video"):
        return False
    return bool(evidence.get("video_mp4")) and "per_period" not in scope


def find_appium_flow_videos(root: Path) -> list[Path]:
    """Localiza MP4 do fluxo em pacote qa-gate ou docs/appium-evidence."""
    if not root.is_dir():
        return []
    candidates: list[Path] = []
    direct = root / "appium-evidence" if (root / "appium-evidence").is_dir() else root
    if direct.is_dir():
        for d in direct.iterdir():
            if d.is_dir() and d.name.lower().startswith("flow_"):
                mp4 = d / "appium-flow.mp4"
                if mp4.is_file():
                    candidates.append(mp4)
            elif d.is_file() and d.suffix.lower() == ".mp4" and (
                d.name.lower() == "appium-flow.mp4" or d.name.lower().startswith("flow_")
            ):
                candidates.append(d)
    if not candidates:
        for p in root.glob("**/flow_*/appium-flow.mp4"):
            candidates.append(p)
    return sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)


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
        # MMDDhhmmYYYY.ss — data fixa QA (08 ago 2026)
        out.append(
            {
                "id": sid,
                "label": label,
                "hour": hour,
                "adb_date": f"0808{hour:02d}002026.00",
            }
        )
    # Ordem canônica do dia: manhã → tarde → noite
    out.sort(key=lambda t: t["hour"])
    return out


def _adb_bin() -> str:
    home = resolve_android_home()
    if not home:
        raise FileNotFoundError("ANDROID_HOME não configurado — instale Android SDK")
    name = "adb.exe" if os.name == "nt" else "adb"
    adb = home / "platform-tools" / name
    if not adb.is_file():
        raise FileNotFoundError(f"adb não encontrado: {adb}")
    return str(adb)


def _run(adb: str, serial: str, *args: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
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


def _timeline_append(timeline: list[dict[str, Any]], phase: str, **extra: Any) -> None:
    timeline.append({"ts": datetime.now(timezone.utc).isoformat(), "phase": phase, **extra})


def _ensure_adb_reverse(adb: str, serial: str, metro_port: int) -> None:
    _run(adb, serial, "reverse", f"tcp:{metro_port}", f"tcp:{metro_port}", timeout=15)
    _run(adb, serial, "reverse", "tcp:3000", "tcp:3000", timeout=15)


def _prepare_clock(adb: str, serial: str, timeline: list[dict[str, Any]]) -> None:
    if os.environ.get("GF_SKIP_ADB_ROOT", "").strip() in ("1", "true", "yes"):
        _timeline_append(timeline, "prepare_clock_skip_root")
        return
    _run(adb, serial, "root", timeout=30)
    _run(adb, serial, "wait-for-device", timeout=60)
    _run(adb, serial, "shell", "settings", "put", "global", "auto_time", "0", timeout=15)
    _run(adb, serial, "shell", "settings", "put", "global", "auto_time_zone", "0", timeout=15)
    _timeline_append(timeline, "prepare_clock", auto_time=0)


def _restore_clock(adb: str, serial: str, timeline: list[dict[str, Any]]) -> None:
    _run(adb, serial, "shell", "settings", "put", "global", "auto_time", "1", timeout=15)
    _run(adb, serial, "shell", "settings", "put", "global", "auto_time_zone", "1", timeout=15)
    # Sync aproximado com host UTC (não crítico se falhar)
    now = datetime.now()
    stamp = now.strftime("%m%d%H%M%Y.%S")
    _run(adb, serial, "shell", "date", stamp, timeout=20)
    _timeline_append(timeline, "restore_clock", auto_time=1, date=stamp)


def _set_device_time(adb: str, serial: str, adb_date: str) -> subprocess.CompletedProcess[str]:
    return _run(adb, serial, "shell", "date", adb_date, timeout=20)


def _relaunch_child_home(adb: str, serial: str, *, hard_stop: bool) -> None:
    """Relança child na home pareada — deep-link Metro (contínuo) ou activity."""
    child = stack("child")
    pkg = child["bundle_id"]
    activity = child["activity"]
    metro = int(child["metro_port"])
    _ensure_adb_reverse(adb, serial, metro)
    if hard_stop:
        _run(adb, serial, "shell", "am", "force-stop", pkg, timeout=30)
        time.sleep(0.8)
    # Deep-link preferencial: mesma entrada do Appium / fast-stack
    view = _run(
        adb,
        serial,
        "shell",
        "am",
        "start",
        "-W",
        "-a",
        "android.intent.action.VIEW",
        "-d",
        _CHILD_DEV_URL,
        pkg,
        timeout=45,
    )
    if view.returncode != 0:
        _run(adb, serial, "shell", "am", "start", "-W", "-n", activity, timeout=45)


def _read_ui_dump(adb: str, serial: str) -> str:
    remote = "/sdcard/_gf_evidence_ui.xml"
    _run(adb, serial, "shell", "uiautomator", "dump", remote, timeout=25)
    dumped = _run(adb, serial, "shell", "cat", remote, timeout=25)
    return dumped.stdout or ""


def _wait_greeting(adb: str, serial: str, label: str, timeout_sec: float) -> tuple[bool, str]:
    deadline = time.time() + timeout_sec
    last_xml = ""
    while time.time() < deadline:
        last_xml = _read_ui_dump(adb, serial)
        if label in last_xml:
            return True, last_xml
        time.sleep(_POLL_SEC)
    return False, last_xml


def _screencap(adb: str, serial: str, dest: Path) -> bool:
    cap = subprocess.run(
        [adb, "-s", serial, "exec-out", "screencap", "-p"],
        capture_output=True,
        timeout=30,
    )
    if cap.returncode != 0 or not cap.stdout:
        return False
    dest.write_bytes(cap.stdout)
    return dest.is_file() and dest.stat().st_size > 0


def capture_scenario_evidence(
    task_id: str,
    scenarios: list[Any],
    *,
    emulator_serial: str = "",
    record_video: bool = False,
    video_sec: int = 8,
    require_child_home: bool = False,
) -> dict[str, Any]:
    """Pipeline contínuo: prepare → capture(08/15/21) → finalize.

    Pré-condição: suite Appium desta execução já concluiu (caller valida suite_ok).
    Não depende de estado salvo em handoff.
    """
    targets = _greeting_targets(scenarios)
    if not targets:
        return {"ok": True, "skipped": True, "reason": "nenhum cenário greeting-* na task"}

    timeline: list[dict[str, Any]] = []
    adb = _adb_bin()
    serial = emulator_serial or stack("child")["emulator"]
    cycle = resolve_agent_cycle(None, "qa-gate")
    base_out = qa_evidence_dir(task_id, cycle=cycle)
    env_ev = (os.environ.get("GF_APPIUM_EVIDENCE_DIR") or "").strip()
    # Se worker já apontou pasta do cenário, usar o parent evidence/ como base
    if env_ev:
        env_path = Path(env_ev)
        base_out = env_path.parent if env_path.name.startswith("greeting-") else env_path
    base_out.mkdir(parents=True, exist_ok=True)

    _timeline_append(timeline, "start", task_id=task_id, targets=[t["id"] for t in targets])

    if require_child_home:
        # Legado: ignorado — evidências usam suite_ok do caller, não handoff.childHome
        _timeline_append(timeline, "note", msg="require_child_home deprecated — using suite gate")

    devices = _run(adb, serial, "get-state", timeout=15)
    if "device" not in (devices.stdout or ""):
        _timeline_append(timeline, "abort", reason="emulator_offline")
        return {
            "ok": False,
            "error": f"emulador {serial} offline — suba stack Appium antes",
            "adb_state": devices.stdout,
            "timeline": timeline,
        }

    # --- 1. prepare (uma vez) ---
    try:
        _ensure_adb_reverse(adb, serial, int(stack("child")["metro_port"]))
        _prepare_clock(adb, serial, timeline)
        _timeline_append(timeline, "prepare_ok")
    except (OSError, subprocess.TimeoutExpired) as exc:
        _timeline_append(timeline, "prepare_fail", error=str(exc))
        return {"ok": False, "error": f"prepare failed: {exc}", "timeline": timeline}

    artifacts: list[dict[str, Any]] = []
    errors: list[str] = []

    # --- 2. capture (contínuo, mesma sessão de relógio) ---
    first = True
    try:
        for scenario in targets:
            sid = scenario["id"]
            label = scenario["label"]
            out_dir = base_out / sid
            out_dir.mkdir(parents=True, exist_ok=True)
            png_path = out_dir / f"capture_{sid}.png"
            _timeline_append(timeline, "period_start", scenario=sid, label=label, hour=scenario["hour"])

            date_r = _set_device_time(adb, serial, scenario["adb_date"])
            if date_r.returncode != 0:
                msg = f"{sid}: date failed: {(date_r.stderr or date_r.stdout)[:200]}"
                errors.append(msg)
                _timeline_append(timeline, "period_fail", scenario=sid, error=msg)
                continue
            _timeline_append(timeline, "date_set", scenario=sid, adb_date=scenario["adb_date"])

            # 1º período: hard stop limpa UI residual; seguintes: soft relaunch
            hard = first
            _relaunch_child_home(adb, serial, hard_stop=hard)
            first = False
            _timeline_append(timeline, "relaunch", scenario=sid, hard_stop=hard)

            ok_greet, _ui = _wait_greeting(adb, serial, label, _GREETING_WAIT_SEC)
            if not ok_greet:
                # Uma retentativa com hard stop (Metro / deep-link falhou)
                _relaunch_child_home(adb, serial, hard_stop=True)
                ok_greet, _ui = _wait_greeting(adb, serial, label, _GREETING_WAIT_SEC)
            if not ok_greet:
                msg = f"{sid}: greeting '{label}' não encontrado na UI após wait"
                errors.append(msg)
                _timeline_append(timeline, "period_fail", scenario=sid, error=msg)
                continue

            if not _screencap(adb, serial, png_path):
                msg = f"{sid}: screencap failed"
                errors.append(msg)
                _timeline_append(timeline, "period_fail", scenario=sid, error=msg)
                continue

            entry: dict[str, Any] = {
                "scenario": sid,
                "label": label,
                "png": str(png_path),
                "hour": scenario["hour"],
                "validated": True,
            }

            if record_video:
                mp4_path = out_dir / f"{sid}.mp4"
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
            _timeline_append(timeline, "period_ok", scenario=sid, png=str(png_path))
    finally:
        # --- 3. finalize (sempre) ---
        try:
            _restore_clock(adb, serial, timeline)
        except (OSError, subprocess.TimeoutExpired) as exc:
            _timeline_append(timeline, "restore_clock_fail", error=str(exc))

    expected = len(targets)
    ok = len(artifacts) >= expected and not errors
    _timeline_append(
        timeline,
        "done",
        ok=ok,
        captured=len(artifacts),
        expected=expected,
        errors=len(errors),
    )
    manifest = {
        "task_id": task_id,
        "type": "scenario_evidence",
        "pipeline": ["prepare", "capture", "finalize"],
        "emulator": serial,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "artifacts": artifacts,
        "errors": errors,
        "timeline": timeline,
        "ok": ok,
    }
    (base_out / "scenario-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest
