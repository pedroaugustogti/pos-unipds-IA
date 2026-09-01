"""Passos developer_implement — usados pelo grafo LangGraph e MCP."""

from __future__ import annotations

import os
from typing import Any

from lib.orchestrator.phase_context import load_actuation, read_agent_docs, task_from_ctx
from lib.paths import LANGGRAPH_DIR, ORCHESTRATION_DIR

import sys

if str(ORCHESTRATION_DIR) not in sys.path:
    sys.path.insert(0, str(ORCHESTRATION_DIR))


def build_plan_prompt(ctx: dict[str, Any], docs: dict[str, str]) -> str:
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


def step_skill(ctx: dict[str, Any] | str) -> dict[str, Any]:
    """C1/S1 — ctx + skill + agent.md."""
    loaded = load_actuation(ctx)
    docs = read_agent_docs(loaded)
    return {
        "actuation_context": loaded,
        "agent_docs": docs,
        "phase_tool": "developer_implement",
        "react_trace": [{
            "thought": "Carregar skill e agent.md",
            "action": "implement:skill",
            "observation": docs.get("skill_path", ""),
            "agent": docs.get("agent_role"),
        }],
        "messages": [f"implement_skill: {docs.get('skill_path', '')}"],
    }


def step_plan(ctx: dict[str, Any], docs: dict[str, str]) -> dict[str, Any]:
    """L1 — LLM → ImplementPlan."""
    from langgraph_app.llm import invoke_structured
    from langgraph_app.schemas import ImplementPlan

    task = task_from_ctx(ctx)
    sel: dict[str, Any] = {}
    usage: dict[str, Any] | None = None
    try:
        plan, sel, usage = invoke_structured(
            task,
            build_plan_prompt(ctx, docs),
            ImplementPlan,
            purpose="implement_high",
        )
        plan_data = plan.model_dump()
    except Exception as exc:  # noqa: BLE001
        plan_data = {
            "summary": f"Plano fallback ({type(exc).__name__})",
            "steps": [],
            "files_to_change": list(task.get("suggested_files") or [])[:5],
            "unit_tests_to_add": [f"tests/test_{task.get('id', 'task').lower().replace('-', '_')}.py"],
            "risks": [str(exc)[:200]],
        }
    return {
        "implement_plan": plan_data,
        "model_tier": sel,
        "last_llm_usage": usage,
        "react_trace": [{
            "thought": plan_data.get("summary", ""),
            "action": "implement:plan",
            "observation": f"files={len(plan_data.get('files_to_change') or [])}",
            "llm_usage": usage,
            "agent": docs.get("agent_role"),
        }],
        "messages": [f"implement_plan: {str(plan_data.get('summary', ''))[:80]}"],
    }


def step_artifact(ctx: dict[str, Any], plan: dict[str, Any], *, mode: str) -> dict[str, Any]:
    """W1 — artefato IMPLEMENTACAO.md (live)."""
    task = task_from_ctx(ctx)
    tid = str(task.get("id") or ctx.get("task_id") or "")
    dry = mode == "dry_run"
    path = None
    if not dry:
        ws = LANGGRAPH_DIR / "workspace" / tid
        ws.mkdir(parents=True, exist_ok=True)
        path = ws / "IMPLEMENTACAO.md"
        steps = plan.get("steps") or []
        path.write_text(
            f"# Implementacao — {tid}\n\n{plan.get('summary', '')}\n\n"
            f"## Passos\n"
            + "\n".join(f"- {s.get('title', '')}: {s.get('description', '')}" for s in steps)
            + "\n\n## Arquivos\n"
            + "\n".join(f"- {f}" for f in (plan.get("files_to_change") or []))
            + "\n\n## Testes\n"
            + "\n".join(f"- {t}" for t in (plan.get("unit_tests_to_add") or [])),
            encoding="utf-8",
        )

    changed_files: list[dict[str, Any]] = []
    if path:
        changed_files.append({"path": str(path), "kind": "artefato"})
    for step in plan.get("steps") or []:
        for f in step.get("files") or []:
            changed_files.append({"path": f, "kind": "planned"})
    for f in plan.get("files_to_change") or []:
        if not any(x.get("path") == f for x in changed_files):
            changed_files.append({"path": f, "kind": "planned"})

    return {
        "implement_path": str(path) if path else None,
        "changed_files": changed_files,
        "unit_tests": list(plan.get("unit_tests_to_add") or []),
        "execution_plan": plan,
        "react_trace": [{
            "thought": "Gravar artefato de implementacao",
            "action": "implement:artifact",
            "observation": str(path) if path else "dry_run_skip",
        }],
        "messages": [f"implement_artifact: {path or 'dry_run'}"],
    }


def step_decide(plan: dict[str, Any], *, creator_role: str = "backend") -> dict[str, Any]:
    """D1 — decision: ready_for_code_review."""
    from board_automation.board.reviewer_pairs import normalize_creator_role
    from board_automation.board.task_status_workflow import build_event

    creator = normalize_creator_role(creator_role)
    next_event = build_event(creator, "Ready for Code Review")
    summary = str(plan.get("summary") or "Implementacao concluida")
    risks = list(plan.get("risks") or [])
    decision = {
        "next_event": next_event,
        "summary": summary,
        "rationale": "; ".join(risks[:3]) or summary,
        "confidence": 0.85,
        "needs_human": False,
    }
    return {
        "decision": decision,
        "phase": "implement",
        "react_trace": [{
            "thought": summary,
            "action": "implement:decide",
            "observation": next_event,
        }],
        "messages": [f"implement_decide: {next_event}"],
    }
