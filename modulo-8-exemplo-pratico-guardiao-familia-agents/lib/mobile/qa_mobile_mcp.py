"""Helpers QA expostos via MCP (seed DB, cleanup, stack Appium parent/child)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Literal

from lib.mobile.mobile_e2e_seed import (
    SEED_PROFILES,
    cleanup_db_seed,
    default_db_seed_config,
    provision_handoff,
    resolve_db_seed,
)
from lib.mobile.mobile_runtime_config import appium_env, stack
from lib.paths import QA_SEED_CACHE_DIR
from lib.mobile.qa_mobile_setup_evidence import collect_artifacts, setup_root
from board_automation.board.task_router import load_tasks

AppTarget = Literal["parent", "child"]

SEED_CACHE_DIR = QA_SEED_CACHE_DIR


def _seed_cache_path(task_id: str) -> Path:
    return SEED_CACHE_DIR / f"{task_id}.json"


def _save_seed_cache(task_id: str, result: dict[str, Any]) -> None:
    SEED_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {k: v for k, v in result.items() if k != "steps"}
    _seed_cache_path(task_id).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )


def _load_seed_cache(task_id: str) -> dict[str, Any] | None:
    path = _seed_cache_path(task_id)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _read_handoff_file(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _stage_handoff_path() -> Path:
    return setup_root() / "docs" / "stage-handoff.json"


def _ensure_stage_handoff(handoff: dict[str, Any], *, source_path: str = "") -> Path:
    """Garante stage-handoff.json no mobile-setup (fonte para ResumeFromHandoff)."""
    target = _stage_handoff_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    if source_path:
        src = Path(source_path)
        if src.is_file() and src.resolve() == target.resolve():
            return target
    target.write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


def _load_handoff_for_seed(*, task_id: str = "") -> tuple[dict[str, Any] | None, str]:
    if task_id:
        cached = _load_seed_cache(task_id)
        if cached:
            handoff = cached.get("handoff")
            if isinstance(handoff, dict):
                return handoff, str(cached.get("handoff_path") or "")
    default_path = _stage_handoff_path()
    handoff = _read_handoff_file(default_path)
    if handoff:
        return handoff, str(default_path)
    return None, ""


def resolve_from_db_seed(app: AppTarget, *, task_id: str = "") -> dict[str, Any]:
    """Resolve flags para retomar do handoff pós-seed e abrir o app na home."""
    handoff, handoff_path = _load_handoff_for_seed(task_id=task_id)
    if not handoff:
        return {
            "ok": False,
            "error": "handoff ausente — rode qa_db_seed antes ou informe task_id com cache válido",
        }

    stage_path = _ensure_stage_handoff(handoff, source_path=handoff_path)
    last_step = str(handoff.get("lastStep") or "")
    child_home = bool(handoff.get("childHome")) or last_step == "go_to_home_child"
    parent_home = bool(handoff.get("parentHome")) or last_step == "go_to_home_parent"

    if app == "child":
        if child_home:
            feature = "go_to_home_child"
            mode = "child_already_home"
        else:
            feature = "pairing"
            mode = "resume_to_child_home"
    elif parent_home:
        feature = "go_to_home_parent"
        mode = "parent_already_home"
    else:
        feature = "pairing"
        mode = "resume_to_parent_home"

    return {
        "ok": True,
        "app": app,
        "mode": mode,
        "feature": feature,
        "resume_from_handoff": True,
        "skip_appium": False,
        "single_emulator": False,
        "handoff_path": str(stage_path),
        "last_step": last_step or None,
        "child_home": child_home,
        "parent_home": parent_home,
        "seed_profile": handoff.get("seed_profile"),
    }


def run_db_seed(
    task_id: str,
    *,
    profile: str = "",
    bootstrap_api: bool = True,
    dry_run: bool = False,
    use_task_config: bool = True,
) -> dict[str, Any]:
    """Cria seed Postgres + stage-handoff para evidências Appium."""
    chosen_profile = profile or "child_home"
    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "task_id": task_id,
            "would_run": {
                "profile": chosen_profile,
                "bootstrap_api": bootstrap_api,
                "use_task_config": use_task_config,
                "profiles_available": sorted(SEED_PROFILES),
                "handoff_path": str(setup_root() / "docs" / "stage-handoff.json"),
            },
        }

    config: dict[str, Any] | None = None
    if use_task_config:
        task = next((t for t in load_tasks() if t.get("id") == task_id), None)
        if task:
            config = resolve_db_seed(task)
    if not config:
        config = default_db_seed_config(task_id, profile=chosen_profile)
    elif profile:
        config["profile"] = profile
    config["bootstrap_api"] = bootstrap_api

    result = provision_handoff(task_id, config=config)
    if result.get("ok"):
        _save_seed_cache(task_id, result)
    return result


def run_db_cleanup(
    *,
    task_id: str = "",
    handoff_path: str = "",
    parent_email: str = "",
    dry_run: bool = False,
) -> dict[str, Any]:
    """Pós-evidência: purge usuários de teste + reset handoff."""
    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "would_run": {
                "task_id": task_id or None,
                "handoff_path": handoff_path or None,
                "parent_email": parent_email or None,
                "fallback": "stage-handoff.json no mobile-setup",
            },
        }

    seed_result: dict[str, Any] | None = None
    if task_id:
        seed_result = _load_seed_cache(task_id)
    if not seed_result and handoff_path:
        handoff = _read_handoff_file(Path(handoff_path))
        if handoff:
            seed_result = {"handoff": handoff, "handoff_path": handoff_path}
    if not seed_result:
        setup = setup_root()
        default_path = setup / "docs" / "stage-handoff.json"
        handoff = _read_handoff_file(default_path)
        if handoff:
            seed_result = {"handoff": handoff, "handoff_path": str(default_path)}
    if not seed_result and parent_email:
        seed_result = {"handoff": {"parent_email": parent_email, "email": parent_email}}
    if not seed_result:
        return {"ok": False, "error": "handoff ausente — informe task_id, handoff_path ou parent_email"}

    if parent_email:
        seed_result.setdefault("handoff", {})
        seed_result["handoff"]["parent_email"] = parent_email
        seed_result["handoff"]["email"] = parent_email

    out = cleanup_db_seed(seed_result)
    if task_id and out.get("ok"):
        cache = _seed_cache_path(task_id)
        if cache.is_file():
            cache.unlink()
    return out


def _parse_fast_stack_report(setup: Path) -> dict[str, Any]:
    report_path = setup / "docs" / "fast-stack-last.json"
    if not report_path.is_file():
        return {}
    try:
        return json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def run_appium_suite(
    app: AppTarget,
    *,
    skip_build: bool = True,
    skip_appium: bool = True,
    phase: str = "Smoke",
    resume_from_handoff: bool = False,
    from_db_seed: bool = False,
    task_id: str = "",
    feature: str = "",
    timeout_sec: int = 1800,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Sobe stack Appium (API → emuladores → Metro → build → APPS_READY)."""
    s = stack(app)
    seed_ctx: dict[str, Any] | None = None
    if from_db_seed:
        seed_ctx = resolve_from_db_seed(app, task_id=task_id)
        if not seed_ctx.get("ok"):
            return seed_ctx
        resume_from_handoff = True
        skip_appium = False
        if not feature:
            feature = str(seed_ctx["feature"])

    use_single = app == "parent" and not from_db_seed
    dual_emulator = app == "child" or from_db_seed

    if dry_run:
        payload: dict[str, Any] = {
            "phase": phase,
            "skip_build": skip_build,
            "skip_appium": skip_appium,
            "single_emulator": use_single,
            "dual_emulator": dual_emulator,
            "resume_from_handoff": resume_from_handoff,
            "from_db_seed": from_db_seed,
            "task_id": task_id or None,
            "feature": feature or ("create_account" if app == "parent" else "pairing"),
            "emulator": s["emulator"],
            "metro_port": s["metro_port"],
            "timeout_sec": timeout_sec,
            "script": str(setup_root() / "scripts" / "fast-stack.ps1"),
        }
        if seed_ctx:
            payload["seed_context"] = seed_ctx
        return {"ok": True, "dry_run": True, "app": app, "would_run": payload}

    setup = setup_root()
    ps1 = setup / "scripts" / "fast-stack.ps1"
    if not ps1.is_file():
        return {"ok": False, "error": f"ausente: {ps1}"}

    shell = shutil.which("powershell") or shutil.which("pwsh")
    if not shell:
        return {"ok": False, "error": "powershell/pwsh não encontrado no PATH"}

    cmd = [shell, "-ExecutionPolicy", "Bypass", "-File", str(ps1), "-Phase", phase]
    if skip_build:
        cmd.append("-SkipBuild")
    if skip_appium:
        cmd.append("-SkipAppium")
    if use_single:
        cmd.append("-Single")
    if resume_from_handoff:
        cmd.append("-ResumeFromHandoff")

    env = dict(os.environ)
    env.update(appium_env(dual_emulator=dual_emulator))
    env["GF_APPIUM_FEATURE"] = feature or ("create_account" if app == "parent" else "pairing")
    if from_db_seed:
        env["GF_SKIP_DB_CLEANUP"] = "1"
        env["GF_RUN_DEPS"] = "0"
        env["GF_RESUME_FROM_HANDOFF"] = "1"

    proc = subprocess.run(
        cmd,
        cwd=str(setup),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_sec,
    )

    log_tail = (proc.stdout or "") + (proc.stderr or "")
    report = _parse_fast_stack_report(setup)
    apps_ready = bool(report.get("apps_ready"))
    report_ok = bool(report.get("ok"))
    ok = proc.returncode == 0 and report_ok

    markers = [
        line.strip()
        for line in log_tail.splitlines()
        if any(
            token in line
            for token in (
                "APPS_READY_OK",
                "APPS_READY_FAIL",
                "SMOKE_PARENT_OK",
                "SMOKE_PARENT_FAIL",
                "SMOKE_CHILD_OK",
                "SMOKE_CHILD_FAIL",
                "APPIUM_SKIP",
                "APPIUM_OK",
                "APPIUM_FAIL",
            )
        )
    ]

    out: dict[str, Any] = {
        "ok": ok,
        "app": app,
        "returncode": proc.returncode,
        "report_ok": report_ok,
        "apps_ready": apps_ready,
        "markers": markers[-12:],
        "fast_stack_report": report,
        "artifacts": collect_artifacts(setup),
        "stdout_tail": log_tail[-3000:],
    }
    if seed_ctx:
        out["seed_context"] = seed_ctx
    return out
