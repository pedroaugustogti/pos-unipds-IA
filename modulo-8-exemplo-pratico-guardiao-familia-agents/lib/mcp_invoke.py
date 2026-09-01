"""Invoca tools MCP in-process — única ponte para LangGraph e runtime."""

from __future__ import annotations

import json
from typing import Any

from guardiao_mcp import server as mcp_server


def _parse(raw: str) -> dict[str, Any]:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"ok": False, "error": "invalid_json", "raw": raw[:500]}


def _ctx_json(ctx: str | dict[str, Any]) -> str:
    return ctx if isinstance(ctx, str) else json.dumps(ctx, ensure_ascii=False)


def unwrap_result(payload: dict[str, Any]) -> dict[str, Any]:
    """Extrai result interno de envelope MCP {ok, result}."""
    if payload.get("ok") and isinstance(payload.get("result"), dict):
        inner = payload["result"]
        if inner.get("task_id") or inner.get("guard_pass_id") or inner.get("decision"):
            return inner
    return payload


def orchestrator_enter_in_progress(**kwargs: Any) -> dict[str, Any]:
    return _parse(mcp_server.orchestrator_enter_in_progress(**kwargs))


def emit_status_event(**kwargs: Any) -> dict[str, Any]:
    return _parse(mcp_server.emit_status_event(**kwargs))


def on_status_event(**kwargs: Any) -> dict[str, Any]:
    return _parse(mcp_server.on_status_event(**kwargs))


def hitl_guard_actuation(
    actuation_context: str | dict[str, Any],
    *,
    mode: str = "dry_run",
    human_clearance: bool = False,
    clearance_note: str = "",
    dry_run: bool = True,
) -> dict[str, Any]:
    return _parse(
        mcp_server.hitl_guard_actuation(
            actuation_context=_ctx_json(actuation_context),
            mode=mode,
            human_clearance=human_clearance,
            clearance_note=clearance_note,
            dry_run=dry_run,
        )
    )


def developer_implement(actuation_context: str | dict[str, Any], *, mode: str = "") -> dict[str, Any]:
    return _parse(mcp_server.developer_implement(actuation_context=_ctx_json(actuation_context), mode=mode))


def developer_review(actuation_context: str | dict[str, Any], *, mode: str = "") -> dict[str, Any]:
    return _parse(mcp_server.developer_review(actuation_context=_ctx_json(actuation_context), mode=mode))


def qa_validate(actuation_context: str | dict[str, Any], *, mode: str = "") -> dict[str, Any]:
    return _parse(mcp_server.qa_validate(actuation_context=_ctx_json(actuation_context), mode=mode))


def execute_agent_actuation_tool(
    actuation_context: str | dict[str, Any],
    *,
    guard_pass_id: str,
    mode: str = "",
    use_role_events: bool = True,
    phase_work: dict[str, Any] | None = None,
) -> dict[str, Any]:
    pw = json.dumps(phase_work, ensure_ascii=False) if phase_work else ""
    return _parse(
        mcp_server.execute_agent_actuation_tool(
            actuation_context=_ctx_json(actuation_context),
            guard_pass_id=guard_pass_id,
            mode=mode,
            use_role_events=use_role_events,
            phase_work=pw,
        )
    )


def qa_db_seed(**kwargs: Any) -> dict[str, Any]:
    return _parse(mcp_server.qa_db_seed(**kwargs))


def qa_db_cleanup(**kwargs: Any) -> dict[str, Any]:
    return _parse(mcp_server.qa_db_cleanup(**kwargs))


def qa_appium_suite_parent(**kwargs: Any) -> dict[str, Any]:
    return _parse(mcp_server.qa_appium_suite_parent(**kwargs))


def qa_appium_suite_child(**kwargs: Any) -> dict[str, Any]:
    return _parse(mcp_server.qa_appium_suite_child(**kwargs))


def list_mcp_catalog() -> dict[str, Any]:
    return _parse(mcp_server.list_mcp_tools())
