"""Trilha JSONL mínima de eventos do pipeline (substitui observability pesado)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lib.paths import OBSERVABILITY_DIR

OUT_DIR = OBSERVABILITY_DIR
LOG_PATH = OUT_DIR / "workflow.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUT_DIR


def log_workflow_event(
    kind: str,
    *,
    task_id: str | None = None,
    agent: str | None = None,
    event: str | None = None,
    from_status: str | None = None,
    to_status: str | None = None,
    dispatch_action: str | None = None,
    summary: str = "",
    extra: dict[str, Any] | None = None,
    dry_run: bool = False,
    **_: Any,
) -> dict[str, Any]:
    """Append-only em workflow.jsonl."""
    ensure_dirs()
    record: dict[str, Any] = {
        "ts": _now(),
        "kind": kind,
        "task_id": task_id,
        "agent": agent,
        "event": event,
        "from_status": from_status,
        "to_status": to_status,
        "dispatch_action": dispatch_action,
        "summary": (summary or "")[:1000],
        "dry_run": dry_run,
    }
    if extra:
        record["extra"] = extra
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def log_from_notification(notification: dict[str, Any], *, dry_run: bool = False) -> dict[str, Any]:
    dispatch = notification.get("dispatch") or {}
    kind = "blocker" if notification.get("type") == "blocker" else "status_change"
    return log_workflow_event(
        kind,
        task_id=notification.get("task_id"),
        agent=notification.get("next_agent") or dispatch.get("call_agent"),
        event=notification.get("event"),
        from_status=notification.get("from"),
        to_status=notification.get("to"),
        dispatch_action=dispatch.get("action"),
        summary=dispatch.get("message") or notification.get("start_hint") or "",
        extra={
            "agent_idle": notification.get("agent_idle"),
            "queued": notification.get("queued"),
            "bug": notification.get("bug"),
            "blocker": bool(notification.get("blocker")),
            "title": notification.get("title"),
        },
        dry_run=dry_run or bool(notification.get("dry_run")),
    )
