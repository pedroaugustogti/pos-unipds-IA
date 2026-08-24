#!/usr/bin/env python3
"""Fase 5 — sessão supervisionada de intercalação até In Pull Request (sem merge)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.claim_lock import check_claim_allowed, release_lock  # noqa: E402
from lib.gateway import approve_hitl, emit_status_event  # noqa: E402
from lib.local_board import get_local_status  # noqa: E402
from lib.observability import build_snapshot, write_dashboard  # noqa: E402
from lib.pilot import PHASE5_TASK_IDS  # noqa: E402
from lib.reviewer_pairs import normalize_creator_role, reviewer_for  # noqa: E402
from lib.task_router import load_tasks  # noqa: E402
from lib.worker_jobs import enqueue_job  # noqa: E402

REPORT_PATH = ROOT / "crew" / "output" / "pilot_session_report.json"

# Pipeline até In Pull Request — nunca merge_pr
STEPS: list[tuple[str, str]] = [
    ("claim", "creator"),
    ("open_pr", "creator"),
    ("start_review", "reviewer"),
    ("approve_review", "reviewer"),
    ("start_test", "qa-gate"),
    ("test_passed", "qa-gate"),
]

# Status atual → próximo índice em STEPS
_RESUME_FROM_STATUS: dict[str, int] = {
    "Todo": 0,
    "In Progress": 1,
    "Ready for Code Review": 2,
    "In Code Review": 3,
    "Ready for Test": 4,
    "In Test": 5,
    "In Pull Request": len(STEPS),
    "Done": len(STEPS),
}


def _initial_step(task_id: str) -> int:
    st = get_local_status(task_id) or "Todo"
    return _RESUME_FROM_STATUS.get(st, 0)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _task(task_id: str) -> dict[str, Any]:
    t = next((x for x in load_tasks() if x["id"] == task_id), None)
    if not t:
        raise SystemExit(f"Task {task_id} nao encontrada")
    return t


def _role_for(task: dict[str, Any], who: str) -> str:
    creator = normalize_creator_role(task.get("agent_role") or "backend")
    if who == "creator":
        return creator
    if who == "reviewer":
        return reviewer_for(creator)
    return "qa-gate"


def _react_trace(task_id: str, step: str) -> list[dict[str, str]]:
    return [
        {
            "thought": f"Piloto Fase 5 — avancar `{task_id}` em `{step}`",
            "action": step,
            "observation": "Sessao supervisionada (sem merge automatico)",
        }
    ]


def _emit(
    task_id: str,
    event: str,
    *,
    role: str,
    dry_run: bool,
    pr_url: str | None = None,
    force_hitl: bool = False,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "from_agent": role,
        "summary": f"pilot_session {event}",
        "dry_run": dry_run,
    }
    if event == "open_pr":
        kwargs["pr_url"] = pr_url or f"https://example.com/pilot/{task_id}"
        kwargs["react_trace"] = _react_trace(task_id, event)
        kwargs["branch"] = f"agent/{task_id.lower()}"
    if force_hitl:
        kwargs["force_hitl_approved"] = True
    try:
        return emit_status_event(task_id, event, **kwargs)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc), "status": "error"}


def advance_one(
    task_id: str,
    event: str,
    who: str,
    *,
    dry_run: bool,
    auto_hitl: bool,
) -> dict[str, Any]:
    task = _task(task_id)
    role = _role_for(task, who)
    before = get_local_status(task_id)
    out = _emit(task_id, event, role=role, dry_run=dry_run)
    hitl_resolved = None

    if (
        auto_hitl
        and out.get("ok")
        and out.get("status") in ("awaiting_human", "propose_only")
    ):
        hitl_resolved = approve_hitl(task_id, event, dry_run=dry_run)
        if isinstance(hitl_resolved, dict) and hitl_resolved.get("ok"):
            if hitl_resolved.get("status") != "applied":
                out = _emit(task_id, event, role=role, dry_run=dry_run, force_hitl=True)
            else:
                out = hitl_resolved

    # dry-run do gateway nao grava Status — espelha localmente para permitir pipeline
    if dry_run and out.get("ok"):
        from lib.local_board import update_local_status
        from lib.task_status_workflow import EVENT_TARGET

        target = EVENT_TARGET.get(event)
        if target:
            update_local_status(task_id, target)

    after = get_local_status(task_id)
    if out.get("ok") and event == "claim" and not dry_run:
        enqueue_job(task_id=task_id, role=role, event="claim")
    if (out.get("ok") or out.get("status") == "applied") and event == "open_pr":
        release_lock(task_id)

    # Board local pode aplicar mesmo se gh falhar (outbox) — piloto segue no JSON
    from lib.task_status_workflow import EVENT_TARGET

    expected = EVENT_TARGET.get(event)
    local_ok = bool(out.get("ok")) or (
        out.get("status") in ("applied", "propose_only")
        and expected is not None
        and after == expected
    )

    return {
        "task_id": task_id,
        "event": event,
        "role": role,
        "before": before,
        "after": after,
        "ok": local_ok,
        "status": out.get("status"),
        "code": out.get("code"),
        "error": out.get("error"),
        "hitl": out.get("hitl"),
        "hitl_resolved": bool(hitl_resolved and hitl_resolved.get("ok")),
        "emit_ok": bool(out.get("ok")),
        "at": _now(),
    }


def run_session(
    task_ids: list[str],
    *,
    dry_run: bool = False,
    auto_hitl: bool = True,
    interleave: bool = True,
) -> dict[str, Any]:
    """
    Intercala com WIP=1 por role: agenda o próximo passo de cada task
    quando o claim do role estiver livre.
    """
    log: list[dict[str, Any]] = []
    step_idx = {tid: _initial_step(tid) for tid in task_ids}

    if not interleave:
        for tid in task_ids:
            for event, who in STEPS:
                log.append(
                    advance_one(tid, event, who, dry_run=dry_run, auto_hitl=auto_hitl)
                )
                if not log[-1].get("ok"):
                    break
    else:
        guard = 0
        max_iter = len(task_ids) * len(STEPS) * 3
        while any(step_idx[t] < len(STEPS) for t in task_ids) and guard < max_iter:
            guard += 1
            progressed = False
            for tid in task_ids:
                i = step_idx[tid]
                if i >= len(STEPS):
                    continue
                event, who = STEPS[i]
                task = _task(tid)
                role = _role_for(task, who)
                if event == "claim":
                    lock = check_claim_allowed(tid, role)
                    if not lock.get("ok") and lock.get("code") != "already_owned":
                        continue
                row = advance_one(tid, event, who, dry_run=dry_run, auto_hitl=auto_hitl)
                log.append(row)
                progressed = True
                if row.get("ok"):
                    step_idx[tid] = i + 1
                else:
                    # falha dura — marca task como esgotada neste passo
                    step_idx[tid] = len(STEPS)
            if not progressed:
                break

    finals = {tid: get_local_status(tid) for tid in task_ids}
    ok_ipr = all(finals.get(t) == "In Pull Request" for t in task_ids)
    report = {
        "ok": ok_ipr and not any(not x.get("ok") for x in log),
        "phase": 5,
        "mode": "dry_run_local_mirror" if dry_run else "supervised",
        "started_at": log[0]["at"] if log else _now(),
        "finished_at": _now(),
        "task_ids": task_ids,
        "steps": STEPS,
        "log": log,
        "final_status": finals,
        "success_criterion": "In Pull Request sem merge_pr",
        "merge_attempted": False,
        "interleaved": interleave,
        "auto_hitl": auto_hitl,
        "failures": [x for x in log if not x.get("ok")],
    }
    write_dashboard(build_snapshot())
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["report_path"] = str(REPORT_PATH)
    return report


def main() -> int:
    p = argparse.ArgumentParser(description="Piloto Fase 5 — intercalacao ate In Pull Request")
    p.add_argument("--tasks", nargs="*", default=list(PHASE5_TASK_IDS))
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--no-interleave", action="store_true", help="Uma task por vez")
    p.add_argument("--no-auto-hitl", action="store_true", help="Para em HITL sem aprovar")
    args = p.parse_args()

    report = run_session(
        list(args.tasks),
        dry_run=args.dry_run,
        auto_hitl=not args.no_auto_hitl,
        interleave=not args.no_interleave,
    )
    print(json.dumps({
        "ok": report.get("ok"),
        "final_status": report.get("final_status"),
        "failures": len(report.get("failures") or []),
        "steps_ok": sum(1 for x in report.get("log") or [] if x.get("ok")),
        "steps_total": len(report.get("log") or []),
        "merge_attempted": report.get("merge_attempted"),
        "report_path": report.get("report_path"),
        "sample": (report.get("log") or [])[:3],
    }, ensure_ascii=False, indent=2))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
