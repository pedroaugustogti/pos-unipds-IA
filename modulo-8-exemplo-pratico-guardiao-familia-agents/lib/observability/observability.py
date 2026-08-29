"""Observabilidade do fluxo de trabalho dos agentes.

Persistencia:
- agents/00-runtime/output/observability/workflow.jsonl  (append-only)
- agents/00-runtime/output/observability/snapshot.json  (estado atual)
- agents/00-runtime/output/observability/dashboard.html (acompanhamento visual)
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lib.paths import OBSERVABILITY_DIR

OUT_DIR = OBSERVABILITY_DIR
LOG_PATH = OUT_DIR / "workflow.jsonl"
SNAPSHOT_PATH = OUT_DIR / "snapshot.json"
DASHBOARD_PATH = OUT_DIR / "dashboard.html"


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
    refresh_dashboard: bool = True,
    correlation_id: str | None = None,
    job_id: str | None = None,
) -> dict[str, Any]:
    """Registra um evento de observabilidade (JSONL + snapshot + dashboard)."""
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
        "correlation_id": correlation_id,
        "job_id": job_id,
    }
    if extra:
        record["extra"] = extra
        if correlation_id is None and extra.get("correlation_id"):
            record["correlation_id"] = extra.get("correlation_id")
        if job_id is None and extra.get("job_id"):
            record["job_id"] = extra.get("job_id")

    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    snap = build_snapshot()
    SNAPSHOT_PATH.write_text(
        json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if refresh_dashboard:
        write_dashboard(snap)
    return record


def read_events(limit: int | None = None) -> list[dict[str, Any]]:
    ensure_dirs()
    if not LOG_PATH.exists():
        return []
    rows: list[dict[str, Any]] = []
    with LOG_PATH.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    if limit is not None and limit > 0:
        return rows[-limit:]
    return rows


def build_snapshot() -> dict[str, Any]:
    """Agrega runtime + jobs + board para acompanhamento ao vivo."""
    from lib.orchestrator.event_orchestrator import load_runtime, list_idle_agents
    from board_automation.board.local_board import status_map
    from lib.orchestrator.outbox import read_pending
    from lib.orchestrator.pilot import PILOT_TASK_IDS
    from board_automation.board.task_action_history import list_task_history_links
    from board_automation.board.task_router import load_tasks
    from board_automation.board.task_status_workflow import STATUSES
    from lib.orchestrator.worker_jobs import load_jobs

    events = read_events()
    runtime = load_runtime()
    agents = runtime.get("agents") or {}
    blockers = runtime.get("blockers") or []
    queue = runtime.get("dispatch_queue") or []
    hitl_queue = runtime.get("hitl_queue") or []

    by_kind = Counter(e.get("kind") or "unknown" for e in events)
    by_event = Counter(e.get("event") for e in events if e.get("event"))
    by_agent = Counter(e.get("agent") for e in events if e.get("agent"))
    by_dispatch = Counter(
        e.get("dispatch_action") for e in events if e.get("dispatch_action")
    )

    try:
        statuses = status_map()
        status_counts = Counter(statuses.values())
    except Exception:  # noqa: BLE001
        statuses = {}
        status_counts = Counter()

    busy = [
        {"agent": name, **meta}
        for name, meta in agents.items()
        if meta.get("state") == "busy"
    ]
    idle = list_idle_agents(runtime)
    timeline = events[-50:]

    recent_tasks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for e in reversed(events):
        tid = e.get("task_id")
        if not tid or tid in seen:
            continue
        seen.add(tid)
        recent_tasks.append({
            "task_id": tid,
            "last_event": e.get("event"),
            "last_kind": e.get("kind"),
            "agent": e.get("agent"),
            "to_status": e.get("to_status"),
            "ts": e.get("ts"),
            "dispatch_action": e.get("dispatch_action"),
            "job_id": e.get("job_id") or (e.get("extra") or {}).get("job_id"),
            "correlation_id": e.get("correlation_id"),
        })
        if len(recent_tasks) >= 25:
            break

    # Kanban: piloto + ativos (nao-Todo/Done) + recentes
    tasks_by_id = {t["id"]: t for t in load_tasks()}
    interesting = set(PILOT_TASK_IDS) | set(seen)
    for tid, st in statuses.items():
        if st not in ("Todo", "Done"):
            interesting.add(tid)

    kanban: dict[str, list[dict[str, Any]]] = {s: [] for s in STATUSES}
    for tid in sorted(interesting):
        st = statuses.get(tid) or "Todo"
        if st not in kanban:
            kanban[st] = []
        t = tasks_by_id.get(tid) or {}
        kanban[st].append({
            "task_id": tid,
            "title": (t.get("title") or "")[:80],
            "role": t.get("agent_role"),
            "pilot": tid in PILOT_TASK_IDS,
            "release_blocker": str(t.get("release_blocker") or "").lower() in ("true", "yes", "1"),
        })

    jobs_data = load_jobs()
    jobs = jobs_data.get("jobs") or []
    job_by_status = Counter(j.get("status") or "?" for j in jobs)
    leased = [
        {
            "job_id": j.get("job_id"),
            "task_id": j.get("task_id"),
            "role": j.get("role"),
            "lease_until": j.get("lease_until"),
            "event": j.get("event"),
        }
        for j in jobs
        if j.get("status") == "leased"
    ]
    queued_jobs = [
        {
            "job_id": j.get("job_id"),
            "task_id": j.get("task_id"),
            "role": j.get("role"),
            "event": j.get("event"),
        }
        for j in jobs
        if j.get("status") == "queued"
    ]

    try:
        outbox_pending = read_pending()
    except Exception:  # noqa: BLE001
        outbox_pending = []

    autonomy = runtime.get("autonomy") or {}
    health = {
        "heartbeat_at": autonomy.get("at"),
        "paused_high_risk": bool(autonomy.get("paused_high_risk") or hitl_queue),
        "hitl_pending": len(hitl_queue),
        "outbox_pending": len(outbox_pending),
        "jobs_queued": int(job_by_status.get("queued") or 0),
        "jobs_leased": int(job_by_status.get("leased") or 0),
        "reconcile_conflicts": (autonomy.get("cycle") or {}).get("reconcile_conflicts", 0),
        "merge_policy": autonomy.get("merge_policy") or "never_auto_merge",
    }

    return {
        "generated_at": _now(),
        "paths": {
            "log": str(LOG_PATH),
            "snapshot": str(SNAPSHOT_PATH),
            "dashboard": str(DASHBOARD_PATH),
        },
        "totals": {
            "events": len(events),
            "by_kind": dict(by_kind),
            "by_event": dict(by_event),
            "by_agent": dict(by_agent),
            "by_dispatch": dict(by_dispatch),
            "board_status": dict(status_counts),
            "idle_agents": len(idle),
            "busy_agents": len(busy),
            "queue_len": len(queue),
            "blockers": len(blockers),
            "hitl_pending": len(hitl_queue),
            "jobs_queued": health["jobs_queued"],
            "jobs_leased": health["jobs_leased"],
            "outbox_pending": health["outbox_pending"],
        },
        "idle_agents": idle,
        "busy_agents": busy,
        "dispatch_queue": queue[-20:],
        "hitl_queue": hitl_queue[:20],
        "autonomy_pause": len(hitl_queue) > 0,
        "blockers": blockers,
        "recent_tasks": recent_tasks,
        "timeline": timeline,
        "bug_counts": runtime.get("bug_counts") or {},
        "autonomy": autonomy,
        "kanban": kanban,
        "worker_jobs": {
            "by_status": dict(job_by_status),
            "queued": queued_jobs[:20],
            "leased": leased[:20],
        },
        "outbox_pending": outbox_pending[:20],
        "health": health,
        "pilot_task_ids": sorted(PILOT_TASK_IDS),
        "task_histories": list_task_history_links(),
    }


def write_dashboard(snapshot: dict[str, Any] | None = None) -> Path:
    """Escreve dashboard live (fetch snapshot.json) + garante snapshot atualizado."""
    ensure_dirs()
    snap = snapshot or build_snapshot()
    SNAPSHOT_PATH.write_text(
        json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    template = Path(__file__).with_name("dashboard_live.html")
    html = template.read_text(encoding="utf-8")
    DASHBOARD_PATH.write_text(html, encoding="utf-8")
    return DASHBOARD_PATH


def log_from_notification(notification: dict[str, Any], *, dry_run: bool = False) -> dict[str, Any]:
    """Converte payload de notify_status_change em log de observabilidade."""
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
            "skill": (notification.get("skill_impact") or {}).get("skill"),
            "blocker": bool(notification.get("blocker")),
            "title": notification.get("title"),
        },
        dry_run=dry_run or bool(notification.get("dry_run")),
    )
