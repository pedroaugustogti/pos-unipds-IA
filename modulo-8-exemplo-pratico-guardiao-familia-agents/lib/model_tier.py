"""D4 — Roteamento de modelo por risco (sem exigir 2 contas)."""

from __future__ import annotations

import os
from typing import Any

HIGH_HINTS = ("sos", "pagamento", "payment", "stripe", "lgpd", "auth", "terraform", "release")


def select_model(task: dict[str, Any] | None = None, *, purpose: str = "implement") -> dict[str, str]:
    """
    purpose: route | implement_low | implement_high
    """
    low = os.environ.get("CREWAI_MODEL", "gpt-4o-mini")
    high = os.environ.get("CREWAI_MODEL_HIGH") or low
    if purpose == "route":
        return {"tier": "route", "model": "deterministic", "note": "claim/roteamento sem LLM"}
    blob = " ".join([
        str((task or {}).get("title") or ""),
        str((task or {}).get("agent_role") or ""),
        str((task or {}).get("epic_id") or ""),
    ]).lower()
    if purpose == "implement_high" or any(h in blob for h in HIGH_HINTS):
        return {"tier": "high", "model": high, "note": "alto risco / dominio sensivel"}
    return {"tier": "low", "model": low, "note": "implementacao padrao"}
