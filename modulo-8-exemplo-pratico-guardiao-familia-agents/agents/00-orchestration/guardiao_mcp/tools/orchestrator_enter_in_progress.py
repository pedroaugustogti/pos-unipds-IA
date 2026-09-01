"""Tool: orchestrator_enter_in_progress — claim de task Todo prioritária."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP

from guardiao_mcp.contract import fail, ok

DESCRIPTION = """\
**Quando:** grafo v2 em Todo ou orchestrator manual iniciando ciclo.

**Faz:**
1. Seleciona task **Todo** (menor `priority_rank`; bonus sprint atual)
2. Emite `orchestrator_enter_in_progress` via gateway (`from_agent=orchestrator`)
3. Status alvo: **In Progress** · creator = `agent_role` da task

**Parâmetros:** sprint, sprint_only, task_id (opcional), summary, dry_run.

**LangGraph v2:** nó `evt_orchestrator_enter_in_progress` executa só esta tool.
**Manual:** próximo passo típico — `on_status_event` → pipeline da fase creator.
"""


def orchestrator_enter_in_progress(
    sprint: Annotated[int, "Sprint para priorização (bonus se task do sprint atual)"] = 1,
    sprint_only: Annotated[bool, "true limita a tasks do sprint informado"] = False,
    task_id: Annotated[str, "ID fixo (opcional); se vazio, escolhe Todo de maior prioridade"] = "",
    summary: Annotated[str, "Resumo do claim (recomendado em dry_run=false)"] = "",
    dry_run: Annotated[bool, "true (padrão) simula; false aplica no board"] = True,
) -> str:
    """Seleciona task Todo prioritária e emite orchestrator_enter_in_progress."""
    from lib.orchestrator.orchestrator_claim import orchestrator_enter_priority_todo

    result = orchestrator_enter_priority_todo(
        task_id=task_id.strip(),
        sprint=sprint,
        sprint_only=sprint_only,
        summary=summary,
        dry_run=dry_run,
    )
    if not result.get("ok"):
        return fail(str(result.get("error") or "falha no claim"), result=result)
    return ok(result, dry_run=dry_run)


def register(mcp: FastMCP) -> None:
    mcp.tool(description=DESCRIPTION)(orchestrator_enter_in_progress)
