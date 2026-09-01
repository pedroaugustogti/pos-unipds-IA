"""Tool: on_status_event — contexto de atuação após transição de status."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP

from guardiao_mcp.contract import fail, ok
from lib.orchestrator.event_actuation_context import prepare_actuation_for_event

DESCRIPTION = """\
**Quando:** após `emit_status_event` ou antes de atuar (status já atualizado).

**Faz:**
1. Resolve evento role-based
2. Identifica `acting_agent` e `assigned_agent`
3. Lê ticket no board (GitHub Project → fallback JSON)
4. Extrai `ticket` por papel: AC, escopo, arquivos, QA, merge, user_flow
5. Anexa `handoff`, `ci`, `model_tier`, `playbook` (skill, passos ReAct)

**Parâmetros:** task_id + event **ou** agent_role + board_status (+ return_event).

**Retorno:** `assigned_agent`, `target_status`, `ticket`, `playbook`, `handoff`.

**Não altera board** — somente leitura/contexto. Handoff canônico: `agents/00-runtime/output/{task_id}/handoff.json`.
"""


def on_status_event(
    task_id: Annotated[str, "ID da task (ex: T-P3-009)"],
    event: Annotated[
        str,
        "Evento emitido (role-based). Opcional se usar agent_role + board_status.",
    ] = "",
    agent_role: Annotated[str, "Monta evento com board_status (mesma regra de emit_status_event)"] = "",
    board_status: Annotated[str, "Status alvo do evento (ex: In Progress, In Test)"] = "",
    return_event: Annotated[bool, "true se o evento foi retrocesso (_return_)"] = False,
) -> str:
    """Após emit_status_event: identifica agente, lê ticket e extrai contexto de atuação."""
    try:
        result = prepare_actuation_for_event(
            task_id,
            event,
            agent_role=agent_role,
            board_status=board_status,
            return_event=return_event,
        )
    except Exception as exc:  # noqa: BLE001
        return fail(f"{type(exc).__name__}: {exc}")
    if not result.get("ok"):
        return fail(str(result.get("error") or "falha ao preparar contexto"), **result)
    return ok(result)


def register(mcp: FastMCP) -> None:
    mcp.tool(description=DESCRIPTION)(on_status_event)
