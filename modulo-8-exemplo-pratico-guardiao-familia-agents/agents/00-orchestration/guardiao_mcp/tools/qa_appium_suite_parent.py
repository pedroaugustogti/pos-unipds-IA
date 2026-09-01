"""Tool: qa_appium_suite_parent — stack Appium app parent."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP

from guardiao_mcp.contract import wrap_call
from ._qa_appium_scenarios import QA_APPIUM_SCENARIOS
from lib.mobile.qa_mobile_mcp import run_appium_suite

DESCRIPTION = """\
**Quando:** validar app **parent** (emulator-5554, Metro 8082).

**Sem seed (UI cadastro/família):**
```
qa_appium_suite_parent(feature="create_account", skip_appium=false, dry_run=false)
```

**Com seed (login→home):**
```
qa_db_seed(task_id="T-XXX", profile="parent_home", dry_run=false)
qa_appium_suite_parent(from_db_seed=true, task_id="T-XXX", feature="login", skip_appium=false, dry_run=false)
```

**Parâmetros:** phase, feature, from_db_seed, task_id, parent_only, reset_handoff_after, skip_build, skip_appium, timeout_sec, dry_run.

---
""" + QA_APPIUM_SCENARIOS


def qa_appium_suite_parent(
    skip_build: Annotated[bool, "true pula rebuild (mais rápido)"] = True,
    skip_appium: Annotated[bool, "true só sobe infra; false roda Appium"] = True,
    phase: Annotated[str, "All (padrão) | Api | Boot | Metro | Build | Smoke"] = "All",
    feature: Annotated[str, "create_account | config_family | login | pairing | go_to_home_parent — vazio=auto"] = "",
    from_db_seed: Annotated[bool, "true retoma handoff pós qa_db_seed"] = False,
    task_id: Annotated[str, "Mesmo task_id do qa_db_seed"] = "",
    parent_only: Annotated[
        bool,
        "true só parent 5554 — auto com from_db_seed (parent_home); evita boot child",
    ] = False,
    reset_handoff_after: Annotated[
        bool,
        "true (padrão com from_db_seed/task_id) zera stage-handoff ao final",
    ] = True,
    timeout_sec: Annotated[int, "Timeout em segundos (padrão 1800)"] = 1800,
    dry_run: Annotated[bool, "true (padrão) simula; false executa fast-stack"] = True,
) -> str:
    """Stack Appium app parent (emulator-5554, Metro 8082)."""
    effective_skip_appium = skip_appium if not from_db_seed else False
    return wrap_call(
        run_appium_suite,
        pass_dry_run=False,
        dry_run=dry_run,
        app="parent",
        skip_build=skip_build,
        skip_appium=effective_skip_appium,
        phase=phase,
        feature=feature,
        from_db_seed=from_db_seed,
        task_id=task_id,
        parent_only=parent_only,
        reset_handoff_after=reset_handoff_after,
        timeout_sec=timeout_sec,
    )


def register(mcp: FastMCP) -> None:
    mcp.tool(description=DESCRIPTION)(qa_appium_suite_parent)
