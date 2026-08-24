"""Artefato de handoff entre agentes (contrato além do Status)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from lib.paths import HANDOFF_DIR


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def handoff_path(task_id: str):
    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    return HANDOFF_DIR / f"{task_id}.json"


def load_handoff(task_id: str) -> dict[str, Any] | None:
    p = handoff_path(task_id)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def write_handoff(
    task_id: str,
    *,
    from_agent: str,
    to_agent: str,
    event: str,
    status: str,
    repo: str | None = None,
    branch: str | None = None,
    pr_url: str | None = None,
    summary: str = "",
    doubts: list[str] | None = None,
    findings: list[str] | None = None,
    metrics: dict[str, Any] | None = None,
    react_trace: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Persiste o pacote que o próximo agente deve consumir."""
    prev = load_handoff(task_id) or {}
    history = list(prev.get("history") or [])
    history.append(
        {
            "at": _now(),
            "from_agent": from_agent,
            "to_agent": to_agent,
            "event": event,
            "status": status,
        }
    )
    history = history[-20:]

    payload = {
        "task_id": task_id,
        "updated_at": _now(),
        "from_agent": from_agent,
        "to_agent": to_agent,
        "event": event,
        "status": status,
        "repo": repo or prev.get("repo"),
        "branch": branch or prev.get("branch"),
        "pr_url": pr_url or prev.get("pr_url"),
        "summary": summary or prev.get("summary") or "",
        "doubts": doubts if doubts is not None else prev.get("doubts") or [],
        "findings": findings if findings is not None else prev.get("findings") or [],
        "metrics": {**(prev.get("metrics") or {}), **(metrics or {})},
        "react_trace": react_trace if react_trace is not None else prev.get("react_trace") or [],
        "history": history,
    }
    p = handoff_path(task_id)
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    payload["path"] = str(p)
    return payload
