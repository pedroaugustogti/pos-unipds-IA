"""Helpers QA expostos via MCP (seed DB, cleanup, stack Appium parent/child)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Literal

from lib.mobile.local_e2e import resolve_android_home
from lib.mobile.mobile_e2e_seed import (
    SEED_PROFILES,
    cleanup_db_seed,
    default_db_seed_config,
    provision_handoff,
    resolve_db_seed,
    _reset_handoff_cycle,
)
from lib.mobile.mobile_runtime_config import appium_env, stack
from lib.ticket_output import ticket_seed_cache_path
from lib.mobile.qa_mobile_setup_evidence import collect_artifacts, setup_root, _package
from board_automation.board.task_router import load_tasks

AppTarget = Literal["parent", "child"]

def _seed_cache_path(task_id: str) -> Path:
    return ticket_seed_cache_path(task_id)


def _save_seed_cache(task_id: str, result: dict[str, Any]) -> None:
    _seed_cache_path(task_id).parent.mkdir(parents=True, exist_ok=True)
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
    _ = source_path  # legado — sempre regrava para evitar handoff stale sem credenciais
    target = _stage_handoff_path()
    target.parent.mkdir(parents=True, exist_ok=True)
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


DUAL_CHILD_FEATURES = frozenset(
    {"pairing", "copy_code_pairing", "paste_code_parent", "allow_permissions", "go_to_home_child"}
)
PARENT_ONLY_SEED_PROFILES = frozenset({"parent_home"})
CHILD_ONLY_SEED_PROFILES = frozenset({"child_home", "basic_parent", "permissions_resume"})


def _infer_emulator_scope(
    app: AppTarget,
    handoff: dict[str, Any],
    *,
    child_only: bool,
    parent_only: bool,
    feature: str = "",
) -> tuple[bool, bool]:
    """Infere child_only / parent_only a partir do seed quando não informado explicitamente."""
    profile = str(handoff.get("seed_profile") or "")
    meta = SEED_PROFILES.get(profile, {})
    target = str(meta.get("target_app") or "")
    feat = feature.strip()

    if app == "parent":
        if parent_only or child_only:
            return child_only, parent_only
        if feat in DUAL_CHILD_FEATURES:
            return False, False
        if profile in PARENT_ONLY_SEED_PROFILES or target == "parent":
            return False, True
        if last := str(handoff.get("lastStep") or ""):
            if last in ("config_family", "create_account", "login"):
                return False, True
        return False, True

    # child
    if child_only or parent_only:
        return child_only, parent_only
    if feat == "pairing" or profile == "pairing_warm" or target == "dual":
        return False, False
    if profile in CHILD_ONLY_SEED_PROFILES or target == "child":
        return True, False
    return True, False


def resolve_from_db_seed(
    app: AppTarget,
    *,
    task_id: str = "",
    child_only: bool = False,
    parent_only: bool = False,
    feature: str = "",
) -> dict[str, Any]:
    """Resolve flags para retomar do handoff pós-seed e abrir o app na home."""
    requested_feature = feature.strip()
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
    elif last_step in ("config_family", "create_account"):
        feature = "login"
        mode = "resume_parent_after_api_seed"
    elif last_step == "login":
        feature = "copy_code_pairing"
        mode = "resume_parent_pairing"
    else:
        feature = "pairing"
        mode = "resume_to_parent_home"

    if requested_feature:
        feature = requested_feature

    child_only, parent_only = _infer_emulator_scope(
        app, handoff, child_only=child_only, parent_only=parent_only, feature=feature
    )

    single_emulator = (app == "parent" and parent_only) or (app == "child" and child_only) or app == "parent"

    return {
        "ok": True,
        "app": app,
        "mode": mode,
        "feature": feature,
        "resume_from_handoff": True,
        "skip_appium": False,
        "single_emulator": single_emulator,
        "child_only": child_only,
        "parent_only": parent_only,
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


def _emulator_ready(serial: str) -> bool:
    home = resolve_android_home()
    if not home:
        return False
    adb = home / "platform-tools" / ("adb.exe" if os.name == "nt" else "adb")
    if not adb.is_file():
        return False
    try:
        state = subprocess.run(
            [str(adb), "-s", serial, "get-state"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if (state.stdout or "").strip() != "device":
            return False
        boot = subprocess.run(
            [str(adb), "-s", serial, "shell", "getprop", "sys.boot_completed"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return (boot.stdout or "").strip() == "1"
    except (OSError, subprocess.TimeoutExpired):
        return False


def _needs_cold_boot(*, dual: bool, child_only: bool = False) -> bool:
    if os.environ.get("GF_COLD_BOOT", "").strip() in ("1", "true", "yes"):
        return True
    parent = stack("parent")["emulator"]
    child = stack("child")["emulator"]
    if child_only:
        return not _emulator_ready(child)
    if not _emulator_ready(parent):
        return True
    if dual and not _emulator_ready(child):
        return True
    return False


def run_appium_suite(
    app: AppTarget,
    *,
    skip_build: bool = True,
    skip_appium: bool = True,
    phase: str = "All",
    resume_from_handoff: bool = False,
    from_db_seed: bool = False,
    task_id: str = "",
    feature: str = "",
    timeout_sec: int = 1800,
    dry_run: bool = False,
    cold_boot: bool | None = None,
    child_only: bool = False,
    parent_only: bool = False,
    reset_handoff_after: bool | None = None,
) -> dict[str, Any]:
    """Sobe stack Appium (API → emuladores → Metro → build → APPS_READY)."""
    s = stack(app)
    seed_ctx: dict[str, Any] | None = None
    if from_db_seed:
        seed_ctx = resolve_from_db_seed(
            app,
            task_id=task_id,
            child_only=child_only,
            parent_only=parent_only,
            feature=feature,
        )
        if not seed_ctx.get("ok"):
            return seed_ctx
        resume_from_handoff = True
        skip_appium = False
        child_only = bool(seed_ctx.get("child_only"))
        parent_only = bool(seed_ctx.get("parent_only"))
        if not feature:
            feature = str(seed_ctx["feature"])

    if reset_handoff_after is None:
        reset_handoff_after = bool(from_db_seed or task_id)

    use_single = (app == "parent" and parent_only) or (app == "child" and child_only) or (
        app == "parent" and not from_db_seed
    )
    dual_emulator = app == "child" and not child_only

    if dry_run:
        payload: dict[str, Any] = {
            "phase": phase,
            "skip_build": skip_build,
            "skip_appium": skip_appium,
            "single_emulator": use_single,
            "dual_emulator": dual_emulator,
            "resume_from_handoff": resume_from_handoff,
            "from_db_seed": from_db_seed,
            "child_only": child_only,
            "parent_only": parent_only,
            "reset_handoff_after": reset_handoff_after,
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
    if use_single or parent_only:
        cmd.append("-Single")
    if resume_from_handoff:
        cmd.append("-ResumeFromHandoff")
    if child_only:
        cmd.append("-ChildOnlyQa")
    if parent_only:
        cmd.append("-ParentOnlyQa")
    use_cold_boot = cold_boot if cold_boot is not None else _needs_cold_boot(dual=dual_emulator, child_only=child_only)
    if use_cold_boot:
        cmd.append("-ColdBoot")

    env = dict(os.environ)
    env.update(appium_env(dual_emulator=dual_emulator))
    home = resolve_android_home()
    if home:
        env["ANDROID_HOME"] = str(home)
        env["PATH"] = str(home / "platform-tools") + os.pathsep + env.get("PATH", "")
    env["GF_APPIUM_FEATURE"] = feature or ("create_account" if app == "parent" else "pairing")
    if from_db_seed:
        env["GF_SKIP_DB_CLEANUP"] = "1"
        env["GF_RUN_DEPS"] = "0"
        env["GF_RESUME_FROM_HANDOFF"] = "1"
        if seed_ctx:
            handoff = _read_handoff_file(_stage_handoff_path()) or {}
            cached = seed_ctx.get("handoff") if isinstance(seed_ctx.get("handoff"), dict) else {}
            if cached.get("email") and cached.get("password"):
                _ensure_stage_handoff(cached)
    if child_only:
        env["GF_QA_CHILD_ONLY"] = "1"
    elif "GF_QA_CHILD_ONLY" in env:
        del env["GF_QA_CHILD_ONLY"]
    if parent_only:
        env["GF_QA_PARENT_ONLY"] = "1"
    elif "GF_QA_PARENT_ONLY" in env:
        del env["GF_QA_PARENT_ONLY"]

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
    handoff_after = _read_handoff_file(_stage_handoff_path()) or {}
    child_home_reached = bool(handoff_after.get("childHome")) or handoff_after.get("lastStep") == "go_to_home_child"
    if not ok and app == "child" and child_home_reached and (task_id or child_only):
        out["partial_success"] = True
        out["partial_reason"] = (
            "child_home_reached; parent go_to_home_parent opcional"
            if child_only
            else "child_home_reached; parent go_to_home_parent opcional para evidências child"
        )
        ok = True
        out["ok"] = True

    if seed_ctx:
        out["seed_context"] = seed_ctx
        out["handoff_after"] = handoff_after

    if ok and task_id:
        try:
            extras: list[Path] = []
            if app == "child":
                task = next((t for t in load_tasks() if t.get("id") == task_id), None)
                scenarios = (task or {}).get("qa", {}).get("scenarios") or []
                evidence = (task or {}).get("qa", {}).get("evidence") or {}
                from lib.mobile.scenario_evidence import capture_scenario_evidence, scenarios_need_capture

                if scenarios_need_capture(scenarios):
                    scenario_out = capture_scenario_evidence(
                        task_id,
                        scenarios,
                        record_video=bool(evidence.get("video_mp4", True)),
                    )
                    out["scenario_evidence"] = scenario_out
                    if not scenario_out.get("ok"):
                        out["ok"] = False
                        ok = False
                    from lib.ticket_output import qa_evidence_dir, resolve_agent_cycle, resolve_handoff_path

                    handoff = _read_handoff_file(_stage_handoff_path()) or {}
                    hp = resolve_handoff_path(task_id)
                    if hp.is_file():
                        loaded = _read_handoff_file(hp)
                        if loaded:
                            handoff = loaded
                    cycle = resolve_agent_cycle(handoff, "qa-gate")
                    ev_dir = qa_evidence_dir(task_id, cycle=cycle)
                    extras = [p for p in ev_dir.glob("*") if p.is_file()] if ev_dir.is_dir() else []
            if ok:
                out["package_dir"] = str(_package(task_id, setup, extra_paths=extras))
        except Exception as exc:  # noqa: BLE001
            out["package_error"] = str(exc)

    if reset_handoff_after:
        out["handoff_cleanup"] = _reset_handoff_cycle(_stage_handoff_path())

    return out
