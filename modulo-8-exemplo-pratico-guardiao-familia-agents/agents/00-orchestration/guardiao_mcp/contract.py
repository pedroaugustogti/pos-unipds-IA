"""Helpers de resposta JSON padronizada (Fase B)."""

from __future__ import annotations

import json
import os
from typing import Any

MCP_QA_ENVELOPE_ENV = "GF_MCP_QA_ENVELOPE"


def _enter_mcp_envelope() -> str | None:
    prev = os.environ.get(MCP_QA_ENVELOPE_ENV)
    os.environ[MCP_QA_ENVELOPE_ENV] = "1"
    return prev


def _exit_mcp_envelope(prev: str | None) -> None:
    if prev is None:
        os.environ.pop(MCP_QA_ENVELOPE_ENV, None)
    else:
        os.environ[MCP_QA_ENVELOPE_ENV] = prev


def ok(result: Any = None, *, dry_run: bool = False, **extra: Any) -> str:
    payload: dict[str, Any] = {
        "ok": True,
        "dry_run": dry_run,
        "result": result if result is not None else {},
        "error": None,
    }
    payload.update(extra)
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)


def fail(error: str, *, dry_run: bool = False, result: Any = None, **extra: Any) -> str:
    payload: dict[str, Any] = {
        "ok": False,
        "dry_run": dry_run,
        "result": result if result is not None else {},
        "error": error,
    }
    payload.update(extra)
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)


def wrap_call(fn, *, dry_run: bool = False, pass_dry_run: bool = True, **kwargs: Any) -> str:
    prev = _enter_mcp_envelope()
    try:
        if pass_dry_run:
            kwargs.setdefault("dry_run", dry_run)
        result = fn(**kwargs)
        if isinstance(result, dict) and "ok" in result:
            return json.dumps(
                {
                    "ok": bool(result.get("ok")),
                    "dry_run": dry_run or bool(result.get("dry_run")),
                    "result": result,
                    "error": result.get("error"),
                },
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        return ok(result, dry_run=dry_run)
    except Exception as exc:  # noqa: BLE001
        return fail(f"{type(exc).__name__}: {exc}", dry_run=dry_run)
    finally:
        _exit_mcp_envelope(prev)


def wrap_qa_call(fn, *, dry_run: bool = False, pass_dry_run: bool = True, **kwargs: Any) -> str:
    """Como wrap_call, mas aplica finalize_qa_envelope em dicts de suite."""
    from lib.mobile.qa_envelope import finalize_qa_envelope

    prev = _enter_mcp_envelope()
    try:
        if pass_dry_run:
            kwargs.setdefault("dry_run", dry_run)
        result = fn(**kwargs)
        if isinstance(result, dict) and "ok" in result:
            if "suite_ok" in result or result.get("app") in ("child", "parent"):
                result = finalize_qa_envelope(result)
            return json.dumps(
                {
                    "ok": bool(result.get("ok")),
                    "dry_run": dry_run or bool(result.get("dry_run")),
                    "result": result,
                    "error": result.get("error") or result.get("blocking_reason"),
                    "suite_ok": result.get("suite_ok"),
                    "evidence_ok": result.get("evidence_ok"),
                    "blocking_reason": result.get("blocking_reason"),
                },
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        return ok(result, dry_run=dry_run)
    except Exception as exc:  # noqa: BLE001
        return fail(f"{type(exc).__name__}: {exc}", dry_run=dry_run)
    finally:
        _exit_mcp_envelope(prev)
