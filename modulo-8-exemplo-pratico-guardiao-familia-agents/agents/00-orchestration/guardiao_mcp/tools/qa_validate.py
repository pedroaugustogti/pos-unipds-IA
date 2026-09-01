"""Tool: qa_validate — fase QA gate com Appium."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP

from guardiao_mcp.contract import fail, ok

DESCRIPTION = """\
**Quando:** fase **qa** (`target_status=In Test`), após `hitl_guard_actuation`.

**Entrada:** `actuation_context` com AC e config QA.

**Faz:**
1. Orquestra MCP: `qa_db_seed` → `qa_appium_suite_*` → `qa_db_cleanup` (quando aplicável)
2. Coleta evidências e valida AC (`ac_validation`)

**Retorno:** `mcp_steps`, `evidence_paths`, `ac_validation`, `decision` (`qa-gate_in_pull_request` | `qa-gate_return_in_progress`).
"""


def qa_validate(
    actuation_context: Annotated[str, "JSON de on_status_event"],
    mode: Annotated[str, "dry_run | live"] = "",
) -> str:
    """QA gate: ambiente mobile MCP + evidências + validação de AC."""
    from board_automation.board.task_status_workflow import build_event
    from lib.orchestrator.phase_qa_validate import run_qa_validate

    fail_event = build_event("qa-gate", "In Progress", return_=True)
    try:
        result = run_qa_validate(actuation_context, mode=mode or None)
    except Exception as exc:  # noqa: BLE001
        return fail(f"{type(exc).__name__}: {exc}")
    if not result.get("ok") and result.get("decision", {}).get("next_event") != fail_event:
        return fail(str(result.get("error") or "falha qa"), result=result)
    return ok(result)


def register(mcp: FastMCP) -> None:
    mcp.tool(description=DESCRIPTION)(qa_validate)
