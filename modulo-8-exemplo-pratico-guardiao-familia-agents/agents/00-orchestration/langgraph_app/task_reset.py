"""Reset de task para `--from-zero` no LangGraph v2."""

from __future__ import annotations

from datetime import datetime, timezone

from board_automation.board.local_board import update_local_status
from board_automation.board.task_action_history import clear_task_history
from lib.orchestrator.claim_lock import load_locks, release_lock, save_locks
from lib.orchestrator.event_orchestrator import load_runtime, save_runtime


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def reset_task(task_id: str) -> None:
    """Volta task ao zero: Todo, sem lock, sem HITL/jobs/idempotência da task."""
    update_local_status(task_id, "Todo")
    release_lock(task_id)
    clear_task_history(task_id)

    locks = load_locks()
    by_role = locks.get("by_role") or {}
    for role, ids in list(by_role.items()):
        by_role[role] = [t for t in ids if t != task_id]
    save_locks(locks)

    rt = load_runtime()
    rt["hitl_queue"] = [
        h for h in (rt.get("hitl_queue") or []) if h.get("task_id") != task_id
    ]
    rt["dispatch_queue"] = [
        d for d in (rt.get("dispatch_queue") or []) if d.get("task_id") != task_id
    ]
    idem = rt.get("idempotency") or {}
    rt["idempotency"] = {
        k: v
        for k, v in idem.items()
        if task_id not in k and (not isinstance(v, dict) or v.get("task_id") != task_id)
    }
    for meta in (rt.get("agents") or {}).values():
        if meta.get("task_id") == task_id:
            meta["state"] = "idle"
            meta["task_id"] = None
            meta["updated_at"] = _now()
    save_runtime(rt)
