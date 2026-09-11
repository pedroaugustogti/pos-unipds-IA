"""Fase QA — evidências via MCP mobile e validação de critérios de aceite."""

from __future__ import annotations

import os
from typing import Any

from board_automation.board.reviewer_pairs import QA_GATE_ROLE
from board_automation.board.task_status_workflow import build_event
from lib.orchestrator.phase_context import load_actuation, task_from_ctx


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
    worker_mode: str | None = None,
) -> dict[str, Any]:
    """Orquestra multi-cenário: caminho local (host) ou docker (1 container/cenário)."""
    from lib.mobile.qa_scenario_orchestrator import run_scenario_orchestrator

    return run_scenario_orchestrator(
        task=task,
        actuation_context=actuation_context,
        dry_run=dry_run,
        worker_mode=worker_mode,  # type: ignore[arg-type]
    )


def run_qa_validate(
    actuation_context: dict[str, Any] | str,
    *,
    mode: str | None = None,
    worker_mode: str | None = None,
) -> dict[str, Any]:
    """MCP / orquestracao — fase QA só com actuation_context + cadeia MCP mobile.

    worker_mode:
      - local  → workers na máquina host (sem Docker)
      - docker → 1 container isolado por cenário
    """
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
                    task,
                    dry_run=dry,
                    actuation_context=actuation_context,
                    worker_mode=worker_mode,
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
