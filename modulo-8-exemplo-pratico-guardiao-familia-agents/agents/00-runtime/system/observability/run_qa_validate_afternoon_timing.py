"""Live local: evidência greeting-afternoon-15h (Boa tarde) + relatório de timing."""

from __future__ import annotations

import json
import sys
import time
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from lib.mobile.qa_timing_report import build_timing_report
from lib.orchestrator.phase_qa_validate import run_qa_validate


SCENARIO = "greeting-afternoon-15h"


def main() -> int:
    ctx_path = (
        ROOT
        / "agents"
        / "00-runtime"
        / "system"
        / "observability"
        / "actuation_context_T-P3-009_qa_validate.json"
    )
    actuation = json.loads(ctx_path.read_text(encoding="utf-8"))
    # isola só Boa tarde
    ticket = actuation.get("ticket") if isinstance(actuation.get("ticket"), dict) else actuation
    qa = ticket.get("qa") if isinstance(ticket.get("qa"), dict) else {}
    qa = deepcopy(qa)
    qa["scenarios"] = [SCENARIO]
    if isinstance(qa.get("evidence"), dict):
        qa["evidence"]["scenarios_count"] = 1
    if "ticket" in actuation and isinstance(actuation["ticket"], dict):
        actuation = deepcopy(actuation)
        actuation["ticket"]["qa"] = qa
    else:
        actuation = deepcopy(actuation)
        actuation["qa"] = qa

    t0 = time.perf_counter()
    result = run_qa_validate(actuation, mode="live", worker_mode="local")
    elapsed = round(time.perf_counter() - t0, 3)
    qa_result = result.get("qa_result") if isinstance(result.get("qa_result"), dict) else {}

    # anexar init do status do worker se existir
    work = qa_result.get("work_dirs") or {}
    status_dir = Path(str(work.get("status") or ""))
    status = {}
    if status_dir.is_dir():
        sp = status_dir / f"{SCENARIO}.json"
        if sp.is_file():
            try:
                status = json.loads(sp.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                status = {}

    # init pode estar só no mcp step — buscar checks no orchestrator package
    # Worker chain returns init in status? Currently status has mcp_steps only.
    # Re-read scenario chain from evidence package if needed.
    for step in status.get("mcp_steps") or qa_result.get("mcp_steps") or []:
        if isinstance(step, dict) and step.get("tool") == "qa_init_suite_mobile":
            if not qa_result.get("init"):
                qa_result["init"] = {
                    "ok": step.get("ok"),
                    "checks_child": step.get("checks_child"),
                    "checks_parent": step.get("checks_parent"),
                    "timeline": step.get("timeline"),
                    "blocking_reason": step.get("blocking_reason"),
                    "appium_mode": step.get("appium_mode"),
                }
    if isinstance(status.get("init"), dict) and not qa_result.get("init"):
        qa_result["init"] = status["init"]

    timing = build_timing_report(scenario_id=SCENARIO, qa_result=qa_result)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "task_id": "T-P3-009",
        "scenario_id": SCENARIO,
        "label": "Boa tarde",
        "mode": "live",
        "worker_mode": "local",
        "wall_elapsed_sec": elapsed,
        "qa_validate_ok": bool(result.get("ok")),
        "blocking_reason": qa_result.get("blocking_reason"),
        "evidence_paths": result.get("evidence_paths") or qa_result.get("evidence_paths") or [],
        "timing": timing,
        "decision_summary": timing.get("decision_summary"),
        "acceleration_insights": timing.get("acceleration_insights"),
    }

    out = (
        ROOT
        / "agents"
        / "00-runtime"
        / "system"
        / "observability"
        / "qa_validate_afternoon_timing_report_T-P3-009.json"
    )
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    # markdown curto para leitura humana
    md = out.with_suffix(".md")
    lines = [
        f"# Timing — {SCENARIO} (Boa tarde)",
        "",
        f"- **ok:** {report['qa_validate_ok']}",
        f"- **worker_mode:** local",
        f"- **wall_elapsed_sec:** {elapsed}",
        f"- **blocking_reason:** {report.get('blocking_reason')}",
        "",
        "## Boot init (suite)",
        f"- total_sec: {timing.get('boot_init', {}).get('total_sec')}",
    ]
    for c in (timing.get("boot_init") or {}).get("top_slow") or []:
        lines.append(f"- `{c['check']}`: {c['duration_sec']}s (ok={c['ok']})")
    lines += ["", "## Boot runtime (Appium session)"]
    for p in (timing.get("boot_runtime") or {}).get("phases") or []:
        lines.append(f"- `{p['phase']}`: {p['duration_sec']}s")
    lines += ["", "## Views / steps (mais lentos)"]
    for s in (timing.get("pipeline_views") or {}).get("top_slow_steps") or []:
        lines.append(
            f"- `{s.get('step_id')}` view=`{s.get('view') or s.get('view_testid')}` "
            f"action={s.get('action')} **{s['duration_sec']}s**"
            + (" (skipped)" if s.get("skipped") else "")
        )
    lines += ["", "## Ações prioritárias"]
    for i, rec in enumerate((timing.get("decision_summary") or {}).get("priority_actions") or [], 1):
        lines.append(f"{i}. {rec}")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "report_json": str(out),
        "report_md": str(md),
        "ok": report["qa_validate_ok"],
        "wall_elapsed_sec": elapsed,
        "decision_summary": report["decision_summary"],
    }
    out_summary = out.with_name(out.stem + "_summary.json")
    out_summary.write_text(json.dumps(summary, ensure_ascii=True, indent=2, default=str), encoding="utf-8")
    # stdout ASCII-safe no Windows console
    print(json.dumps(summary, ensure_ascii=True, indent=2, default=str))
    return 0 if report["qa_validate_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
