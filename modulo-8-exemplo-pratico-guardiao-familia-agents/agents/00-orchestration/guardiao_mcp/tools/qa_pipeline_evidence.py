"""Tool: qa_pipeline_evidence — monta scenario_pipeline para evidência."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP

from guardiao_mcp.contract import wrap_qa_call
from lib.mobile.qa_pipeline_evidence import run_qa_pipeline_evidence

DESCRIPTION = """\
**Quando:** após `qa_init_suite_mobile` com `apps_ready_ok=true`, antes de `qa_generate_evidence`.

**Entrada:**
1. `actuation_context` — JSON de `on_status_event` / `qa_validate`
2. `apps_ready_ok` — bool do retorno de `qa_init_suite_mobile`
3. `scenario_id` — id do cenário de teste (ex. `greeting-morning-08h`)

**Retorno:**
- `scenario_pipeline` — `suites_mobile`, `screenshot`, `video_record`, `description`, `steps[]`, `binding`
  - steps de `launch`/`set_clock` incluem `hooks: ["dismiss_expo"]` (overlay Expo no wait; sem testID fictício)
- `device` — irmão do pipeline: serial, avd, bundle_id, activity, metro, `dev_client_url`,
  deep links, appium host/port, `adb_reverse_ports`, preconds de launch (só de
  `APP_STACKS` + `mobile-setup/env/stacks.json` — sem inventar valores)

**Regra:** se `apps_ready_ok=false` → `scenario_pipeline=null` e `device=null`.

**Próximo:** `qa_generate_evidence(pipeline_result=<este retorno completo>)`.
"""


def qa_pipeline_evidence(
    actuation_context: Annotated[str, "JSON de on_status_event (mesmo de qa_validate)"],
    apps_ready_ok: Annotated[bool, "apps_ready_ok do retorno de qa_init_suite_mobile"],
    scenario_id: Annotated[
        str,
        "Id do cenário de teste (ex. greeting-morning-08h). Vazio = 1º de qa.scenarios",
    ] = "",
    dry_run: Annotated[bool, "true simula"] = True,
) -> str:
    """Gera scenario_pipeline para o scenario_id informado."""
    return wrap_qa_call(
        run_qa_pipeline_evidence,
        pass_dry_run=True,
        dry_run=dry_run,
        actuation_context=actuation_context,
        apps_ready_ok=apps_ready_ok,
        scenario_id=scenario_id,
    )


def register(mcp: FastMCP) -> None:
    mcp.tool(description=DESCRIPTION)(qa_pipeline_evidence)
