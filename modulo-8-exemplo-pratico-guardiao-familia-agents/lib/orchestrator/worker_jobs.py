"""Fila de jobs do worker local (compartilhada por gateway e CLI)."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from lib.core.agent_paths import agent_prompt_path
from lib.orchestrator.event_orchestrator import load_runtime, save_runtime
from lib.paths import HANDOFF_DIR, WORKER_JOBS_PATH

JOBS_PATH = WORKER_JOBS_PATH


def _iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_jobs() -> dict[str, Any]:
    if not JOBS_PATH.exists():
        return {"version": 1, "jobs": []}
    return json.loads(JOBS_PATH.read_text(encoding="utf-8"))


def save_jobs(data: dict[str, Any]) -> None:
    JOBS_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = _iso()
    JOBS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def enqueue_job(
    *,
    task_id: str,
    role: str,
    event: str,
    agent_prompt: str | None = None,
    mirror_runtime_queue: bool = True,
) -> dict[str, Any]:
    data = load_jobs()
    # evita duplicata queued mesma task+role
    for j in data.get("jobs") or []:
        if (
            j.get("task_id") == task_id
            and j.get("role") == role
            and j.get("status") in ("queued", "leased")
        ):
            return j
    job = {
        "job_id": str(uuid.uuid4()),
        "task_id": task_id,
        "role": role,
        "event": event,
        "handoff_path": str(HANDOFF_DIR / f"{task_id}.json"),
        "agent_prompt": agent_prompt
        or agent_prompt_path(role).relative_to(MODULE_ROOT).as_posix(),
        "status": "queued",
        "created_at": _iso(),
        "lease_until": None,
    }
    data.setdefault("jobs", []).append(job)
    save_jobs(data)
    if mirror_runtime_queue:
        rt = load_runtime()
        q = rt.setdefault("dispatch_queue", [])
        q.append({
            "task_id": task_id,
            "agent": role,
            "status": "queued",
            "event": event,
            "job_id": job["job_id"],
            "at": _iso(),
        })
        save_runtime(rt)
    return job
