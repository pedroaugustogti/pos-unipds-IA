"""Fase QA — evidências via MCP mobile e validação de critérios de aceite."""

from __future__ import annotations

import os
from typing import Any

from board_automation.board.reviewer_pairs import QA_GATE_ROLE
from board_automation.board.task_status_workflow import build_event
from lib.orchestrator.phase_context import load_actuation, task_from_ctx


def _unwrap_mcp(payload: dict[str, Any]) -> dict[str, Any]:
    """Extrai `result` do envelope MCP e propaga `ok` do envelope quando faltar no inner."""
    inner = payload.get("result")
    if not isinstance(inner, dict):
        return payload
    # generate summary não traz `ok`; init/pipeline trazem apps_ready / scenario_pipeline
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


def _validate_ac_from_context(task: dict[str, Any], qa_result: dict[str, Any]) -> dict[str, Any]:
    """AC só do actuation_context — sem LLM / skill / board externo."""
    ac = list(task.get("acceptance_criteria") or [])
    mcp_ok = bool(qa_result.get("ok")) and not qa_result.get("skipped")
    if not ac:
        return {
            "summary": "Sem AC no actuation_context; gate = resultado da cadeia MCP",
            "all_passed": mcp_ok,
            "ac_checks": [],
        }
    checks = [
        {
            "criterion": str(c),
            "status": "pass" if mcp_ok else "fail",
            "evidence": "mcp_chain" if mcp_ok else str(qa_result.get("blocking_reason") or "FAIL"),
        }
        for c in ac
    ]
    return {
        "summary": "AC avaliados pelo resultado MCP" if mcp_ok else "AC falharam — cadeia MCP não ok",
        "all_passed": mcp_ok,
        "ac_checks": checks,
    }


def _run_mobile_mcp_chain(
    task: dict[str, Any],
    *,
    dry_run: bool,
    actuation_context: dict[str, Any] | str,
) -> dict[str, Any]:
    """Orquestra MCP: qa_init_suite_mobile → qa_pipeline_evidence → qa_generate_evidence."""
    from lib.mobile.mobile_task import (
        mobile_setup_evidence_params,
        resolve_evidence_pipeline,
        resolve_suites_mobile,
        wants_mobile_setup_evidence,
    )
    from lib.mobile.qa_mobile_setup_evidence import format_evidence_comment

    tid = str(task.get("id") or "")
    if not wants_mobile_setup_evidence(task):
        return {"ok": False, "skipped": True, "reason": "task sem QA mobile MCP"}

    evidence_pipeline = resolve_evidence_pipeline(task)
    params = mobile_setup_evidence_params(task)
    suites_mobile = params.get("suites_mobile") or resolve_suites_mobile(task)
    timeout_sec = int(params.get("timeout_sec") or 900)
    feature = str(params.get("feature") or "")

    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "task_id": tid,
            "mode": "mcp-qa",
            "suites_mobile": suites_mobile,
            "would_run": "qa_init_suite_mobile → qa_pipeline_evidence → qa_generate_evidence",
            "evidence_pipeline": evidence_pipeline,
        }

    from lib.mcp_invoke import qa_generate_evidence, qa_init_suite_mobile, qa_pipeline_evidence
    import json

    mcp_steps: list[dict[str, Any]] = []
    ctx_json = (
        actuation_context
        if isinstance(actuation_context, str)
        else json.dumps(actuation_context, default=str)
    )

    init_raw = qa_init_suite_mobile(
        task_id=tid,
        suites_mobile=json.dumps(suites_mobile),
        skip_build=True,
        feature=feature,
        timeout_sec=min(timeout_sec, 600),
        dry_run=False,
    )
    init = _unwrap_mcp(init_raw if isinstance(init_raw, dict) else {})
    apps_ready_ok = bool(init.get("apps_ready_ok", init.get("apps_ready")))
    init_ok = bool(init.get("ok") and apps_ready_ok)
    mcp_steps.append({
        "tool": "qa_init_suite_mobile",
        "ok": init_ok,
        "suites_mobile": suites_mobile,
        "apps_ready_ok": apps_ready_ok,
        "blocking_reason": init.get("blocking_reason"),
        "checks_parent": init.get("checks_parent"),
        "checks_child": init.get("checks_child"),
    })
    if not init_ok:
        return {
            "ok": False,
            "task_id": tid,
            "mode": "mcp-qa",
            "suites_mobile": suites_mobile,
            "suite_ok": False,
            "evidence_ok": False,
            "evidence_pipeline": evidence_pipeline,
            "mcp_steps": mcp_steps,
            "executed": ["qa_init_suite_mobile"],
            "blocking_reason": init.get("blocking_reason") or "INIT_APPS_NOT_READY",
            "init": init,
            "suite": {},
            "db_seed": None,
            "db_cleanup": None,
        }

    qa_scenarios = list((task.get("qa") or {}).get("scenarios") or [])
    scenario_id = str(qa_scenarios[0]).strip() if qa_scenarios else ""

    pipe_raw = qa_pipeline_evidence(
        actuation_context=ctx_json,
        apps_ready_ok=apps_ready_ok,
        scenario_id=scenario_id,
        dry_run=False,
    )
    pipe = _unwrap_mcp(pipe_raw if isinstance(pipe_raw, dict) else {})
    pipe_ok = bool(pipe.get("ok") and pipe.get("scenario_pipeline"))
    mcp_steps.append({
        "tool": "qa_pipeline_evidence",
        "ok": pipe_ok,
        "apps_ready_ok": apps_ready_ok,
        "scenario_id": pipe.get("scenario_id"),
        "blocking_reason": pipe.get("blocking_reason"),
    })
    if not pipe_ok:
        return {
            "ok": False,
            "task_id": tid,
            "mode": "mcp-qa",
            "suites_mobile": suites_mobile,
            "suite_ok": False,
            "evidence_ok": False,
            "evidence_pipeline": evidence_pipeline,
            "mcp_steps": mcp_steps,
            "executed": [s["tool"] for s in mcp_steps],
            "blocking_reason": pipe.get("blocking_reason") or "PIPELINE_NOT_READY",
            "init": init,
            "pipeline": pipe,
            "suite": {},
            "db_seed": None,
            "db_cleanup": None,
        }

    evidence_raw = qa_generate_evidence(
        pipeline_result=json.dumps(pipe_raw if isinstance(pipe_raw, dict) else pipe, default=str),
        timeout_sec=timeout_sec,
        dry_run=False,
    )
    evidence = _unwrap_mcp(evidence_raw if isinstance(evidence_raw, dict) else {})
    shot = evidence.get("screenshot") if isinstance(evidence.get("screenshot"), dict) else {}
    video = evidence.get("video_record") if isinstance(evidence.get("video_record"), dict) else {}
    shot_err = str((shot.get("error_runtime") or {}).get("type") or "")
    video_err = str((video.get("error_runtime") or {}).get("type") or "")
    shot_ok = not shot_err
    video_ok = not video_err
    evidence_envelope_ok = bool(evidence.get("ok", evidence_raw.get("ok")))
    has_artifact = bool(shot.get("evidence") or video.get("evidence"))
    # passa só com envelope ok + sem error_runtime + (artefato OU runtime ok explícito)
    suite_pass = evidence_envelope_ok and shot_ok and video_ok and (
        has_artifact or bool(evidence.get("suite_ok") or evidence.get("evidence_ok"))
    )
    if not suite_pass and has_artifact and shot_ok and video_ok and evidence_envelope_ok:
        suite_pass = True
    blocking = None
    if not suite_pass:
        blocking = (
            shot_err
            or video_err
            or str(evidence.get("blocking_reason") or evidence.get("error") or "")
            or ("EVIDENCE_FAIL" if evidence_envelope_ok else "GENERATE_EVIDENCE_FAIL")
        )
    mcp_steps.append({
        "tool": "qa_generate_evidence",
        "ok": suite_pass,
        "ticket_id": evidence.get("ticket_id"),
        "scenario_id": evidence.get("scenario_id"),
        "screenshot": shot,
        "video_record": video,
        "blocking_reason": blocking,
    })
    package_dir = str(shot.get("evidence") or video.get("evidence") or "")
    if package_dir:
        from pathlib import Path
        package_dir = str(Path(package_dir).parent)
    comment = format_evidence_comment(
        {
            "task_id": tid,
            "ok": suite_pass,
            "package_dir": package_dir,
            "artifacts": {},
            "setup_root": "",
        }
    )
    return {
        "ok": suite_pass,
        "task_id": tid,
        "mode": "mcp-qa",
        "suites_mobile": suites_mobile,
        "suite_ok": suite_pass,
        "evidence_ok": suite_pass,
        "evidence_pipeline": evidence_pipeline,
        "mcp_steps": mcp_steps,
        "executed": [s["tool"] for s in mcp_steps],
        "evidence_paths": [str(package_dir)] if package_dir else [],
        "package_dir": package_dir or None,
        "comment": comment,
        "init": init,
        "pipeline": pipe,
        "evidence": evidence,
        "suite": {"ok": suite_pass, "package_dir": package_dir},
        "db_seed": None,
        "db_cleanup": None,
        "blocking_reason": blocking,
    }


def run_qa_validate(
    actuation_context: dict[str, Any] | str,
    *,
    mode: str | None = None,
) -> dict[str, Any]:
    """MCP / orquestracao — fase QA só com actuation_context + cadeia MCP mobile."""
    ctx = load_actuation(actuation_context)
    task = task_from_ctx(ctx)
    tid = str(task.get("id") or "")
    run_mode = (mode or os.environ.get("GUARDIAO_LANGGRAPH_MODE") or "dry_run").strip()
    dry = run_mode == "dry_run"

    qa_pass_event = build_event(QA_GATE_ROLE, "In Pull Request")
    qa_fail_event = build_event(QA_GATE_ROLE, "In Progress", return_=True)
    qa_result: dict[str, Any] = {"ok": True, "skipped": True}
    next_event = qa_pass_event
    summary = "QA tipado OK"
    rationale = "qa_validate"

    try:
        from board_automation.board.infra_policy import (
            POLICY_SUMMARY,
            is_infra_okr_task,
            validate_infra_executed,
        )

        if is_infra_okr_task(task):
            ho = ctx.get("handoff") or {}
            executed = list((ho.get("metrics") or {}).get("executed") or [])
            ok_policy, reason = validate_infra_executed(executed)
            qa_result = {"ok": ok_policy, "infra": True, "policy": POLICY_SUMMARY, "reason": reason}
            if ok_policy:
                summary = "OKR infra: Terraform only"
                rationale = POLICY_SUMMARY
            else:
                next_event = qa_fail_event
                summary = f"Violacao politica infra: {reason}"
                rationale = reason
    except Exception as exc:  # noqa: BLE001
        qa_result = {"ok": False, "error": str(exc)[:200]}

    if not qa_result.get("infra"):
        try:
            from lib.mobile.mobile_task import wants_mobile_setup_evidence

            if wants_mobile_setup_evidence(task):
                qa_result = _run_mobile_mcp_chain(
                    task, dry_run=dry, actuation_context=actuation_context
                )
            else:
                qa_result = {
                    "ok": False,
                    "skipped": True,
                    "reason": "task sem QA mobile no actuation_context.ticket.qa",
                    "task_id": tid,
                }
        except Exception as exc:  # noqa: BLE001
            qa_result = {"ok": False, "error": str(exc)[:300]}
            next_event = qa_fail_event
            summary = f"QA erro: {type(exc).__name__}"
            rationale = str(exc)[:200]

    if qa_result.get("ok") is False and not qa_result.get("skipped"):
        next_event = qa_fail_event
        summary = summary if summary != "QA tipado OK" else "QA FAIL"
        rationale = str(
            qa_result.get("error")
            or qa_result.get("blocking_reason")
            or qa_result.get("reason")
            or "FAIL"
        )[:500]
    elif qa_result.get("ok") and not qa_result.get("skipped"):
        next_event = qa_pass_event
        summary = "QA PASS — evidencias MCP validadas"

    ac_report = _validate_ac_from_context(task, qa_result)
    if ac_report.get("ac_checks") and not ac_report.get("all_passed"):
        next_event = qa_fail_event
        summary = "AC nao atendidos"
        rationale = ac_report.get("summary") or "AC fail"

    return {
        "ok": bool(qa_result.get("ok")) and ac_report.get("all_passed", True),
        "phase": "qa",
        "qa_result": qa_result,
        "ac_validation": ac_report,
        "evidence_paths": qa_result.get("evidence_paths") or [],
        "mcp_steps": qa_result.get("mcp_steps") or [],
        "decision": {
            "next_event": next_event,
            "summary": summary,
            "rationale": rationale,
            "confidence": 0.95 if next_event == qa_pass_event else 0.7,
            "needs_human": False,
        },
        "messages": [f"qa: {next_event}"],
        "react_trace": [
            {
                "thought": ac_report.get("summary") or summary,
                "action": "qa_validate",
                "observation": f"{next_event} mcp_steps={len(qa_result.get('mcp_steps') or [])}",
                "agent": "qa-gate",
            }
        ],
    }
