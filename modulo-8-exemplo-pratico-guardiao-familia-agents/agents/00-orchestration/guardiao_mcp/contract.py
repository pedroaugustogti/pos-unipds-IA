"""Helpers de resposta JSON padronizada (Fase B)."""

from __future__ import annotations

import json
from typing import Any


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
