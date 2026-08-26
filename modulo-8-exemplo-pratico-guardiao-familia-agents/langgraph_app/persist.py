"""Persistência de runs LangGraph."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lib.paths import MODULE_ROOT

OUT_DIR = MODULE_ROOT / "crew" / "output" / "langgraph"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_run(task_id: str, state: dict[str, Any]) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{task_id}.json"
    payload = {
        "task_id": task_id,
        "saved_at": _now(),
        "mode": state.get("mode"),
        "board_status": state.get("board_status"),
        "decision": state.get("decision"),
        "review": state.get("review"),
        "model_tier": state.get("model_tier"),
        "token_usage": state.get("token_usage"),
        "langsmith": state.get("langsmith"),
        "hitl_pending": state.get("hitl_pending"),
        "done": bool(state.get("done")) or state.get("board_status") == "Done",
        "steps": state.get("steps"),
        "messages": state.get("messages"),
        "react_trace": state.get("react_trace"),
        "last_tool_results": state.get("last_tool_results"),
        "error": state.get("error"),
        "cycle": state.get("cycle"),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    return path
