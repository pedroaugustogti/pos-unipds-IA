"""Tool: qa_init_suite_mobile — prep async até apps_ready_ok + checks por suite."""

from __future__ import annotations

import json
from typing import Annotated

from mcp.server.fastmcp import FastMCP

from guardiao_mcp.contract import wrap_qa_call
from lib.mobile.qa_init_suite_mobile import run_qa_init_suite_mobile

DESCRIPTION = """\
**Quando:** início da suite mobile (child e/ou parent) — precheck + recovery.

**Entrada:** `suites_mobile` JSON — ex. `{"parent":false,"child":true}` ou dual.

**Fluxo:** Wave A (api∥adb∥emulator) → Wave B (metro∥apk) → Appium; recovery máx. 3/check.

**Retorno contrato:**
```
task_id, apps_ready_ok,
checks_parent? / checks_child?: {
  docker_api|adb|emulator|metro|apk|appium: {ok, attempts, time_exec, detail, mode?},
  error_runtime: { <check>: {type, time_exec, detail} }
}
```

**Próximo:** `qa_pipeline_evidence(actuation_context, apps_ready_ok)` → `qa_generate_evidence(...)`.

**Orquestração:** `qa_validate` resolve `suites_mobile` do ticket e chama esta tool.
"""


def qa_init_suite_mobile(
    task_id: Annotated[str, "ID da task (ex. T-P3-009)"] = "",
    suites_mobile: Annotated[
        str,
        'JSON {"parent": bool, "child": bool} — quais suites iniciar',
    ] = "",
    skip_build: Annotated[bool, "true pula rebuild APK no repair"] = True,
    feature: Annotated[str, "Feature Appium — vazio usa ticket"] = "",
    timeout_sec: Annotated[int, "Timeout total do init (s)"] = 600,
    max_attempts: Annotated[int, "Máx. tentativas de recovery por check"] = 3,
    dry_run: Annotated[bool, "true simula"] = True,
) -> str:
    """Init suite mobile com precheck async, recovery e plan do ticket."""
    suites: dict | str | None = suites_mobile.strip() or None
    if isinstance(suites, str):
        try:
            suites = json.loads(suites)
        except json.JSONDecodeError:
            pass
    return wrap_qa_call(
        run_qa_init_suite_mobile,
        pass_dry_run=True,
        dry_run=dry_run,
        task_id=task_id,
        suites_mobile=suites,
        skip_build=skip_build,
        feature=feature,
        timeout_sec=timeout_sec,
        max_attempts=max_attempts,
    )


def register(mcp: FastMCP) -> None:
    mcp.tool(description=DESCRIPTION)(qa_init_suite_mobile)
