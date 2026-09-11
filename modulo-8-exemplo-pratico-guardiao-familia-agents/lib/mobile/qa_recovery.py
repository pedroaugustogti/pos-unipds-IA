"""Orquestração resiliente QA mobile — precheck, matriz reuse/reset e tiers T0–T4."""

from __future__ import annotations

import json
import os
import re
import signal
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from board_automation.board.task_router import load_tasks
from lib.mobile.local_e2e import bootstrap_api_stack, resolve_android_home
from lib.mobile.mobile_e2e_seed import _reset_handoff_cycle
from lib.mobile.mobile_runtime_config import appium_env, stack
from lib.mobile.qa_mobile_mcp import (
    _emulator_ready,
    _load_seed_cache,
    _read_handoff_file,
    _seed_cache_path,
    _stage_handoff_path,
    run_appium_suite,
    run_db_cleanup,
    run_db_seed,
)
from lib.mobile.qa_mobile_setup_evidence import setup_root

RecoveryTier = str  # "T0" | "T1" | "T2" | "T3" | "T4"

RECOVERY_LOG = (
    Path(__file__).resolve().parents[2]
    / "agents"
    / "00-runtime"
    / "system"
    / "observability"
    / "recovery_log.jsonl"
)

HANDOFF_MAX_AGE_SEC = 30 * 60
CHILD_PAIRING_FEATURES = frozenset({"paste_code_parent", "allow_permissions", "go_to_home_child", "pairing"})
STACK_STAGE_ORDER = ("api", "boot", "metro", "apk", "apps_ready")
STACK_REPAIR_TIERS: tuple[RecoveryTier, ...] = ("T0", "T1", "T2", "T4")
MAX_RETRIES_PER_STACK_STAGE = 4
METRO_WAIT_ATTEMPTS = 25
METRO_WAIT_DELAY_SEC = 2.0


def _kill_process_tree(pid: int) -> None:
    """Mata o PID e toda a árvore filha (Windows: taskkill /T; Unix: killpg)."""
    if pid <= 0:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
        return
    try:
        os.killpg(pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        try:
            os.kill(pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError):
            pass


def _run_cmd_tree_timeout(
    cmd: list[str],
    *,
    cwd: str | Path,
    env: dict[str, str],
    timeout_sec: int,
) -> dict[str, Any]:
    """Popen + communicate; no timeout mata a árvore (evita Node/adb órfãos no Windows)."""
    popen_kwargs: dict[str, Any] = {
        "cwd": str(cwd),
        "env": env,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
    }
    if os.name == "nt":
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        popen_kwargs["start_new_session"] = True

    proc = subprocess.Popen(cmd, **popen_kwargs)
    try:
        stdout, stderr = proc.communicate(timeout=timeout_sec)
        return {
            "timed_out": False,
            "returncode": proc.returncode,
            "stdout": stdout or "",
            "stderr": stderr or "",
        }
    except subprocess.TimeoutExpired:
        _kill_process_tree(proc.pid)
        try:
            stdout, stderr = proc.communicate(timeout=20)
        except subprocess.TimeoutExpired:
            try:
                proc.kill()
            except OSError:
                pass
            stdout, stderr = proc.communicate()
        return {
            "timed_out": True,
            "returncode": proc.returncode if proc.returncode is not None else -1,
            "stdout": stdout or "",
            "stderr": stderr or "",
        }
METRO_FAST_STACK_TIMEOUT_SEC = 60
APPIUM_PORT = 4723


def _adb_bin() -> Path | None:
    home = resolve_android_home()
    if not home:
        return None
    adb = home / "platform-tools" / ("adb.exe" if os.name == "nt" else "adb")
    return adb if adb.is_file() else None


def _package_installed(serial: str, bundle_id: str) -> bool:
    """Alinhado com Test-Pkg do fast-stack: `adb shell pm path <pkg>`."""
    adb = _adb_bin()
    if not adb or not serial or not bundle_id:
        return False
    try:
        proc = subprocess.run(
            [str(adb), "-s", serial, "shell", "pm", "path", bundle_id],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    out = (proc.stdout or "") + (proc.stderr or "")
    return "package:" in out


def _probe_apk(*, child_only: bool = True) -> dict[str, Any]:
    """Pacote(s) instalado(s) no emulador — pré-requisito do Appium."""
    child = stack("child")
    missing: list[str] = []
    detail: dict[str, Any] = {}
    child_ok = _package_installed(str(child["emulator"]), str(child["bundle_id"]))
    detail["child"] = {"serial": child["emulator"], "bundle_id": child["bundle_id"], "ok": child_ok}
    if not child_ok:
        missing.append(str(child["bundle_id"]))
    if not child_only:
        parent = stack("parent")
        parent_ok = _package_installed(str(parent["emulator"]), str(parent["bundle_id"]))
        detail["parent"] = {"serial": parent["emulator"], "bundle_id": parent["bundle_id"], "ok": parent_ok}
        if not parent_ok:
            missing.append(str(parent["bundle_id"]))
    return {
        "ok": not missing,
        "detail": detail,
        "missing": missing,
        "source": "pm_path",
    }


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_recovery(
    *,
    task_id: str,
    phase: str,
    from_tier: RecoveryTier | None = None,
    to_tier: RecoveryTier | None = None,
    reason: str = "",
    reusable: list[str] | None = None,
    must_reset: list[str] | None = None,
    ok: bool | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    entry = {
        "ts": _utc_now(),
        "task_id": task_id,
        "phase": phase,
        "from_tier": from_tier,
        "to_tier": to_tier,
        "reason": reason,
        "reusable": reusable or [],
        "must_reset": must_reset or [],
        "ok": ok,
        **(extra or {}),
    }
    try:
        RECOVERY_LOG.parent.mkdir(parents=True, exist_ok=True)
        with RECOVERY_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
    except OSError:
        # container com /workspace:ro — não bloqueia a suite
        alt = Path(os.environ.get("GF_STATUS_DIR") or "/tmp") / "recovery_log.jsonl"
        try:
            alt.parent.mkdir(parents=True, exist_ok=True)
            with alt.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
        except OSError:
            pass


def _kill_listeners_ps(ports: list[int], *, command_match: str = "") -> dict[str, Any]:
    port_csv = ",".join(str(p) for p in ports)
    cmd_clause = ""
    if command_match:
        cmd_clause = (
            "Get-CimInstance Win32_Process -Filter \"Name='node.exe'\" -ErrorAction SilentlyContinue | "
            f"ForEach-Object {{ if ($_.CommandLine -match '{command_match}') "
            "{ Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue } }; "
        )
    ps = (
        f"Get-NetTCPConnection -LocalPort {port_csv} -ErrorAction SilentlyContinue | "
        "ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }; "
        + cmd_clause
    )
    proc = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=45,
    )
    return {"ok": proc.returncode == 0, "returncode": proc.returncode, "stderr": (proc.stderr or "")[-500:]}


def stop_appium_only() -> dict[str, Any]:
    """Encerra só Appium (:4723), preserva Metro."""
    out = _kill_listeners_ps([APPIUM_PORT], command_match="appium")
    out["ports"] = [APPIUM_PORT]
    return out


def stop_metro_only(port: int | None = None) -> dict[str, Any]:
    """Encerra só o Metro da porta (sessão inativa / occupant não-Metro)."""
    resolved = int(port or stack("child")["metro_port"])
    out = _kill_listeners_ps(
        [resolved],
        command_match=rf"expo start --port {resolved}|RCT_METRO_PORT=.{{0,2}}{resolved}|metro",
    )
    out["ports"] = [resolved]
    return out


def stop_appium_runtime() -> dict[str, Any]:
    """Encerra Appium + Metro nas portas do fast-stack (T4 / kill all)."""
    child_metro = int(stack("child")["metro_port"])
    parent_metro = int(stack("parent")["metro_port"])
    return _kill_listeners_ps(
        [APPIUM_PORT, child_metro, parent_metro],
        command_match="appium|metro|react-native|expo start",
    )


def _metro_timeout_sec() -> int:
    raw = str(os.environ.get("GF_METRO_TIMEOUT_SEC") or METRO_FAST_STACK_TIMEOUT_SEC)
    try:
        return max(25, int(raw))
    except ValueError:
        return METRO_FAST_STACK_TIMEOUT_SEC


def _metro_ready(port: int, timeout: float = 3.0) -> bool:
    """Alinhado com Test-Metro do fast-stack: JSON packagerStatus ou body contém 'running'."""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/status", timeout=timeout) as resp:
            if resp.status != 200:
                return False
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                body = json.loads(raw)
                if str(body.get("packagerStatus") or "").lower() == "running":
                    return True
            except (json.JSONDecodeError, ValueError, TypeError):
                pass
            return bool(re.search(r"running", raw, re.IGNORECASE))
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def _metro_log_path(port: int) -> Path:
    return Path(os.environ.get("TEMP") or os.environ.get("TMP") or "/tmp") / f"gf-metro-{port}.log"


def _metro_log_tail(port: int, n: int = 40) -> str:
    path = _metro_log_path(port)
    if not path.is_file():
        return ""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[-n:])
    except OSError:
        return ""


def _metro_ok_from_report(report: dict[str, Any] | None = None) -> bool:
    data = report if isinstance(report, dict) else _parse_fast_stack_report()
    phases = data.get("phases") if isinstance(data.get("phases"), dict) else {}
    metro = phases.get("metro") if isinstance(phases.get("metro"), dict) else {}
    return bool(metro.get("ok"))


def _metro_marker_ok(port: int, *, max_age_sec: int = 180) -> bool:
    setup = setup_root()
    markers = setup / "docs" / "fast-stack.markers"
    if not markers.is_file():
        return False
    text = markers.read_text(encoding="utf-8", errors="replace")
    token = "METRO_READY_OK"
    for line in reversed(text.splitlines()):
        if token not in line or str(port) not in line:
            continue
        ts = line.split("\t", 1)[0].strip()
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return (datetime.now(timezone.utc) - dt).total_seconds() <= max_age_sec
        except ValueError:
            return False
    return False


def _wait_metro_ready(
    port: int,
    *,
    attempts: int | None = None,
    delay_sec: float | None = None,
) -> bool:
    n = attempts if attempts is not None else METRO_WAIT_ATTEMPTS
    delay = METRO_WAIT_DELAY_SEC if delay_sec is None else delay_sec
    for _ in range(n):
        if _metro_ready(port, timeout=5.0):
            return True
        time.sleep(delay)
    return False


def _confirm_metro_after_fast_stack(port: int, report: dict[str, Any] | None) -> bool:
    if _wait_metro_ready(port):
        return True
    if _metro_ok_from_report(report) or _metro_marker_ok(port):
        return _wait_metro_ready(port, attempts=8, delay_sec=2.0) or _metro_ready(port, timeout=5.0)
    return False


def _wait_emulator_ready(serial: str, *, attempts: int = 8, delay_sec: float = 3.0) -> bool:
    for _ in range(attempts):
        if _emulator_ready(serial):
            return True
        time.sleep(delay_sec)
    return False


def _ensure_adb_reverse(*, child_only: bool = True) -> dict[str, Any]:
    home = resolve_android_home()
    if not home:
        return {"ok": False, "error": "ANDROID_HOME ausente"}
    adb = home / "platform-tools" / ("adb.exe" if os.name == "nt" else "adb")
    if not adb.is_file():
        return {"ok": False, "error": f"adb ausente: {adb}"}
    targets = [("child", stack("child"))]
    if not child_only:
        targets.insert(0, ("parent", stack("parent")))
    applied: list[str] = []
    errors: list[str] = []
    for label, cfg in targets:
        serial = str(cfg["emulator"])
        port = int(cfg["metro_port"])
        if not _emulator_ready(serial):
            errors.append(f"{label}:{serial}:not_ready")
            continue
        for args in (
            ["reverse", f"tcp:{port}", f"tcp:{port}"],
            ["reverse", "tcp:3000", "tcp:3000"],
        ):
            try:
                subprocess.run(
                    [str(adb), "-s", serial, *args],
                    capture_output=True,
                    text=True,
                    timeout=20,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                errors.append(f"{label}:{exc}")
        applied.append(f"{serial}:{port}")
    return {"ok": bool(applied) and not errors, "applied": applied, "errors": errors}


def _api_health_ok(url: str = "http://127.0.0.1:3000/api/v1/health") -> bool:
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def precheck_mobile_qa(
    task_id: str,
    *,
    child_only: bool = True,
    require_pairing_code: bool = False,
) -> dict[str, Any]:
    """Checagens de status da suite (API/Docker, emulador, metro, apk) — sem handoff/seed."""
    del require_pairing_code  # seed sempre fresco em qa_validate; não gateia precheck
    checks: dict[str, Any] = {}
    failures: list[str] = []
    child_serial = stack("child")["emulator"]
    child_metro = int(stack("child")["metro_port"])

    checks["api_health"] = _api_health_ok()
    if not checks["api_health"]:
        failures.append("api_health")

    checks["child_emulator"] = _emulator_ready(child_serial)
    if not checks["child_emulator"]:
        failures.append("child_emulator")

    checks["child_metro"] = _metro_ready(child_metro)
    if not checks["child_metro"]:
        failures.append("child_metro")

    child_bundle = str(stack("child")["bundle_id"])
    checks["child_apk"] = _package_installed(child_serial, child_bundle)
    if not checks["child_apk"]:
        failures.append("child_apk")

    # Stack repair: API/emulador → T2; metro/apk → T1. Seed não entra no precheck.
    suggested_stack_tier: RecoveryTier = "T0"
    if "child_emulator" in failures or "api_health" in failures:
        suggested_stack_tier = "T2"
    elif "child_metro" in failures or "child_apk" in failures:
        suggested_stack_tier = "T1"

    stack_stages = probe_stack_stages(child_only=child_only)

    return {
        "ok": not failures,
        "task_id": task_id,
        "child_only": child_only,
        "checks": checks,
        "failures": failures,
        "suggested_tier": suggested_stack_tier,
        "suggested_stack_tier": suggested_stack_tier,
        "suggested_seed_tier": "T3",  # sempre seed fresco após stack
        "stack_stages": stack_stages,
    }


def assess_reuse_matrix(task_id: str) -> dict[str, Any]:
    """Sempre reset: qa_validate não reaproveita seed/handoff."""
    del task_id
    return {
        "task_id": "",
        "reusable": [],
        "must_reset": ["api_stack", "seed", "credentials_file", "child_emulator", "child_metro"],
        "reasons": {"policy": "fresh_seed_every_qa_validate"},
        "needs_fresh_seed": True,
    }


def _classify_suite_failure(suite: dict[str, Any]) -> tuple[RecoveryTier, str]:
    tail = str(suite.get("stdout_tail") or "")
    markers = suite.get("markers") or []
    joined = tail + "\n".join(str(m) for m in markers)

    if "STACK_NOT_READY" in joined or "STACK_NOT_READY" in str(suite.get("blocking_reason") or ""):
        return "T2", "STACK_NOT_READY"
    if "APPS_READY_FAIL" in joined:
        return "T2", "APPS_READY_FAIL"
    if "ECONNREFUSED" in joined or "APPIUM_FAIL" in joined:
        return "T1", "APPIUM_SESSION_FAIL"
    if "Timeout waiting for metro" in joined:
        return "T1", "METRO_TIMEOUT"
    if not suite.get("apps_ready"):
        return "T1", "APPS_NOT_READY"
    if suite.get("suite_ok") and not suite.get("evidence_ok", True):
        return "T0", "EVIDENCE_FAIL"
    return "T2", "SUITE_FAIL"


def _tier_rank(tier: RecoveryTier) -> int:
    return {"T0": 0, "T1": 1, "T2": 2, "T3": 3, "T4": 4}.get(tier, 4)


def _next_stack_repair_tier(tier: RecoveryTier) -> RecoveryTier:
    order = STACK_REPAIR_TIERS
    try:
        idx = order.index(tier)
    except ValueError:
        return "T4"
    return order[min(idx + 1, len(order) - 1)]


def _parse_fast_stack_report(setup: Path | None = None) -> dict[str, Any]:
    root = setup or setup_root()
    report_path = root / "docs" / "fast-stack-last.json"
    if not report_path.is_file():
        return {}
    try:
        return json.loads(report_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return {}


def stop_emulators(*, child_only: bool = True) -> dict[str, Any]:
    """Encerra AVDs child (ou parent+child) via adb emu kill."""
    home = resolve_android_home()
    if not home:
        return {"ok": False, "error": "ANDROID_HOME ausente"}
    adb = home / "platform-tools" / ("adb.exe" if os.name == "nt" else "adb")
    if not adb.is_file():
        return {"ok": False, "error": f"adb ausente: {adb}"}
    serials = [stack("child")["emulator"]]
    if not child_only:
        serials.insert(0, stack("parent")["emulator"])
    killed: list[str] = []
    errors: list[str] = []
    for serial in serials:
        try:
            proc = subprocess.run(
                [str(adb), "-s", serial, "emu", "kill"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if proc.returncode == 0:
                killed.append(serial)
            else:
                err = (proc.stderr or proc.stdout or "").strip()
                if "10061" in err or "refused" in err.lower() or "not found" in err.lower():
                    killed.append(serial)
                else:
                    errors.append(f"{serial}:{err[-120:]}")
        except (OSError, subprocess.TimeoutExpired) as exc:
            errors.append(f"{serial}:{exc}")
    return {"ok": not errors, "killed": killed, "errors": errors}


def kill_all_stack_processes(*, child_only: bool = True) -> dict[str, Any]:
    """T4: mata Appium/Metro/node e emuladores antes de subir stack limpa."""
    stop = stop_appium_runtime()
    emu = stop_emulators(child_only=child_only)
    emu_ok = bool(emu.get("ok")) or bool(emu.get("killed"))
    return {
        "ok": bool(stop.get("ok")) and emu_ok,
        "stop_appium_runtime": stop,
        "stop_emulators": emu,
    }


def _probe_apps_ready(*, child_only: bool = True) -> dict[str, Any]:
    """Alinhado com Invoke-DevicesReadyGate: child-only = emu bootado + Metro /status."""
    child_serial = stack("child")["emulator"]
    child_metro = int(stack("child")["metro_port"])
    if not _emulator_ready(child_serial) or not _metro_ready(child_metro):
        return {"ok": False, "source": "live_gate"}
    if not child_only:
        parent_serial = stack("parent")["emulator"]
        parent_metro = int(stack("parent")["metro_port"])
        if not _emulator_ready(parent_serial) or not _metro_ready(parent_metro):
            return {"ok": False, "source": "live_gate"}
    return {"ok": True, "source": "live_gate"}


def probe_stack_stages(*, child_only: bool = True) -> dict[str, dict[str, Any]]:
    """Valida cada etapa da stack antes de iniciar Appium."""
    child_serial = stack("child")["emulator"]
    parent_serial = stack("parent")["emulator"]
    child_metro = int(stack("child")["metro_port"])
    parent_metro = int(stack("parent")["metro_port"])

    boot_ok = _emulator_ready(child_serial)
    if not child_only:
        boot_ok = boot_ok and _emulator_ready(parent_serial)

    metro_live = _metro_ready(child_metro)
    metro_source = "live" if metro_live else "down"
    if not metro_live and (_metro_ok_from_report() or _metro_marker_ok(child_metro)):
        metro_live = _metro_ready(child_metro, timeout=5.0)
        metro_source = "report_retry" if metro_live else "report_stale"
    if not child_only:
        parent_live = _metro_ready(parent_metro)
        metro_live = metro_live and parent_live

    return {
        "api": {"ok": _api_health_ok(), "detail": "health :3000"},
        "boot": {
            "ok": boot_ok,
            "detail": child_serial if child_only else f"{parent_serial}+{child_serial}",
        },
        "metro": {
            "ok": metro_live,
            "detail": f":{child_metro}" if child_only else f":{parent_metro}+:{child_metro}",
            "source": metro_source,
        },
        "apk": _probe_apk(child_only=child_only),
        "apps_ready": _probe_apps_ready(child_only=child_only),
    }


def _run_fast_stack_phase(
    phase: str,
    *,
    child_only: bool = True,
    parent_only: bool = False,
    skip_build: bool = True,
    skip_appium: bool = True,
    cold_boot: bool = False,
    feature: str = "pairing",
    timeout_sec: int = 900,
    extra_env: dict[str, str] | None = None,
    force_build: bool = False,
) -> dict[str, Any]:
    """Folha fast-stack (Api|Boot|Metro|Build|Smoke|Appium). Só via MCP tool. -Phase All recusado."""
    if os.environ.get("GF_MCP_QA_ENVELOPE") != "1":
        return {
            "ok": False,
            "error": "fast_stack_leaf_requires_mcp",
            "phase": phase,
            "hint": "use qa_init_suite_mobile / qa_generate_evidence / qa_validate",
        }
    chosen = phase.strip() or "Smoke"
    if chosen.lower() == "all":
        return {"ok": False, "error": "phase_all_blocked", "phase": chosen}

    setup = setup_root()
    ps1 = setup / "scripts" / "fast-stack.ps1"
    if not ps1.is_file():
        return {"ok": False, "error": f"ausente: {ps1}"}
    shell = shutil.which("powershell") or shutil.which("pwsh")
    if not shell:
        return {"ok": False, "error": "powershell/pwsh não encontrado"}

    cmd = [shell, "-ExecutionPolicy", "Bypass", "-File", str(ps1), "-Phase", chosen]
    if skip_build and chosen.lower() != "build":
        cmd.append("-SkipBuild")
    elif force_build or chosen.lower() == "build":
        cmd.append("-ForceBuild")
    if skip_appium:
        cmd.append("-SkipAppium")
    if child_only:
        cmd.append("-ChildOnlyQa")
    if parent_only:
        cmd.append("-ParentOnlyQa")
    if cold_boot:
        cmd.append("-ColdBoot")
    if chosen.lower() in ("metro", "smoke"):
        cmd.extend(["-MetroTimeoutSec", str(_metro_timeout_sec())])

    env = dict(os.environ)
    env.update(appium_env(dual_emulator=not child_only and not parent_only))
    env["GF_APPIUM_FEATURE"] = feature
    env["GF_METRO_TIMEOUT_SEC"] = str(_metro_timeout_sec())
    env.pop("GF_ALLOW_FAST_STACK_ORCHESTRATOR", None)
    if extra_env:
        env.update(extra_env)
    if child_only:
        env["GF_QA_CHILD_ONLY"] = "1"
    if parent_only:
        env["GF_QA_PARENT_ONLY"] = "1"
    home = resolve_android_home()
    if home:
        env["ANDROID_HOME"] = str(home)
        env["PATH"] = str(home / "platform-tools") + os.pathsep + env.get("PATH", "")

    report_path = setup / "docs" / "fast-stack-last.json"
    started_mtime = report_path.stat().st_mtime if report_path.is_file() else 0.0
    run = _run_cmd_tree_timeout(cmd, cwd=setup, env=env, timeout_sec=timeout_sec)
    tail = (run.get("stdout") or "") + (run.get("stderr") or "")
    if run.get("timed_out"):
        return {
            "ok": False,
            "error": "fast_stack_timeout",
            "phase": phase,
            "returncode": run.get("returncode"),
            "stdout_tail": tail[-800:],
            "tree_killed": True,
        }

    report = _parse_fast_stack_report(setup)
    if report_path.is_file() and report_path.stat().st_mtime <= started_mtime:
        report = {}
    returncode = int(run.get("returncode") or 1)
    ok = returncode == 0
    if report:
        ok = ok and bool(report.get("ok", True))
    if phase.lower() == "smoke":
        phases = report.get("phases") if isinstance(report.get("phases"), dict) else {}
        apps_phase = phases.get("apps_ready") if isinstance(phases.get("apps_ready"), dict) else {}
        ok = ok or bool(report.get("apps_ready")) or bool(apps_phase.get("ok"))
    if phase.lower() == "build" and returncode == 0:
        # Build leaf: package probe is the source of truth after installDebug
        apk = _probe_apk(child_only=child_only)
        ok = bool(apk.get("ok"))
        report = {**(report or {}), "apk": apk}
    return {
        "ok": ok,
        "phase": phase,
        "returncode": returncode,
        "apps_ready": bool(report.get("apps_ready")) if report else False,
        "report": report,
        "stdout_tail": tail[-1500:],
        "force_build": force_build or chosen.lower() == "build",
    }


def _repair_stack_stage(
    stage: str,
    tier: RecoveryTier,
    *,
    child_only: bool = True,
    skip_build: bool = True,
    feature: str = "pairing",
    timeout_sec: int = 900,
) -> dict[str, Any]:
    """Repara uma etapa da stack conforme tier (T1 Metro/Appium → T2 boot → T4 kill all)."""
    cold = tier in ("T2", "T4")
    actions: list[dict[str, Any]] = []

    if tier == "T4":
        kill = kill_all_stack_processes(child_only=child_only)
        actions.append({"kill_all_stack_processes": kill})
        if not kill.get("ok") and not kill.get("stop_appium_runtime", {}).get("ok"):
            return {"ok": False, "stage": stage, "tier": tier, "actions": actions, "error": "kill_all_failed"}

    if stage == "api":
        if tier in ("T1", "T2", "T4"):
            stop = stop_appium_only()
            actions.append({"stop_appium_only": stop})
        api = bootstrap_api_stack(seed=False)
        actions.append({"bootstrap_api_stack": {"ok": bool(api.get("ok"))}})
        return {"ok": bool(api.get("ok")), "stage": stage, "tier": tier, "actions": actions, "error": api.get("error")}

    if stage == "boot":
        if tier in ("T1", "T2", "T4"):
            stop = stop_appium_only()
            actions.append({"stop_appium_only": stop})
        if tier == "T4":
            emu = stop_emulators(child_only=child_only)
            actions.append({"stop_emulators": emu})
        boot = _run_fast_stack_phase(
            "Boot",
            child_only=child_only,
            skip_build=skip_build,
            cold_boot=cold,
            feature=feature,
            timeout_sec=timeout_sec,
        )
        actions.append({"fast_stack_boot": boot})
        child_serial = stack("child")["emulator"]
        boot_ok = _wait_emulator_ready(child_serial)
        if not child_only:
            boot_ok = boot_ok and _wait_emulator_ready(stack("parent")["emulator"])
        return {
            "ok": boot_ok,
            "stage": stage,
            "tier": tier,
            "actions": actions,
            "error": None if boot_ok else "emulator_not_ready_after_boot",
        }

    if stage == "metro":
        child_serial = stack("child")["emulator"]
        if not _emulator_ready(child_serial):
            boot = _run_fast_stack_phase(
                "Boot",
                child_only=child_only,
                skip_build=skip_build,
                cold_boot=cold,
                feature=feature,
                timeout_sec=timeout_sec,
            )
            actions.append({"fast_stack_boot_before_metro": boot})
            boot_ok = _wait_emulator_ready(child_serial)
            if not child_only:
                boot_ok = boot_ok and _wait_emulator_ready(stack("parent")["emulator"])
            if not boot_ok:
                return {
                    "ok": False,
                    "stage": stage,
                    "tier": tier,
                    "actions": actions,
                    "error": "emulator_not_ready_before_metro",
                }
        if tier in ("T1", "T2"):
            stop = stop_metro_only()
            actions.append({"stop_metro_only": stop})
            if not child_only:
                actions.append({"stop_metro_parent": stop_metro_only(int(stack("parent")["metro_port"]))})
        reverse = _ensure_adb_reverse(child_only=child_only)
        actions.append({"adb_reverse": reverse})
        metro = _run_fast_stack_phase(
            "Metro",
            child_only=child_only,
            skip_build=skip_build,
            cold_boot=False,
            feature=feature,
            timeout_sec=timeout_sec,
        )
        actions.append({"fast_stack_metro": metro})
        port = int(stack("child")["metro_port"])
        metro_ok = _confirm_metro_after_fast_stack(port, metro.get("report") if isinstance(metro.get("report"), dict) else None)
        if not child_only:
            parent_port = int(stack("parent")["metro_port"])
            metro_ok = metro_ok and _confirm_metro_after_fast_stack(parent_port, metro.get("report") if isinstance(metro.get("report"), dict) else None)
        if not metro_ok:
            return {
                "ok": False,
                "stage": stage,
                "tier": tier,
                "actions": actions,
                "metro_log_tail": _metro_log_tail(port),
                "error": "metro_not_ready_after_repair",
            }
        return {
            "ok": True,
            "stage": stage,
            "tier": tier,
            "actions": actions,
            "error": None,
        }

    if stage == "apk":
        if not _emulator_ready(stack("child")["emulator"]):
            boot = _run_fast_stack_phase(
                "Boot",
                child_only=child_only,
                skip_build=True,
                cold_boot=cold,
                feature=feature,
                timeout_sec=timeout_sec,
            )
            actions.append({"fast_stack_boot_before_apk": boot})
            if not _wait_emulator_ready(stack("child")["emulator"]):
                return {
                    "ok": False,
                    "stage": stage,
                    "tier": tier,
                    "actions": actions,
                    "error": "emulator_not_ready_before_apk",
                }
        build = _run_fast_stack_phase(
            "Build",
            child_only=child_only,
            skip_build=False,
            force_build=True,
            feature=feature,
            timeout_sec=timeout_sec,
        )
        actions.append({"fast_stack_build": build})
        apk = _probe_apk(child_only=child_only)
        ok = bool(apk.get("ok")) and bool(build.get("ok"))
        return {
            "ok": ok,
            "stage": stage,
            "tier": tier,
            "actions": actions,
            "apk": apk,
            "error": None if ok else "apk_install_failed",
        }

    if stage == "apps_ready":
        if not (probe_stack_stages(child_only=child_only).get("metro") or {}).get("ok"):
            restart = stop_metro_only()
            actions.append({"watchdog_stop_metro": restart})
            reverse = _ensure_adb_reverse(child_only=child_only)
            actions.append({"adb_reverse": reverse})
            metro = _run_fast_stack_phase(
                "Metro",
                child_only=child_only,
                skip_build=skip_build,
                cold_boot=False,
                feature=feature,
                timeout_sec=timeout_sec,
            )
            actions.append({"watchdog_fast_stack_metro": metro})
            port = int(stack("child")["metro_port"])
            if not _confirm_metro_after_fast_stack(port, metro.get("report") if isinstance(metro.get("report"), dict) else None):
                return {
                    "ok": False,
                    "stage": stage,
                    "tier": tier,
                    "actions": actions,
                    "metro_log_tail": _metro_log_tail(port),
                    "error": "metro_inactive_before_apps_ready",
                }
        if tier == "T4":
            stop = stop_appium_only()
            actions.append({"stop_appium_only": stop})
        smoke = _run_fast_stack_phase(
            "Smoke",
            child_only=child_only,
            skip_build=skip_build,
            cold_boot=cold,
            feature=feature,
            timeout_sec=timeout_sec,
        )
        actions.append({"fast_stack_smoke": smoke})
        ready = _probe_apps_ready(child_only=child_only)
        ok = bool(ready.get("ok"))
        return {
            "ok": ok,
            "stage": stage,
            "tier": tier,
            "actions": actions,
            "apps_ready": ready,
            "error": None if ok else "apps_ready_gate_failed",
        }

    return {"ok": False, "stage": stage, "tier": tier, "actions": actions, "error": f"unknown_stage:{stage}"}


def _repair_t4_full_stack(
    *,
    child_only: bool = True,
    skip_build: bool = True,
    feature: str = "pairing",
    timeout_sec: int = 900,
) -> dict[str, Any]:
    """T4 atômico: kill all → API → boot (cold) → metro → APPS_READY (sem Appium)."""
    actions: list[dict[str, Any]] = []

    kill = kill_all_stack_processes(child_only=child_only)
    actions.append({"kill_all_stack_processes": kill})

    if not _api_health_ok():
        api = bootstrap_api_stack(seed=False)
        actions.append({"bootstrap_api_stack": {"ok": bool(api.get("ok"))}})
        if not api.get("ok"):
            return {
                "ok": False,
                "stage": "t4_full",
                "tier": "T4",
                "actions": actions,
                "error": api.get("error") or "t4_api_failed",
            }

    boot = _run_fast_stack_phase(
        "Boot",
        child_only=child_only,
        skip_build=skip_build,
        cold_boot=True,
        feature=feature,
        timeout_sec=timeout_sec,
    )
    actions.append({"fast_stack_boot": boot})
    child_serial = stack("child")["emulator"]
    boot_ok = _wait_emulator_ready(child_serial, attempts=20, delay_sec=4.0)
    if not child_only:
        boot_ok = boot_ok and _wait_emulator_ready(stack("parent")["emulator"], attempts=20, delay_sec=4.0)
    if not boot_ok:
        return {
            "ok": False,
            "stage": "t4_full",
            "tier": "T4",
            "actions": actions,
            "error": "t4_boot_failed",
        }

    reverse = _ensure_adb_reverse(child_only=child_only)
    actions.append({"adb_reverse": reverse})
    metro = _run_fast_stack_phase(
        "Metro",
        child_only=child_only,
        skip_build=skip_build,
        cold_boot=False,
        feature=feature,
        timeout_sec=timeout_sec,
    )
    actions.append({"fast_stack_metro": metro})
    child_port = int(stack("child")["metro_port"])
    metro_ok = _confirm_metro_after_fast_stack(
        child_port,
        metro.get("report") if isinstance(metro.get("report"), dict) else None,
    )
    if not child_only:
        metro_ok = metro_ok and _confirm_metro_after_fast_stack(
            int(stack("parent")["metro_port"]),
            metro.get("report") if isinstance(metro.get("report"), dict) else None,
        )
    if not metro_ok:
        return {
            "ok": False,
            "stage": "t4_full",
            "tier": "T4",
            "actions": actions,
            "metro_log_tail": _metro_log_tail(child_port),
            "error": "t4_metro_failed",
        }

    build = _run_fast_stack_phase(
        "Build",
        child_only=child_only,
        skip_build=False,
        force_build=True,
        feature=feature,
        timeout_sec=timeout_sec,
    )
    actions.append({"fast_stack_build": build})
    apk = _probe_apk(child_only=child_only)
    if not apk.get("ok") or not build.get("ok"):
        return {
            "ok": False,
            "stage": "t4_full",
            "tier": "T4",
            "actions": actions,
            "apk": apk,
            "error": "t4_apk_failed",
        }

    smoke = _run_fast_stack_phase(
        "Smoke",
        child_only=child_only,
        skip_build=True,
        cold_boot=False,
        feature=feature,
        timeout_sec=timeout_sec,
    )
    actions.append({"fast_stack_smoke": smoke})
    ready = _probe_apps_ready(child_only=child_only)
    ok = bool(ready.get("ok"))
    return {
        "ok": ok,
        "stage": "t4_full",
        "tier": "T4",
        "actions": actions,
        "apps_ready": ready,
        "error": None if ok else "t4_apps_ready_failed",
    }


def _coerce_stack_repair_tier(tier: RecoveryTier) -> RecoveryTier:
    """T3 é seed/DB — ensure de stack usa só T0/T1/T2/T4 (T3 → T2)."""
    if tier in STACK_REPAIR_TIERS:
        return tier
    if tier == "T3":
        return "T2"
    return "T0"


def ensure_suite_stack_ready(
    *,
    task_id: str = "",
    child_only: bool = True,
    skip_build: bool = True,
    feature: str = "pairing",
    repair_tier: RecoveryTier = "T0",
    max_tier: RecoveryTier = "T4",
    timeout_sec: int = 900,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Valida API → boot → Metro → APKS → APPS_READY em ordem.
    Em cada falha, aplica reset incremental (T1→T2→T4) até a stack inteira estar pronta.
    """
    phases: list[dict[str, Any]] = []
    tier = _coerce_stack_repair_tier(repair_tier)
    stage_idx = 0
    retries = 0
    # skip_build=false → força um -ForceBuild no estágio apk mesmo com pacote instalado
    force_rebuild_pending = not skip_build

    while stage_idx < len(STACK_STAGE_ORDER):
        stage = STACK_STAGE_ORDER[stage_idx]
        probed = probe_stack_stages(child_only=child_only)
        stage_info = probed.get(stage) or {}
        stage_ok = bool(stage_info.get("ok"))
        if stage == "apk" and force_rebuild_pending:
            stage_ok = False
        if stage_ok:
            log_recovery(
                task_id=task_id or "unknown",
                phase="stack_stage_ok",
                to_tier=tier,
                reason=stage,
                ok=True,
                extra={"stage_detail": stage_info},
            )
            stage_idx += 1
            retries = 0
            continue

        if dry_run:
            return {
                "ok": False,
                "dry_run": True,
                "blocking_stage": stage,
                "stages": probed,
                "repair_tier": tier,
                "phases": phases,
            }

        if _tier_rank(tier) > _tier_rank(max_tier) or retries >= MAX_RETRIES_PER_STACK_STAGE:
            log_recovery(
                task_id=task_id or "unknown",
                phase="stack_stage_fail",
                from_tier=tier,
                reason=stage,
                ok=False,
                extra={"stages": probed, "retries": retries},
            )
            return {
                "ok": False,
                "apps_ready": False,
                "apps_ready_ok": False,
                "blocking_stage": stage,
                "stages": probed,
                "stack_stages": probed,
                "repair_tier": tier,
                "stack_repair_tier": tier,
                "stack_ensure_phases": phases,
                "phases": phases,
                "error": f"stack_not_ready:{stage}",
            }

        repair = (
            _repair_t4_full_stack(
                child_only=child_only,
                skip_build=skip_build,
                feature=feature,
                timeout_sec=timeout_sec,
            )
            if tier == "T4"
            else _repair_stack_stage(
                stage,
                tier,
                child_only=child_only,
                skip_build=skip_build,
                feature=feature,
                timeout_sec=timeout_sec,
            )
        )
        phases.append(repair)
        if stage == "apk":
            force_rebuild_pending = False
        log_recovery(
            task_id=task_id or "unknown",
            phase="stack_stage_repair",
            from_tier=tier,
            to_tier=tier,
            reason=stage if tier != "T4" else "t4_full",
            ok=repair.get("ok"),
        )

        if tier == "T4" and repair.get("ok"):
            stage_idx = len(STACK_STAGE_ORDER)
            retries = 0
            continue

        after = probe_stack_stages(child_only=child_only)
        stage_ok = bool((after.get(stage) or {}).get("ok"))
        if not stage_ok and stage == "metro" and repair.get("ok"):
            stage_ok = True
        if not stage_ok and stage == "apk" and repair.get("ok"):
            stage_ok = bool((_probe_apk(child_only=child_only) or {}).get("ok"))
        if stage_ok:
            stage_idx += 1
            retries = 0
            continue

        retries += 1
        tier = _next_stack_repair_tier(tier)

    final_stages = probe_stack_stages(child_only=child_only)
    all_ok = all((final_stages.get(s) or {}).get("ok") for s in STACK_STAGE_ORDER)
    log_recovery(
        task_id=task_id or "unknown",
        phase="stack_ready",
        to_tier=tier,
        ok=all_ok,
        extra={"stages": final_stages},
    )
    return {
        "ok": all_ok,
        "apps_ready": all_ok,
        "apps_ready_ok": all_ok,
        "stages": final_stages,
        "stack_stages": final_stages,
        "repair_tier": tier,
        "stack_repair_tier": tier,
        "stack_ensure_phases": phases,
        "phases": phases,
        "error": None if all_ok else "stack_incomplete",
    }


def run_ensure_stack_mobile(
    task_id: str = "",
    *,
    child_only: bool = True,
    skip_build: bool = True,
    feature: str = "",
    repair_tier: RecoveryTier = "T0",
    max_tier: RecoveryTier = "T4",
    timeout_sec: int = 600,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    API pública para ensure de stack (usada por qa_init_suite_mobile).
    Sobe/repara stack até APPS_READY_OK sem executar Appium.
    """
    appium_feature = feature or "pairing"
    if task_id and not feature:
        task = next((t for t in load_tasks() if t.get("id") == task_id), None)
        from lib.mobile.mobile_task import resolve_appium_feature_from_ticket

        appium_feature = resolve_appium_feature_from_ticket(task or {"id": task_id, "qa": {}})

    start_tier = _coerce_stack_repair_tier(repair_tier)
    if start_tier == "T0" and task_id:
        pre = precheck_mobile_qa(task_id, child_only=child_only, require_pairing_code=False)
        if not pre.get("ok"):
            sug = pre.get("suggested_stack_tier") or pre.get("suggested_tier") or "T1"
            sug = _coerce_stack_repair_tier(str(sug))
            if _tier_rank(sug) > _tier_rank(start_tier):
                start_tier = sug

    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "task_id": task_id,
            "would_run": {
                "child_only": child_only,
                "skip_build": skip_build,
                "feature": appium_feature,
                "repair_tier": start_tier,
                "max_tier": max_tier,
                "timeout_sec": timeout_sec,
                "stages": STACK_STAGE_ORDER,
            },
        }

    log_recovery(task_id=task_id or "ensure", phase="stack_ensure_start", to_tier=start_tier, ok=True)
    result = ensure_suite_stack_ready(
        task_id=task_id,
        child_only=child_only,
        skip_build=skip_build,
        feature=appium_feature,
        repair_tier=start_tier,
        max_tier=max_tier,
        timeout_sec=timeout_sec,
        dry_run=False,
    )
    log_recovery(
        task_id=task_id or "ensure",
        phase="stack_ensure_done",
        to_tier=result.get("repair_tier"),
        ok=result.get("ok"),
        reason=result.get("blocking_stage") or ("ready" if result.get("ok") else result.get("error")),
    )
    ready = bool(result.get("ok"))
    out = {
        "ok": ready,
        "task_id": task_id,
        "apps_ready": bool(result.get("apps_ready")),
        "apps_ready_ok": bool(result.get("apps_ready_ok")),
        "blocking_stage": result.get("blocking_stage"),
        "blocking_reason": None if ready else f"STACK_NOT_READY:{result.get('blocking_stage') or result.get('error')}",
        **result,
        "ok": ready,
        "appium_ran": False,
        "skipped_appium": True,
        "suite_ok": ready,
        "evidence_ok": False,
    }
    from lib.mobile.qa_envelope import finalize_qa_envelope

    return finalize_qa_envelope(out, evidence_required=False, recovery_tier=str(result.get("repair_tier") or ""))


def _apply_tier(
    tier: RecoveryTier,
    task_id: str,
    *,
    profile: str,
    bootstrap_api: bool,
    dry_run: bool,
    child_only: bool = True,
) -> dict[str, Any]:
    actions: list[dict[str, Any]] = []

    if tier == "T0":
        return {"ok": True, "tier": tier, "actions": actions}

    if tier == "T4":
        kill = kill_all_stack_processes(child_only=child_only)
        actions.append({"kill_all_stack_processes": kill})

    if tier in ("T1", "T2", "T4"):
        if (probe_stack_stages(child_only=child_only).get("metro") or {}).get("ok") and tier != "T4":
            stop = stop_appium_only()
            actions.append({"stop_appium_only": stop})
        else:
            if tier == "T1":
                actions.append({"stop_metro_only": stop_metro_only()})
                actions.append({"stop_appium_only": stop_appium_only()})
            else:
                stop = stop_appium_runtime()
                actions.append({"stop_appium_runtime": stop})

    if tier in ("T3", "T4"):
        cleanup = run_db_cleanup(task_id=task_id, dry_run=dry_run)
        actions.append({"qa_db_cleanup": cleanup})
        cache = _seed_cache_path(task_id)
        if cache.is_file():
            cache.unlink()
            actions.append({"seed_cache_removed": str(cache)})

    if tier in ("T3", "T4"):
        seed = run_db_seed(
            task_id,
            profile=profile,
            bootstrap_api=bootstrap_api,
            use_task_config=True,
            dry_run=dry_run,
        )
        actions.append({"qa_db_seed": {"ok": bool(seed.get("ok"))}})
        if not seed.get("ok"):
            return {"ok": False, "tier": tier, "actions": actions, "error": seed.get("error")}

    return {"ok": True, "tier": tier, "actions": actions}
