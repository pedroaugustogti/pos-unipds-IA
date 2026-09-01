"""Tool: developer_implement — fase de codificação."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP

from guardiao_mcp.contract import fail, ok

DESCRIPTION = """\
**Quando:** fase **implement** (`target_status=In Progress`), após `hitl_guard_actuation`.

**Entrada:** `actuation_context` = JSON de `on_status_event`.

**Faz:** skill + agent.md → `execution_plan` (LLM) → implementação → `changed_files`, `unit_tests`.

**Retorno:** `execution_plan`, `changed_files`, `unit_tests`, `decision.next_event` (ex: `{creator}_ready_for_code_review`).
"""


def developer_implement(
    actuation_context: Annotated[
        str,
        "JSON retornado por on_status_event (objeto completo ou campo result)",
    ],
    mode: Annotated[str, "dry_run | live"] = "",
) -> str:
    """Codificação + testes unitários a partir do contexto e skill do agente."""
    from lib.orchestrator.phase_developer_implement import run_developer_implement

    try:
        result = run_developer_implement(actuation_context, mode=mode or None)
    except Exception as exc:  # noqa: BLE001
        return fail(f"{type(exc).__name__}: {exc}")
    if not result.get("ok"):
        return fail(str(result.get("error") or "falha implement"), result=result)
    return ok(result)


def register(mcp: FastMCP) -> None:
    mcp.tool(description=DESCRIPTION)(developer_implement)
