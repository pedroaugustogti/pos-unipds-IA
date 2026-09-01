"""Fase implement — codificação, testes unitários, plano de execução."""

from __future__ import annotations

import os
import sys
from typing import Any

from lib.orchestrator.phase_context import load_actuation, read_agent_docs, task_from_ctx
from lib.paths import ORCHESTRATION_DIR

if str(ORCHESTRATION_DIR) not in sys.path:
    sys.path.insert(0, str(ORCHESTRATION_DIR))


def _build_plan_prompt(ctx: dict[str, Any], docs: dict[str, str]) -> str:
    ticket = ctx.get("ticket") or {}
    return (
        "Voce e desenvolvedor do Guardiao Familia.\n"
        f"Task: {ctx.get('task_id')} — {ticket.get('title')}\n"
        f"Role: {docs['agent_role']}\n"
        f"AC: {ticket.get('acceptance_criteria')}\n"
        f"In scope: {ticket.get('in_scope')}\n"
        f"Out of scope: {ticket.get('out_of_scope')}\n"
        f"Do not touch: {ticket.get('do_not_touch')}\n"
        f"Suggested files: {ticket.get('suggested_files')}\n"
        f"Handoff: {(ctx.get('handoff') or {}).get('summary', '')}\n\n"
        "## Skill do agente\n"
        f"{docs['skill'][:4000]}\n\n"
        "Monte um plano de implementacao com passos ordenados, arquivos a alterar "
        "e testes unitarios a criar/ajustar. Respeite escopo e skill."
    )


def run_developer_implement(
    actuation_context: dict[str, Any] | str,
    *,
    mode: str | None = None,
) -> dict[str, Any]:
    """MCP / orquestracao — fase implement (skill → plan → artifact → decide)."""
    from lib.orchestrator.phase_steps_implement import step_artifact, step_decide, step_plan, step_skill

    run_mode = (mode or os.environ.get("GUARDIAO_LANGGRAPH_MODE") or "dry_run").strip()
    s1 = step_skill(actuation_context)
    ctx = s1["actuation_context"]
    docs = s1["agent_docs"]
    s2 = step_plan(ctx, docs)
    s3 = step_artifact(ctx, s2["implement_plan"], mode=run_mode)
    s4 = step_decide(s2["implement_plan"], creator_role=str(ctx.get("creator_role") or ""))

    trace = (
        list(s1.get("react_trace") or [])
        + list(s2.get("react_trace") or [])
        + list(s3.get("react_trace") or [])
        + list(s4.get("react_trace") or [])
    )
    return {
        "ok": True,
        "phase": "implement",
        "phase_tool": "developer_implement",
        **s1,
        **s2,
        **s3,
        **s4,
        "messages": (s1.get("messages") or []) + (s2.get("messages") or []) + (s3.get("messages") or []) + (s4.get("messages") or []),
        "react_trace": trace,
    }
