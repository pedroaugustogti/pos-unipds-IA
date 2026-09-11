"""Smoke: qa_validate multi-cenário T-P3-009 (dry_run fan-out + relatório agregado)."""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from lib.mobile.qa_scenario_orchestrator import run_scenario_orchestrator
from lib.orchestrator.phase_context import load_actuation, task_from_ctx
from lib.orchestrator.phase_qa_validate import run_qa_validate


def main() -> int:
    tid = "T-P3-009"
    ctx_path = (
        ROOT
        / "agents"
        / "00-runtime"
        / "system"
        / "observability"
        / "actuation_context_T-P3-009_qa_validate.json"
    )
    if not ctx_path.is_file():
        print(json.dumps({"ok": False, "error": f"missing {ctx_path}"}))
        return 2

    actuation = json.loads(ctx_path.read_text(encoding="utf-8"))
    task = task_from_ctx(load_actuation(actuation))

    report: dict = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "task_id": tid,
        "entry": "run_qa_validate(mode=dry_run) + orchestrator fan-out",
        "phases": [],
        "verdict": {},
    }

    t0 = time.perf_counter()
    orch = run_scenario_orchestrator(
        task=task,
        actuation_context=actuation,
        dry_run=True,
        worker_mode="local",
    )
    report["phases"].append(
        {
            "phase": "orchestrator_dry_fanout",
            "ok": bool(orch.get("ok")),
            "elapsed_sec": round(time.perf_counter() - t0, 3),
            "scenarios": orch.get("scenarios"),
            "scenarios_count": orch.get("scenarios_count"),
            "scenarios_results": orch.get("scenarios_results"),
            "worker_mode": orch.get("worker_mode"),
            "blocking_reason": orch.get("blocking_reason"),
            "work_dirs": orch.get("work_dirs"),
        }
    )

    t1 = time.perf_counter()
    qa = run_qa_validate(actuation, mode="dry_run")
    qa_result = qa.get("qa_result") if isinstance(qa.get("qa_result"), dict) else {}
    report["phases"].append(
        {
            "phase": "qa_validate_dry_run",
            "ok": bool(qa.get("ok")),
            "elapsed_sec": round(time.perf_counter() - t1, 3),
            "scenarios_count": qa_result.get("scenarios_count"),
            "scenarios": qa_result.get("scenarios"),
            "decision": (qa.get("decision") or {}).get("next_event"),
            "ac_all_passed": (qa.get("ac_validation") or {}).get("all_passed"),
        }
    )

    expected = ["greeting-morning-08h", "greeting-afternoon-15h", "greeting-evening-21h"]
    got = list(orch.get("scenarios") or [])
    fanout_ok = got == expected and bool(orch.get("ok")) and int(orch.get("scenarios_count") or 0) == 3
    status_dir = Path(str((orch.get("work_dirs") or {}).get("status") or ""))
    status_files = list(status_dir.glob("*.json")) if status_dir.is_dir() else []
    all_done = all(
        json.loads(p.read_text(encoding="utf-8")).get("phase") == "done" for p in status_files
    ) if status_files else False

    report["verdict"] = {
        "orchestration_contract_ok": fanout_ok and all_done and len(status_files) == 3,
        "scenarios_expected": expected,
        "scenarios_got": got,
        "status_files": [p.name for p in status_files],
        "qa_validate_ok": bool(qa.get("ok")),
        "overall": "PASS" if (fanout_ok and all_done and qa.get("ok")) else "FAIL",
    }

    out = (
        ROOT
        / "agents"
        / "00-runtime"
        / "system"
        / "observability"
        / "qa_validate_multi_scenario_report_T-P3-009.json"
    )
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"report_path": str(out), "verdict": report["verdict"]}, ensure_ascii=False, indent=2))
    return 0 if report["verdict"]["overall"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
