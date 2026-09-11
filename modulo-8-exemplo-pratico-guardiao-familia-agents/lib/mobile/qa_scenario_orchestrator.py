"""Orquestrador multi-cenário: fan-out paralelo (local subprocess | docker) + gate all-pass."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from lib.mobile.qa_scenario_worker import read_status, write_status

WorkerMode = Literal["local", "docker"]

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = os.environ.get("GF_QA_SCENARIO_IMAGE", "guardiao-qa-scenario-worker:latest")


def resolve_worker_mode(worker_mode: str | None = None) -> WorkerMode:
    """Caminho explícito: local (host, sem container) | docker (1 container por cenário)."""
    raw = (worker_mode or os.environ.get("GF_QA_SCENARIO_WORKER") or "local").strip().lower()
    if raw in ("docker", "container", "containers"):
        return "docker"
    return "local"


@dataclass
class ScenarioJob:
    task_id: str
    scenario_id: str
    actuation_context_path: Path
    suites_mobile: dict[str, Any]
    feature: str
    timeout_sec: int
    evidence_host_dir: Path
    status_dir: Path
    container_name: str = ""
    ok: bool | None = None
    blocking_reason: str | None = None
    result: dict[str, Any] = field(default_factory=dict)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_scenarios(task: dict[str, Any]) -> list[str]:
    qa = task.get("qa") if isinstance(task.get("qa"), dict) else {}
    raw = list(qa.get("scenarios") or [])
    out = [str(s).strip() for s in raw if str(s).strip()]
    return out


def work_dirs(task_id: str, run_index: int = 1) -> dict[str, Path]:
    base = ROOT / "agents" / "00-runtime" / "output" / task_id / f"qa-gate-({run_index})"
    evidence = base / "evidence"
    status = base / "status"
    scenarios = base / "scenarios"
    for p in (evidence, status, scenarios):
        p.mkdir(parents=True, exist_ok=True)
    return {"base": base, "evidence": evidence, "status": status, "scenarios": scenarios}


def next_run_index(task_id: str) -> int:
    root = ROOT / "agents" / "00-runtime" / "output" / task_id
    if not root.is_dir():
        return 1
    n = 1
    for child in root.iterdir():
        if child.is_dir() and child.name.startswith("qa-gate-("):
            try:
                n = max(n, int(child.name.split("(")[1].rstrip(")")) + 1)
            except (IndexError, ValueError):
                continue
    return n


def build_jobs(
    *,
    task: dict[str, Any],
    actuation_context: dict[str, Any] | str,
    run_index: int | None = None,
) -> tuple[list[ScenarioJob], dict[str, Path], str | None]:
    from lib.mobile.mobile_task import mobile_setup_evidence_params, resolve_suites_mobile

    tid = str(task.get("id") or "").strip()
    scenarios = resolve_scenarios(task)
    if not scenarios:
        return [], {}, "NO_SCENARIOS"

    params = mobile_setup_evidence_params(task)
    suites = params.get("suites_mobile") or resolve_suites_mobile(task)
    feature = str(params.get("feature") or "")
    timeout_sec = int(os.environ.get("GF_TIMEOUT_SEC") or params.get("timeout_sec") or 900)
    idx = run_index if run_index is not None else next_run_index(tid)
    dirs = work_dirs(tid, idx)

    ctx_path = dirs["scenarios"] / "actuation_context.json"
    if isinstance(actuation_context, str):
        ctx_path.write_text(actuation_context, encoding="utf-8")
    else:
        ctx_path.write_text(json.dumps(actuation_context, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    jobs: list[ScenarioJob] = []
    for sid in scenarios:
        ev = dirs["evidence"] / sid
        ev.mkdir(parents=True, exist_ok=True)
        jobs.append(
            ScenarioJob(
                task_id=tid,
                scenario_id=sid,
                actuation_context_path=ctx_path,
                suites_mobile=dict(suites) if isinstance(suites, dict) else {"parent": False, "child": True},
                feature=feature,
                timeout_sec=timeout_sec,
                evidence_host_dir=ev,
                status_dir=dirs["status"],
                container_name=f"gf-qa-{tid}-{sid}".replace("/", "-")[:63],
            )
        )
    return jobs, dirs, None


def _kvm_available() -> bool:
    return Path("/dev/kvm").exists()


def _docker_available() -> bool:
    return shutil.which("docker") is not None


def _spawn_local(job: ScenarioJob, *, dry_run: bool) -> subprocess.Popen[Any]:
    env = os.environ.copy()
    env.update(
        {
            "GF_TASK_ID": job.task_id,
            "GF_SCENARIO_ID": job.scenario_id,
            "GF_ACTUATION_CONTEXT_PATH": str(job.actuation_context_path),
            "GF_STATUS_DIR": str(job.status_dir),
            "GF_SUITES_MOBILE_JSON": json.dumps(job.suites_mobile),
            "GF_FEATURE": job.feature,
            "GF_TIMEOUT_SEC": str(job.timeout_sec),
            "GF_DRY_RUN": "1" if dry_run else "0",
            "GF_SKIP_BUILD": "1",
            "PYTHONPATH": str(ROOT) + os.pathsep + env.get("PYTHONPATH", ""),
            "GF_APPIUM_EVIDENCE_DIR": str(job.evidence_host_dir),
        }
    )
    return subprocess.Popen(
        [sys_executable(), "-m", "lib.mobile.qa_scenario_worker"],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def sys_executable() -> str:
    import sys

    return sys.executable


def _docker_path(path: Path) -> str:
    """Path absoluto aceito pelo Docker Desktop (Windows → forward slashes)."""
    return str(path.resolve()).replace("\\", "/")


def _spawn_docker(job: ScenarioJob, *, dry_run: bool, image: str) -> subprocess.Popen[Any]:
    # Linux sem /dev/kvm → fail tipado; Windows/WSL2 confia no Docker Desktop
    if os.name != "nt" and not _kvm_available():
        raise RuntimeError("DOCKER_KVM_UNAVAILABLE")

    mounts = [
        "-v",
        f"{_docker_path(ROOT)}:/workspace:rw",
        "-v",
        f"{_docker_path(job.status_dir)}:/status:rw",
        "-v",
        f"{_docker_path(job.evidence_host_dir)}:/evidence:rw",
        "-v",
        f"{_docker_path(job.actuation_context_path.parent)}:/ctx:ro",
    ]
    env_flags = [
        "-e",
        f"GF_TASK_ID={job.task_id}",
        "-e",
        f"GF_SCENARIO_ID={job.scenario_id}",
        "-e",
        f"GF_ACTUATION_CONTEXT_PATH=/ctx/{job.actuation_context_path.name}",
        "-e",
        "GF_STATUS_DIR=/status",
        "-e",
        f"GF_SUITES_MOBILE_JSON={json.dumps(job.suites_mobile)}",
        "-e",
        f"GF_FEATURE={job.feature}",
        "-e",
        f"GF_TIMEOUT_SEC={job.timeout_sec}",
        "-e",
        f"GF_DRY_RUN={'1' if dry_run else '0'}",
        "-e",
        "GF_SKIP_BUILD=1",
        "-e",
        "GF_APPIUM_EVIDENCE_DIR=/evidence",
        "-e",
        "PYTHONPATH=/workspace",
    ]
    # nome docker: lowercase + safe
    safe_name = "".join(c if c.isalnum() or c in "-_" else "-" for c in job.container_name).lower()[:63]
    job.container_name = safe_name
    cmd = [
        "docker",
        "run",
        "--rm",
        "--name",
        safe_name,
        "--privileged",
        *mounts,
        *env_flags,
    ]
    if Path("/dev/kvm").exists():
        cmd.extend(["--device", "/dev/kvm"])
    cmd.append(image)

    return subprocess.Popen(
        cmd,
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _kill_job(job: ScenarioJob, proc: subprocess.Popen[Any] | None, mode: WorkerMode) -> None:
    if mode == "docker":
        try:
            subprocess.run(
                ["docker", "kill", job.container_name],
                capture_output=True,
                timeout=30,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass
    if proc and proc.poll() is None:
        try:
            proc.kill()
        except OSError:
            pass


def _wait_job(
    job: ScenarioJob,
    proc: subprocess.Popen[Any],
    *,
    mode: WorkerMode,
    poll_sec: float = 2.0,
) -> ScenarioJob:
    deadline = time.monotonic() + max(60, job.timeout_sec + 120)
    stdout_chunks: list[str] = []

    def _reader() -> None:
        try:
            if proc.stdout:
                for line in proc.stdout:
                    stdout_chunks.append(line)
        except Exception:  # noqa: BLE001
            return

    t = threading.Thread(target=_reader, daemon=True)
    t.start()

    while True:
        st = read_status(job.status_dir, job.scenario_id)
        if st and st.get("phase") == "done":
            job.ok = bool(st.get("ok"))
            job.blocking_reason = st.get("blocking_reason")
            job.result = st
            # deixa processo encerrar
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                _kill_job(job, proc, mode)
            return job

        if proc.poll() is not None:
            # processo saiu sem status done — sintetiza
            st = read_status(job.status_dir, job.scenario_id) or {}
            if st.get("phase") == "done":
                job.ok = bool(st.get("ok"))
                job.blocking_reason = st.get("blocking_reason")
                job.result = st
            else:
                rc = proc.returncode
                job.ok = rc == 0
                job.blocking_reason = None if job.ok else (st.get("blocking_reason") or f"WORKER_EXIT_{rc}")
                write_status(
                    job.status_dir,
                    job.scenario_id,
                    {
                        "scenario_id": job.scenario_id,
                        "task_id": job.task_id,
                        "phase": "done",
                        "ok": job.ok,
                        "blocking_reason": job.blocking_reason,
                        "evidence": st.get("evidence"),
                        "mcp_steps": st.get("mcp_steps") or [],
                        "finished_at": _utc_now(),
                        "stdout_tail": "".join(stdout_chunks)[-4000:],
                    },
                )
                job.result = read_status(job.status_dir, job.scenario_id) or {}
            return job

        if time.monotonic() > deadline:
            _kill_job(job, proc, mode)
            job.ok = False
            job.blocking_reason = "TIMEOUT"
            write_status(
                job.status_dir,
                job.scenario_id,
                {
                    "scenario_id": job.scenario_id,
                    "task_id": job.task_id,
                    "phase": "done",
                    "ok": False,
                    "blocking_reason": "TIMEOUT",
                    "evidence": None,
                    "mcp_steps": [],
                    "finished_at": _utc_now(),
                },
            )
            job.result = read_status(job.status_dir, job.scenario_id) or {}
            return job

        time.sleep(poll_sec)


def run_scenario_orchestrator(
    *,
    task: dict[str, Any],
    actuation_context: dict[str, Any] | str,
    dry_run: bool = False,
    worker_mode: WorkerMode | None = None,
    image: str | None = None,
    max_workers: int | None = None,
) -> dict[str, Any]:
    """Fan-out paralelo por cenário; PASS só se todos ok."""
    from lib.mobile.mobile_task import resolve_evidence_pipeline, wants_mobile_setup_evidence
    from lib.mobile.qa_mobile_setup_evidence import format_evidence_comment

    tid = str(task.get("id") or "")
    if not wants_mobile_setup_evidence(task):
        return {"ok": False, "skipped": True, "reason": "task sem QA mobile MCP"}

    evidence_pipeline = resolve_evidence_pipeline(task)
    mode: WorkerMode = resolve_worker_mode(worker_mode)
    img = image or DEFAULT_IMAGE

    jobs, dirs, err = build_jobs(task=task, actuation_context=actuation_context)
    if err:
        return {
            "ok": False,
            "task_id": tid,
            "mode": "mcp-qa-multi",
            "blocking_reason": err,
            "scenarios_results": [],
            "mcp_steps": [],
            "suite_ok": False,
            "evidence_ok": False,
            "evidence_pipeline": evidence_pipeline,
        }

    if dry_run:
        # Fan-out in-process (sem Docker/Appium) para validar status + all-pass
        from lib.mobile.qa_scenario_worker import run_worker

        def _dry_one(job: ScenarioJob) -> ScenarioJob:
            res = run_worker(
                task_id=job.task_id,
                scenario_id=job.scenario_id,
                actuation_context=job.actuation_context_path.read_text(encoding="utf-8"),
                suites_mobile=job.suites_mobile,
                status_dir=job.status_dir,
                feature=job.feature,
                timeout_sec=job.timeout_sec,
                dry_run=True,
            )
            job.ok = bool(res.get("ok"))
            job.blocking_reason = res.get("blocking_reason")
            job.result = read_status(job.status_dir, job.scenario_id) or {
                "phase": "done",
                "ok": job.ok,
                "scenario_id": job.scenario_id,
                "mcp_steps": res.get("mcp_steps") or [],
            }
            return job

        dry_workers = max(1, min(len(jobs), int(os.environ.get("GF_QA_SCENARIO_MAX_PARALLEL") or len(jobs))))
        finished_dry: list[ScenarioJob] = []
        with ThreadPoolExecutor(max_workers=dry_workers) as pool:
            for fut in as_completed({pool.submit(_dry_one, j): j for j in jobs}):
                finished_dry.append(fut.result())
        by_id = {j.scenario_id: j for j in finished_dry}
        ordered_dry = [by_id[j.scenario_id] for j in jobs if j.scenario_id in by_id]
        all_pass_dry = bool(ordered_dry) and all(bool(j.ok) for j in ordered_dry)
        return {
            "ok": all_pass_dry,
            "dry_run": True,
            "task_id": tid,
            "mode": "mcp-qa-multi",
            "worker_mode": "local-dry",
            "suites_mobile": jobs[0].suites_mobile if jobs else {},
            "scenarios": [j.scenario_id for j in jobs],
            "scenarios_count": len(jobs),
            "scenarios_results": [
                {
                    "scenario_id": j.scenario_id,
                    "ok": bool(j.ok),
                    "blocking_reason": j.blocking_reason,
                    "phase": (j.result or {}).get("phase"),
                }
                for j in ordered_dry
            ],
            "would_run": [
                {
                    "scenario_id": j.scenario_id,
                    "worker": mode,
                    "chain": ["qa_init_suite_mobile", "qa_pipeline_evidence", "qa_generate_evidence"],
                }
                for j in jobs
            ],
            "evidence_pipeline": evidence_pipeline,
            "work_dirs": {k: str(v) for k, v in dirs.items()},
            "suite_ok": all_pass_dry,
            "evidence_ok": all_pass_dry,
            "mcp_steps": [],
            "blocking_reason": None if all_pass_dry else "DRY_SCENARIO_FAIL",
        }

    if mode == "docker":
        if not _docker_available():
            return {
                "ok": False,
                "task_id": tid,
                "mode": "mcp-qa-multi",
                "blocking_reason": "DOCKER_UNAVAILABLE",
                "scenarios_results": [],
                "mcp_steps": [],
                "suite_ok": False,
                "evidence_ok": False,
                "evidence_pipeline": evidence_pipeline,
            }
        if os.name != "nt" and not _kvm_available():
            return {
                "ok": False,
                "task_id": tid,
                "mode": "mcp-qa-multi",
                "blocking_reason": "DOCKER_KVM_UNAVAILABLE",
                "scenarios_results": [],
                "mcp_steps": [],
                "suite_ok": False,
                "evidence_ok": False,
                "evidence_pipeline": evidence_pipeline,
            }

    workers = max_workers or int(os.environ.get("GF_QA_SCENARIO_MAX_PARALLEL") or len(jobs) or 1)
    workers = max(1, min(workers, len(jobs)))

    def _run_one(job: ScenarioJob) -> ScenarioJob:
        try:
            if mode == "docker":
                proc = _spawn_docker(job, dry_run=False, image=img)
            else:
                proc = _spawn_local(job, dry_run=False)
        except RuntimeError as exc:
            job.ok = False
            job.blocking_reason = str(exc)
            write_status(
                job.status_dir,
                job.scenario_id,
                {
                    "scenario_id": job.scenario_id,
                    "task_id": job.task_id,
                    "phase": "done",
                    "ok": False,
                    "blocking_reason": job.blocking_reason,
                    "finished_at": _utc_now(),
                },
            )
            job.result = read_status(job.status_dir, job.scenario_id) or {}
            return job
        return _wait_job(job, proc, mode=mode)

    finished: list[ScenarioJob] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(_run_one, j): j for j in jobs}
        for fut in as_completed(futs):
            finished.append(fut.result())

    # ordem estável = ordem do plano
    by_id = {j.scenario_id: j for j in finished}
    ordered = [by_id[j.scenario_id] for j in jobs if j.scenario_id in by_id]

    scenarios_results: list[dict[str, Any]] = []
    mcp_steps: list[dict[str, Any]] = []
    evidence_paths: list[str] = []
    fails: list[str] = []

    for j in ordered:
        st = j.result or read_status(j.status_dir, j.scenario_id) or {}
        ok = bool(j.ok)
        br = j.blocking_reason
        scenarios_results.append(
            {
                "scenario_id": j.scenario_id,
                "ok": ok,
                "blocking_reason": br,
                "phase": st.get("phase"),
                "evidence": st.get("evidence"),
                "evidence_paths": st.get("evidence_paths") or [],
                "package_dir": st.get("package_dir"),
                "mcp_steps": st.get("mcp_steps") or [],
                "timing_gap": st.get("timing_gap"),
            }
        )
        for step in st.get("mcp_steps") or []:
            step2 = dict(step) if isinstance(step, dict) else {"raw": step}
            step2.setdefault("scenario_id", j.scenario_id)
            mcp_steps.append(step2)
        for p in st.get("evidence_paths") or []:
            if p:
                evidence_paths.append(str(p))
        if st.get("package_dir"):
            evidence_paths.append(str(st["package_dir"]))
        if not ok:
            fails.append(f"{j.scenario_id}:{br or 'FAIL'}")

    all_pass = bool(ordered) and all(bool(j.ok) for j in ordered)
    blocking = None if all_pass else ("; ".join(fails) if fails else "SCENARIO_FAIL")
    # dedupe paths
    evidence_paths = list(dict.fromkeys(evidence_paths))

    comment = format_evidence_comment(
        {
            "task_id": tid,
            "ok": all_pass,
            "package_dir": str(dirs["evidence"]),
            "artifacts": {},
            "setup_root": "",
        }
    )
    return {
        "ok": all_pass,
        "task_id": tid,
        "mode": "mcp-qa-multi",
        "worker_mode": mode,
        "suites_mobile": jobs[0].suites_mobile if jobs else {},
        "suite_ok": all_pass,
        "evidence_ok": all_pass,
        "evidence_pipeline": evidence_pipeline,
        "scenarios": [j.scenario_id for j in jobs],
        "scenarios_count": len(jobs),
        "scenarios_results": scenarios_results,
        "mcp_steps": mcp_steps,
        "executed": ["qa_scenario_orchestrator"] + [s.get("tool") for s in mcp_steps if isinstance(s, dict)],
        "evidence_paths": evidence_paths,
        "package_dir": str(dirs["evidence"]),
        "work_dirs": {k: str(v) for k, v in dirs.items()},
        "comment": comment,
        "suite": {"ok": all_pass, "package_dir": str(dirs["evidence"])},
        "blocking_reason": blocking,
        "db_seed": None,
        "db_cleanup": None,
    }
