"""Helpers QA expostos via MCP (seed DB, cleanup, stack Appium parent/child)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
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
from lib.mobile.seed_db_scripts import ensure_seed_db_scripts, seed_db_github_tree
from lib.ticket_output import ticket_seed_cache_path
from lib.mobile.qa_mobile_setup_evidence import collect_artifacts, setup_root, _package
from lib.mobile.qa_envelope import finalize_qa_envelope
from board_automation.board.task_router import load_tasks

AppTarget = Literal["parent", "child"]

def _load_qa_task(task_id: str) -> dict[str, Any] | None:
    """Task enriquecida: BACKLOG Project3 + cache issue + agent-task GitHub."""
    if not task_id:
        return None
    row: dict[str, Any] = {"id": task_id}
    try:
        csv_row = next(
            (t for t in load_tasks(refresh_board_status=False) if t.get("id") == task_id),
            None,
        )
        if csv_row:
            row.update(csv_row)
    except Exception:  # noqa: BLE001
        pass

    try:
        from lib.paths import BOARD_IMPORTS_DIR, PROJECT3_ITEM_CACHE_PATH

        backlog_path = BOARD_IMPORTS_DIR / "BACKLOG_PROJECT3.json"
        extra_path = BOARD_IMPORTS_DIR / "PROJECT3_REFINEMENT_EXTRA.json"
        if backlog_path.is_file():
            backlog = json.loads(backlog_path.read_text(encoding="utf-8"))
            local = next((t for t in (backlog.get("tasks") or []) if t.get("id") == task_id), None)
            if isinstance(local, dict):
                for key in ("qa", "refinement", "agent_responsibilities", "title", "repo", "repo_path"):
                    if not local.get(key):
                        continue
                    if key in ("qa", "refinement") and isinstance(local[key], dict):
                        base = row.get(key) if isinstance(row.get(key), dict) else {}
                        row[key] = {**base, **local[key]}
                    else:
                        row.setdefault(key, local[key])
        if extra_path.is_file():
            extra_all = json.loads(extra_path.read_text(encoding="utf-8"))
            extra = extra_all.get(task_id) if isinstance(extra_all, dict) else None
            if isinstance(extra, dict):
                for key in ("qa", "refinement", "agent_responsibilities"):
                    block = extra.get(key)
                    if not isinstance(block, dict):
                        continue
                    base = row.get(key) if isinstance(row.get(key), dict) else {}
                    merged = dict(base)
                    for ek, ev in block.items():
                        if isinstance(ev, dict) and isinstance(merged.get(ek), dict):
                            merged[ek] = {**merged[ek], **ev}
                        else:
                            merged[ek] = ev
                    row[key] = merged
        if PROJECT3_ITEM_CACHE_PATH.is_file():
            cache = json.loads(PROJECT3_ITEM_CACHE_PATH.read_text(encoding="utf-8"))
            hit = cache.get(task_id) if isinstance(cache, dict) else None
            if isinstance(hit, dict):
                if hit.get("issue_number"):
                    row.setdefault("issue_number", str(hit["issue_number"]))
                url = str(hit.get("issue_url") or "")
                if url.startswith("https://github.com/") and not row.get("repo"):
                    segs = url.removeprefix("https://github.com/").split("/")
                    if len(segs) >= 2:
                        row["repo"] = segs[1]
    except Exception:  # noqa: BLE001
        pass

    try:
        from lib.orchestrator.issue_ticket_enrichment import enrich_task_ticket

        return enrich_task_ticket(row)
    except Exception:  # noqa: BLE001
        return row


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
CHILD_PAIRING_FEATURES = DUAL_CHILD_FEATURES
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
    """Garante credenciais frescas do seed no arquivo Appium — sem resume por lastStep/childHome.

    Feature vem do ticket (caller). O arquivo `stage-handoff.json` só carrega pairingCode
    da seed desta execução (sempre sobrescrito por `qa_db_seed`).
    """
    requested_feature = feature.strip()
    handoff, handoff_path = _load_handoff_for_seed(task_id=task_id)
    if not handoff:
        return {
            "ok": False,
            "error": "credenciais de seed ausentes — rode qa_db_seed nesta execução",
        }

    # Força fluxo do zero: nunca retomar home/estado de run anterior
    handoff = {
        **handoff,
        "childHome": False,
        "parentHome": False,
        "lastStep": handoff.get("lastStep") or "config_family",
    }
    stage_path = _ensure_stage_handoff(handoff, source_path=handoff_path)

    if requested_feature:
        feature = requested_feature
    elif task_id:
        task = _load_qa_task(task_id)
        from lib.mobile.mobile_task import resolve_appium_feature_from_ticket

        feature = resolve_appium_feature_from_ticket(task or {"id": task_id, "qa": {}})
    else:
        feature = "pairing" if app == "child" else "login"

    if app == "child" and child_only:
        child_only, parent_only = True, False
    elif app == "parent" and parent_only:
        child_only, parent_only = False, True
    else:
        child_only, parent_only = _infer_emulator_scope(
            app, handoff, child_only=child_only, parent_only=parent_only, feature=feature
        )

    single_emulator = (app == "parent" and parent_only) or (app == "child" and child_only) or app == "parent"

    return {
        "ok": True,
        "app": app,
        "mode": "fresh_seed_credentials",
        "feature": feature,
        "resume_from_handoff": True,  # Appium: usar pairingCode do seed (não UI parent)
        "skip_appium": False,
        "single_emulator": single_emulator,
        "child_only": child_only,
        "parent_only": parent_only,
        "handoff_path": str(stage_path),
        "last_step": None,
        "resume_target": None,
        "child_home": False,
        "parent_home": False,
        "seed_profile": handoff.get("seed_profile"),
        "feature_coerced": None,
        "pairing_code_present": bool(
            str(handoff.get("pairingCode") or handoff.get("pairing_code") or "").strip()
        ),
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
        setup = setup_root()
        scripts = ensure_seed_db_scripts(setup)
        return {
            "ok": True,
            "dry_run": True,
            "task_id": task_id,
            "would_run": {
                "profile": chosen_profile,
                "bootstrap_api": bootstrap_api,
                "use_task_config": use_task_config,
                "profiles_available": sorted(SEED_PROFILES),
                "handoff_path": str(setup / "docs" / "stage-handoff.json"),
                "seed_scripts_github": seed_db_github_tree(),
                "seed_scripts": scripts,
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
    config["reuse_handoff"] = False

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
        return json.loads(report_path.read_text(encoding="utf-8-sig"))
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
    phase: str = "",
    resume_from_handoff: bool = False,
    from_db_seed: bool = False,
    task_id: str = "",
    feature: str = "",
    timeout_sec: int = 600,
    dry_run: bool = False,
    cold_boot: bool | None = None,
    child_only: bool = False,
    parent_only: bool = False,
    reset_handoff_after: bool | None = None,
) -> dict[str, Any]:
    """Suite Appium: ensure MCP (se preciso) + folha Phase Appium. `phase` é ignorado."""
    del phase
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
        # Feature do ticket prevalece; seed só entrega pairingCode
        if not feature:
            feature = str(seed_ctx.get("feature") or "pairing")

    if reset_handoff_after is None:
        reset_handoff_after = bool(from_db_seed or task_id)

    use_single = (app == "parent" and parent_only) or (app == "child" and child_only) or (
        app == "parent" and not from_db_seed
    )
    dual_emulator = app == "child" and not child_only

    if dry_run:
        payload: dict[str, Any] = {
            "phase": "Appium",
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
            "orchestration": "mcp_qa_ensure_then_appium_leaf",
        }
        if seed_ctx:
            payload["seed_context"] = seed_ctx
        return {"ok": True, "dry_run": True, "app": app, "would_run": payload}

    setup = setup_root()
    feature = feature or ("create_account" if app == "parent" else "pairing")
    extra_env: dict[str, str] = {}
    if from_db_seed:
        extra_env["GF_SKIP_DB_CLEANUP"] = "1"
        extra_env["GF_RUN_DEPS"] = "0"
        extra_env["GF_RESUME_FROM_HANDOFF"] = "1"
        if seed_ctx:
            cached = seed_ctx.get("handoff") if isinstance(seed_ctx.get("handoff"), dict) else {}
            if cached.get("email") and cached.get("password"):
                _ensure_stage_handoff(cached)

    evidence_required = False
    task = None
    evidence: dict[str, Any] = {}
    if task_id and app == "child":
        task = _load_qa_task(task_id)
        scenarios = (task or {}).get("qa", {}).get("scenarios") or []
        evidence = (task or {}).get("qa", {}).get("evidence") or {}
        from lib.mobile.scenario_evidence import scenarios_need_capture, wants_appium_flow_video

        evidence_required = scenarios_need_capture(scenarios) or wants_appium_flow_video(evidence)

    from lib.mobile.scenario_evidence import wants_appium_flow_video as _wants_flow

    if _wants_flow(evidence):
        extra_env["GF_APPIUM_FLOW_VIDEO"] = "1"
        extra_env.setdefault("GF_APPIUM_FLOW_VIDEO_SEC", "600")

    from lib.mobile.qa_recovery import (
        _run_fast_stack_phase,
        probe_stack_stages,
        run_ensure_stack_mobile,
    )

    precheck_out: dict[str, Any] | None = None
    stack_ensure_out: dict[str, Any] | None = None
    stages = probe_stack_stages(child_only=child_only)
    stack_ready = all((stages.get(s) or {}).get("ok") for s in ("api", "boot", "metro", "apps_ready"))
    if not stack_ready:
        stack_ensure_out = run_ensure_stack_mobile(
            task_id,
            child_only=child_only,
            skip_build=skip_build,
            feature=feature,
            repair_tier="T1",
            max_tier="T4",
            timeout_sec=min(timeout_sec, 600),
            dry_run=False,
        )
        if not stack_ensure_out.get("ok"):
            return finalize_qa_envelope(
                {
                    "ok": False,
                    "app": app,
                    "suite_ok": False,
                    "apps_ready": False,
                    "appium_ran": False,
                    "evidence_ok": False,
                    "stack_ensure": stack_ensure_out,
                    "stack_stages": stack_ensure_out.get("stack_stages") or stages,
                    "blocking_reason": stack_ensure_out.get("blocking_reason") or "STACK_NOT_READY",
                },
                evidence_required=evidence_required,
            )
        stages = stack_ensure_out.get("stack_stages") or probe_stack_stages(child_only=child_only)

    run_started_at = datetime.now(timezone.utc)
    if skip_appium:
        apps_ready = all((stages.get(s) or {}).get("ok") for s in ("api", "boot", "metro", "apps_ready"))
        return finalize_qa_envelope(
            {
                "ok": apps_ready,
                "suite_ok": apps_ready,
                "appium_ran": False,
                "apps_ready": apps_ready,
                "app": app,
                "blocking_reason": None if apps_ready else "STACK_NOT_READY",
                "stack_ensure": stack_ensure_out,
                "stack_stages": stages,
                "skipped_appium": True,
            },
            evidence_required=False,
        )

    appium = _run_fast_stack_phase(
        "Appium",
        child_only=child_only,
        parent_only=parent_only,
        skip_build=True,
        skip_appium=False,
        cold_boot=False,
        feature=feature,
        timeout_sec=timeout_sec,
        extra_env=extra_env,
    )
    log_tail = str(appium.get("stdout_tail") or "")
    report = appium.get("report") if isinstance(appium.get("report"), dict) else _parse_fast_stack_report(setup)
    apps_ready = bool(report.get("apps_ready")) or bool((stages.get("apps_ready") or {}).get("ok"))
    report_ok = bool(report.get("ok"))
    suite_ok = bool(appium.get("ok")) and int(appium.get("returncode") or 1) == 0
    ok = suite_ok

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
                "APPIUM_BLOCKED",
            )
        )
    ]

    appium_ran = any("APPIUM_OK" in m for m in markers) or bool(
        ((report.get("phases") or {}).get("appium") or {}).get("ok")
    )
    blocking_reason: str | None = None
    if not suite_ok:
        if not apps_ready:
            blocking_reason = "APPS_READY_FAIL"
        elif not appium_ran:
            blocking_reason = "APPIUM_FAIL"
        else:
            blocking_reason = "APPIUM_LEAF_FAIL"
    out: dict[str, Any] = {
        "ok": ok,
        "suite_ok": suite_ok,
        "appium_ran": appium_ran,
        "blocking_reason": blocking_reason,
        "app": app,
        "returncode": appium.get("returncode"),
        "report_ok": report_ok,
        "apps_ready": apps_ready,
        "markers": markers[-12:],
        "fast_stack_report": report,
        "stack_ensure": stack_ensure_out,
        "stack_stages": stages,
        "artifacts": collect_artifacts(setup),
        "stdout_tail": log_tail[-3000:],
        "orchestration": "mcp_appium_leaf",
    }
    if precheck_out:
        out["precheck"] = precheck_out
    handoff_after = _read_handoff_file(_stage_handoff_path()) or {}

    if seed_ctx:
        out["seed_context"] = seed_ctx
        out["handoff_after"] = handoff_after

    if task_id:
        try:
            extras: list[Path] = []
            flow_required = False
            scenario_ok = True
            if app == "child":
                if not task:
                    task = _load_qa_task(task_id)
                scenarios = (task or {}).get("qa", {}).get("scenarios") or []
                evidence = (task or {}).get("qa", {}).get("evidence") or {}
                from lib.mobile.scenario_evidence import (
                    capture_scenario_evidence,
                    find_appium_flow_videos,
                    scenarios_need_capture,
                    wants_appium_flow_video,
                )

                flow_required = wants_appium_flow_video(evidence)
                need_scenarios = scenarios_need_capture(scenarios)

                if need_scenarios:
                    # Gate = suite Appium desta run (não estado salvo de handoff)
                    if not (suite_ok and appium_ran):
                        out["scenario_evidence"] = {
                            "ok": False,
                            "skipped": True,
                            "reason": "suite Appium não concluiu — evidências exigem fluxo completo desta execução",
                        }
                        scenario_ok = False
                        out["ok"] = False
                        ok = False
                    else:
                        video_scope = str(evidence.get("video_scope") or "")
                        record_greeting_video = bool(evidence.get("greeting_video")) or (
                            "per_period" in video_scope
                        )
                        scenario_out = capture_scenario_evidence(
                            task_id,
                            scenarios,
                            record_video=record_greeting_video,
                            require_child_home=False,
                        )
                        out["scenario_evidence"] = scenario_out
                        scenario_ok = bool(scenario_out.get("ok"))
                        if not scenario_ok:
                            out["ok"] = False
                            ok = False
                    from lib.ticket_output import qa_evidence_dir, resolve_agent_cycle

                    cycle = resolve_agent_cycle(None, "qa-gate")
                    ev_dir = qa_evidence_dir(task_id, cycle=cycle)
                    extras = [p for p in ev_dir.glob("*") if p.is_file()] if ev_dir.is_dir() else []
            if ok or task_id:
                out["package_dir"] = str(
                    _package(task_id, setup, extra_paths=extras, run_started_at=run_started_at)
                )
            flow_ok = True
            if flow_required and app == "child":
                pkg = Path(str(out.get("package_dir") or ""))
                flows = find_appium_flow_videos(pkg) if pkg.is_dir() else []
                if not flows:
                    # pacote pode não ter corrido; procurar no mobile-setup desta run
                    flows = [
                        p
                        for p in find_appium_flow_videos(setup / "docs" / "appium-evidence")
                        if run_started_at is None
                        or p.stat().st_mtime >= run_started_at.timestamp() - 5
                    ]
                if flows:
                    out["flow_video"] = {"ok": True, "path": str(flows[0])}
                    # garantir cópia no pacote qa-gate se veio só do setup
                    if out.get("package_dir"):
                        dest_root = Path(str(out["package_dir"])) / "appium-evidence" / flows[0].parent.name
                        if not (dest_root / flows[0].name).is_file():
                            dest_root.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(flows[0], dest_root / flows[0].name)
                            meta_src = flows[0].parent / "meta.json"
                            if meta_src.is_file():
                                shutil.copy2(meta_src, dest_root / "meta.json")
                else:
                    flow_ok = False
                    out["flow_video"] = {
                        "ok": False,
                        "error": "MP4 do fluxo Appium ausente (GF_APPIUM_FLOW_VIDEO / startRecordingScreen)",
                    }
                    out["ok"] = False
                    ok = False
            if evidence_required:
                out["evidence_ok"] = bool(scenario_ok and flow_ok)
                if not out["evidence_ok"]:
                    out["ok"] = False
                    ok = False
        except Exception as exc:  # noqa: BLE001
            out["package_error"] = str(exc)

    if reset_handoff_after:
        out["handoff_cleanup"] = _reset_handoff_cycle(_stage_handoff_path())

    return finalize_qa_envelope(out, evidence_required=evidence_required)
