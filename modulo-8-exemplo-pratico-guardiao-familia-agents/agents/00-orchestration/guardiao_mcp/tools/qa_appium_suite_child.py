"""Tool: qa_appium_suite_child — stack Appium dual parent+child."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP

from guardiao_mcp.contract import wrap_call
from ._qa_appium_scenarios import QA_APPIUM_SCENARIOS
from lib.mobile.qa_mobile_mcp import run_appium_suite

DESCRIPTION = """\
**Quando:** validar app **child** (emulator-5556, Metro 9090).

**Child-only (massa parent no DB):**
```
qa_db_seed(task_id="T-XXX", profile="child_home", dry_run=false)
qa_appium_suite_child(from_db_seed=true, task_id="T-XXX", child_only=true, skip_appium=false, dry_run=false)
```

**Pairing dual:**
```
qa_appium_suite_child(from_db_seed=true, task_id="T-XXX", child_only=false, feature="pairing", skip_appium=false, dry_run=false)
```

**Parâmetros:** child_only, from_db_seed, task_id, feature, phase, reset_handoff_after, skip_build, skip_appium, timeout_sec, dry_run.

**Próximo:** evidências → `qa_db_cleanup` → `emit_status_event` (`qa-gate_in_pull_request` ou retrocesso).

---
""" + QA_APPIUM_SCENARIOS


def qa_appium_suite_child(
    skip_build: Annotated[bool, "true pula rebuild (mais rápido)"] = True,
    skip_appium: Annotated[bool, "true só infra; false roda Appium (auto com from_db_seed)"] = True,
    phase: Annotated[str, "All (padrão) | Api | Boot | Metro | Build | Smoke"] = "All",
    feature: Annotated[str, "pairing | go_to_home_child — vazio=auto com from_db_seed"] = "",
    resume_from_handoff: Annotated[bool, "legado — prefira from_db_seed=true"] = False,
    child_only: Annotated[bool, "true: QA child sem exigir parent home — auto com seed child"] = False,
    from_db_seed: Annotated[bool, "true após qa_db_seed — retoma handoff e abre ChildHome"] = False,
    task_id: Annotated[str, "Mesmo task_id do qa_db_seed (obrigatório com from_db_seed)"] = "",
    reset_handoff_after: Annotated[
        bool,
        "true (padrão com from_db_seed/task_id) zera stage-handoff ao final",
    ] = True,
    timeout_sec: Annotated[int, "Timeout em segundos (padrão 1800)"] = 1800,
    dry_run: Annotated[bool, "true (padrão) simula; false executa fast-stack dual emulator"] = True,
) -> str:
    """Stack Appium dual parent+child (5554+5556, Metro 9090)."""
    effective_skip_appium = skip_appium if not (from_db_seed or child_only) else False
    return wrap_call(
        run_appium_suite,
        pass_dry_run=False,
        dry_run=dry_run,
        app="child",
        skip_build=skip_build,
        skip_appium=effective_skip_appium,
        phase=phase,
        feature=feature,
        resume_from_handoff=resume_from_handoff,
        from_db_seed=from_db_seed,
        task_id=task_id,
        timeout_sec=timeout_sec,
        child_only=child_only,
        reset_handoff_after=reset_handoff_after,
    )


def register(mcp: FastMCP) -> None:
    mcp.tool(description=DESCRIPTION)(qa_appium_suite_child)
