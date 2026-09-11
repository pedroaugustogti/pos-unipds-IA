"""Helpers compartilhados para fases implement / review / qa."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from lib.core.agent_paths import agent_prompt_path, skill_path
from lib.orchestrator.event_actuation_runner import normalize_actuation_context


def load_actuation(actuation_context: dict[str, Any] | str) -> dict[str, Any]:
    return normalize_actuation_context(actuation_context)


def read_agent_docs(ctx: dict[str, Any]) -> dict[str, str]:
    role = str(ctx.get("assigned_agent") or ctx.get("creator_role") or "backend")
    skill_p = Path(str((ctx.get("playbook") or {}).get("skill_path") or skill_path(role)))
    prompt_p = Path(str((ctx.get("playbook") or {}).get("agent_prompt") or agent_prompt_path(role)))
    return {
        "agent_role": role,
        "skill": skill_p.read_text(encoding="utf-8") if skill_p.is_file() else "",
        "agent_prompt": prompt_p.read_text(encoding="utf-8") if prompt_p.is_file() else "",
        "skill_path": str(skill_p),
        "agent_prompt_path": str(prompt_p),
    }


def phase_llm_prompt(ctx: dict[str, Any], *, suffix: str = "") -> str:
    """Usa actuation_prompt de on_status_event; fallback mínimo se ausente."""
    base = str(ctx.get("actuation_prompt") or "").strip()
    if base:
        return f"{base}\n\n{suffix}".strip() if suffix else base
    docs = read_agent_docs(ctx)
    ticket = ctx.get("ticket") or {}
    return (
        f"Task: {ctx.get('task_id')} — {ticket.get('title')}\n"
        f"Role: {docs['agent_role']}\n"
        f"AC: {ticket.get('acceptance_criteria')}\n"
        f"{suffix}"
    ).strip()


def task_from_ctx(ctx: dict[str, Any]) -> dict[str, Any]:
    """Extrai task só do actuation_context (ticket) — sem load_tasks."""
    ticket = ctx.get("ticket") if isinstance(ctx.get("ticket"), dict) else {}
    qa = ticket.get("qa") if isinstance(ticket.get("qa"), dict) else {}
    return {
        "id": ctx.get("task_id") or ticket.get("task_id") or "",
        "title": ticket.get("title") or ctx.get("title") or "",
        "agent_role": ticket.get("creator_role") or ctx.get("assigned_agent") or "",
        "board_status": ctx.get("target_status") or "Todo",
        "repo": ticket.get("repo") or "",
        "track": ticket.get("track") or "produto",
        "acceptance_criteria": list(ticket.get("acceptance_criteria") or []),
        "in_scope": list(ticket.get("in_scope") or []),
        "out_of_scope": list(ticket.get("out_of_scope") or []),
        "do_not_touch": list(ticket.get("do_not_touch") or []),
        "suggested_files": list(ticket.get("suggested_files") or []),
        "qa": qa,
        "user_flow": ticket.get("user_flow") if isinstance(ticket.get("user_flow"), dict) else {},
        "refinement": ticket.get("refinement") if isinstance(ticket.get("refinement"), dict) else {},
    }
