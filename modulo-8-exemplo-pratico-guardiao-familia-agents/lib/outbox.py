"""Outbox de operacoes GitHub (retry se gh falhar)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from lib.paths import MODULE_ROOT

OUTBOX_PATH = MODULE_ROOT / "crew" / "output" / "outbox.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def enqueue(op: str, payload: dict[str, Any], *, error: str | None = None) -> dict[str, Any]:
    row = {
        "at": _now(),
        "op": op,
        "payload": payload,
        "attempts": 0 if not error else 1,
        "last_error": error,
        "status": "pending" if error else "pending",
    }
    if error:
        row["status"] = "pending"
    OUTBOX_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTBOX_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def read_pending() -> list[dict[str, Any]]:
    if not OUTBOX_PATH.exists():
        return []
    rows = []
    for line in OUTBOX_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("status") in (None, "pending", "error"):
            rows.append(row)
    return rows


def rewrite_all(rows: list[dict[str, Any]]) -> None:
    OUTBOX_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTBOX_PATH.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def process_pending(
    handlers: dict[str, Callable[[dict[str, Any]], dict[str, Any]]],
    *,
    max_attempts: int = 5,
) -> dict[str, Any]:
    """Reprocessa outbox. handlers[op](payload) -> {ok: bool, error?: str}."""
    if not OUTBOX_PATH.exists():
        return {"ok": True, "processed": 0, "remaining": 0}
    all_rows = [json.loads(l) for l in OUTBOX_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    done = 0
    for row in all_rows:
        if row.get("status") == "done":
            continue
        if int(row.get("attempts") or 0) >= max_attempts:
            row["status"] = "dead"
            continue
        op = row.get("op")
        handler = handlers.get(op or "")
        if not handler:
            row["status"] = "error"
            row["last_error"] = f"Sem handler para op={op}"
            continue
        row["attempts"] = int(row.get("attempts") or 0) + 1
        try:
            result = handler(row.get("payload") or {})
            if result.get("ok"):
                row["status"] = "done"
                row["done_at"] = _now()
                row["last_error"] = None
                done += 1
            else:
                row["status"] = "pending"
                row["last_error"] = result.get("error") or "falha"
        except Exception as exc:  # noqa: BLE001
            row["status"] = "pending"
            row["last_error"] = str(exc)
    rewrite_all(all_rows)
    remaining = sum(1 for r in all_rows if r.get("status") in ("pending", "error"))
    return {"ok": True, "processed": done, "remaining": remaining, "path": str(OUTBOX_PATH)}
