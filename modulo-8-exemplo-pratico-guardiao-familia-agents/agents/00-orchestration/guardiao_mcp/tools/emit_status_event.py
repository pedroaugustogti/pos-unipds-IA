"""Tool: emit_status_event — porta única de status do board Kanban."""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP

from board_automation.board.task_status_workflow import build_event, is_known_event, validate_role_event_for_task
from guardiao_mcp._helpers import task_by_id
from guardiao_mcp.contract import fail, wrap_call
from lib.gateway import emit_status_event as gateway_emit

DESCRIPTION = """\
**Quando:** mover task no board Kanban (única porta de status).

**Faz:** valida evento role-based → transição de status → atualiza board GitHub → opcionalmente handoff.

**Formato:**
- Avanço: `{agent_role}_{status_slug}` — ex: `frontend-mobile_in_progress`
- Retrocesso: `{agent_role}_return_{status_slug}` — ex: `frontend-mobile-reviewer_return_in_progress`

**Alternativa:** `agent_role` + `board_status` (+ `return_event=true` para retrocesso).

**Parâmetros:**
- task_id: ID da task (ex: T-P3-009)
- event: string role-based (opcional se usar agent_role + board_status)
- agent_role + board_status: montam o evento automaticamente
- return_event: true para retrocesso
- summary: motivo (obrigatório em produção)
- dry_run: true (padrão) simula; false aplica
- pr_url: URL do PR (`{creator}_ready_for_code_review`)
- from_agent: papel emissor — deve bater com o prefixo do evento

**Catálogo:** `list_status_events` · **Antes de dry_run=false:** confirme handoff, AC e papel.
"""


def emit_status_event(
    task_id: Annotated[str, "ID da task no board (ex: T-P3-009)"],
    event: Annotated[
        str,
        "Evento role-based ({agent_role}_{status_slug}). "
        "Alternativa: deixe vazio e use agent_role + board_status.",
    ] = "",
    agent_role: Annotated[
        str,
        "Papel que emite (ex: frontend-mobile, frontend-mobile-reviewer, qa-gate). "
        "Com board_status monta o evento automaticamente.",
    ] = "",
    board_status: Annotated[
        str,
        "Status alvo no board (ex: In Progress, Ready for Code Review). "
        "Usado com agent_role para montar o evento.",
    ] = "",
    return_event: Annotated[
        bool,
        "true → evento de retrocesso ({agent_role}_return_{status_slug}), ex: request_changes",
    ] = False,
    summary: Annotated[str, "Resumo curto do motivo da transição (recomendado em dry_run=false)"] = "",
    dry_run: Annotated[bool, "true (padrão) simula; false aplica no board"] = True,
    pr_url: Annotated[str, "URL do PR — use em {creator}_ready_for_code_review"] = "",
    from_agent: Annotated[str, "Papel que dispara (deve bater com o prefixo do evento role-based)"] = "",
) -> str:
    """Porta única de Status do board Kanban."""
    task = task_by_id(task_id)
    if not task:
        return fail(f"Task nao encontrada: {task_id}", dry_run=dry_run)

    resolved_event = (event or "").strip()
    if agent_role and board_status:
        resolved_event = build_event(agent_role, board_status, return_=return_event)
    elif not resolved_event:
        return fail(
            "Informe event OU (agent_role + board_status)",
            dry_run=dry_run,
            hint="Ex: event=frontend-mobile_in_progress ou agent_role=frontend-mobile, board_status=In Progress",
        )

    if not is_known_event(resolved_event) and resolved_event not in (
        "hitl_approved",
        "hitl_rejected",
    ):
        return fail(
            f"Evento invalido: {resolved_event}",
            dry_run=dry_run,
            catalog_tool="list_status_events",
        )

    role_err = validate_role_event_for_task(
        resolved_event,
        from_agent=from_agent,
        task_agent_role=task.get("agent_role"),
    )
    if role_err:
        return fail(role_err, dry_run=dry_run, event=resolved_event, from_agent=from_agent)

    return wrap_call(
        gateway_emit,
        task_id=task_id,
        event=resolved_event,
        summary=summary,
        dry_run=dry_run,
        apply_board=True,
        pr_url=pr_url or None,
        from_agent=from_agent or None,
    )


def register(mcp: FastMCP) -> None:
    mcp.tool(description=DESCRIPTION)(emit_status_event)
