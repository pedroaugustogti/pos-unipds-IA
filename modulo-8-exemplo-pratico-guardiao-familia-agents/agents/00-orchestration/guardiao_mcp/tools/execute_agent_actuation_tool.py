"""Tool: execute_agent_actuation_tool — executa fase e emite próximo evento."""

from __future__ import annotations

import json
from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP

from guardiao_mcp.contract import fail, ok

DESCRIPTION = """\
**Quando:** após `hitl_guard_actuation` com `proceed=true`.

**Entrada:** `actuation_context` + `guard_pass_id` (obrigatório).

**Faz:**
1. Identifica fase pelo `target_status`
2. Marca `assigned_agent` busy → executa fase (ou usa `phase_work`) → emite próximo evento role-based → idle

**Cursor (manual):** chame `developer_implement` | `developer_review` | `qa_validate` antes; passe o JSON retornado em `phase_work` para `execute` não reexecutar a fase.

**Mapeamento target_status → fase → emit típico:**
| target_status | fase | emit seguinte (exemplo) |
|---------------|------|-------------------------|
| In Progress | implement | `{creator}_ready_for_code_review` |
| Ready for Code Review | start_review | `{reviewer}_in_code_review` |
| In Code Review | review | `{reviewer}_ready_for_test` ou `_return_in_progress` |
| Ready for Test | start_test | `qa-gate_in_test` |
| In Test | qa | `qa-gate_in_pull_request` ou `_return_in_progress` |
| In Pull Request | merge | `devops-cicd_done` (HITL em live) |

**Parâmetros:**
- actuation_context, guard_pass_id (obrigatórios)
- phase_work: JSON opcional de developer_* / qa_validate
- mode: dry_run | live
- use_role_events: true (padrão) emite eventos role-based

**Retorno:** phase, emit_event, board_status_out, work, apply.gateway

**LangGraph v2:** o grafo chama este pipeline automaticamente em cada nó `evt_*`.
"""


def execute_agent_actuation_tool(
    actuation_context: Annotated[
        str,
        "JSON retornado por on_status_event (objeto completo ou campo result)",
    ],
    guard_pass_id: Annotated[
        str,
        "Token de uso único retornado por hitl_guard_actuation (obrigatório)",
    ],
    mode: Annotated[
        str,
        "dry_run (padrão) simula trabalho+emit; live aplica no board",
    ] = "",
    use_role_events: Annotated[
        bool,
        "true (padrão) emite evento role-based no final (ex: frontend-mobile_ready_for_code_review)",
    ] = True,
    phase_work: Annotated[
        str,
        "JSON opcional — resultado de developer_implement/review/qa_validate; evita reexecutar fase",
    ] = "",
) -> str:
    """Executa fase do agente a partir do contexto on_status_event e emite próximo evento."""
    from lib.orchestrator.event_actuation_runner import execute_agent_actuation

    pw: dict[str, Any] | None = None
    if phase_work.strip():
        try:
            pw = json.loads(phase_work)
        except json.JSONDecodeError:
            return fail("phase_work JSON invalido")

    try:
        result = execute_agent_actuation(
            actuation_context,
            guard_pass_id=guard_pass_id,
            mode=mode or None,
            use_role_events=use_role_events,
            phase_work=pw,
        )
    except Exception as exc:  # noqa: BLE001
        return fail(f"{type(exc).__name__}: {exc}")
    if not result.get("ok"):
        return fail(str(result.get("error") or "falha na execucao"), result=result)
    return ok(result)


def register(mcp: FastMCP) -> None:
    mcp.tool(description=DESCRIPTION)(execute_agent_actuation_tool)
