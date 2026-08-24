"""Aplica o contrato de conclusão do dispatch (gateway + worker complete)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lib.gateway import emit_status_event
from lib.observability import log_workflow_event
from lib.paths import MODULE_ROOT
from lib.worker_jobs import load_jobs, save_jobs

RESULTS_DIR = MODULE_ROOT / "crew" / "output" / "dispatch_results"


def _complete_job(job_id: str) -> dict[str, Any]:
    from lib.event_orchestrator import set_agent_state

    data = load_jobs()
    for job in data.get("jobs") or []:
        if job.get("job_id") == job_id:
            job["status"] = "done"
            from datetime import datetime, timezone

            job["done_at"] = datetime.now(timezone.utc).isoformat()
            set_agent_state(job["role"], "idle", None)
            save_jobs(data)
            return {"ok": True, "job": job}
    return {"ok": False, "error": "job not found"}


def apply_dispatch_result(
    result: dict[str, Any] | Path,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Contrato:
      job_id, task_id, role, result_event, pr_url?, react_trace?, metrics?, summary?
    """
    if isinstance(result, Path):
        payload = json.loads(result.read_text(encoding="utf-8"))
        source = str(result)
    else:
        payload = result
        source = "inline"

    job_id = payload.get("job_id")
    task_id = payload.get("task_id")
    event = payload.get("result_event") or payload.get("event")
    if not job_id or not task_id or not event:
        return {"ok": False, "error": "job_id, task_id e result_event sao obrigatorios", "source": source}

    try:
        emit = emit_status_event(
            task_id,
            event,
            from_agent=payload.get("role"),
            summary=payload.get("summary") or f"dispatch complete ({event})",
            pr_url=payload.get("pr_url"),
            branch=payload.get("branch"),
            react_trace=payload.get("react_trace"),
            metrics=payload.get("metrics") or {},
            dry_run=dry_run,
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "source": source,
            "error": str(exc),
            "dry_run": dry_run,
            "payload": {"task_id": task_id, "event": event, "job_id": job_id},
        }

    out: dict[str, Any] = {
        "ok": bool(emit.get("ok")),
        "source": source,
        "emit": {
            "status": emit.get("status"),
            "code": emit.get("code"),
            "error": emit.get("error"),
            "to": (emit.get("notification") or {}).get("to"),
            "dispatch": (emit.get("notification") or {}).get("dispatch"),
        },
        "dry_run": dry_run,
    }

    if dry_run:
        return out

    if emit.get("ok") and emit.get("status") != "awaiting_human":
        done = _complete_job(job_id)
        out["job_complete"] = done
    elif emit.get("status") == "awaiting_human":
        out["job_complete"] = {"ok": False, "deferred": "hitl"}
    else:
        out["job_complete"] = {"ok": False, "skipped": True}

    note = emit.get("notification") or {}
    dispatch = note.get("dispatch") if isinstance(note.get("dispatch"), dict) else {}
    log_workflow_event(
        "dispatch_complete",
        task_id=task_id,
        agent=payload.get("role"),
        event=event,
        to_status=note.get("to"),
        dispatch_action=dispatch.get("action"),
        summary=payload.get("summary") or "",
        extra={"job_id": job_id, "pr_url": payload.get("pr_url"), "emit_status": emit.get("status")},
        dry_run=dry_run,
    )
    return out
