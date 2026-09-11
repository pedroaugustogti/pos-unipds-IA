"""Executa qa_validate via plano MCP (on_status_event → qa_validate live)."""

from __future__ import annotations

import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from lib.mcp_invoke import on_status_event, qa_validate as mcp_qa_validate, unwrap_result


def _steps_summary(qa_result: dict) -> list[dict]:
    out = []
    for s in qa_result.get("mcp_steps") or []:
        out.append(
            {
                "tool": s.get("tool"),
                "ok": s.get("ok"),
                "apps_ready_ok": s.get("apps_ready_ok"),
                "scenario_id": s.get("scenario_id"),
                "blocking_reason": s.get("blocking_reason"),
            }
        )
    return out


def main() -> int:
    tid = "T-P3-009"
    scenario = "greeting-morning-08h"

    report: dict = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "task_id": tid,
        "scenario_focus": scenario,
        "orchestration": (
            "MCP on_status_event → qa_validate → "
            "qa_init_suite_mobile → qa_pipeline_evidence → qa_generate_evidence"
        ),
        "entry": "lib.mcp_invoke.on_status_event + qa_validate(mode=live)",
        "phases": [],
        "verdict": {},
    }

    # 1) Plano MCP oficial
    t0 = time.perf_counter()
    ose_err = None
    ose_raw = None
    try:
        ose_raw = on_status_event(
            task_id=tid,
            event="qa-gate_in_test",
        )
    except Exception as exc:  # noqa: BLE001
        ose_err = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()

    ose = unwrap_result(ose_raw if isinstance(ose_raw, dict) else {})
    # actuation_context pode vir como o próprio result ou nested
    actuation = ose
    if isinstance(ose.get("actuation_context"), (dict, str)):
        actuation = ose["actuation_context"]
    ticket = {}
    if isinstance(actuation, dict):
        ticket = actuation.get("ticket") if isinstance(actuation.get("ticket"), dict) else {}
    elif isinstance(ose.get("ticket"), dict):
        ticket = ose["ticket"]
        actuation = ose

    report["phases"].append(
        {
            "phase": "mcp_on_status_event",
            "ok": bool(ose_raw and ose_raw.get("ok")) and bool(ticket.get("qa") or (isinstance(actuation, dict) and actuation.get("task_id"))),
            "elapsed_sec": round(time.perf_counter() - t0, 3),
            "error": ose_err or (None if (ose_raw or {}).get("ok") else (ose_raw or {}).get("error")),
            "has_ticket_qa": bool(ticket.get("qa")),
            "qa_scenarios": list((ticket.get("qa") or {}).get("scenarios") or []),
            "task_id": (actuation.get("task_id") if isinstance(actuation, dict) else tid),
        }
    )

    if not isinstance(actuation, dict) or not actuation.get("task_id"):
        report["verdict"] = {
            "orchestration_contract_ok": False,
            "live_execution_ok": False,
            "mcp_chain_complete": False,
            "overall": "FAIL",
            "notes": ["on_status_event nao produziu actuation_context"],
        }
        out_path = Path(__file__).resolve().parent / "qa_validate_orchestration_report_T-P3-009.json"
        out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        print(json.dumps({"report_path": str(out_path), "verdict": report["verdict"]}, indent=2))
        return 1

    # 2) qa_validate live — só consome actuation_context
    t0 = time.perf_counter()
    mcp_raw = None
    mcp_err = None
    try:
        mcp_raw = mcp_qa_validate(actuation, mode="live")
    except Exception as exc:  # noqa: BLE001
        mcp_err = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()

    envelope_ok = bool(mcp_raw and mcp_raw.get("ok"))
    result = unwrap_result(mcp_raw if isinstance(mcp_raw, dict) else {})
    qa_result = result.get("qa_result") if isinstance(result.get("qa_result"), dict) else result
    if not isinstance(qa_result, dict):
        qa_result = {}

    pipe = qa_result.get("pipeline") if isinstance(qa_result.get("pipeline"), dict) else {}
    sp = pipe.get("scenario_pipeline") if isinstance(pipe.get("scenario_pipeline"), dict) else {}
    evidence = qa_result.get("evidence") if isinstance(qa_result.get("evidence"), dict) else {}

    report["phases"].append(
        {
            "phase": "mcp_qa_validate_live",
            "ok": envelope_ok and bool(qa_result.get("ok")),
            "elapsed_sec": round(time.perf_counter() - t0, 3),
            "error": mcp_err or result.get("error"),
            "entry_tool": "qa_validate",
            "mode": "live",
            "decision": result.get("decision"),
            "blocking_reason": qa_result.get("blocking_reason"),
            "executed": qa_result.get("executed"),
            "suite_ok": qa_result.get("suite_ok"),
            "evidence_ok": qa_result.get("evidence_ok"),
            "mcp_steps": _steps_summary(qa_result) or _steps_summary(result),
            "package_dir": qa_result.get("package_dir") or result.get("package_dir"),
            "evidence_paths": qa_result.get("evidence_paths") or result.get("evidence_paths") or [],
            "ac_validation": result.get("ac_validation"),
            "scenario_id": pipe.get("scenario_id") or evidence.get("scenario_id") or scenario,
            "pipeline_binding": (sp.get("binding") or {}),
            "pipeline_steps_count": len(sp.get("steps") or []),
            "has_ticket_qa_in_pipeline": bool(sp.get("ticket_qa")),
        }
    )

    live = report["phases"][1]
    steps = live.get("mcp_steps") or []
    chain_tools = [s.get("tool") for s in steps]
    expected = ["qa_init_suite_mobile", "qa_pipeline_evidence", "qa_generate_evidence"]
    chain_complete = all(t in chain_tools for t in expected)
    orch_ok = bool(report["phases"][0].get("ok")) and chain_complete
    exec_ok = bool(live.get("ok"))
    notes: list[str] = []
    if not chain_complete:
        notes.append(f"cadeia MCP incompleta: executed={live.get('executed') or chain_tools}")
    if live.get("blocking_reason"):
        notes.append(f"blocking_reason: {live.get('blocking_reason')}")
    if mcp_err:
        notes.append(f"mcp error: {mcp_err}")
    if orch_ok and exec_ok:
        notes.append("Cadeia MCP completa a partir de on_status_event.")
    report["verdict"] = {
        "orchestration_contract_ok": orch_ok,
        "live_execution_ok": exec_ok,
        "mcp_chain_complete": chain_complete,
        "overall": "PASS" if (orch_ok and exec_ok) else ("PARTIAL" if orch_ok else "FAIL"),
        "notes": notes,
    }

    out_path = Path(__file__).resolve().parent / "qa_validate_orchestration_report_T-P3-009.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(
        json.dumps(
            {
                "report_path": str(out_path),
                "verdict": report["verdict"],
                "phases": [
                    {
                        "phase": p.get("phase"),
                        "ok": p.get("ok"),
                        "elapsed_sec": p.get("elapsed_sec"),
                        "blocking_reason": p.get("blocking_reason"),
                        "error": p.get("error"),
                        "mcp_steps": p.get("mcp_steps"),
                        "executed": p.get("executed"),
                        "has_ticket_qa": p.get("has_ticket_qa") or p.get("has_ticket_qa_in_pipeline"),
                    }
                    for p in report["phases"]
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0 if orch_ok and exec_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
