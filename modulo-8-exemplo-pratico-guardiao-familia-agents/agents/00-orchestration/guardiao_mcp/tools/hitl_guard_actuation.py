"""Tool: hitl_guard_actuation — guardrail HITL antes de execute."""

from __future__ import annotations

import os
from typing import Annotated

from mcp.server.fastmcp import FastMCP

from guardiao_mcp.contract import fail, ok
from lib.gateway.actuation_guardrail import evaluate_actuation_guard

DESCRIPTION = """\
**Quando:** obrigatório **antes de cada** `execute_agent_actuation_tool`.

**Entrada:** `actuation_context` = JSON de `on_status_event`.

**Faz:**
1. Carrega `agents/_shared/ACTUATION_GUARDRAIL_POLICY.md`
2. Analisa ticket, handoff e playbook (injection, alto risco, merge live)
3. Decide `proceed` ou `blocked` + `importance_score`
4. Se blocked: enfileira HITL e comenta na issue (`dry_run=false`)
5. Se proceed: retorna `guard_pass_id` (uso único, TTL 1h)

**Parâmetros:** actuation_context (obrigatório), mode, human_clearance, clearance_note, dry_run.

**Após bloqueio:** triagem humana → `hitl_guard_actuation(human_clearance=true)` → novo `guard_pass_id`.
"""


def hitl_guard_actuation(
    actuation_context: Annotated[
        str,
        "JSON retornado por on_status_event (objeto completo ou campo result)",
    ],
    mode: Annotated[
        str,
        "dry_run | live — influencia score de merge/release (padrão: GUARDIAO_LANGGRAPH_MODE)",
    ] = "",
    human_clearance: Annotated[
        bool,
        "true após triagem humana no board libera contexto bloqueado",
    ] = False,
    clearance_note: Annotated[str, "Motivo da liberação humana (obrigatório se human_clearance=true)"] = "",
    dry_run: Annotated[bool, "true (padrão) não comenta na issue; false notifica board em bloqueio"] = True,
) -> str:
    """Valida contexto contra policy antes de execute_agent_actuation_tool."""
    run_mode = (mode or os.environ.get("GUARDIAO_LANGGRAPH_MODE") or "dry_run").strip()
    if human_clearance and not clearance_note.strip():
        return fail("clearance_note obrigatório quando human_clearance=true")
    try:
        result = evaluate_actuation_guard(
            actuation_context,
            mode=run_mode,
            human_clearance=human_clearance,
            clearance_note=clearance_note,
            dry_run=dry_run,
        )
    except Exception as exc:  # noqa: BLE001
        return fail(f"{type(exc).__name__}: {exc}")
    if result.get("blocked"):
        return fail(result.get("message") or "contexto bloqueado pelo guardrail", **result)
    return ok(result)


def register(mcp: FastMCP) -> None:
    mcp.tool(description=DESCRIPTION)(hitl_guard_actuation)
