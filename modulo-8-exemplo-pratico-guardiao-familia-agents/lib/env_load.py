"""Carrega `crew/.env` (e opcionalmente `.env` na raiz do módulo) em os.environ."""

from __future__ import annotations

import os
from pathlib import Path

from lib.paths import MODULE_ROOT

_LOADED = False


def load_dotenv(override: bool = False) -> Path | None:
    """
    Lê chave=valor de crew/.env (preferido) ou .env na raiz do módulo.
    Nao sobrescreve variaveis ja definidas, salvo override=True.
    """
    global _LOADED
    candidates = (
        MODULE_ROOT / "crew" / ".env",
        MODULE_ROOT / ".env",
    )
    path = next((p for p in candidates if p.exists()), None)
    if path is None:
        _LOADED = True
        return None

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip("'").strip('"')
        if not key:
            continue
        if override or key not in os.environ or not str(os.environ.get(key) or "").strip():
            os.environ[key] = val
    _LOADED = True
    return path


def ensure_env() -> None:
    if not _LOADED:
        load_dotenv()
