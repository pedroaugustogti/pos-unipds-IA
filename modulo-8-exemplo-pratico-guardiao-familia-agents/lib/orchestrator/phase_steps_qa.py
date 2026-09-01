"""Passos qa_validate — usados pelo grafo LangGraph e MCP."""

from __future__ import annotations

import os
from typing import Any

from lib.orchestrator.phase_context import load_actuation, read_agent_docs, task_from_ctx
from lib.orchestrator.phase_qa_validate import _run_mobile_mcp_chain, _validate_ac_with_llm


def step_qa_execute(ctx: dict[str, Any] | str, *, mode: str) -> dict[str, Any]:
    """INF → mobile / hero / infra — evidências de teste."""
    loaded = load_actuation(ctx)
    task = task_from_ctx(loaded)
    tid = str(task.get("id") or "")
    dry = mode == "dry_run"
    qa_result: dict[str, Any] = {"ok": True, "skipped": True, "mode": "dry_run" if dry else "live"}
    branch = "skipped"

    try:
        from board_automation.board.infra_policy import (
            POLICY_SUMMARY,
            is_infra_okr_task,
            validate_infra_executed,
        )

        if is_infra_okr_task(task):
            branch = "infra"
            ho = loaded.get("handoff") or {}
            executed = list((ho.get("metrics") or {}).get("executed") or [])
            ok_policy, reason = validate_infra_executed(executed)
            qa_result = {
                "ok": ok_policy,
                "infra": True,
                "policy": POLICY_SUMMARY,
                "reason": reason,
                "mode": "infra",
            }
    except Exception as exc:  # noqa: BLE001
        branch = "error"
        qa_result = {"ok": False, "error": str(exc)[:200]}

    if not qa_result.get("infra") and not dry:
        try:
            from board_automation.board.board_client import comment_issue_with_image
            from lib.mobile.mobile_task import (
                is_mobile_e2e_task,
                is_mobile_pairing_task,
                wants_mobile_setup_evidence,
            )
            from lib.mobile.qa_mobile import format_qa_mobile_comment, run_mobile_pairing_qa
            from lib.mobile.qa_playwright import format_qa_issue_comment
            from lib.site.site_hero_work import is_site_hero_task, run_hero_qa

            if is_site_hero_task(task):
                branch = "hero"
                qa_result = run_hero_qa(tid)
                qa_result["mode"] = "hero"
                png = qa_result.get("png_bytes")
                comment_issue_with_image(
                    str(task.get("repo") or "guardiao-familia-site"),
                    tid,
                    format_qa_issue_comment(qa_result),
                    png if isinstance(png, (bytes, bytearray)) else None,
                    filename=str(qa_result.get("filename") or f"{tid}_hero.png"),
                    dry_run=False,
                )
                qa_result["evidence_paths"] = [str(qa_result.get("filename") or "hero.png")]
            elif wants_mobile_setup_evidence(task):
                branch = "mobile_mcp"
                qa_result = _run_mobile_mcp_chain(task, dry_run=False)
            elif is_mobile_e2e_task(task) or is_mobile_pairing_task(task):
                branch = "pairing"
                qa_result = run_mobile_pairing_qa(tid, full_ui=is_mobile_pairing_task(task))
                comment_issue_with_image(
                    str(task.get("repo") or "guardiao-familia-api"),
                    tid,
                    format_qa_mobile_comment(qa_result),
                    None,
                    dry_run=False,
                )
        except Exception as exc:  # noqa: BLE001
            branch = "error"
            qa_result = {"ok": False, "error": str(exc)[:300]}

    return {
        "actuation_context": loaded,
        "qa_result": qa_result,
        "qa_branch": branch,
        "evidence_paths": qa_result.get("evidence_paths") or [],
        "mcp_steps": qa_result.get("mcp_steps") or [],
        "phase_tool": "qa_validate",
        "react_trace": [{
            "thought": f"Executar QA ({branch})",
            "action": f"qa:execute:{branch}",
            "observation": f"ok={qa_result.get('ok')} steps={len(qa_result.get('mcp_steps') or [])}",
            "agent": "qa-gate",
        }],
        "messages": [f"qa_execute: branch={branch} ok={qa_result.get('ok')}"],
    }


def step_qa_ac_validate(ctx: dict[str, Any], qa_result: dict[str, Any]) -> dict[str, Any]:
    """AC — LLM → ac_validation → decision."""
    docs = read_agent_docs(ctx)
    task = task_from_ctx(ctx)
    ac_report = _validate_ac_with_llm(task, qa_result, docs)

    next_event = "test_passed"
    summary = "QA PASS — evidencias e AC validados"
    rationale = "qa_validate"

    if qa_result.get("ok") is False and not qa_result.get("skipped"):
        next_event = "test_failed_bug"
        summary = "QA FAIL"
        rationale = str(qa_result.get("error") or qa_result.get("reason") or "FAIL")[:500]
    elif qa_result.get("infra") and not qa_result.get("ok"):
        next_event = "test_failed_bug"
        summary = f"Violacao politica infra: {qa_result.get('reason')}"
        rationale = str(qa_result.get("reason") or "")

    if ac_report.get("ac_checks") and not ac_report.get("all_passed"):
        next_event = "test_failed_bug"
        summary = "AC nao atendidos"
        rationale = ac_report.get("summary") or "AC fail"

    return {
        "ac_validation": ac_report,
        "phase": "qa",
        "decision": {
            "next_event": next_event,
            "summary": summary,
            "rationale": rationale,
            "confidence": 0.95 if next_event == "test_passed" else 0.7,
            "needs_human": False,
        },
        "react_trace": [{
            "thought": ac_report.get("summary") or summary,
            "action": "qa:ac_validate",
            "observation": f"{next_event} all_passed={ac_report.get('all_passed')}",
            "agent": "qa-gate",
        }],
        "messages": [f"qa_ac_validate: {next_event}"],
    }
