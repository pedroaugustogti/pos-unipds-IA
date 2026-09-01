"""Helpers compartilhados entre nós LangGraph."""

from __future__ import annotations

import os
from typing import Any


def mode(state: dict[str, Any]) -> str:
    return (state.get("mode") or os.environ.get("GUARDIAO_LANGGRAPH_MODE") or "dry_run").strip()


def dry_run(state: dict[str, Any]) -> bool:
    return mode(state) == "dry_run"


def step(state: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    out = {**patch}
    out["steps"] = int(state.get("steps") or 0) + 1
    if patch.get("messages"):
        out["messages"] = list(state.get("messages") or []) + list(patch["messages"])
    if patch.get("react_trace"):
        out["react_trace"] = list(patch.get("react_trace") or [])
    return out
