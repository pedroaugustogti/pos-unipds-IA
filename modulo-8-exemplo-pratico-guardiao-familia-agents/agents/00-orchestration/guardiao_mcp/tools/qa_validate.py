"""Tool: qa_validate — fase QA gate com Appium."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP

from guardiao_mcp.contract import fail, ok

DESCRIPTION = """\
**Quando:** fase **qa** (`target_status=In Test`), após `hitl_guard_actuation`.

**Entrada:** `actuation_context` de `on_status_event` (AC + `ticket.qa.scenarios`).

**Caminhos (worker_mode) — escolhas distintas, sem fallback:**
- `local` (default): 1 worker por cenário **na máquina host** (sem Docker)
- `docker`: 1 **container** isolado por cenário (imagem `GF_QA_SCENARIO_IMAGE`)

**Por cenário:** `qa_init_suite_mobile` → `qa_pipeline_evidence` → `qa_generate_evidence` (paralelo; PASS = todos ok).

**Env (opcional):** `GF_QA_SCENARIO_WORKER`, `GF_QA_SCENARIO_IMAGE`, `GF_QA_SCENARIO_MAX_PARALLEL`.

**Retorno:** `worker_mode`, `scenarios_results`, `mcp_steps`, `evidence_paths`, `ac_validation`, `decision`.
"""


def qa_validate(
    actuation_context: Annotated[str, "JSON de on_status_event"],
    mode: Annotated[str, "dry_run | live"] = "",
    worker_mode: Annotated[
        str,
        "Caminho de execução: local (host, sem container) | docker (1 container por cenário)",
    ] = "local",
) -> str:
    """QA gate: caminho local ou docker — multi-cenário + evidências + AC."""
    from board_automation.board.task_status_workflow import build_event
    from lib.orchestrator.phase_qa_validate import run_qa_validate

    fail_event = build_event("qa-gate", "In Progress", return_=True)
    try:
        result = run_qa_validate(
            actuation_context,
            mode=mode or None,
            worker_mode=worker_mode or None,
        )
    except Exception as exc:  # noqa: BLE001
        return fail(f"{type(exc).__name__}: {exc}")
    if not result.get("ok") and result.get("decision", {}).get("next_event") != fail_event:
        return fail(str(result.get("error") or "falha qa"), result=result)
    return ok(result)


def register(mcp: FastMCP) -> None:
    mcp.tool(description=DESCRIPTION)(qa_validate)
