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


def task_from_ctx(ctx: dict[str, Any]) -> dict[str, Any]:
    ticket = ctx.get("ticket") or {}
    board = ctx.get("board_task") or {}
    return {
        "id": ctx.get("task_id") or ticket.get("task_id") or board.get("id"),
        "title": ticket.get("title") or board.get("title") or "",
        "agent_role": ticket.get("creator_role") or board.get("agent_role") or ctx.get("assigned_agent"),
        "board_status": ctx.get("target_status") or board.get("board_status") or "Todo",
        "repo": ticket.get("repo") or board.get("repo") or "",
        "track": ticket.get("track") or board.get("track") or "produto",
        "acceptance_criteria": list(ticket.get("acceptance_criteria") or []),
        "in_scope": list(ticket.get("in_scope") or []),
        "out_of_scope": list(ticket.get("out_of_scope") or []),
        "do_not_touch": list(ticket.get("do_not_touch") or []),
        "suggested_files": list(ticket.get("suggested_files") or []),
        "qa": ticket.get("qa") if isinstance(ticket.get("qa"), dict) else {},
    }
