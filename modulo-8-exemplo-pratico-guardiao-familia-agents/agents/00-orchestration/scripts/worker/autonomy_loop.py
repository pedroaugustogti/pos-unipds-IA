#!/usr/bin/env python3
"""Fase 1 — Loop de controle contínuo (expire, outbox, reconcile, claim piloto, snapshot)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_bs = Path(__file__).resolve().parents[2] / "bootstrap.py"
_spec = importlib.util.spec_from_file_location("orch_bootstrap", _bs)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
_mod.setup()

import argparse
import importlib.util
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lib.orchestrator.claim_lock import DEFAULT_WIP_PER_ROLE, check_claim_allowed, count_in_progress_for_role  # noqa: E402
from lib.orchestrator.dispatch_adapter import drain_queued  # noqa: E402
from lib.env_load import ensure_env  # noqa: E402
from lib.gateway import emit_status_event, list_hitl_queue  # noqa: E402

ensure_env()
from lib.gateway.hitl_gates import is_high_risk_task  # noqa: E402
from lib.observability import SNAPSHOT_PATH, log_workflow_event  # noqa: E402
from lib.orchestrator.outbox import process_pending, read_pending  # noqa: E402
from lib.orchestrator.pilot import PILOT_ROLES, PILOT_SPRINT, PILOT_TASK_IDS  # noqa: E402
from board_automation.board.task_router import load_tasks, pick_task  # noqa: E402
from lib.orchestrator.worker_jobs import enqueue_job  # noqa: E402


_SCRIPT_BUCKETS = {
    "worker_run": ("worker", "worker_run"),
    "reconcile_board": ("cli", "reconcile_board"),
}


def _load_script(name: str):
    from lib.paths import orch_script

    bucket, stem = _SCRIPT_BUCKETS.get(name, ("cli", name))
    path = orch_script(bucket, f"{stem}.py")
    spec = importlib.util.spec_from_file_location(f"guardiao_{name}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Nao carregou {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_worker = _load_script("worker_run")
_reconcile_mod = _load_script("reconcile_board")
expire_leases = _worker.expire_leases
sync_from_runtime_queue = _worker.sync_from_runtime_queue
reconcile = _reconcile_mod.reconcile


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _retry_outbox(*, dry_run: bool) -> dict[str, Any]:
    if dry_run:
        pending = read_pending()
        return {"ok": True, "dry_run": True, "pending": len(pending), "processed": 0}
    from board_automation.board.board_client import _update_github_status, add_labels

    def handle_status(payload: dict) -> dict:
        return _update_github_status(payload["task_id"], payload["title"], payload["status"])

    def handle_labels(payload: dict) -> dict:
        return add_labels(payload["repo"], payload["task_id"], payload["labels"], dry_run=False)

    return process_pending({
        "update_status": handle_status,
        "add_labels": handle_labels,
    })


def _pilot_exclude() -> set[str]:
    return {t["id"] for t in load_tasks() if t["id"] not in PILOT_TASK_IDS}


def _pick_for_role(role: str) -> dict | None:
    return pick_task(
        role,
        sprint_atual=PILOT_SPRINT,
        exclude_ids=_pilot_exclude(),
        sprint_only=False,
    )


def _role_idle(role: str, idle: list[str]) -> bool:
    return role in idle


def _wip_free(role: str) -> bool:
    return count_in_progress_for_role(role) < DEFAULT_WIP_PER_ROLE


def _claim_and_enqueue(
    role: str,
    task: dict,
    *,
    dry_run: bool,
    pause_high_risk: bool,
) -> dict[str, Any]:
    tid = task["id"]
    if pause_high_risk and is_high_risk_task(task):
        return {
            "ok": False,
            "skipped": True,
            "code": "hitl_pause_high_risk",
            "task_id": tid,
            "role": role,
        }

    lock = check_claim_allowed(tid, role)
    if not lock.get("ok") and lock.get("code") != "already_owned":
        return {"ok": False, "skipped": True, "code": lock.get("code"), "task_id": tid, "role": role, "lock": lock}

    result = emit_status_event(
        tid,
        "claim",
        from_agent=role,
        summary=f"autonomy_loop claim ({'dry-run' if dry_run else 'live'})",
        dry_run=dry_run,
    )
    out: dict[str, Any] = {
        "ok": bool(result.get("ok")),
        "task_id": tid,
        "role": role,
        "dry_run": dry_run,
        "emit": {
            "status": result.get("status"),
            "code": result.get("code"),
            "error": result.get("error"),
            "duplicate": result.get("duplicate"),
        },
    }
    if dry_run:
        out["simulated"] = True
        return out

    if result.get("ok") and result.get("status") in ("applied", None) and not result.get("duplicate"):
        # awaiting_human / propose_only não enqueue de implementação
        if result.get("status") == "awaiting_human":
            out["enqueued"] = False
            return out
        job = enqueue_job(task_id=tid, role=role, event="claim")
        out["job_id"] = job.get("job_id")
        out["enqueued"] = True
    return out


def run_cycle(
    *,
    dry_run: bool = False,
    do_reconcile: bool = True,
    do_outbox: bool = True,
    do_dispatch: bool = True,
) -> dict[str, Any]:
    cycle: dict[str, Any] = {"at": _now(), "dry_run": dry_run, "steps": {}}

    # 1. expire leases
    expired = [] if dry_run else expire_leases()
    if dry_run:
        # ainda detecta leases vencidos sem mutar
        from datetime import datetime as dt
        from lib.orchestrator.worker_jobs import load_jobs

        now = dt.now(timezone.utc)
        for job in (load_jobs().get("jobs") or []):
            if job.get("status") != "leased" or not job.get("lease_until"):
                continue
            until = dt.fromisoformat(job["lease_until"])
            if until <= now:
                expired.append({"job_id": job["job_id"], "task_id": job["task_id"], "dry_run": True})
    cycle["steps"]["expire"] = {"count": len(expired), "jobs": [
        {"job_id": j.get("job_id"), "task_id": j.get("task_id")} for j in expired
    ]}
    for j in expired:
        log_workflow_event(
            "lease_expired",
            task_id=j.get("task_id"),
            agent=j.get("role"),
            event="busy_ttl",
            summary="Lease expirado → queued",
            extra={"job_id": j.get("job_id"), "dry_run": dry_run},
            dry_run=dry_run,
            refresh_dashboard=False,
        )

    # 2. outbox
    if do_outbox:
        cycle["steps"]["outbox"] = _retry_outbox(dry_run=dry_run)
    else:
        cycle["steps"]["outbox"] = {"skipped": True}

    # 3. reconcile (sem --force)
    if do_reconcile:
        try:
            rec = reconcile(dry_run=dry_run, force=False)
            cycle["steps"]["reconcile"] = {
                "ok": rec.get("ok"),
                "changed": rec.get("changed"),
                "conflicts": len(rec.get("skipped_conflicts") or []),
                "skipped_conflicts": rec.get("skipped_conflicts") or [],
            }
            if rec.get("skipped_conflicts"):
                log_workflow_event(
                    "reconcile_conflict",
                    summary=f"{len(rec['skipped_conflicts'])} conflito(s) Project×local",
                    extra={"conflicts": rec["skipped_conflicts"][:10]},
                    dry_run=dry_run,
                    refresh_dashboard=False,
                )
        except Exception as exc:  # noqa: BLE001
            cycle["steps"]["reconcile"] = {"ok": False, "error": str(exc)}
    else:
        cycle["steps"]["reconcile"] = {"skipped": True}

    # 4. HITL → pausa claims de alto risco
    hitl = list_hitl_queue()
    pause_high_risk = len(hitl) > 0
    cycle["steps"]["hitl"] = {
        "pending": len(hitl),
        "pause_high_risk_claims": pause_high_risk,
        "items": [
            {"task_id": h.get("task_id"), "event": h.get("event")}
            for h in hitl[:10]
        ],
    }
    if pause_high_risk:
        log_workflow_event(
            "autonomy_pause",
            summary=f"HITL pendente ({len(hitl)}) — sem claim de alto risco; sem merge",
            extra={"hitl_pending": len(hitl)},
            dry_run=dry_run,
            refresh_dashboard=False,
        )

    # 5. claim piloto para roles idle com WIP livre
    sync_from_runtime_queue()
    from lib.orchestrator.event_orchestrator import list_idle_agents

    idle = list_idle_agents()
    claims: list[dict[str, Any]] = []
    for role in PILOT_ROLES:
        if not _role_idle(role, idle):
            claims.append({"role": role, "skipped": True, "code": "busy"})
            continue
        if not _wip_free(role):
            claims.append({"role": role, "skipped": True, "code": "wip_exceeded"})
            continue
        task = _pick_for_role(role)
        if not task:
            claims.append({"role": role, "skipped": True, "code": "no_task"})
            continue
        claims.append(_claim_and_enqueue(role, task, dry_run=dry_run, pause_high_risk=pause_high_risk))
        # após claim live, role deixa de estar idle no próximo pick deste ciclo
        if not dry_run and claims[-1].get("ok") and claims[-1].get("enqueued"):
            idle = [a for a in idle if a != role]

    cycle["steps"]["claims"] = claims
    for c in claims:
        if c.get("skipped"):
            continue
        log_workflow_event(
            "autonomy_claim",
            task_id=c.get("task_id"),
            agent=c.get("role"),
            event="claim",
            summary="claim simulado" if dry_run else "claim autonomy_loop",
            extra={"emit": c.get("emit"), "job_id": c.get("job_id"), "simulated": dry_run},
            dry_run=dry_run,
            refresh_dashboard=False,
        )

    # 6. drain dispatch (Fase 1 = stub)
    if do_dispatch:
        drained = drain_queued(dry_run=dry_run)
        cycle["steps"]["dispatch"] = {"count": len(drained), "results": drained[:10]}
    else:
        cycle["steps"]["dispatch"] = {"skipped": True}

    # 7. snapshot + dashboard (estado autonomy no runtime para build_snapshot)
    from lib.orchestrator.event_orchestrator import load_runtime, save_runtime

    autonomy_state = {
        "at": cycle["at"],
        "dry_run": dry_run,
        "paused_high_risk": pause_high_risk,
        "hitl_pending": len(hitl),
        "pilot_sprint": PILOT_SPRINT,
        "pilot_roles": list(PILOT_ROLES),
        "pilot_task_ids": sorted(PILOT_TASK_IDS),
        "cycle": {
            "expire": cycle["steps"]["expire"]["count"],
            "claims_ok": sum(1 for c in claims if c.get("ok") and not c.get("skipped")),
            "claims_simulated": sum(1 for c in claims if c.get("simulated")),
            "reconcile_conflicts": (cycle["steps"].get("reconcile") or {}).get("conflicts", 0),
        },
        "merge_policy": "never_auto_merge",
    }
    rt = load_runtime()
    rt["autonomy"] = autonomy_state
    save_runtime(rt)

    log_workflow_event(
        "autonomy_cycle",
        summary=f"ciclo autonomy_loop dry_run={dry_run}",
        extra={"autonomy": autonomy_state["cycle"], "pause": pause_high_risk},
        dry_run=dry_run,
        refresh_dashboard=True,
    )
    cycle["snapshot"] = str(SNAPSHOT_PATH)
    cycle["autonomy"] = autonomy_state

    if os.environ.get("GUARDAO_PUBLISH_LIVE", "").strip() in ("1", "true", "True"):
        _spec = importlib.util.spec_from_file_location(
            "guardiao_publish_live", __import__("lib.paths", fromlist=["orch_script"]).orch_script("demo", "publish_live_pages.py")
        )
        if _spec and _spec.loader:
            _mod = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            cycle["pages"] = _mod.publish(refresh=False)

    return cycle


def main() -> int:
    p = argparse.ArgumentParser(description="Loop de autonomia — controle contínuo (Fase 1)")
    p.add_argument("--interval", type=float, default=30.0, help="Segundos entre ciclos (default 30)")
    p.add_argument("--once", action="store_true", help="Executa um único ciclo")
    p.add_argument("--duration", type=float, default=None, help="Roda por N segundos e sai")
    p.add_argument("--dry-run", action="store_true", help="Simula claims; não muta board/jobs (exceto snapshot)")
    p.add_argument("--no-reconcile", action="store_true")
    p.add_argument("--no-outbox", action="store_true")
    p.add_argument("--no-dispatch", action="store_true")
    args = p.parse_args()

    cycles: list[dict[str, Any]] = []
    started = time.monotonic()
    while True:
        cycle = run_cycle(
            dry_run=args.dry_run,
            do_reconcile=not args.no_reconcile,
            do_outbox=not args.no_outbox,
            do_dispatch=not args.no_dispatch,
        )
        cycles.append(cycle)
        print(json.dumps({
            "cycle": len(cycles),
            "at": cycle["at"],
            "expire": cycle["steps"]["expire"]["count"],
            "hitl_pending": cycle["steps"]["hitl"]["pending"],
            "pause_high_risk": cycle["steps"]["hitl"]["pause_high_risk_claims"],
            "claims": [
                {
                    "role": c.get("role"),
                    "task_id": c.get("task_id"),
                    "ok": c.get("ok"),
                    "skipped": c.get("skipped"),
                    "code": c.get("code"),
                    "simulated": c.get("simulated"),
                }
                for c in cycle["steps"]["claims"]
            ],
            "reconcile": cycle["steps"].get("reconcile"),
            "snapshot": cycle.get("snapshot"),
        }, ensure_ascii=False, indent=2))

        if args.once:
            break
        if args.duration is not None and (time.monotonic() - started) >= args.duration:
            break
        time.sleep(max(0.5, args.interval))

    summary = {
        "ok": True,
        "cycles": len(cycles),
        "dry_run": args.dry_run,
        "claims_simulated_total": sum(
            1
            for cyc in cycles
            for c in cyc["steps"]["claims"]
            if c.get("simulated")
        ),
        "last_snapshot": cycles[-1].get("snapshot") if cycles else None,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
