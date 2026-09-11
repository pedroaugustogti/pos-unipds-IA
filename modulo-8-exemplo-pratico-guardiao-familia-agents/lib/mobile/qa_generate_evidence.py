"""qa_generate_evidence — consome retorno de qa_pipeline_evidence.

Gera script Appium em tempo de execução a partir de scenario_pipeline.steps,
executa e produz evidências (screenshot/vídeo).
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from lib.mobile.mobile_e2e_seed import _reset_handoff_cycle
from lib.mobile.mobile_runtime_config import stack
from lib.mobile.mobile_setup_client import handoff_path
from lib.mobile.qa_appium_runtime_script import generate_and_run_from_pipeline
from lib.mobile.qa_init_suite_mobile import _appium_status
from lib.mobile.qa_mobile_mcp import (
    _seed_cache_path,
    _stage_handoff_path,
    resolve_from_db_seed,
    run_db_cleanup,
)
from lib.mobile.qa_recovery import (
    _apply_tier,
    _package_installed,
    _probe_apk,
    _repair_stack_stage,
    log_recovery,
    probe_stack_stages,
)


def _seed_values_from_handoff(handoff_file: str = "") -> dict[str, str]:
    """Credenciais explícitas para embutir no script (não depender só de re-leitura implícita)."""
    path = Path(handoff_file) if handoff_file else handoff_path()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {
        "seed.pairing_code": str(data.get("pairingCode") or data.get("pairing_code") or "").strip(),
        "seed.parent_email": str(data.get("email") or data.get("parent_email") or "").strip(),
        "seed.parent_password": str(data.get("password") or data.get("parent_password") or "").strip(),
        "seed.child_name": str(data.get("childName") or data.get("child_name") or "").strip(),
    }


def _with_pairing_clean_launch(device: dict[str, Any] | None, *, feature: str, app: str) -> dict[str, Any] | None:
    """Pairing child: sessão warm (noReset); um launch; sem pm_clear/forceStop no caminho feliz.

    Override: GF_APPIUM_PM_CLEAR=1 → pm_clear + hard_stop (cold).
    Default: clock pré-launch no pipeline; reload/forceStop só se GF_APPIUM_HARD_RELOAD=1.
    """
    if not isinstance(device, dict) or not device:
        return device
    if app != "child" or feature != "pairing":
        return device
    launch = dict(device.get("launch") or {})
    force_clear = os.environ.get("GF_APPIUM_PM_CLEAR", "").strip().lower() in ("1", "true", "yes")
    if force_clear:
        launch["pm_clear_before_launch"] = True
        launch["hard_stop"] = True
        launch["prefer_warm_session"] = False
        launch["pm_clear_if_dirty"] = False
        launch["reload_mode"] = "hard"
        launch["reload_after_set_clock"] = True
    else:
        if "pm_clear_before_launch" not in launch:
            launch["pm_clear_before_launch"] = False
        if "hard_stop" not in launch:
            launch["hard_stop"] = False
        launch["prefer_warm_session"] = True
        launch["pm_clear_if_dirty"] = False
        launch.setdefault("reload_mode", "none")
        launch.setdefault("reload_after_set_clock", False)
    return {**device, "launch": launch}


def _evidence_slot(
    *,
    path: str = "",
    err_type: str = "",
    description: str = "",
) -> dict[str, Any]:
    return {
        "evidence": str(path or ""),
        "error_runtime": {
            "type": str(err_type or ""),
            "description": str(description or ""),
        },
    }


def _first_png(package_dir: str, scenario_ev: dict[str, Any] | None, runtime: dict[str, Any]) -> str:
    arts = ((runtime.get("execution") or {}).get("result") or {}).get("artifacts") or {}
    shots = arts.get("screenshots") if isinstance(arts, dict) else None
    if isinstance(shots, list) and shots:
        return str(shots[0] or "")
    if isinstance(scenario_ev, dict):
        for item in scenario_ev.get("artifacts") or []:
            if isinstance(item, dict) and item.get("png"):
                return str(item["png"])
    if package_dir:
        from pathlib import Path

        root = Path(package_dir)
        if root.is_dir():
            pngs = sorted(root.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
            if pngs:
                return str(pngs[0])
            nested = sorted(root.rglob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
            if nested:
                return str(nested[0])
    return ""


def _first_video(package_dir: str, runtime: dict[str, Any]) -> str:
    arts = ((runtime.get("execution") or {}).get("result") or {}).get("artifacts") or {}
    if isinstance(arts, dict) and arts.get("video"):
        return str(arts["video"])
    if package_dir:
        from pathlib import Path

        root = Path(package_dir)
        if root.is_dir():
            vids = sorted(root.rglob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
            if vids:
                return str(vids[0])
    return ""


def _summarize_return(
    *,
    ticket_id: str,
    scenario_id: str,
    pipe: dict[str, Any],
    runtime: dict[str, Any] | None = None,
    scenario_ev: dict[str, Any] | None = None,
    fail_type: str = "",
    fail_description: str = "",
    dry_run: bool = False,
) -> dict[str, Any]:
    """Contrato público resumido de qa_generate_evidence."""
    runtime = runtime or {}
    want_shot = bool(pipe.get("screenshot", True)) if pipe else True
    want_video = bool(pipe.get("video_record", True)) if pipe else True
    package_dir = str(
        runtime.get("package_dir")
        or (runtime.get("generated") or {}).get("evidence_dir")
        or ""
    )

    if dry_run:
        return {
            "ticket_id": ticket_id,
            "scenario_id": scenario_id,
            "ok": True,
            "blocking_reason": None,
            "screenshot": _evidence_slot(
                path="",
                err_type="",
                description="" if want_shot else "screenshot_not_requested",
            ),
            "video_record": _evidence_slot(
                path="",
                err_type="",
                description="" if want_video else "video_not_requested",
            ),
        }

    if fail_type:
        shot_err = fail_type if want_shot else ""
        vid_err = fail_type if want_video else ""
        return {
            "ticket_id": ticket_id,
            "scenario_id": scenario_id,
            "ok": False,
            "blocking_reason": fail_type,
            "screenshot": _evidence_slot(
                path="",
                err_type=shot_err,
                description=fail_description if shot_err else ("screenshot_not_requested" if not want_shot else ""),
            ),
            "video_record": _evidence_slot(
                path="",
                err_type=vid_err,
                description=fail_description if vid_err else ("video_not_requested" if not want_video else ""),
            ),
        }

    png = _first_png(package_dir, scenario_ev, runtime) if want_shot else ""
    mp4 = _first_video(package_dir, runtime) if want_video else ""
    runtime_err = str(
        runtime.get("blocking_reason")
        or ((runtime.get("execution") or {}).get("result") or {}).get("error")
        or ""
    )

    if want_shot and not png:
        shot = _evidence_slot(
            path="",
            err_type="SCREENSHOT_MISSING",
            description=runtime_err or "screenshot não gerado",
        )
    elif not want_shot:
        shot = _evidence_slot(path="", err_type="", description="screenshot_not_requested")
    else:
        shot = _evidence_slot(path=png)

    if want_video and not mp4:
        # se runtime falhou, propaga; se só vídeo faltou
        vid = _evidence_slot(
            path="",
            err_type="VIDEO_MISSING" if runtime.get("ok") else (runtime.get("blocking_reason") or "VIDEO_MISSING"),
            description=runtime_err or "vídeo não gerado",
        )
    elif not want_video:
        vid = _evidence_slot(path="", err_type="", description="video_not_requested")
    else:
        vid = _evidence_slot(path=mp4)

    # se execução Appium falhou: NÃO tratar capture_FAIL/flow_fail como PASS
    if not runtime.get("ok"):
        err_type = str(runtime.get("blocking_reason") or "RUNTIME_APPIUM_FAIL")
        if want_shot:
            shot = _evidence_slot(
                path=str(shot.get("evidence") or ""),
                err_type=err_type if not shot["error_runtime"]["type"] else shot["error_runtime"]["type"],
                description=runtime_err or shot["error_runtime"].get("description") or "Appium runtime fail",
            )
        if want_video:
            vid = _evidence_slot(
                path=str(vid.get("evidence") or ""),
                err_type=err_type if not vid["error_runtime"]["type"] else vid["error_runtime"]["type"],
                description=runtime_err or vid["error_runtime"].get("description") or "Appium runtime fail",
            )

    if scenario_ev is not None and want_shot and not scenario_ev.get("ok") and not shot["evidence"]:
        shot = _evidence_slot(
            path="",
            err_type="SCENARIO_EVIDENCE_FAIL",
            description=str(scenario_ev.get("error") or scenario_ev.get("reason") or "capture_scenario_evidence fail"),
        )

    return {
        "ticket_id": ticket_id,
        "scenario_id": scenario_id,
        "screenshot": shot,
        "video_record": vid,
        "ok": _slots_ok(shot, vid) and bool(runtime.get("ok", True)),
        "blocking_reason": None if (bool(runtime.get("ok", True)) and _slots_ok(shot, vid)) else (
            str(runtime.get("blocking_reason") or runtime_err or "EVIDENCE_FAIL")
        ),
        "pre_script": runtime.get("pre_script"),
        "runtime_timing": ((runtime.get("execution") or {}).get("result") or {}).get("timing")
        or runtime.get("timing"),
    }


def _slots_ok(shot: dict[str, Any], vid: dict[str, Any]) -> bool:
    shot_err = str((shot.get("error_runtime") or {}).get("type") or "")
    vid_err = str((vid.get("error_runtime") or {}).get("type") or "")
    return not shot_err and not vid_err


def _summary_ok(summary: dict[str, Any]) -> bool:
    if "ok" in summary:
        return bool(summary.get("ok"))
    shot_err = str((summary.get("screenshot") or {}).get("error_runtime", {}).get("type") or "")
    vid_err = str((summary.get("video_record") or {}).get("error_runtime", {}).get("type") or "")
    # "not_requested" fica só em description
    return not shot_err and not vid_err


def _unwrap_pipeline_result(raw: dict[str, Any] | str | None) -> dict[str, Any]:
    """Aceita retorno completo de qa_pipeline_evidence (ou envelope MCP)."""
    if raw is None:
        return {}
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return {"ok": False, "error": "pipeline_result_invalid_json"}
    if not isinstance(raw, dict):
        return {}

    if isinstance(raw.get("result"), dict) and (
        raw.get("result", {}).get("tool") == "qa_pipeline_evidence"
        or "scenario_pipeline" in (raw.get("result") or {})
        or raw.get("result", {}).get("ok") is not None
    ):
        return raw["result"]

    if raw.get("tool") == "qa_pipeline_evidence" or "scenario_pipeline" in raw:
        return raw

    if "suites_mobile" in raw and "steps" in raw:
        return {
            "ok": True,
            "apps_ready_ok": True,
            "scenario_pipeline": raw,
            "scenario_id": "",
            "task_id": "",
        }

    return raw


def _verify_suite_prepared(
    *,
    apps_ready_ok: bool,
    child_only: bool,
    parent_only: bool = False,
    device: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not apps_ready_ok:
        return {"ok": False, "reason": "init_apps_not_ready", "detail": "apps_ready_ok=false"}
    if parent_only:
        parent = stack("parent")
        serial = str((device or {}).get("serial") or parent["emulator"])
        metro = int((device or {}).get("metro_port") or parent["metro_port"])
        bundle = str((device or {}).get("bundle_id") or parent["bundle_id"])
        from lib.mobile.qa_mobile_mcp import _emulator_ready
        from lib.mobile.qa_recovery import _metro_ready

        ok = _emulator_ready(serial) and _metro_ready(metro) and _package_installed(serial, bundle)
        return {
            "ok": ok,
            "scope": "parent_only",
            "detail": {"serial": serial, "metro": metro, "bundle": bundle},
            "reason": None if ok else "parent_stack_probe_fail",
        }
    if device and device.get("serial"):
        serial = str(device["serial"])
        metro = int(device.get("metro_port") or stack("child")["metro_port"])
        bundle = str(device.get("bundle_id") or stack("child")["bundle_id"])
        from lib.mobile.qa_mobile_mcp import _emulator_ready
        from lib.mobile.qa_recovery import _metro_ready

        ok = _emulator_ready(serial) and _metro_ready(metro) and _package_installed(serial, bundle)
        if ok:
            return {
                "ok": True,
                "scope": "device",
                "detail": {"serial": serial, "metro": metro, "bundle": bundle},
            }
        # fallback para probe completo se device parcial
    stages = probe_stack_stages(child_only=child_only)
    required = ("api", "boot", "metro", "apk", "apps_ready")
    missing = [s for s in required if not bool((stages.get(s) or {}).get("ok"))]
    if missing:
        return {"ok": False, "reason": "stack_probe_fail", "missing": missing, "stages": stages}
    return {"ok": True, "stages": stages}


def _ensure_apk_or_rebuild(*, child_only: bool, feature: str, timeout_sec: int) -> dict[str, Any]:
    apk = _probe_apk(child_only=child_only)
    if apk.get("ok"):
        return {"ok": True, "rebuilt": False, "apk": apk}
    repair = _repair_stack_stage(
        "apk",
        "T1",
        child_only=child_only,
        skip_build=False,
        feature=feature,
        timeout_sec=timeout_sec,
    )
    after = _probe_apk(child_only=child_only)
    return {
        "ok": bool(after.get("ok")),
        "rebuilt": True,
        "repair": repair,
        "apk": after,
        "error": None if after.get("ok") else "apk_rebuild_failed",
    }


def run_qa_generate_evidence(
    pipeline_result: dict[str, Any] | str | None = None,
    *,
    # compat legado
    actuation_context: dict[str, Any] | str | None = None,
    apps_ready_ok: bool | None = None,
    scenario_pipeline: dict[str, Any] | str | None = None,
    skip_build: bool = True,
    timeout_sec: int = 900,
    cleanup_on_success: bool = True,
    bootstrap_api: bool = True,
    profile: str = "",
    dry_run: bool = False,
) -> dict[str, Any]:
    """Consome retorno de qa_pipeline_evidence → gera script Appium → evidências."""
    # Preferência: pipeline_result; fallback monta a partir dos params legados
    if pipeline_result is None and scenario_pipeline is not None:
        pipeline_result = {
            "ok": True,
            "apps_ready_ok": True if apps_ready_ok is None else bool(apps_ready_ok),
            "scenario_pipeline": scenario_pipeline,
            "task_id": "",
            "scenario_id": "",
        }

    pipe_res = _unwrap_pipeline_result(pipeline_result)
    pipe = pipe_res.get("scenario_pipeline") if isinstance(pipe_res.get("scenario_pipeline"), dict) else {}
    device = pipe_res.get("device") if isinstance(pipe_res.get("device"), dict) else None
    if not pipe and isinstance(scenario_pipeline, (dict, str)):
        pipe = _unwrap_pipeline_result({"scenario_pipeline": scenario_pipeline}).get("scenario_pipeline") or {}
        if isinstance(scenario_pipeline, dict) and "steps" in scenario_pipeline:
            pipe = scenario_pipeline

    ready = pipe_res.get("apps_ready_ok")
    if ready is None:
        ready = True if apps_ready_ok is None else bool(apps_ready_ok)
    else:
        ready = bool(ready)
    if apps_ready_ok is False:
        ready = False

    tid = str(pipe_res.get("task_id") or "").strip()
    scenario_id = str(pipe_res.get("scenario_id") or "").strip()

    # task_id via actuation_context legado se faltar
    if not tid and actuation_context:
        try:
            from lib.orchestrator.phase_context import load_actuation, task_from_ctx

            ctx = load_actuation(actuation_context)
            tid = str(task_from_ctx(ctx).get("id") or "").strip()
        except Exception:  # noqa: BLE001
            pass

    if not pipe:
        return _fail(tid, scenario_id, pipe or {}, "MISSING_SCENARIO_PIPELINE", "scenario_pipeline ausente")
    if pipe_res.get("ok") is False:
        return _fail(
            tid,
            scenario_id,
            pipe,
            str(pipe_res.get("blocking_reason") or "PIPELINE_NOT_OK"),
            str(pipe_res.get("error") or pipe_res.get("note") or "pipeline não ok"),
        )
    binding = pipe.get("binding") if isinstance(pipe.get("binding"), dict) else {}
    if binding.get("ok") is False:
        return _fail(
            tid,
            scenario_id,
            pipe,
            "UNBOUND_ACTION",
            "binding.ok=false — corrija catálogo/steps antes de gerar evidência",
        )

    # Plano QA só do pipeline (ticket_qa embutido por qa_pipeline_evidence) — sem load_tasks
    qa = pipe.get("ticket_qa") if isinstance(pipe.get("ticket_qa"), dict) else {}
    if not qa and isinstance(pipe_res.get("ticket_qa"), dict):
        qa = pipe_res["ticket_qa"]
    db_seed_cfg = qa.get("db_seed") if isinstance(qa.get("db_seed"), dict) else {}

    suites = pipe.get("suites_mobile") if isinstance(pipe.get("suites_mobile"), dict) else {"parent": False, "child": True}
    parent_only = bool(suites.get("parent")) and not bool(suites.get("child"))
    child_only = bool(suites.get("child")) and not bool(suites.get("parent"))
    app = str((device or {}).get("app") or ("parent" if parent_only else "child"))
    feature = str(
        pipe.get("appium_feature") or pipe.get("feature") or ("login" if app == "parent" else "pairing")
    ).strip()
    device = _with_pairing_clean_launch(device, feature=feature, app=app)
    if not scenario_id:
        # tenta do step capture
        for st in pipe.get("steps") or []:
            if isinstance(st, dict) and st.get("action") == "capture":
                for f in st.get("fields") or []:
                    if isinstance(f, dict) and f.get("value"):
                        scenario_id = str(f.get("value"))
                        break
            if scenario_id:
                break
        if not scenario_id:
            for st in pipe.get("steps") or []:
                if isinstance(st, dict) and str(st.get("action") or "") == "capture":
                    sid = str(st.get("step_id") or "")
                    if sid.startswith("capture."):
                        scenario_id = sid.replace("capture.", "", 1)
                        break
    chosen_profile = profile or str(
        db_seed_cfg.get("profile") or ("parent_home" if app == "parent" else "basic_parent")
    )
    use_bootstrap = bool(db_seed_cfg.get("bootstrap_api", bootstrap_api))
    gate_meta = {
        "apps_ready_ok": ready,
        "task_id": tid,
        "scenario_id": scenario_id,
        "scenario_pipeline": pipe,
        "device": device,
    }

    if dry_run:
        generate_and_run_from_pipeline(
            pipeline=pipe,
            task_id=tid or "dry-run",
            scenario_id=scenario_id or "scenario",
            app=app,
            timeout_sec=timeout_sec,
            dry_run=True,
            device=device,
        )
        return _summarize_return(
            ticket_id=tid,
            scenario_id=scenario_id,
            pipe=pipe,
            dry_run=True,
        )

    phases: list[dict[str, Any]] = []
    pre_t0 = time.perf_counter()
    log_recovery(task_id=tid or "evidence", phase="qa_generate_evidence_start", ok=True)

    t0 = time.perf_counter()
    suite_gate = _verify_suite_prepared(
        apps_ready_ok=ready,
        child_only=bool(child_only) and app != "parent",
        parent_only=app == "parent",
        device=device,
    )
    phases.append({
        "phase": "verify_suite_prepared",
        **suite_gate,
        "duration_ms": int((time.perf_counter() - t0) * 1000),
    })
    if not suite_gate.get("ok"):
        return _fail(
            tid,
            scenario_id,
            pipe,
            "SUITE_NOT_PREPARED",
            str(suite_gate.get("reason") or suite_gate.get("detail") or "stack não pronta"),
        )

    t0 = time.perf_counter()
    live = _appium_status()
    phases.append({
        "phase": "verify_appium_session",
        "ok": True,
        "mode": "warm" if live.get("ok") else "cold",
        "live": live,
        "duration_ms": int((time.perf_counter() - t0) * 1000),
    })

    if tid:
        cache = _seed_cache_path(tid)
        if cache.is_file():
            cache.unlink(missing_ok=True)
            phases.append({"phase": "purge_seed_cache", "ok": True, "duration_ms": 0})
    _reset_handoff_cycle(_stage_handoff_path())
    phases.append({"phase": "purge_credentials_file", "ok": True, "duration_ms": 0})

    t0 = time.perf_counter()
    seed_prep = _apply_tier(
        "T3",
        tid,
        profile=chosen_profile,
        bootstrap_api=use_bootstrap,
        dry_run=False,
        child_only=bool(child_only) if app == "child" else True,
    )
    phases.append({
        "phase": "qa_db_seed",
        **seed_prep,
        "duration_ms": int((time.perf_counter() - t0) * 1000),
    })
    if not seed_prep.get("ok"):
        return _fail(
            tid,
            scenario_id,
            pipe,
            str(seed_prep.get("error") or "SEED_FAIL"),
            str(seed_prep.get("error") or seed_prep.get("detail") or "seed falhou"),
        )

    t0 = time.perf_counter()
    seed_ctx = resolve_from_db_seed(
        "child" if app == "child" else "parent",
        task_id=tid,
        child_only=bool(child_only) and app == "child",
        parent_only=bool(parent_only) or app == "parent",
        feature=feature,
    )
    phases.append({
        "phase": "seed_credentials",
        "ok": bool(seed_ctx.get("ok")),
        "pairing_code_present": seed_ctx.get("pairing_code_present"),
        "feature": feature,
        "duration_ms": int((time.perf_counter() - t0) * 1000),
    })
    if not seed_ctx.get("ok"):
        return _fail(
            tid,
            scenario_id,
            pipe,
            str(seed_ctx.get("error") or "SEED_CREDENTIALS_FAIL"),
            str(seed_ctx.get("error") or "credenciais do seed ausentes"),
        )

    seed_values = _seed_values_from_handoff(str(seed_ctx.get("handoff_path") or ""))
    if feature == "pairing" and not seed_values.get("seed.pairing_code"):
        return _fail(
            tid,
            scenario_id,
            pipe,
            "SEED_PAIRING_CODE_EMPTY",
            "pairing_code ausente no handoff após seed",
        )
    if feature == "login" and not (
        seed_values.get("seed.parent_email") and seed_values.get("seed.parent_password")
    ):
        return _fail(
            tid,
            scenario_id,
            pipe,
            "SEED_LOGIN_EMPTY",
            "email/password ausentes no handoff após seed",
        )

    serial = str((device or {}).get("serial") or stack(app)["emulator"])
    bundle = str((device or {}).get("bundle_id") or stack(app)["bundle_id"])
    t0 = time.perf_counter()
    if app == "parent":
        if _package_installed(serial, bundle):
            apk_gate: dict[str, Any] = {"ok": True, "rebuilt": False, "serial": serial}
        else:
            repair = _repair_stack_stage(
                "apk",
                "T1",
                child_only=False,
                skip_build=False,
                feature=feature,
                timeout_sec=min(timeout_sec, 600),
            )
            apk_gate = {
                "ok": _package_installed(serial, bundle),
                "rebuilt": True,
                "repair": repair,
                "serial": serial,
            }
    else:
        apk_gate = _ensure_apk_or_rebuild(
            child_only=bool(child_only),
            feature=feature,
            timeout_sec=min(timeout_sec, 600),
        )
        apk_gate = {**apk_gate, "serial": serial, "bundle": bundle}
        if apk_gate.get("ok") and not _package_installed(serial, bundle):
            apk_gate = {
                "ok": False,
                "error": "apk_not_on_device_serial",
                "serial": serial,
                "bundle": bundle,
            }
    phases.append({
        "phase": "apk_open_or_rebuild",
        **apk_gate,
        "duration_ms": int((time.perf_counter() - t0) * 1000),
    })
    if not apk_gate.get("ok"):
        return _fail(
            tid,
            scenario_id,
            pipe,
            "APK_REBUILD_FAIL",
            str(apk_gate.get("error") or "apk não instalado"),
        )

    pre_script = {
        "total_ms": int((time.perf_counter() - pre_t0) * 1000),
        "phases": [
            {"phase": p.get("phase"), "ok": p.get("ok"), "duration_ms": p.get("duration_ms")}
            for p in phases
            if p.get("phase")
        ],
    }

    # --- gera + executa script Appium a partir do pipeline ---
    prev_skip = os.environ.get("GF_SKIP_PRECHECK")
    os.environ["GF_SKIP_PRECHECK"] = "1"
    try:
        runtime = generate_and_run_from_pipeline(
            pipeline=pipe,
            task_id=tid,
            scenario_id=scenario_id or "scenario",
            app=app,
            timeout_sec=timeout_sec,
            dry_run=False,
            device=device,
            seed_values=seed_values,
        )
    finally:
        if prev_skip is None:
            os.environ.pop("GF_SKIP_PRECHECK", None)
        else:
            os.environ["GF_SKIP_PRECHECK"] = prev_skip

    if isinstance(runtime, dict):
        runtime["pre_script"] = pre_script

    phases.append({
        "phase": "generate_and_run_appium_script",
        "ok": bool(runtime.get("ok")),
        "script_path": (runtime.get("generated") or {}).get("script_path"),
        "blocking_reason": runtime.get("blocking_reason"),
    })

    # greeting-*: só reforça captura se o pipeline NÃO gerou PNG
    scenario_ev: dict[str, Any] | None = None
    pipeline_png = _first_png(str(runtime.get("package_dir") or ""), None, runtime)
    if (
        runtime.get("ok")
        and pipe.get("screenshot")
        and scenario_id.lower().startswith("greeting-")
        and not pipeline_png
    ):
        try:
            from lib.mobile.scenario_evidence import capture_scenario_evidence

            scenario_ev = capture_scenario_evidence(
                tid,
                [scenario_id],
                emulator_serial=serial,
                record_video=False,
            )
            phases.append({"phase": "capture_scenario_evidence", **scenario_ev})
        except Exception as exc:  # noqa: BLE001
            phases.append({"phase": "capture_scenario_evidence", "ok": False, "error": str(exc)})
    elif pipeline_png and scenario_id.lower().startswith("greeting-"):
        phases.append({
            "phase": "capture_scenario_evidence",
            "ok": True,
            "skipped": True,
            "reason": "pipeline_capture_ok",
            "png": pipeline_png,
        })

    suite_ok = bool(runtime.get("suite_ok", runtime.get("ok")))
    evidence_ok = bool(runtime.get("evidence_ok", runtime.get("ok")))
    if scenario_ev is not None:
        evidence_ok = evidence_ok and bool(scenario_ev.get("ok"))
    final_ok = suite_ok and evidence_ok

    cleanup_result: dict[str, Any] | None = None
    do_cleanup = cleanup_on_success and final_ok and bool(db_seed_cfg.get("cleanup", True))
    if do_cleanup and tid:
        cleanup_result = run_db_cleanup(task_id=tid, dry_run=False)
        phases.append({"phase": "cleanup_seed", "ok": bool(cleanup_result.get("ok"))})
        reset = _reset_handoff_cycle(_stage_handoff_path())
        phases.append({"phase": "credentials_reset", "ok": bool(reset.get("ok"))})
    elif not final_ok:
        phases.append({"phase": "cleanup_seed", "ok": None, "skipped": True, "reason": "suite_or_evidence_fail"})

    summary = _summarize_return(
        ticket_id=tid,
        scenario_id=scenario_id,
        pipe=pipe,
        runtime=runtime,
        scenario_ev=scenario_ev,
    )
    log_recovery(
        task_id=tid or "evidence",
        phase="qa_generate_evidence_done",
        ok=_summary_ok(summary),
        reason="ok" if _summary_ok(summary) else "EVIDENCE_OR_SUITE_FAIL",
    )
    return summary


def _fail(
    ticket_id: str,
    scenario_id: str,
    pipe: dict[str, Any],
    reason: str,
    description: str,
) -> dict[str, Any]:
    summary = _summarize_return(
        ticket_id=ticket_id,
        scenario_id=scenario_id,
        pipe=pipe if isinstance(pipe, dict) else {},
        fail_type=reason,
        fail_description=description,
    )
    log_recovery(
        task_id=ticket_id or "evidence",
        phase="qa_generate_evidence_fail",
        ok=False,
        reason=reason,
    )
    return summary
