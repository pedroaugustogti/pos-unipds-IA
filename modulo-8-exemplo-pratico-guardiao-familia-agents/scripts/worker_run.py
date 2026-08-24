#!/usr/bin/env python3
"""Worker local: consome dispatch_queue / jobs e gera bundle para Cursor."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.event_orchestrator import list_idle_agents, load_runtime, save_runtime, set_agent_state  # noqa: E402
from lib.handoff import load_handoff  # noqa: E402
from lib.paths import MODULE_ROOT  # noqa: E402
from lib.react_policy import max_iterations_for  # noqa: E402
from lib.worker_jobs import enqueue_job, load_jobs, save_jobs, JOBS_PATH  # noqa: E402

PROMPTS_DIR = MODULE_ROOT / "crew" / "output" / "prompts"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).isoformat()


def sync_from_runtime_queue() -> int:
    """Promove itens da dispatch_queue sem job_id para worker_jobs."""
    rt = load_runtime()
    data = load_jobs()
    existing = {(j.get("task_id"), j.get("role"), j.get("status")) for j in data.get("jobs") or []}
    n = 0
    for item in rt.get("dispatch_queue") or []:
        if item.get("job_id"):
            continue
        key = (item.get("task_id"), item.get("agent"), "queued")
        if key in existing:
            continue
        job = enqueue_job(
            task_id=item["task_id"],
            role=item.get("agent") or "backend",
            event=item.get("event") or "claim",
        )
        item["job_id"] = job["job_id"]
        n += 1
    save_runtime(rt)
    return n


def _lease_minutes() -> int:
    import os
    return int(os.environ.get("WORKER_LEASE_MINUTES", "45"))


def next_job(role: str | None = None) -> dict | None:
    sync_from_runtime_queue()
    data = load_jobs()
    now = _now()
    for job in data.get("jobs") or []:
        if job.get("status") != "queued":
            continue
        if role and job.get("role") != role:
            continue
        job["status"] = "leased"
        job["lease_until"] = _iso(now + timedelta(minutes=_lease_minutes()))
        set_agent_state(job["role"], "busy", job["task_id"])
        save_jobs(data)
        return job
    return None


def expire_leases() -> list[dict]:
    data = load_jobs()
    now = _now()
    expired = []
    for job in data.get("jobs") or []:
        if job.get("status") != "leased" or not job.get("lease_until"):
            continue
        until = datetime.fromisoformat(job["lease_until"])
        if until <= now:
            job["status"] = "queued"
            job["lease_until"] = None
            set_agent_state(job["role"], "idle", None)
            expired.append(job)
            rt = load_runtime()
            hq = rt.setdefault("hitl_queue", [])
            hq.append({
                "task_id": job["task_id"],
                "event": "busy_ttl",
                "hitl": {"reason": "Lease do worker expirou", "mode": "block_until_human"},
            })
            save_runtime(rt)
    save_jobs(data)
    return expired


def complete_job(job_id: str) -> dict:
    data = load_jobs()
    for job in data.get("jobs") or []:
        if job.get("job_id") == job_id:
            job["status"] = "done"
            job["done_at"] = _iso()
            set_agent_state(job["role"], "idle", None)
            save_jobs(data)
            return job
    return {"ok": False, "error": "job not found"}


def build_prompt_bundle(job: dict) -> Path:
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    role = job["role"]
    task_id = job["task_id"]
    agent_md = MODULE_ROOT / job.get("agent_prompt", f"agents/{role}.agent.md")
    handoff = load_handoff(task_id) or {}
    skill = MODULE_ROOT / "skills" / (role if not role.endswith("-reviewer") else role) / "SKILL.md"
    if role == "qa-author":
        skill = MODULE_ROOT / "skills" / "qa" / "SKILL.md"
    if role == "qa-gate":
        skill = MODULE_ROOT / "skills" / "qa" / "SKILL.md"

    parts = [
        f"# Worker bundle — `{role}` / `{task_id}`",
        f"job_id: `{job['job_id']}`",
        f"event: `{job.get('event')}`",
        f"ReAct max: {max_iterations_for(role)}",
        "",
        "## Instrucao",
        "Execute a task no workspace do repo alvo. Ao terminar:",
        "1. Abra PR (se implementacao) com template do modulo agents.",
        "2. Grave o contrato JSON em:",
        f"   `crew/output/dispatch_results/{job['job_id']}.json`",
        "3. Rode (a partir do modulo agents):",
        f"   `python scripts/complete_dispatch.py --job {job['job_id']}`",
        "",
        "### Contrato JSON (obrigatorio)",
        "```json",
        json.dumps({
            "job_id": job["job_id"],
            "task_id": task_id,
            "role": role,
            "result_event": "open_pr",
            "pr_url": "https://github.com/org/repo/pull/N",
            "react_trace": [
                {"thought": "...", "action": "...", "observation": "..."}
            ],
            "metrics": {},
            "summary": "1-2 frases",
        }, ensure_ascii=False, indent=2),
        "```",
        "",
        "Fallback manual (se Automation/SDK indisponivel):",
        f"`python scripts/worker_run.py --complete --job {job['job_id']}`",
        f"`python scripts/gateway_cli.py --task {task_id} --event <evento> ...`",
        "",
        "## Handoff",
        "```json",
        json.dumps(handoff, ensure_ascii=False, indent=2),
        "```",
        "",
    ]
    if agent_md.exists():
        parts += ["## Agent prompt", agent_md.read_text(encoding="utf-8"), ""]
    if skill.exists():
        parts += ["## Skill (trecho)", skill.read_text(encoding="utf-8")[:4000], ""]

    out = PROMPTS_DIR / f"{job['job_id']}.md"
    out.write_text("\n".join(parts), encoding="utf-8")
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--list", action="store_true")
    p.add_argument("--next", action="store_true")
    p.add_argument("--role", default=None)
    p.add_argument("--complete", action="store_true")
    p.add_argument("--job", default=None)
    p.add_argument("--expire", action="store_true")
    p.add_argument("--enqueue", action="store_true")
    p.add_argument("--task", default=None)
    p.add_argument("--event", default="claim")
    args = p.parse_args()

    if args.enqueue:
        if not args.task or not args.role:
            p.error("--enqueue requer --task e --role")
        job = enqueue_job(task_id=args.task, role=args.role, event=args.event)
        print(json.dumps(job, ensure_ascii=False, indent=2))
        return 0

    if args.list:
        sync_from_runtime_queue()
        data = load_jobs()
        print(json.dumps({
            "jobs": data.get("jobs"),
            "idle": list_idle_agents(),
        }, ensure_ascii=False, indent=2))
        return 0

    if args.expire:
        exp = expire_leases()
        print(json.dumps({"expired": exp}, ensure_ascii=False, indent=2))
        return 0

    if args.complete:
        if not args.job:
            p.error("--complete requer --job")
        print(json.dumps(complete_job(args.job), ensure_ascii=False, indent=2))
        return 0

    if args.next:
        job = next_job(args.role)
        if not job:
            print(json.dumps({"ok": False, "error": "fila vazia"}, ensure_ascii=False))
            return 1
        path = build_prompt_bundle(job)
        print(json.dumps({
            "ok": True,
            "job": job,
            "prompt_bundle": str(path),
            "hint": f"Abra {path} e cole no Cursor Agent",
        }, ensure_ascii=False, indent=2))
        return 0

    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
