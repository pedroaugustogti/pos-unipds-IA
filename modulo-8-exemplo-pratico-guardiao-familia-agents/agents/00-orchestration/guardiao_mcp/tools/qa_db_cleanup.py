"""Tool: qa_db_cleanup — purge pós-evidência QA."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP

from guardiao_mcp.contract import wrap_call
from lib.mobile.qa_mobile_mcp import run_db_cleanup

DESCRIPTION = """\
**Quando:** APÓS capturar evidências QA.

**Faz:** purge Postgres + reset stage-handoff + remove cache seed.

**Parâmetros:** task_id (preferido) | handoff_path | parent_email · dry_run.
"""


def qa_db_cleanup(
    task_id: Annotated[str, "ID da task — usa cache do último qa_db_seed"] = "",
    handoff_path: Annotated[str, "Caminho explícito ao stage-handoff.json"] = "",
    parent_email: Annotated[str, "Email do parent de teste (fallback)"] = "",
    dry_run: Annotated[bool, "true (padrão) simula; false executa purge"] = True,
) -> str:
    """Cleanup pós-evidência: purge DB + reset handoff."""
    return wrap_call(
        run_db_cleanup,
        pass_dry_run=False,
        dry_run=dry_run,
        task_id=task_id,
        handoff_path=handoff_path,
        parent_email=parent_email,
    )


def register(mcp: FastMCP) -> None:
    mcp.tool(description=DESCRIPTION)(qa_db_cleanup)
