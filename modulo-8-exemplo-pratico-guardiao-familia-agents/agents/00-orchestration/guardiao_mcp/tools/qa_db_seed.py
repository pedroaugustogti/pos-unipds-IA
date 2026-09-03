"""Tool: qa_db_seed — seed Postgres para QA Appium."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP

from guardiao_mcp.contract import wrap_call
from lib.mobile.qa_mobile_mcp import run_db_seed
from lib.mobile.seed_db_scripts import seed_db_github_tree

DESCRIPTION = f"""\
**Quando:** massa de teste via API (Postgres) **sem** cadastro/família na UI.

**Importante:** profiles criam parent via `POST /auth/register` — nunca insira usuários direto no Postgres.

**Não use quando:** AC exige telas de cadastro/família no app parent — use `qa_appium_suite_parent` com `feature` adequado.

**Faz:** bootstrap API → executa `seed_db/seed.mjs` do [mobile-setup/seed_db]({seed_db_github_tree()}) → `stage-handoff.json` → cache em `output/{{task_id}}/seed-cache.json`.

**Profiles:** pairing_warm | basic_parent | parent_home | child_home | permissions_resume

**Child-only:** seed parent + `qa_appium_suite_child(from_db_seed=true, child_only=true)` — não boota parent 5554.

**Scripts:** sincronizados de `{seed_db_github_tree()}` (local → git pull → GitHub raw).

**Parâmetros:** task_id (obrigatório), profile, use_task_config, bootstrap_api, dry_run.

**Próximo:** suite Appium com `from_db_seed=true` e mesmo `task_id`.
"""


def qa_db_seed(
    task_id: Annotated[str, "ID da task (ex: T-P3-009) — obrigatório"],
    profile: Annotated[str, "pairing_warm | basic_parent | parent_home | child_home | permissions_resume — vazio=child_home"] = "",
    bootstrap_api: Annotated[bool, "true sobe stack API Docker se necessário"] = True,
    use_task_config: Annotated[bool, "true lê qa.db_seed da task no CSV/issue"] = True,
    dry_run: Annotated[bool, "true (padrão) simula; false executa seed Postgres + handoff"] = True,
) -> str:
    """Seed Postgres + stage-handoff para QA Appium."""
    return wrap_call(
        run_db_seed,
        pass_dry_run=False,
        dry_run=dry_run,
        task_id=task_id,
        profile=profile,
        bootstrap_api=bootstrap_api,
        use_task_config=use_task_config,
    )


def register(mcp: FastMCP) -> None:
    mcp.tool(description=DESCRIPTION)(qa_db_seed)
