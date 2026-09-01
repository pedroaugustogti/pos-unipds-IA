"""Tool: developer_review — fase de code review."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP

from guardiao_mcp.contract import fail, ok

DESCRIPTION = """\
**Quando:** fase **review** (`target_status=In Code Review`), após `hitl_guard_actuation`.

**Entrada:** `actuation_context` com handoff/PR.

**Faz:** review estruturado — arquitetura, manutenibilidade, testes.

**Retorno:** `review`, `findings`, `verdict`, `decision` (`{reviewer}_ready_for_test` | `_return_in_progress`).
"""


def developer_review(
    actuation_context: Annotated[str, "JSON de on_status_event"],
    mode: Annotated[str, "dry_run | live"] = "",
) -> str:
    """Review de código: arquitetura, manutenibilidade, testes, boas práticas."""
    from lib.orchestrator.phase_developer_review import run_developer_review

    try:
        result = run_developer_review(actuation_context, mode=mode or None)
    except Exception as exc:  # noqa: BLE001
        return fail(f"{type(exc).__name__}: {exc}")
    if not result.get("ok"):
        return fail(str(result.get("error") or "falha review"), result=result)
    return ok(result)


def register(mcp: FastMCP) -> None:
    mcp.tool(description=DESCRIPTION)(developer_review)
