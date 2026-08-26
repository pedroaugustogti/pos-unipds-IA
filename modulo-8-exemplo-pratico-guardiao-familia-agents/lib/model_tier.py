"""Fase A — Roteamento de modelo por purpose/risco (orquestração ≠ Cursor)."""

from __future__ import annotations

import os
from typing import Any

from lib.react_policy import max_iterations_for

HIGH_HINTS = (
    "sos",
    "pagamento",
    "payment",
    "stripe",
    "lgpd",
    "auth",
    "terraform",
    "release",
)

_PURPOSE_ALIASES: dict[str, str] = {
    "implement": "implement_low",
    "impl": "implement_low",
    "low": "implement_low",
    "high": "implement_high",
    "orchestration": "implement_low",
    "code": "cursor",
    "cursor_implement": "cursor",
}

DEFAULT_LOW = "openai/gpt-4o-mini"
DEFAULT_HIGH = "x-ai/grok-4.3"
DEFAULT_CURSOR = "composer-2.5"

_BUDGET: dict[str, dict[str, int]] = {
    "route": {"max_tokens": 0, "max_tool_calls": 0},
    "implement_low": {"max_tokens": 4096, "max_tool_calls": 4},
    "implement_high": {"max_tokens": 8192, "max_tool_calls": 4},
    "review": {"max_tokens": 3072, "max_tool_calls": 3},
    "summarize": {"max_tokens": 1024, "max_tool_calls": 1},
    "cursor": {"max_tokens": 0, "max_tool_calls": 0},
}


def _env(*keys: str, default: str = "") -> str:
    for key in keys:
        val = (os.environ.get(key) or "").strip()
        if val:
            return val
    return default


def _normalize_purpose(purpose: str) -> str:
    p = (purpose or "implement_low").strip().lower()
    return _PURPOSE_ALIASES.get(p, p)


def _task_blob(task: dict[str, Any] | None) -> str:
    return " ".join(
        [
            str((task or {}).get("title") or ""),
            str((task or {}).get("agent_role") or ""),
            str((task or {}).get("epic_id") or ""),
        ]
    ).lower()


def is_high_risk(task: dict[str, Any] | None = None) -> bool:
    return any(h in _task_blob(task) for h in HIGH_HINTS)


def orchestration_model_low() -> str:
    return _env("GUARDIAO_LLM_DEFAULT", "CREWAI_MODEL", default=DEFAULT_LOW)


def orchestration_model_high() -> str:
    explicit = _env("GUARDIAO_LLM_HIGH", "CREWAI_MODEL_HIGH")
    if explicit:
        return explicit
    low = orchestration_model_low()
    if "mini" in low.lower():
        return DEFAULT_HIGH
    return low


def cursor_model() -> str:
    """Modelo de implementação de código (Cursor SDK) — separado da orquestração."""
    return _env("GUARDIAO_CURSOR_MODEL", "GUARDAO_CURSOR_MODEL", default=DEFAULT_CURSOR)


def budget_for(purpose: str, *, role: str | None = None) -> dict[str, int]:
    """
    max_tokens: teto de geração LLM (0 = sem LLM).
    max_tool_calls: alinhado a react_policy quando role informado.
    """
    canon = _normalize_purpose(purpose)
    base = dict(_BUDGET.get(canon, _BUDGET["implement_low"]))
    if role and canon in ("implement_low", "implement_high", "review"):
        base["max_tool_calls"] = max_iterations_for(role)
    return base


def select_model(
    task: dict[str, Any] | None = None,
    *,
    purpose: str = "implement_low",
    role: str | None = None,
) -> dict[str, Any]:
    """
    purpose: route | implement_low | implement_high | review | summarize | cursor

    Retorno:
      tier, model, note, purpose, max_tokens, max_tool_calls, uses_llm, cursor_model
    """
    canon = _normalize_purpose(purpose)
    role = role or str((task or {}).get("agent_role") or "") or None
    budget = budget_for(canon, role=role)
    cur = cursor_model()

    if canon == "route":
        route_model = _env("GUARDIAO_LLM_ROUTE", default="deterministic")
        uses_llm = route_model not in ("", "deterministic", "none", "off")
        return {
            "tier": "route",
            "purpose": "route",
            "model": route_model if uses_llm else "deterministic",
            "note": "claim/roteamento sem LLM" if not uses_llm else "roteamento com LLM leve",
            "uses_llm": uses_llm,
            "cursor_model": cur,
            **budget,
        }

    if canon == "cursor":
        return {
            "tier": "cursor",
            "purpose": "cursor",
            "model": cur,
            "note": "implementacao de codigo via Cursor SDK (nao e orquestracao)",
            "uses_llm": False,
            "cursor_model": cur,
            **budget,
        }

    if canon == "summarize":
        return {
            "tier": "low",
            "purpose": "summarize",
            "model": orchestration_model_low(),
            "note": "resumo de handoff / PR",
            "uses_llm": True,
            "cursor_model": cur,
            **budget,
        }

    if canon == "review":
        high = is_high_risk(task)
        return {
            "tier": "high" if high else "low",
            "purpose": "review",
            "model": orchestration_model_high() if high else orchestration_model_low(),
            "note": "review alto risco" if high else "review padrao",
            "uses_llm": True,
            "cursor_model": cur,
            **budget,
        }

    force_high = canon == "implement_high" or is_high_risk(task)
    if force_high:
        return {
            "tier": "high",
            "purpose": "implement_high",
            "model": orchestration_model_high(),
            "note": "alto risco / dominio sensivel",
            "uses_llm": True,
            "cursor_model": cur,
            **budget_for("implement_high", role=role),
        }

    return {
        "tier": "low",
        "purpose": "implement_low",
        "model": orchestration_model_low(),
        "note": "implementacao padrao (orquestracao)",
        "uses_llm": True,
        "cursor_model": cur,
        **budget_for("implement_low", role=role),
    }
