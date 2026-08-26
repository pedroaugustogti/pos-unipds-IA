"""ChatOpenAI via OpenRouter + select_model + captura de usage."""

from __future__ import annotations

import os
from typing import Any, TypeVar

from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from lib.model_tier import select_model

T = TypeVar("T", bound=BaseModel)


def get_llm(
    task: dict[str, Any] | None = None,
    *,
    purpose: str = "implement_low",
) -> tuple[ChatOpenAI, dict[str, Any]]:
    sel = select_model(task, purpose=purpose)
    if not sel.get("uses_llm"):
        raise ValueError(f"purpose={purpose} nao usa LLM (model={sel.get('model')})")

    api_key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY ausente")

    base = (
        (os.environ.get("OPENAI_API_BASE") or os.environ.get("OPENAI_BASE_URL") or "")
        .strip()
        or "https://openrouter.ai/api/v1"
    )
    max_tokens = int(sel.get("max_tokens") or 2048)
    llm = ChatOpenAI(
        model=str(sel["model"]),
        api_key=api_key,
        base_url=base,
        temperature=0.2,
        max_tokens=max_tokens if max_tokens > 0 else 2048,
    )
    return llm, sel


def _usage_from_message(msg: Any, *, model: str, purpose: str) -> dict[str, Any]:
    usage = getattr(msg, "usage_metadata", None) or {}
    if not usage and hasattr(msg, "response_metadata"):
        meta = msg.response_metadata or {}
        tok = meta.get("token_usage") or meta.get("usage") or {}
        usage = {
            "input_tokens": tok.get("prompt_tokens") or tok.get("input_tokens") or 0,
            "output_tokens": tok.get("completion_tokens") or tok.get("output_tokens") or 0,
            "total_tokens": tok.get("total_tokens") or 0,
        }
    inp = int(usage.get("input_tokens") or 0)
    out = int(usage.get("output_tokens") or 0)
    total = int(usage.get("total_tokens") or (inp + out))
    return {
        "model": model,
        "purpose": purpose,
        "input_tokens": inp,
        "output_tokens": out,
        "total_tokens": total,
    }


def invoke_text(
    task: dict[str, Any] | None,
    prompt: str,
    *,
    purpose: str = "summarize",
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """Retorna (texto, select_model, usage)."""
    llm, sel = get_llm(task, purpose=purpose)
    msg = llm.invoke(prompt)
    text = (getattr(msg, "content", None) or str(msg))[:2000]
    usage = _usage_from_message(msg, model=str(sel["model"]), purpose=purpose)
    return text, sel, usage


def invoke_structured(
    task: dict[str, Any] | None,
    prompt: str,
    schema: type[T],
    *,
    purpose: str = "implement_low",
) -> tuple[T, dict[str, Any], dict[str, Any]]:
    """Retorna (parsed, select_model, usage) via include_raw."""
    llm, sel = get_llm(task, purpose=purpose)
    structured = llm.with_structured_output(schema, include_raw=True)
    result = structured.invoke(prompt)
    if isinstance(result, dict) and "parsed" in result:
        parsed = result["parsed"]
        raw = result.get("raw")
        usage = _usage_from_message(raw, model=str(sel["model"]), purpose=purpose)
        if parsed is None:
            raise RuntimeError("structured_output parsed=None")
        return parsed, sel, usage  # type: ignore[return-value]
    # fallback: alguns backends devolvem só o modelo
    usage = {
        "model": str(sel["model"]),
        "purpose": purpose,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "note": "usage_unavailable",
    }
    return result, sel, usage  # type: ignore[return-value]


def format_usage_line(usage: dict[str, Any] | None) -> str:
    if not usage:
        return "model=n/a tokens=0"
    return (
        f"model={usage.get('model')} "
        f"in={usage.get('input_tokens', 0)} "
        f"out={usage.get('output_tokens', 0)} "
        f"total={usage.get('total_tokens', 0)}"
    )


def merge_usage_totals(
    totals: dict[str, Any] | None,
    usage: dict[str, Any] | None,
) -> dict[str, Any]:
    base = dict(totals or {})
    base.setdefault("input_tokens", 0)
    base.setdefault("output_tokens", 0)
    base.setdefault("total_tokens", 0)
    base.setdefault("calls", 0)
    base.setdefault("by_model", {})
    if not usage:
        return base
    base["input_tokens"] += int(usage.get("input_tokens") or 0)
    base["output_tokens"] += int(usage.get("output_tokens") or 0)
    base["total_tokens"] += int(usage.get("total_tokens") or 0)
    base["calls"] += 1
    model = str(usage.get("model") or "unknown")
    by = base["by_model"].setdefault(model, {"calls": 0, "total_tokens": 0})
    by["calls"] += 1
    by["total_tokens"] += int(usage.get("total_tokens") or 0)
    return base
