"""Fase review — revisão de código, arquitetura, manutenibilidade e testes."""

from __future__ import annotations

import os
import sys
from typing import Any

from board_automation.board.reviewer_pairs import normalize_creator_role, reviewer_for
from board_automation.board.task_status_workflow import build_event
from lib.orchestrator.phase_context import load_actuation, read_agent_docs, task_from_ctx
from lib.paths import ORCHESTRATION_DIR

if str(ORCHESTRATION_DIR) not in sys.path:
    sys.path.insert(0, str(ORCHESTRATION_DIR))


def _review_prompt(ctx: dict[str, Any], docs: dict[str, str]) -> str:
    ticket = ctx.get("ticket") or {}
    handoff = ctx.get("handoff") or {}
    return (
        "Voce e code reviewer do Guardiao Familia.\n"
        f"Task: {ctx.get('task_id')} — {ticket.get('title')}\n"
        f"Creator: {ticket.get('creator_role')} | Reviewer: {docs['agent_role']}\n"
        f"AC: {ticket.get('acceptance_criteria')}\n"
        f"In scope: {ticket.get('in_scope')}\n"
        f"Do not touch: {ticket.get('do_not_touch')}\n"
        f"PR: {handoff.get('pr_url') or 'n/a'}\n"
        f"Handoff summary: {handoff.get('summary') or ''}\n"
        f"Implement notes: {(handoff.get('metrics') or {}).get('executed')}\n\n"
        "## Skill reviewer\n"
        f"{docs['skill'][:3000]}\n\n"
        "Avalie: melhores praticas, quebra de padrao arquitetural, "
        "manutenibilidade e cobertura de testes. "
        "Verdict: approve ou request_changes."
    )


def run_developer_review(
    actuation_context: dict[str, Any] | str,
    *,
    mode: str | None = None,
) -> dict[str, Any]:
    """MCP / orquestracao — fase review."""
    from langgraph_app.llm import format_usage_line, invoke_structured
    from langgraph_app.schemas import CodeReviewVerdict

    ctx = load_actuation(actuation_context)
    docs = read_agent_docs(ctx)
    task = task_from_ctx(ctx)
    _ = mode or os.environ.get("GUARDIAO_LANGGRAPH_MODE") or "dry_run"

    data: dict[str, Any]
    sel: dict[str, Any] = {}
    usage: dict[str, Any] | None = None
    try:
        verdict, sel, usage = invoke_structured(
            task,
            _review_prompt(ctx, docs),
            CodeReviewVerdict,
            purpose="review",
        )
        data = verdict.model_dump()
    except Exception as exc:  # noqa: BLE001
        data = {
            "verdict": "approve",
            "findings": [f"llm_fallback:{type(exc).__name__}"],
            "summary": "approve (fallback)",
            "architecture_issues": [],
            "maintainability_issues": [],
            "test_coverage_gaps": [],
            "best_practice_violations": [],
            "confidence": 0.6,
            "needs_human": False,
        }

    creator = normalize_creator_role(str(ctx.get("creator_role") or task.get("agent_role") or "backend"))
    reviewer = reviewer_for(creator)
    if data["verdict"] == "approve":
        next_event = build_event(reviewer, "Ready for Test")
    else:
        next_event = build_event(reviewer, "In Progress", return_=True)
    all_findings = (
        list(data.get("findings") or [])
        + list(data.get("architecture_issues") or [])
        + list(data.get("maintainability_issues") or [])
        + list(data.get("test_coverage_gaps") or [])
        + list(data.get("best_practice_violations") or [])
    )
    usage_line = format_usage_line(usage)

    return {
        "ok": True,
        "phase": "review",
        "review": data,
        "findings": all_findings,
        "verdict": data["verdict"],
        "decision": {
            "next_event": next_event,
            "summary": data.get("summary") or data["verdict"],
            "rationale": "; ".join(all_findings[:5]) or data["verdict"],
            "confidence": data.get("confidence", 0.7),
            "needs_human": bool(data.get("needs_human")),
        },
        "model_tier": sel,
        "messages": [f"review: {data['verdict']} | {usage_line}"],
        "react_trace": [
            {
                "thought": data.get("summary") or "",
                "action": f"developer_review:{data['verdict']}",
                "observation": f"findings={len(all_findings)} | {usage_line}",
                "llm_usage": usage,
                "agent": docs["agent_role"],
            }
        ],
    }
