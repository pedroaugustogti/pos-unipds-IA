"""Cadeia single-scenario: init → pipeline → generate (host e worker)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


def unwrap_tool_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Extrai `result` do envelope e propaga `ok` quando faltar no inner."""
    if not isinstance(payload, dict):
        return {}
    inner = payload.get("result")
    if not isinstance(inner, dict):
        return payload
    looks_like_tool = (
        "ok" in inner
        or "apps_ready" in inner
        or "apps_ready_ok" in inner
        or "scenario_pipeline" in inner
        or "screenshot" in inner
        or "video_record" in inner
    )
    if not looks_like_tool:
        return payload
    out = dict(inner)
    if "ok" not in out and "ok" in payload:
        out["ok"] = bool(payload.get("ok"))
    return out


def score_generate_evidence(
    evidence: dict[str, Any],
    evidence_raw: dict[str, Any] | None = None,
) -> tuple[bool, str | None]:
    """Avalia PASS do generate a partir de slots screenshot/video_record."""
    evidence_raw = evidence_raw or {}
    shot = evidence.get("screenshot") if isinstance(evidence.get("screenshot"), dict) else {}
    video = evidence.get("video_record") if isinstance(evidence.get("video_record"), dict) else {}
    shot_err = str((shot.get("error_runtime") or {}).get("type") or "")
    video_err = str((video.get("error_runtime") or {}).get("type") or "")
    shot_ok = not shot_err
    video_ok = not video_err
    envelope_ok = bool(evidence.get("ok", evidence_raw.get("ok")))
    # artefato nomeado *_FAIL* sem erro tipado ainda conta como falha
    shot_path = str(shot.get("evidence") or "").replace("\\", "/").lower()
    video_path = str(video.get("evidence") or "").replace("\\", "/").lower()
    fail_named = ("capture_fail" in shot_path) or ("/flow_fail_" in video_path) or ("\\flow_fail_" in str(video.get("evidence") or "").lower())
    has_artifact = bool(shot.get("evidence") or video.get("evidence"))
    suite_pass = envelope_ok and shot_ok and video_ok and not fail_named and (
        has_artifact or bool(evidence.get("suite_ok") or evidence.get("evidence_ok"))
    )
    blocking = None
    if not suite_pass:
        blocking = (
            shot_err
            or video_err
            or str(evidence.get("blocking_reason") or evidence.get("error") or "")
            or ("EVIDENCE_FAIL_NAMED" if fail_named else "")
            or ("EVIDENCE_FAIL" if envelope_ok else "GENERATE_EVIDENCE_FAIL")
        )
    return suite_pass, blocking or None


def run_single_scenario_chain(
    *,
    task_id: str,
    scenario_id: str,
    actuation_context: dict[str, Any] | str,
    suites_mobile: dict[str, Any],
    feature: str = "",
    timeout_sec: int = 900,
    dry_run: bool = False,
    skip_build: bool = True,
    on_phase: Any | None = None,
) -> dict[str, Any]:
    """Executa init → pipeline → generate para um cenário.

    `on_phase(phase, payload)` é opcional (status do worker).
    """
    from lib.mobile.qa_generate_evidence import run_qa_generate_evidence
    from lib.mobile.qa_init_suite_mobile import run_qa_init_suite_mobile
    from lib.mobile.qa_pipeline_evidence import run_qa_pipeline_evidence

    def _notify(phase: str, **extra: Any) -> None:
        if on_phase:
            on_phase(phase, extra)

    mcp_steps: list[dict[str, Any]] = []
    ctx = actuation_context
    chain_t0 = time.perf_counter()

    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "task_id": task_id,
            "scenario_id": scenario_id,
            "mode": "scenario-chain",
            "suites_mobile": suites_mobile,
            "mcp_steps": [],
            "executed": [],
            "would_run": ["qa_init_suite_mobile", "qa_pipeline_evidence", "qa_generate_evidence"],
        }

    _notify("init", scenario_id=scenario_id)
    t_init = time.perf_counter()
    init = run_qa_init_suite_mobile(
        task_id=task_id,
        suites_mobile=suites_mobile,
        skip_build=skip_build,
        feature=feature,
        timeout_sec=min(timeout_sec, 600),
        dry_run=False,
    )
    init_ms = int((time.perf_counter() - t_init) * 1000)
    if not isinstance(init, dict):
        init = {}
    apps_ready_ok = bool(init.get("apps_ready_ok", init.get("apps_ready")))
    init_ok = bool(init.get("ok") and apps_ready_ok)
    # marca quando emulador ficou ok na timeline do init (se houver)
    emu_ready_ts = None
    for ev in init.get("timeline") or []:
        if (
            isinstance(ev, dict)
            and ev.get("check") == "emulator"
            and ev.get("ok")
            and ev.get("type") == "check_result"
        ):
            emu_ready_ts = ev.get("ts")
    mcp_steps.append(
        {
            "tool": "qa_init_suite_mobile",
            "ok": init_ok,
            "suites_mobile": suites_mobile,
            "apps_ready_ok": apps_ready_ok,
            "blocking_reason": init.get("blocking_reason"),
            "scenario_id": scenario_id,
            "checks_parent": init.get("checks_parent"),
            "checks_child": init.get("checks_child"),
            "timeline": init.get("timeline"),
            "appium_mode": init.get("appium_mode"),
            "metro_bundle_refreshed": bool(init.get("metro_bundle_refreshed")),
            "duration_ms": init_ms,
            "emulator_ready_ts": emu_ready_ts,
        }
    )
    if not init_ok:
        blocking = str(init.get("blocking_reason") or "INIT_APPS_NOT_READY")
        _notify("done", ok=False, blocking_reason=blocking)
        return {
            "ok": False,
            "task_id": task_id,
            "scenario_id": scenario_id,
            "mode": "scenario-chain",
            "suites_mobile": suites_mobile,
            "suite_ok": False,
            "evidence_ok": False,
            "mcp_steps": mcp_steps,
            "executed": ["qa_init_suite_mobile"],
            "blocking_reason": blocking,
            "init": init,
            "evidence": {},
            "evidence_paths": [],
        }

    _notify("pipeline", scenario_id=scenario_id, apps_ready_ok=apps_ready_ok)
    t_pipe = time.perf_counter()
    pipe = run_qa_pipeline_evidence(
        actuation_context=ctx,
        apps_ready_ok=apps_ready_ok,
        scenario_id=scenario_id,
        metro_bundle_refreshed=bool(init.get("metro_bundle_refreshed")),
        dry_run=False,
    )
    pipe_ms = int((time.perf_counter() - t_pipe) * 1000)
    if not isinstance(pipe, dict):
        pipe = {}
    pipe_ok = bool(pipe.get("ok") and pipe.get("scenario_pipeline"))
    mcp_steps.append(
        {
            "tool": "qa_pipeline_evidence",
            "ok": pipe_ok,
            "apps_ready_ok": apps_ready_ok,
            "scenario_id": pipe.get("scenario_id") or scenario_id,
            "blocking_reason": pipe.get("blocking_reason"),
            "duration_ms": pipe_ms,
        }
    )
    if not pipe_ok:
        blocking = str(pipe.get("blocking_reason") or "PIPELINE_NOT_READY")
        _notify("done", ok=False, blocking_reason=blocking)
        return {
            "ok": False,
            "task_id": task_id,
            "scenario_id": scenario_id,
            "mode": "scenario-chain",
            "suites_mobile": suites_mobile,
            "suite_ok": False,
            "evidence_ok": False,
            "mcp_steps": mcp_steps,
            "executed": [s["tool"] for s in mcp_steps],
            "blocking_reason": blocking,
            "init": init,
            "pipeline": pipe,
            "evidence": {},
            "evidence_paths": [],
        }

    _notify("generate", scenario_id=scenario_id)
    t_gen = time.perf_counter()
    # pipeline_result aceita dict ou JSON string
    evidence = run_qa_generate_evidence(
        pipeline_result=pipe,
        timeout_sec=timeout_sec,
        dry_run=False,
    )
    gen_ms = int((time.perf_counter() - t_gen) * 1000)
    if not isinstance(evidence, dict):
        evidence = {}
    # run_qa_generate_evidence retorna summary direto (sem envelope MCP)
    # Normaliza ok via score
    scored = dict(evidence)
    if "ok" not in scored:
        from lib.mobile.qa_generate_evidence import _summary_ok

        scored["ok"] = _summary_ok(evidence)
    suite_pass, blocking = score_generate_evidence(scored, evidence)
    shot = scored.get("screenshot") if isinstance(scored.get("screenshot"), dict) else {}
    video = scored.get("video_record") if isinstance(scored.get("video_record"), dict) else {}
    pre_script = scored.get("pre_script") if isinstance(scored.get("pre_script"), dict) else {}
    mcp_steps.append(
        {
            "tool": "qa_generate_evidence",
            "ok": suite_pass,
            "ticket_id": scored.get("ticket_id") or task_id,
            "scenario_id": scored.get("scenario_id") or scenario_id,
            "screenshot": shot,
            "video_record": video,
            "blocking_reason": blocking,
            "duration_ms": gen_ms,
            "pre_script": pre_script,
        }
    )
    package_dir = str(shot.get("evidence") or video.get("evidence") or "")
    if package_dir:
        package_dir = str(Path(package_dir).parent)
    evidence_paths = [package_dir] if package_dir else []
    pre_script_ms = int(pre_script.get("total_ms") or 0)
    boot_runtime_ms = int(
        (
            ((scored.get("runtime_timing") or {}).get("boot_total_ms"))
            if isinstance(scored.get("runtime_timing"), dict)
            else 0
        )
        or 0
    )
    timing_gap = {
        "init_ms": init_ms,
        "pipeline_ms": pipe_ms,
        "generate_total_ms": gen_ms,
        "pre_script_ms": pre_script_ms,
        "boot_runtime_ms": boot_runtime_ms,
        "post_init_to_app_open_estimate_ms": pipe_ms + pre_script_ms + boot_runtime_ms,
        "chain_total_ms": int((time.perf_counter() - chain_t0) * 1000),
        "note": "post_init_to_app_open ≈ pipeline + seed/verify/write + boot (metro/reverse/session/video) antes do step launch",
    }
    _notify(
        "done",
        ok=suite_pass,
        blocking_reason=blocking,
        evidence={"screenshot": shot, "video_record": video},
        timing_gap=timing_gap,
    )
    return {
        "ok": suite_pass,
        "task_id": task_id,
        "scenario_id": scenario_id,
        "mode": "scenario-chain",
        "suites_mobile": suites_mobile,
        "suite_ok": suite_pass,
        "evidence_ok": suite_pass,
        "mcp_steps": mcp_steps,
        "executed": [s["tool"] for s in mcp_steps],
        "evidence_paths": evidence_paths,
        "package_dir": package_dir or None,
        "init": init,
        "pipeline": pipe,
        "evidence": scored,
        "suite": {"ok": suite_pass, "package_dir": package_dir},
        "blocking_reason": blocking,
        "screenshot": shot,
        "video_record": video,
        "timing_gap": timing_gap,
    }


def dump_ctx(actuation_context: dict[str, Any] | str) -> str:
    if isinstance(actuation_context, str):
        return actuation_context
    return json.dumps(actuation_context, ensure_ascii=False, default=str)
