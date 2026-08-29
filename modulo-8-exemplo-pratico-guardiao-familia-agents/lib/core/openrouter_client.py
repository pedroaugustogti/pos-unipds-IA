"""Cliente OpenRouter (SDK OpenAI-compat) — chave e base URL centralizados."""

from __future__ import annotations

import os

OPENROUTER_DEFAULT_BASE = "https://openrouter.ai/api/v1"


def openrouter_api_key() -> str:
    """Chave OpenRouter; fallback OPENAI_API_KEY (legado .env)."""
    return (os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY") or "").strip()


def openrouter_base_url() -> str:
    """Base OpenRouter; default https://openrouter.ai/api/v1."""
    return (
        (os.environ.get("OPENROUTER_BASE_URL") or "").strip()
        or (os.environ.get("OPENAI_API_BASE") or "").strip()
        or (os.environ.get("OPENAI_BASE_URL") or "").strip()
        or OPENROUTER_DEFAULT_BASE
    )


def has_openrouter_api_key() -> bool:
    return bool(openrouter_api_key())


def require_openrouter_api_key() -> str:
    key = openrouter_api_key()
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY ausente (ou OPENAI_API_KEY legado)")
    return key


def get_openai_client():
    """OpenAI SDK apontando para OpenRouter."""
    from openai import OpenAI

    return OpenAI(api_key=require_openrouter_api_key(), base_url=openrouter_base_url())
