"""Cliente fino — módulo 8 só delega execução Appium ao mobile-setup."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from lib.core.repo_paths import resolve_repo_path

# Scripts Python canônicos (relativos a mobile-setup/appium/)
SCRIPTS = {
    "pairing": "pairing/run.py",
    "create_account": "create_account/run.py",
    "config_family": "config_family/run.py",
    "run_all": "run_all.py",
    "phase2": "phase2_evidence/run.py",
    "login": "pairing/login/run.py",
    "copy_code_pairing": "pairing/copy_code_pairing/run.py",
    "paste_code_parent": "pairing/paste_code_parent/run.py",
    "allow_permissions": "pairing/allow_permissions/run.py",
    "go_to_home_child": "pairing/go_to_home_child/run.py",
    "go_to_home_parent": "pairing/go_to_home_parent/run.py",
}


def setup_root() -> Path:
    root = resolve_repo_path("guardiao-familia-mobile-setup")
    if not root:
        raise FileNotFoundError(
            "guardiao-familia-mobile-setup não encontrado — defina GUARDAO_MOBILE_SETUP_PATH"
        )
    return root


def appium_root() -> Path:
    return setup_root() / "appium"


def handoff_path() -> Path:
    return setup_root() / "docs" / "stage-handoff.json"


def phase2_report_path() -> Path:
    return setup_root() / "docs" / "phase2_runtime" / "phase2_reconcile_report.json"


def start_emulators_script() -> Path:
    return setup_root() / "scripts" / "start-emulators.ps1"


def has_appium_deps() -> bool:
    return (appium_root() / "node_modules" / "webdriverio" / "package.json").is_file()


def run_python(
    script_key: str,
    *,
    args: list[str] | None = None,
    timeout_sec: int = 900,
    extra_env: dict[str, str] | None = None,
) -> dict[str, Any]:
    rel = SCRIPTS.get(script_key)
    if not rel:
        raise ValueError(f"script Appium desconhecido: {script_key}")

    script = appium_root() / rel
    if not script.is_file():
        return {"ok": False, "error": f"ausente: {script}", "script_key": script_key}

    import os

    env = {**os.environ, **(extra_env or {})}
    proc = subprocess.run(
        [__import__("sys").executable, str(script), *(args or [])],
        cwd=str(appium_root()),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_sec,
    )
    stdout = (proc.stdout or "") + (proc.stderr or "")
    payload: dict[str, Any] | None = None
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if line.startswith("{") and '"ok"' in line:
            try:
                payload = json.loads(line)
                break
            except json.JSONDecodeError:
                continue

    ok = proc.returncode == 0
    if isinstance(payload, dict) and "ok" in payload:
        ok = bool(payload.get("ok"))

    return {
        "ok": ok,
        "script_key": script_key,
        "script": rel,
        "engine": "guardiao-familia-mobile-setup/appium",
        "cwd": str(appium_root()),
        "returncode": proc.returncode,
        "result": payload,
        "stdout_tail": stdout[-4000:],
    }


def run_pairing(*, single_emulator: bool = False, timeout_sec: int = 900) -> dict[str, Any]:
    args = ["--single-emu"] if single_emulator else []
    return run_python("pairing", args=args, timeout_sec=timeout_sec)


def run_golden(*, single_emulator: bool = False, timeout_sec: int = 900) -> dict[str, Any]:
    args = ["--single-emu"] if single_emulator else []
    return run_python("run_all", args=args, timeout_sec=timeout_sec)


def run_phase2(
    *,
    flows: list[str] | None = None,
    single_emulator: bool = False,
    start_emu: bool = True,
    timeout_sec: int = 900,
) -> dict[str, Any]:
    args: list[str] = []
    if single_emulator:
        args.append("--single-emu")
    if not start_emu:
        args.append("--no-start-emu")
    for flow in flows or []:
        args.extend(["--flow", flow])
    out = run_python("phase2", args=args, timeout_sec=timeout_sec)
    if out.get("ok") and phase2_report_path().is_file():
        try:
            out["report"] = json.loads(phase2_report_path().read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return out
