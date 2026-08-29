"""Adapter de disparo de jobs — manual_fallback | cursor_automation (Cursor SDK)."""

from __future__ import annotations

import importlib.util
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from lib.orchestrator.event_orchestrator import set_agent_state
from lib.observability.observability import log_workflow_event
from lib.paths import MODULE_ROOT
from lib.core.repo_paths import github_repo_url, resolve_repo_path
from board_automation.board.task_router import load_tasks
from lib.orchestrator.worker_jobs import load_jobs, save_jobs

from lib.paths import DISPATCH_RESULTS_DIR

RESULTS_DIR = DISPATCH_RESULTS_DIR

# auto | manual_fallback | cursor_automation
DEFAULT_BACKEND = os.environ.get("GUARDAO_DISPATCH_BACKEND", "auto")
# local | cloud
CURSOR_RUNTIME = os.environ.get("GUARDAO_CURSOR_RUNTIME", "local")
CURSOR_MODEL = (
    os.environ.get("GUARDIAO_CURSOR_MODEL")
    or os.environ.get("GUARDAO_CURSOR_MODEL")
    or "composer-2.5"
)
# 1 = Agent.prompt e espera; 0 = só lease+bundle
DISPATCH_WAIT = os.environ.get("GUARDAO_DISPATCH_WAIT", "1").strip() not in ("0", "false", "False")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).isoformat()


def _lease_minutes() -> int:
    return int(os.environ.get("WORKER_LEASE_MINUTES", "45"))


def cursor_sdk_status() -> dict[str, Any]:
    """Disponibilidade do backend cursor_automation (sem expor o valor da chave)."""
    key_set = bool((os.environ.get("CURSOR_API_KEY") or "").strip())
    sdk = importlib.util.find_spec("cursor_sdk") is not None
    ok = key_set and sdk
    reasons = []
    if not key_set:
        reasons.append("CURSOR_API_KEY ausente")
    if not sdk:
        reasons.append("pacote cursor-sdk nao instalado (pip install cursor-sdk)")
    return {"ok": ok, "api_key_configured": key_set, "sdk_installed": sdk, "reasons": reasons}


def resolve_backend(requested: str | None = None) -> str:
    be = (requested or DEFAULT_BACKEND or "auto").strip().lower()
    if be == "auto":
        return "cursor_automation" if cursor_sdk_status()["ok"] else "manual_fallback"
    if be in ("manual_fallback", "cursor_automation"):
        return be
    return "manual_fallback"


def _task_repo(task_id: str) -> str | None:
    for t in load_tasks():
        if t["id"] == task_id:
            return t.get("repo")
    return None


def lease_job(job_id: str) -> dict[str, Any] | None:
    data = load_jobs()
    now = _now()
    for job in data.get("jobs") or []:
        if job.get("job_id") != job_id:
            continue
        if job.get("status") not in ("queued", "leased"):
            return None
        job["status"] = "leased"
        job["lease_until"] = _iso(now + timedelta(minutes=_lease_minutes()))
        set_agent_state(job["role"], "busy", job["task_id"])
        save_jobs(data)
        return job
    return None


def _mark_dispatch(job_id: str, meta: dict[str, Any]) -> None:
    data = load_jobs()
    for job in data.get("jobs") or []:
        if job.get("job_id") == job_id:
            job["dispatch"] = {**(job.get("dispatch") or {}), **meta, "at": _iso()}
            save_jobs(data)
            return


def _load_worker_mod():
    path = __import__("lib.paths", fromlist=["orch_script"]).orch_script("worker", "worker_run.py")
    spec = importlib.util.spec_from_file_location("guardiao_worker_run", path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _build_bundle(job: dict[str, Any]) -> Path:
    return _load_worker_mod().build_prompt_bundle(job)


def _run_cursor_agent(*, prompt: str, repo: str) -> dict[str, Any]:
    from cursor_sdk import Agent, AgentOptions

    api_key = (os.environ.get("CURSOR_API_KEY") or "").strip()
    runtime = CURSOR_RUNTIME.strip().lower()
    opts_kwargs: dict[str, Any] = {
        "api_key": api_key,
        "model": CURSOR_MODEL,
    }

    if runtime == "cloud":
        try:
            from cursor_sdk import CloudAgentOptions
        except ImportError:
            return {"ok": False, "error": "CloudAgentOptions indisponivel nesta versao do SDK"}
        cloud_kw: dict[str, Any] = {
            "url": github_repo_url(repo),
            "auto_create_pr": True,
        }
        try:
            opts_kwargs["cloud"] = CloudAgentOptions(**cloud_kw)
        except TypeError:
            cloud_kw.pop("auto_create_pr", None)
            try:
                opts_kwargs["cloud"] = CloudAgentOptions(**cloud_kw)
            except TypeError:
                # algumas versoes usam `repository` / `github_url`
                opts_kwargs["cloud"] = CloudAgentOptions(repository=github_repo_url(repo))
    else:
        cwd = resolve_repo_path(repo)
        if not cwd or not Path(cwd).exists():
            return {
                "ok": False,
                "error": (
                    f"Repo local nao encontrado para `{repo}`. "
                    "Defina GUARDAO_*_PATH (ver lib/repo_paths.py)."
                ),
            }
        from cursor_sdk import LocalAgentOptions

        opts_kwargs["local"] = LocalAgentOptions(cwd=str(cwd))

    try:
        result = Agent.prompt(prompt, AgentOptions(**opts_kwargs))
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"Agent.prompt falhou: {exc}", "retryable": True}

    status = getattr(result, "status", None)
    if status is None and isinstance(result, dict):
        status = result.get("status")
    text = getattr(result, "result", None)
    if text is None and isinstance(result, dict):
        text = result.get("result")
    agent_id = getattr(result, "agent_id", None) or getattr(result, "agentId", None)
    run_id = getattr(result, "id", None) or getattr(result, "run_id", None)

    finished = str(status or "").lower() in ("finished", "ok", "completed", "success", "")
    return {
        "ok": finished and not (str(status or "").lower() == "error"),
        "status": status,
        "result_text": (str(text) if text is not None else "")[:4000],
        "agent_id": agent_id,
        "run_id": run_id,
        "runtime": runtime,
        "repo": repo,
    }


def dispatch_job(
    job: dict[str, Any],
    *,
    dry_run: bool = False,
    backend: str | None = None,
    lease: bool = True,
) -> dict[str, Any]:
    """
    Despacha um job queued/leased.

    - manual_fallback: gera bundle (worker_run)
    - cursor_automation: Cursor SDK Agent.prompt no workspace do repo
    """
    be = resolve_backend(backend)
    base: dict[str, Any] = {
        "ok": True,
        "backend": be,
        "job_id": job.get("job_id"),
        "task_id": job.get("task_id"),
        "role": job.get("role"),
        "dry_run": dry_run,
    }

    if dry_run:
        st = cursor_sdk_status() if be == "cursor_automation" else {"ok": True}
        return {
            **base,
            "action": "would_dispatch",
            "cursor_sdk": st if be == "cursor_automation" else None,
            "resolved_backend": be,
            "message": f"dry-run: usaria backend `{be}`",
        }

    job_id = job["job_id"]
    if lease and job.get("status") == "queued":
        leased = lease_job(job_id)
        if not leased:
            return {**base, "ok": False, "error": "falha ao leasear job"}
        job = leased

    try:
        bundle = _build_bundle(job)
    except Exception as exc:  # noqa: BLE001
        return {**base, "ok": False, "error": f"bundle: {exc}"}

    base["prompt_bundle"] = str(bundle)
    repo = _task_repo(job["task_id"]) or ""
    base["repo"] = repo

    if be == "manual_fallback":
        _mark_dispatch(job_id, {
            "backend": be,
            "action": "bundle_ready",
            "prompt_bundle": str(bundle),
            "repo": repo,
        })
        log_workflow_event(
            "dispatch",
            task_id=job.get("task_id"),
            agent=job.get("role"),
            event=job.get("event"),
            dispatch_action="manual_fallback",
            summary=f"bundle pronto: {bundle.name}",
            extra={"job_id": job_id, "repo": repo},
        )
        return {
            **base,
            "action": "bundle_ready",
            "message": "Abra o bundle no Cursor Agent; ao terminar use complete_dispatch.py",
        }

    st = cursor_sdk_status()
    if not st["ok"]:
        fb = dispatch_job(job, dry_run=False, backend="manual_fallback", lease=False)
        fb["fallback_from"] = "cursor_automation"
        fb["fallback_reasons"] = st["reasons"]
        return fb

    if not DISPATCH_WAIT:
        _mark_dispatch(job_id, {
            "backend": be,
            "action": "bundle_ready_no_wait",
            "prompt_bundle": str(bundle),
            "repo": repo,
        })
        return {
            **base,
            "action": "bundle_ready_no_wait",
            "message": "GUARDAO_DISPATCH_WAIT=0 — bundle gerado sem Agent.prompt",
        }

    prompt = bundle.read_text(encoding="utf-8")
    run = _run_cursor_agent(prompt=prompt, repo=repo)
    _mark_dispatch(job_id, {
        "backend": be,
        "action": "cursor_prompt",
        "prompt_bundle": str(bundle),
        "repo": repo,
        "cursor": {k: run.get(k) for k in ("status", "agent_id", "run_id", "runtime", "error")},
    })
    log_workflow_event(
        "dispatch",
        task_id=job.get("task_id"),
        agent=job.get("role"),
        event=job.get("event"),
        dispatch_action="cursor_automation",
        summary="Agent.prompt concluido" if run.get("ok") else f"Agent.prompt falhou: {run.get('error')}",
        extra={"job_id": job_id, "cursor": {k: run.get(k) for k in ("status", "agent_id", "run_id", "error")}},
    )

    if not run.get("ok"):
        return {**base, "ok": False, "action": "cursor_failed", "cursor": run, "error": run.get("error")}

    result_path = RESULTS_DIR / f"{job_id}.json"
    completion = None
    if result_path.exists():
        from lib.orchestrator.complete_dispatch import apply_dispatch_result

        completion = apply_dispatch_result(result_path, dry_run=False)

    return {
        **base,
        "ok": True,
        "action": "cursor_finished",
        "cursor": run,
        "completion": completion,
        "result_path": str(result_path) if result_path.exists() else None,
        "hint": (
            None
            if completion and completion.get("ok")
            else (
                f"Grave o contrato em {result_path} e rode "
                f"python agents/00-orchestration/scripts/worker/complete_dispatch.py --job {job_id}"
            )
        ),
    }


def drain_queued(
    *,
    dry_run: bool = False,
    limit: int = 20,
    backend: str | None = None,
) -> list[dict[str, Any]]:
    """Lease + dispatch dos jobs queued (até `limit`)."""
    try:
        _load_worker_mod().sync_from_runtime_queue()
    except Exception:  # noqa: BLE001
        pass

    data = load_jobs()
    results: list[dict[str, Any]] = []
    queued = [j for j in (data.get("jobs") or []) if j.get("status") == "queued"]
    for job in queued[:limit]:
        results.append(dispatch_job(job, dry_run=dry_run, backend=backend, lease=not dry_run))
    return results
