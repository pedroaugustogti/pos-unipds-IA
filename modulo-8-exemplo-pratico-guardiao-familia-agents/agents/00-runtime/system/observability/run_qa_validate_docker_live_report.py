"""Live Docker: qa_validate multi-cenário T-P3-009 + relatório dos 3 containers."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from lib.mobile.qa_scenario_orchestrator import run_scenario_orchestrator
from lib.orchestrator.phase_context import load_actuation, task_from_ctx


def _docker_ps_related(prefix: str = "gf-qa-") -> list[dict]:
    try:
        raw = subprocess.check_output(
            ["docker", "ps", "-a", "--format", "{{json .}}"],
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        return [{"error": str(exc)}]
    out = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        name = str(row.get("Names") or "")
        if prefix in name or "tp3-009" in name.lower() or "greeting" in name.lower():
            out.append(row)
    return out


def main() -> int:
    os.environ["GF_QA_SCENARIO_WORKER"] = "docker"
    os.environ.setdefault("GF_QA_SCENARIO_IMAGE", "guardiao-qa-scenario-worker:latest")
    os.environ.setdefault("GF_QA_SCENARIO_MAX_PARALLEL", "3")

    tid = "T-P3-009"
    ctx_path = (
        ROOT
        / "agents"
        / "00-runtime"
        / "system"
        / "observability"
        / "actuation_context_T-P3-009_qa_validate.json"
    )
    actuation = json.loads(ctx_path.read_text(encoding="utf-8"))
    task = task_from_ctx(load_actuation(actuation))

    report: dict = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "task_id": tid,
        "mode": "live",
        "worker_mode": "docker",
        "image": os.environ["GF_QA_SCENARIO_IMAGE"],
        "phases": [],
        "containers": [],
        "verdict": {},
    }

    # preflight imagem
    t0 = time.perf_counter()
    img_ok = False
    img_err = None
    try:
        insp = subprocess.run(
            ["docker", "image", "inspect", os.environ["GF_QA_SCENARIO_IMAGE"]],
            capture_output=True,
            text=True,
            timeout=60,
        )
        img_ok = insp.returncode == 0
        if not img_ok:
            img_err = (insp.stderr or insp.stdout or "image missing")[:500]
    except Exception as exc:  # noqa: BLE001
        img_err = str(exc)
    report["phases"].append(
        {
            "phase": "docker_image_preflight",
            "ok": img_ok,
            "elapsed_sec": round(time.perf_counter() - t0, 3),
            "error": img_err,
        }
    )
    if not img_ok:
        report["verdict"] = {
            "overall": "FAIL",
            "reason": "IMAGE_MISSING",
            "hint": "docker build -t guardiao-qa-scenario-worker:latest -f docker/qa-scenario-worker/Dockerfile .",
        }
        out = (
            ROOT
            / "agents"
            / "00-runtime"
            / "system"
            / "observability"
            / "qa_validate_docker_live_report_T-P3-009.json"
        )
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        print(json.dumps({"report_path": str(out), "verdict": report["verdict"]}, indent=2))
        return 2

    t1 = time.perf_counter()
    orch = run_scenario_orchestrator(
        task=task,
        actuation_context=actuation,
        dry_run=False,
        worker_mode="docker",
        image=os.environ["GF_QA_SCENARIO_IMAGE"],
        max_workers=3,
    )
    elapsed = round(time.perf_counter() - t1, 3)

    status_dir = Path(str((orch.get("work_dirs") or {}).get("status") or ""))
    containers_report = []
    for sc in orch.get("scenarios_results") or []:
        sid = str(sc.get("scenario_id") or "")
        st_path = status_dir / f"{sid}.json" if status_dir else None
        status = {}
        if st_path and st_path.is_file():
            try:
                status = json.loads(st_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                status = {"parse_error": True}
        cname = f"gf-qa-{tid}-{sid}".replace("/", "-")
        cname = "".join(c if c.isalnum() or c in "-_" else "-" for c in cname).lower()[:63]
        containers_report.append(
            {
                "scenario_id": sid,
                "container_name": cname,
                "ok": bool(sc.get("ok")),
                "blocking_reason": sc.get("blocking_reason"),
                "phase": status.get("phase") or sc.get("phase"),
                "mcp_steps": status.get("mcp_steps") or sc.get("mcp_steps") or [],
                "evidence": status.get("evidence") or sc.get("evidence"),
                "evidence_paths": status.get("evidence_paths") or sc.get("evidence_paths") or [],
                "finished_at": status.get("finished_at"),
                "stdout_tail": (status.get("stdout_tail") or "")[-2000:],
            }
        )

    report["phases"].append(
        {
            "phase": "qa_validate_orchestrator_docker_live",
            "ok": bool(orch.get("ok")),
            "elapsed_sec": elapsed,
            "blocking_reason": orch.get("blocking_reason"),
            "scenarios_count": orch.get("scenarios_count"),
            "work_dirs": orch.get("work_dirs"),
        }
    )
    report["containers"] = containers_report
    report["docker_ps_snapshot"] = _docker_ps_related()
    report["orchestrator"] = {
        "ok": orch.get("ok"),
        "blocking_reason": orch.get("blocking_reason"),
        "scenarios": orch.get("scenarios"),
        "scenarios_results": orch.get("scenarios_results"),
        "evidence_paths": orch.get("evidence_paths"),
        "mcp_steps_count": len(orch.get("mcp_steps") or []),
    }

    all_ok = bool(orch.get("ok")) and len(containers_report) == 3 and all(c["ok"] for c in containers_report)
    report["verdict"] = {
        "overall": "PASS" if all_ok else "FAIL",
        "containers_ok": sum(1 for c in containers_report if c["ok"]),
        "containers_total": len(containers_report),
        "gate": "all_pass_required",
        "blocking_reason": orch.get("blocking_reason"),
    }

    out = (
        ROOT
        / "agents"
        / "00-runtime"
        / "system"
        / "observability"
        / "qa_validate_docker_live_report_T-P3-009.json"
    )
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"report_path": str(out), "verdict": report["verdict"], "containers": [
        {"scenario_id": c["scenario_id"], "ok": c["ok"], "blocking_reason": c["blocking_reason"], "container_name": c["container_name"]}
        for c in containers_report
    ]}, indent=2, ensure_ascii=False))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
