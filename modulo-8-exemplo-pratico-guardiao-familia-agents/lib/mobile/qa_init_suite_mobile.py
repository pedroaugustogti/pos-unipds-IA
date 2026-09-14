"""qa_init_suite_mobile — prep async por suite (parent/child) até apps_ready_ok.

Contrato de entrada: suites_mobile = {parent: bool, child: bool}
Contrato de saída:
  task_id, apps_ready_ok,
  checks_parent? / checks_child?: {docker_api|adb|emulator|metro|apk|appium, error_runtime}
  cada check: {ok, attempts, time_exec, detail, mode?}
  error_runtime[check]: {type, time_exec, detail}
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from queue import Empty, Queue
from typing import Any

from lib.mobile.local_e2e import bootstrap_api_stack, resolve_android_home
from lib.mobile.mobile_runtime_config import stack
from lib.mobile.qa_mobile_mcp import _emulator_ready
from lib.mobile.metro_bundle_state import assess_metro_bundle, record_metro_bundle_served
from lib.mobile.qa_recovery import (
    _api_health_ok,
    _metro_ready,
    _package_installed,
    _repair_stack_stage,
    _run_fast_stack_phase,
    _wait_metro_ready,
    log_recovery,
    stop_appium_only,
    stop_metro_only,
)

MAX_ATTEMPTS_PER_CHECK = 3
EVENT_POLL_SEC = 0.25
DEFAULT_APPIUM_PORT = int(os.environ.get("GF_APPIUM_PORT") or "4723")

WAVE_A = ("docker_api", "adb", "emulator")
WAVE_B = ("metro", "apk")
STACK_CHECKS = WAVE_A + WAVE_B
ALL_CHECKS = STACK_CHECKS + ("appium",)

INIT_LOG = (
    Path(__file__).resolve().parents[2]
    / "agents"
    / "00-runtime"
    / "system"
    / "observability"
    / "qa_init_suite_mobile.jsonl"
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_init_log(row: dict[str, Any]) -> None:
    INIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with INIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": _now(), **row}, ensure_ascii=False, default=str) + "\n")


def _port_open(host: str, port: int, timeout: float = 1.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _adb_bin() -> str | None:
    home = resolve_android_home()
    if home:
        cand = home / "platform-tools" / ("adb.exe" if os.name == "nt" else "adb")
        if cand.is_file():
            return str(cand)
    return shutil.which("adb")


def _adb_server_ok() -> dict[str, Any]:
    adb = _adb_bin()
    if not adb:
        return {"ok": False, "detail": "adb binary ausente"}
    try:
        r = subprocess.run(
            [adb, "devices"],
            capture_output=True,
            text=True,
            timeout=12,
            check=False,
        )
        out = (r.stdout or "") + (r.stderr or "")
        ok = r.returncode == 0 and "List of devices" in out
        return {"ok": ok, "detail": out.strip()[:240], "adb": adb}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "detail": str(exc), "adb": adb}


def _appium_status(port: int = DEFAULT_APPIUM_PORT) -> dict[str, Any]:
    if not _port_open("127.0.0.1", port):
        return {"ok": False, "mode": "cold", "detail": f"port {port} closed", "port": port}
    url = f"http://127.0.0.1:{port}/status"
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            body = resp.read().decode("utf-8", errors="replace")[:400]
            return {
                "ok": True,
                "mode": "warm",
                "detail": body,
                "port": port,
                "http_status": getattr(resp, "status", 200),
            }
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {
            "ok": False,
            "mode": "cold",
            "detail": f"port open but /status fail: {exc}",
            "port": port,
        }


def _listening_pids(port: int) -> list[int]:
    """PIDs em LISTEN na porta (Windows via Get-NetTCPConnection)."""
    if os.name != "nt":
        return []
    ps = (
        f"Get-NetTCPConnection -LocalPort {int(port)} -State Listen "
        "-ErrorAction SilentlyContinue | "
        "Select-Object -ExpandProperty OwningProcess -Unique"
    )
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    pids: list[int] = []
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if line.isdigit():
            pids.append(int(line))
    return pids


def _pid_cmdline(pid: int) -> str:
    if os.name != "nt" or pid <= 0:
        return ""
    ps = (
        f"$p = Get-CimInstance Win32_Process -Filter \"ProcessId={int(pid)}\" "
        "-ErrorAction SilentlyContinue; if ($p) { $p.CommandLine }"
    )
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            check=False,
        )
        return (proc.stdout or "").strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _cmdline_is_appium(cmdline: str) -> bool:
    low = (cmdline or "").lower()
    return "appium" in low


def _classify_port_occupant(port: int) -> dict[str, Any]:
    """Classifica quem ocupa a porta: appium | foreign | free."""
    st = _appium_status(port)
    if st.get("ok"):
        return {
            "kind": "appium",
            "pids": _listening_pids(port),
            "detail": "appium /status ok",
            "status": st,
        }
    pids = _listening_pids(port)
    if not pids and not _port_open("127.0.0.1", port):
        return {"kind": "free", "pids": [], "detail": f"port {port} free", "status": st}
    cmds = {pid: _pid_cmdline(pid) for pid in pids}
    if any(_cmdline_is_appium(c) for c in cmds.values()):
        return {
            "kind": "appium",
            "pids": pids,
            "cmds": cmds,
            "detail": "appium process on port but /status not ready",
            "status": st,
        }
    if pids or _port_open("127.0.0.1", port):
        return {
            "kind": "foreign",
            "pids": pids,
            "cmds": cmds,
            "detail": f"non-appium occupant on :{port}",
            "status": st,
        }
    return {"kind": "free", "pids": [], "detail": f"port {port} free", "status": st}


def _kill_pids(pids: list[int]) -> dict[str, Any]:
    killed: list[int] = []
    errors: list[str] = []
    for pid in pids:
        try:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/PID", str(pid), "/F", "/T"],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    check=False,
                )
            else:
                os.kill(pid, 9)
            killed.append(pid)
        except (OSError, subprocess.TimeoutExpired) as exc:
            errors.append(f"{pid}:{exc}")
    time.sleep(0.6)
    return {"ok": not errors, "killed": killed, "errors": errors}


def _resolve_appium_cwd() -> Path:
    from lib.mobile.mobile_setup_client import appium_root, setup_root

    candidates = [appium_root(), setup_root()]
    for cand in candidates:
        try:
            if (cand / "node_modules" / "appium").is_dir():
                return cand
        except OSError:
            continue
    for cand in candidates:
        try:
            if cand.is_dir():
                return cand
        except OSError:
            continue
    return Path.cwd()


def _start_appium_cold(
    *,
    host: str = "127.0.0.1",
    port: int = DEFAULT_APPIUM_PORT,
    wait_sec: int = 60,
) -> dict[str, Any]:
    """Sobe Appium (cold) — preferência: ensureAppiumRunning do mobile-setup."""
    from lib.mobile.mobile_setup_client import appium_root

    cwd = _resolve_appium_cwd()
    node_opts = " ".join(
        x
        for x in [
            os.environ.get("NODE_OPTIONS", ""),
            "--max-old-space-size=2048",
            "--use-system-ca",
        ]
        if x
    ).strip()
    env = {
        **os.environ,
        "NODE_OPTIONS": node_opts,
        "npm_config_yes": "true",
        "APPIUM_HOST": host,
        "APPIUM_PORT": str(port),
    }

    driver = appium_root() / "_shared" / "driver.mjs"
    if driver.is_file():
        js = (
            "import { ensureAppiumRunning } from './_shared/driver.mjs';"
            f"await ensureAppiumRunning({host!r}, {int(port)});"
            "console.log('APPIUM_ENSURE_OK');"
        )
        try:
            proc = subprocess.run(
                ["node", "--input-type=module", "-e", js],
                cwd=str(appium_root()),
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=max(30, int(wait_sec) + 15),
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {
                "ok": False,
                "error": f"ensureAppiumRunning failed: {exc}",
                "cwd": str(appium_root()),
                "mode": "cold",
                "port": port,
            }
        out = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
        st = _appium_status(port)
        if st.get("ok"):
            return {
                "ok": True,
                "cwd": str(appium_root()),
                "port": port,
                "mode": "cold",
                "via": "ensureAppiumRunning",
                "log_tail": out[-800:],
            }
        return {
            "ok": False,
            "error": (
                f"ensureAppiumRunning exit={proc.returncode}; "
                f"status={st.get('detail')}; log={out[-600:]}"
            ),
            "cwd": str(appium_root()),
            "port": port,
            "mode": "cold",
            "returncode": proc.returncode,
        }

    # fallback: npx appium detached
    npx = "npx.cmd" if os.name == "nt" else "npx"
    cmd = f"{npx} --yes appium --address {host} --port {int(port)} --relaxed-security"
    log_path = Path(os.environ.get("TEMP") or os.environ.get("TMP") or ".") / f"qa_appium_cold_{port}.log"
    try:
        log_f = log_path.open("w", encoding="utf-8")
    except OSError:
        log_f = subprocess.DEVNULL
        log_path = None
    popen_kwargs: dict[str, Any] = {
        "cwd": str(cwd),
        "env": env,
        "stdout": log_f,
        "stderr": subprocess.STDOUT if log_f is not subprocess.DEVNULL else subprocess.DEVNULL,
        "stdin": subprocess.DEVNULL,
    }
    if os.name == "nt":
        popen_kwargs["shell"] = True
        popen_kwargs["creationflags"] = (
            getattr(subprocess, "DETACHED_PROCESS", 0)
            | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        )
    else:
        popen_kwargs["start_new_session"] = True
    try:
        child = subprocess.Popen(cmd, **popen_kwargs)
    except OSError as exc:
        if hasattr(log_f, "close"):
            log_f.close()
        return {"ok": False, "error": f"spawn_failed: {exc}", "cwd": str(cwd), "cmd": cmd}

    if hasattr(log_f, "close"):
        log_f.close()

    for i in range(max(1, int(wait_sec))):
        time.sleep(1)
        st = _appium_status(port)
        if st.get("ok"):
            return {
                "ok": True,
                "pid": child.pid,
                "waited_sec": i + 1,
                "cwd": str(cwd),
                "port": port,
                "mode": "cold",
                "via": "npx",
            }
    log_tail = ""
    if log_path and log_path.is_file():
        try:
            log_tail = log_path.read_text(encoding="utf-8", errors="replace")[-800:]
        except OSError:
            log_tail = ""
    return {
        "ok": False,
        "error": f"appium not ready at http://{host}:{port}/status; {log_tail}",
        "pid": child.pid,
        "cwd": str(cwd),
        "port": port,
        "mode": "cold",
        "via": "npx",
    }


def _ensure_appium_for_check(
    *,
    host: str = "127.0.0.1",
    port: int = DEFAULT_APPIUM_PORT,
    wait_sec: int = 60,
) -> dict[str, Any]:
    """Fluxo do check Appium:
    1) porta em uso → se Appium: warm; se não: mata ocupante
    2) se Appium off → sobe cold na porta
    3) retorno para a fila re-probrar / notificar
    """
    actions: list[dict[str, Any]] = []
    occ = _classify_port_occupant(port)
    actions.append({"classify": occ})

    if occ.get("kind") == "appium" and bool((occ.get("status") or {}).get("ok")):
        return {
            "ok": True,
            "check": "appium",
            "mode": "warm",
            "detail": f"appium warm on :{port}",
            "actions": actions,
        }

    if occ.get("kind") == "foreign":
        kill = _kill_pids(list(occ.get("pids") or []))
        actions.append({"kill_foreign": kill})
        # fallback: limpa listeners da porta se ainda ocupada
        if _port_open(host, port):
            actions.append({"kill_port_fallback": stop_appium_only()})
    elif occ.get("kind") == "appium":
        # processo Appium sem /status → reinicia cold
        actions.append({"kill_broken_appium": stop_appium_only()})

    # porta livre / Appium off → cold start
    if _appium_status(port).get("ok"):
        return {
            "ok": True,
            "check": "appium",
            "mode": "warm",
            "detail": f"appium ready after cleanup :{port}",
            "actions": actions,
        }

    start = _start_appium_cold(host=host, port=port, wait_sec=wait_sec)
    actions.append({"start_cold": start})
    ok = bool(start.get("ok"))
    return {
        "ok": ok,
        "check": "appium",
        "mode": "cold",
        "detail": (
            f"appium cold started on :{port}"
            if ok
            else str(start.get("error") or f"appium cold start failed :{port}")
        ),
        "actions": actions,
        "error": None if ok else str(start.get("error") or "APPIUM_COLD_START_FAIL"),
    }


def normalize_suites_mobile(
    suites_mobile: dict[str, Any] | str | None = None,
    *,
    child_only: bool | None = None,
    parent_only: bool | None = None,
) -> dict[str, bool]:
    """Normaliza suites_mobile = {parent, child}."""
    raw = suites_mobile
    if isinstance(raw, str) and raw.strip():
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            raw = None
    if isinstance(raw, dict):
        parent = bool(raw.get("parent"))
        child = bool(raw.get("child"))
        if parent or child:
            return {"parent": parent, "child": child}
    if parent_only is True:
        return {"parent": True, "child": False}
    if child_only is False and parent_only is False:
        return {"parent": True, "child": True}
    if child_only is False and parent_only is True:
        return {"parent": True, "child": False}
    if child_only is True:
        return {"parent": False, "child": True}
    return {"parent": False, "child": True}


def _probe_check(name: str, *, app: str = "child") -> dict[str, Any]:
    target = stack("parent" if app == "parent" else "child")
    serial = str(target["emulator"])
    metro = int(target["metro_port"])
    bundle = str(target["bundle_id"])

    if name == "docker_api":
        ok = _api_health_ok()
        return {"check": name, "ok": ok, "detail": "health :3000" if ok else "api health down"}
    if name == "adb":
        probe = _adb_server_ok()
        return {"check": name, "ok": bool(probe.get("ok")), "detail": probe.get("detail")}
    if name == "emulator":
        ok = _emulator_ready(serial)
        return {"check": name, "ok": ok, "detail": serial if ok else f"{serial} not device"}
    if name == "metro":
        if not _metro_ready(metro):
            return {"check": name, "ok": False, "detail": f":{metro} down"}
        bundle = assess_metro_bundle(app)
        if bundle.get("stale"):
            dirty = int((bundle.get("current") or {}).get("dirty_count") or 0)
            dirty_hint = f", {dirty} file(s) changed" if dirty else ""
            return {
                "check": name,
                "ok": False,
                "detail": (
                    f":{metro} bundle_stale ({bundle.get('reason')}{dirty_hint}) "
                    f"served={bundle.get('served_fingerprint', '')[:16]} "
                    f"current={bundle.get('current_fingerprint', '')[:16]}"
                ),
                "bundle_stale": True,
                "bundle": bundle,
                "error_type": "metro_bundle_stale",
            }
        return {
            "check": name,
            "ok": True,
            "detail": f":{metro} fresh ({bundle.get('current_fingerprint', '')[:20]})",
            "bundle": bundle,
        }
    if name == "apk":
        ok = _package_installed(serial, bundle) if _emulator_ready(serial) else False
        return {
            "check": name,
            "ok": ok,
            "detail": bundle if ok else f"pm path fail / emu down ({bundle})",
        }
    if name == "appium":
        st = _appium_status()
        return {
            "check": name,
            "ok": bool(st.get("ok")),
            "detail": st.get("detail"),
            "mode": st.get("mode"),
            "port": st.get("port"),
        }
    return {"check": name, "ok": False, "detail": f"unknown check {name}"}


def _repair_check(
    name: str,
    *,
    app: str,
    task_id: str,
    skip_build: bool,
    feature: str,
    timeout_sec: int,
    appium_mode: str,
) -> dict[str, Any]:
    os.environ.setdefault("GF_MCP_QA_ENVELOPE", "1")
    actions: list[dict[str, Any]] = []
    parent_only = app == "parent"

    if name == "docker_api":
        api = bootstrap_api_stack(seed=False)
        actions.append({"bootstrap_api_stack": {"ok": bool(api.get("ok"))}})
        return {"ok": bool(api.get("ok")), "check": name, "actions": actions, "error": api.get("error")}

    if name == "adb":
        adb = _adb_bin()
        if not adb:
            return {"ok": False, "check": name, "actions": actions, "error": "adb missing"}
        for cmd in ([adb, "kill-server"], [adb, "start-server"]):
            subprocess.run(cmd, capture_output=True, text=True, timeout=20, check=False)
        probe = _adb_server_ok()
        actions.append({"adb_restart": probe})
        return {"ok": bool(probe.get("ok")), "check": name, "actions": actions}

    if name == "emulator":
        if parent_only:
            repair = _run_fast_stack_phase(
                "Boot", child_only=False, parent_only=True, skip_build=True,
                feature=feature, timeout_sec=timeout_sec,
            )
        else:
            repair = _repair_stack_stage(
                "boot", "T2", child_only=True, skip_build=True,
                feature=feature, timeout_sec=timeout_sec,
            )
        actions.append(repair)
        return {"ok": bool(repair.get("ok")), "check": name, "actions": actions, "error": repair.get("error")}

    if name == "metro":
        bundle_before = assess_metro_bundle(app)
        actions.append({"metro_bundle_before": bundle_before})
        stop_metro_only(int(stack(app)["metro_port"]))
        if parent_only:
            repair = _run_fast_stack_phase(
                "Metro", child_only=False, parent_only=True, skip_build=True,
                feature=feature, timeout_sec=timeout_sec,
            )
        else:
            repair = _repair_stack_stage(
                "metro", "T1", child_only=True, skip_build=True,
                feature=feature, timeout_sec=timeout_sec,
            )
        actions.append(repair)
        ok = bool(repair.get("ok"))
        port = int(stack(app)["metro_port"])
        if ok and not _wait_metro_ready(port, attempts=12, delay_sec=2.0):
            ok = False
            repair = {**repair, "error": "metro_not_ready_after_bundle_refresh"}
        if ok:
            recorded = record_metro_bundle_served(app, task_id=task_id)
            actions.append({"metro_bundle_recorded": recorded})
        return {
            "ok": ok,
            "check": name,
            "actions": actions,
            "error": repair.get("error"),
            "detail": (
                f"metro refreshed for {bundle_before.get('reason') or 'bundle_sync'}"
                if ok
                else repair.get("error")
            ),
        }

    if name == "apk":
        if parent_only:
            repair = _run_fast_stack_phase(
                "Build" if not skip_build else "Smoke",
                child_only=False, parent_only=True,
                skip_build=skip_build, force_build=not skip_build,
                feature=feature, timeout_sec=timeout_sec,
            )
        else:
            repair = _repair_stack_stage(
                "apk", "T1", child_only=True, skip_build=skip_build,
                feature=feature, timeout_sec=timeout_sec,
            )
        actions.append(repair)
        return {"ok": bool(repair.get("ok")), "check": name, "actions": actions, "error": repair.get("error")}

    if name == "appium":
        ensure = _ensure_appium_for_check(
            port=DEFAULT_APPIUM_PORT,
            wait_sec=min(60, max(20, timeout_sec // 4)),
        )
        actions.extend(list(ensure.get("actions") or []))
        return {
            "ok": bool(ensure.get("ok")),
            "check": name,
            "actions": actions,
            "mode": ensure.get("mode") or "cold",
            "detail": ensure.get("detail"),
            "error": ensure.get("error"),
        }

    return {"ok": False, "check": name, "actions": actions, "error": f"unknown repair {name}"}


def _emit(q: Queue, event: dict[str, Any]) -> None:
    event = {**event, "ts": _now()}
    q.put(event)
    _append_init_log({"phase": "event", **event})


def _metro_bundle_refreshed(timeline: list[dict[str, Any]]) -> bool:
    """True se algum repair metro gravou bundle novo nesta execução."""
    return any(
        isinstance(ev, dict)
        and ev.get("type") == "repair_result"
        and ev.get("check") == "metro"
        and ev.get("ok")
        and "metro refreshed" in str(ev.get("detail") or "").lower()
        for ev in timeline
    )


def _fmt_time_exec(seconds: float) -> str:
    if seconds < 0:
        seconds = 0.0
    if seconds < 10:
        return f"{seconds:.1f}s"
    return f"{int(round(seconds))}s"


def _checks_block(
    state: dict[str, dict[str, Any]],
    *,
    fatal: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Monta checks_* com time_exec + error_runtime aninhado."""
    checks: dict[str, Any] = {}
    error_runtime: dict[str, Any] = {}
    for c in ALL_CHECKS:
        st = state[c]
        elapsed = float(st.get("elapsed_sec") or 0.0)
        time_exec = _fmt_time_exec(elapsed)
        row: dict[str, Any] = {
            "ok": bool(st.get("ok")),
            "attempts": int(st.get("attempts") or 0),
            "time_exec": time_exec,
            "detail": st.get("detail") or "",
        }
        if "mode" in st:
            row["mode"] = st["mode"]
        checks[c] = row

        err_type = ""
        err_detail = ""
        if not st.get("ok"):
            if fatal and fatal.get("check") == c:
                err_type = str(fatal.get("reason") or "check_failed")
                err_detail = str(fatal.get("detail") or st.get("detail") or "")
            else:
                err_type = str(st.get("error_type") or "check_failed")
                err_detail = str(st.get("detail") or "")
        error_runtime[c] = {
            "type": err_type,
            "time_exec": time_exec,
            "detail": err_detail,
        }
    checks["error_runtime"] = error_runtime
    return checks


def _init_one_app(
    app: str,
    *,
    task_id: str,
    skip_build: bool,
    feature: str,
    timeout_sec: int,
    max_attempts: int,
) -> dict[str, Any]:
    """Fila de eventos + recovery para um app (parent|child)."""
    events: Queue = Queue()
    state: dict[str, dict[str, Any]] = {
        c: {
            "ok": False,
            "attempts": 0,
            "detail": "",
            "events": [],
            "started_at": None,
            "elapsed_sec": 0.0,
            "error_type": "",
        }
        for c in ALL_CHECKS
    }
    repair_inflight: set[str] = set()
    wave_b_started = False
    appium_started = False
    fatal: dict[str, Any] | None = None
    timeline: list[dict[str, Any]] = []
    pool = ThreadPoolExecutor(max_workers=6, thread_name_prefix=f"qa-init-{app}")

    def _mark_start(check: str) -> None:
        if state[check]["started_at"] is None:
            state[check]["started_at"] = time.monotonic()

    def _mark_elapsed(check: str) -> None:
        started = state[check].get("started_at")
        if started is not None:
            state[check]["elapsed_sec"] = max(
                float(state[check].get("elapsed_sec") or 0.0),
                time.monotonic() - float(started),
            )

    def _run_probe(check: str) -> None:
        _mark_start(check)
        t0 = time.monotonic()
        try:
            result = _probe_check(check, app=app)
            _emit(
                events,
                {
                    "type": "check_result",
                    "app": app,
                    "check": check,
                    "ok": bool(result.get("ok")),
                    "detail": result.get("detail"),
                    "mode": result.get("mode"),
                    "attempt": state[check]["attempts"],
                    "elapsed_sec": time.monotonic() - t0,
                },
            )
        except Exception as exc:  # noqa: BLE001
            _emit(
                events,
                {
                    "type": "check_result",
                    "app": app,
                    "check": check,
                    "ok": False,
                    "detail": f"probe_exception: {exc}",
                    "attempt": state[check]["attempts"],
                    "elapsed_sec": time.monotonic() - t0,
                    "error_type": "probe_exception",
                },
            )

    def _run_repair(check: str, appium_mode: str = "cold") -> None:
        _mark_start(check)
        t0 = time.monotonic()
        try:
            repair = _repair_check(
                check,
                app=app,
                task_id=task_id,
                skip_build=skip_build,
                feature=feature,
                timeout_sec=timeout_sec,
                appium_mode=appium_mode,
            )
            _emit(
                events,
                {
                    "type": "repair_result",
                    "app": app,
                    "check": check,
                    "ok": bool(repair.get("ok")),
                    "detail": repair.get("detail") or repair.get("error") or repair.get("mode") or "",
                    "mode": repair.get("mode"),
                    "attempt": state[check]["attempts"],
                    "elapsed_sec": time.monotonic() - t0,
                    "error_type": "" if repair.get("ok") else str(repair.get("error") or "repair_failed"),
                },
            )
        except Exception as exc:  # noqa: BLE001
            _emit(
                events,
                {
                    "type": "repair_result",
                    "app": app,
                    "check": check,
                    "ok": False,
                    "detail": f"repair_exception: {exc}",
                    "attempt": state[check]["attempts"],
                    "elapsed_sec": time.monotonic() - t0,
                    "error_type": "repair_exception",
                },
            )
        finally:
            repair_inflight.discard(check)

    for check in WAVE_A:
        pool.submit(_run_probe, check)

    deadline = time.time() + max(timeout_sec, 120)
    apps_ready = False
    try:
        while time.time() < deadline and fatal is None:
            try:
                ev = events.get(timeout=EVENT_POLL_SEC)
            except Empty:
                if not wave_b_started and all(state[c]["ok"] for c in WAVE_A):
                    wave_b_started = True
                    for check in WAVE_B:
                        pool.submit(_run_probe, check)
                if wave_b_started and not appium_started and all(state[c]["ok"] for c in STACK_CHECKS):
                    appium_started = True
                    pool.submit(_run_probe, "appium")
                if all(state[c]["ok"] for c in ALL_CHECKS):
                    apps_ready = True
                    break
                continue

            timeline.append(ev)
            et = ev.get("type")
            check = str(ev.get("check") or "")
            if check in state and ev.get("elapsed_sec") is not None:
                state[check]["elapsed_sec"] = float(state[check].get("elapsed_sec") or 0.0) + float(
                    ev.get("elapsed_sec") or 0.0
                )
                _mark_elapsed(check)

            if et == "check_result" and check in state:
                state[check]["ok"] = bool(ev.get("ok"))
                state[check]["detail"] = ev.get("detail")
                if ev.get("mode"):
                    state[check]["mode"] = ev.get("mode")
                if ev.get("error_type"):
                    state[check]["error_type"] = ev.get("error_type")
                if not state[check]["ok"]:
                    if state[check]["attempts"] >= max_attempts:
                        _mark_elapsed(check)
                        fatal = {
                            "app": app,
                            "check": check,
                            "reason": "max_attempts_exceeded",
                            "attempts": state[check]["attempts"],
                            "detail": state[check]["detail"],
                        }
                        state[check]["error_type"] = "max_attempts_exceeded"
                        break
                    if check not in repair_inflight:
                        state[check]["attempts"] += 1
                        repair_inflight.add(check)
                        mode = str(state[check].get("mode") or ev.get("mode") or "cold")
                        pool.submit(_run_repair, check, mode)
                else:
                    _mark_elapsed(check)
                    state[check]["error_type"] = ""
                    if not wave_b_started and all(state[c]["ok"] for c in WAVE_A):
                        wave_b_started = True
                        for c in WAVE_B:
                            pool.submit(_run_probe, c)
                    if wave_b_started and not appium_started and all(state[c]["ok"] for c in STACK_CHECKS):
                        appium_started = True
                        pool.submit(_run_probe, "appium")

            elif et == "repair_result" and check in state:
                if ev.get("error_type"):
                    state[check]["error_type"] = ev.get("error_type")
                if ev.get("mode"):
                    state[check]["mode"] = ev.get("mode")
                if ev.get("ok"):
                    # re-notifica o check na fila (probe → check_result)
                    pool.submit(_run_probe, check)
                else:
                    state[check]["ok"] = False
                    state[check]["detail"] = ev.get("detail")
                    if state[check]["attempts"] >= max_attempts:
                        _mark_elapsed(check)
                        fatal = {
                            "app": app,
                            "check": check,
                            "reason": "repair_exhausted",
                            "attempts": state[check]["attempts"],
                            "detail": state[check]["detail"],
                        }
                        state[check]["error_type"] = "repair_exhausted"
                        break
                    if state[check]["attempts"] < max_attempts and check not in repair_inflight:
                        state[check]["attempts"] += 1
                        repair_inflight.add(check)
                        pool.submit(_run_repair, check, str(state[check].get("mode") or "cold"))

            if all(state[c]["ok"] for c in ALL_CHECKS):
                apps_ready = True
                break
    finally:
        pool.shutdown(wait=False, cancel_futures=True)
        for c in ALL_CHECKS:
            _mark_elapsed(c)

    if not apps_ready and fatal is None:
        apps_ready = all(state[c]["ok"] for c in ALL_CHECKS)

    appium_mode = str(state["appium"].get("mode") or ("warm" if state["appium"]["ok"] else "cold"))
    checks_block = _checks_block(state, fatal=fatal)
    return {
        "app": app,
        "ok": bool(apps_ready) and fatal is None,
        "apps_ready": bool(apps_ready) and fatal is None,
        "checks_block": checks_block,
        "fatal": fatal,
        "appium_mode": appium_mode,
        "timeline": timeline[-40:],
    }


def run_qa_init_suite_mobile(
    task_id: str = "",
    *,
    suites_mobile: dict[str, Any] | str | None = None,
    child_only: bool | None = None,
    parent_only: bool | None = None,
    skip_build: bool = True,
    feature: str = "",
    timeout_sec: int = 600,
    max_attempts: int = MAX_ATTEMPTS_PER_CHECK,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Init suites mobile conforme suites_mobile {parent, child}.

    Plano vem só dos params MCP (task_id + suites_mobile + feature) —
    sem load_tasks / board.
    """
    suites = normalize_suites_mobile(
        suites_mobile, child_only=child_only, parent_only=parent_only
    )

    want_parent = bool(suites.get("parent"))
    want_child = bool(suites.get("child"))
    parent_only_flag = want_parent and not want_child
    child_only_flag = want_child and not want_parent

    appium_feature = feature.strip() or ("login" if parent_only_flag else "pairing")
    evidence_plan: dict[str, Any] = {}

    if dry_run:
        empty_err = {
            c: {"type": "", "time_exec": "0s", "detail": ""} for c in ALL_CHECKS
        }
        empty_checks = {
            **{c: {"ok": True, "attempts": 0, "time_exec": "0s", "detail": ""} for c in ALL_CHECKS},
            "error_runtime": empty_err,
        }
        if "appium" in empty_checks:
            empty_checks["appium"]["mode"] = "cold"
        return {
            "ok": True,
            "dry_run": True,
            "task_id": task_id,
            "tool": "qa_init_suite_mobile",
            "suites_mobile": suites,
            "apps_ready_ok": True,
            "would_run": {
                "suites": suites,
                "waves": {"A": list(WAVE_A), "B": list(WAVE_B), "appium": True},
                "max_attempts_per_check": max_attempts,
                "feature": appium_feature,
                "plan": evidence_plan,
            },
            "checks_parent": dict(empty_checks) if want_parent else None,
            "checks_child": dict(empty_checks) if want_child else None,
        }

    log_recovery(task_id=task_id or "init", phase="qa_init_suite_start", ok=True, to_tier="T0")
    _append_init_log({"phase": "start", "task_id": task_id, "suites_mobile": suites, "feature": appium_feature})

    checks_parent: dict[str, Any] | None = None
    checks_child: dict[str, Any] | None = None
    timeline: list[dict[str, Any]] = []
    appium_modes: list[str] = []
    fatals: dict[str, Any] = {}

    per_app_timeout = max(120, timeout_sec // max(1, int(want_parent) + int(want_child)))

    if want_parent:
        parent_res = _init_one_app(
            "parent",
            task_id=task_id,
            skip_build=skip_build,
            feature=appium_feature,
            timeout_sec=per_app_timeout,
            max_attempts=max_attempts,
        )
        checks_parent = parent_res["checks_block"]
        timeline.extend(parent_res.get("timeline") or [])
        appium_modes.append(str(parent_res.get("appium_mode") or "cold"))
        if parent_res.get("fatal"):
            fatals["parent"] = parent_res["fatal"]

    if want_child:
        child_res = _init_one_app(
            "child",
            task_id=task_id,
            skip_build=skip_build,
            feature=appium_feature,
            timeout_sec=per_app_timeout,
            max_attempts=max_attempts,
        )
        checks_child = child_res["checks_block"]
        timeline.extend(child_res.get("timeline") or [])
        appium_modes.append(str(child_res.get("appium_mode") or "cold"))
        if child_res.get("fatal"):
            fatals["child"] = child_res["fatal"]

    def _suite_ok(checks: dict[str, Any] | None) -> bool:
        if not checks:
            return False
        return all(bool((checks.get(c) or {}).get("ok")) for c in ALL_CHECKS)

    parent_ok = (not want_parent) or _suite_ok(checks_parent)
    child_ok = (not want_child) or _suite_ok(checks_child)
    apps_ready_ok = parent_ok and child_ok

    appium_mode = "cold" if "cold" in appium_modes else (appium_modes[0] if appium_modes else "cold")
    app_target = (
        "dual" if want_parent and want_child else ("parent" if want_parent else "child")
    )
    plan = {
        "app": app_target,
        "appium_feature": appium_feature,
        "appium_mode": appium_mode,
        "scenarios": [],
        "evidence": {},
        "evidence_pipeline": evidence_plan,
        "suites_mobile": suites,
        "child_only": child_only_flag,
        "parent_only": parent_only_flag,
    }

    blocking = None
    if not apps_ready_ok:
        if fatals.get("parent"):
            fatal = fatals["parent"]
            blocking = f"INIT_FATAL:parent:{fatal.get('check') or fatal.get('reason')}"
        elif fatals.get("child"):
            fatal = fatals["child"]
            blocking = f"INIT_FATAL:child:{fatal.get('check') or fatal.get('reason')}"
        else:
            blocking = "INIT_APPS_NOT_READY"

    # compat: checks flat (sem error_runtime) para consumidores legados
    def _flat_checks(block: dict[str, Any] | None) -> dict[str, Any]:
        if not block:
            return {}
        return {k: v for k, v in block.items() if k != "error_runtime"}

    metro_bundle_refreshed = _metro_bundle_refreshed(timeline)

    out: dict[str, Any] = {
        "ok": apps_ready_ok,
        "task_id": task_id,
        "tool": "qa_init_suite_mobile",
        "suites_mobile": suites,
        "apps_ready": apps_ready_ok,
        "apps_ready_ok": apps_ready_ok,
        "metro_bundle_refreshed": metro_bundle_refreshed,
        "checks_parent": checks_parent,
        "checks_child": checks_child,
        "appium_mode": appium_mode,
        "appium_feature": appium_feature,
        "plan": plan,
        "timeline": timeline[-80:],
        "log_path": str(INIT_LOG),
        "blocking_reason": blocking,
        "skipped_appium_suite": True,
        "checks": _flat_checks(checks_child or checks_parent),
        "fatal": next(iter(fatals.values()), None) if fatals else None,
        "child_only": child_only_flag,
        "parent_only": parent_only_flag,
    }

    log_recovery(
        task_id=task_id or "init",
        phase="qa_init_suite_done",
        ok=apps_ready_ok,
        reason=blocking or "apps_ready_ok",
        extra={"suites_mobile": suites, "appium_mode": appium_mode},
    )
    _append_init_log(
        {
            "phase": "done",
            "ok": apps_ready_ok,
            "apps_ready_ok": apps_ready_ok,
            "blocking_reason": blocking,
        }
    )

    from lib.mobile.qa_envelope import finalize_qa_envelope

    return finalize_qa_envelope(out, evidence_required=False, recovery_tier=appium_mode)
