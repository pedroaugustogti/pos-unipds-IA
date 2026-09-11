"""Live local: greeting-evening-21h + timing até evidência."""

from __future__ import annotations

import json
import sys
import time
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from lib.orchestrator.phase_qa_validate import run_qa_validate

SCENARIO = "greeting-evening-21h"


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
    ticket = actuation.get("ticket") if isinstance(actuation.get("ticket"), dict) else actuation
    qa = deepcopy(ticket.get("qa") if isinstance(ticket.get("qa"), dict) else {})
    qa["scenarios"] = [SCENARIO]
    if isinstance(qa.get("evidence"), dict):
        qa["evidence"]["scenarios_count"] = 1
    actuation = deepcopy(actuation)
    if "ticket" in actuation and isinstance(actuation["ticket"], dict):
        actuation["ticket"]["qa"] = qa
    else:
        actuation["qa"] = qa

    t0 = time.perf_counter()
    result = run_qa_validate(actuation, mode="live", worker_mode="local")
    elapsed = round(time.perf_counter() - t0, 3)
    qa_result = result.get("qa_result") if isinstance(result.get("qa_result"), dict) else {}
    sr = (qa_result.get("scenarios_results") or [{}])[0]
    steps = sr.get("mcp_steps") or qa_result.get("mcp_steps") or []
    init = next((s for s in steps if s.get("tool") == "qa_init_suite_mobile"), {}) or {}
    pipe = next((s for s in steps if s.get("tool") == "qa_pipeline_evidence"), {}) or {}
    gen = next((s for s in steps if s.get("tool") == "qa_generate_evidence"), {}) or {}

    timing_gap = (
        qa_result.get("timing_gap")
        or sr.get("timing_gap")
        or {}
    )
    pre = gen.get("pre_script") if isinstance(gen.get("pre_script"), dict) else {}
    if not timing_gap:
        timing_gap = {
            "init_ms": init.get("duration_ms"),
            "pipeline_ms": pipe.get("duration_ms"),
            "generate_total_ms": gen.get("duration_ms"),
            "pre_script_ms": pre.get("total_ms"),
        }

    work = qa_result.get("work_dirs") or {}
    status_dir = Path(str(work.get("status") or ""))
    if status_dir.is_dir():
        sp = status_dir / f"{SCENARIO}.json"
        if sp.is_file():
            try:
                st = json.loads(sp.read_text(encoding="utf-8"))
                if isinstance(st.get("timing_gap"), dict):
                    timing_gap = st["timing_gap"]
                for s in st.get("mcp_steps") or []:
                    if s.get("tool") == "qa_generate_evidence":
                        if isinstance(s.get("pre_script"), dict):
                            pre = s["pre_script"]
                        if s.get("duration_ms") is not None:
                            gen = {**gen, "duration_ms": s.get("duration_ms")}
            except json.JSONDecodeError:
                pass

    out = {
        "scenario_id": SCENARIO,
        "label": "Boa noite",
        "mode": "live",
        "worker_mode": "local",
        "wall_elapsed_sec": elapsed,
        "ok": bool(result.get("ok")),
        "blocking_reason": qa_result.get("blocking_reason") or sr.get("blocking_reason"),
        "decision": result.get("decision") or qa_result.get("decision"),
        "timing": {
            "wall_sec": elapsed,
            "init_ms": init.get("duration_ms"),
            "pipeline_ms": pipe.get("duration_ms"),
            "generate_ms": gen.get("duration_ms"),
            "pre_script": pre,
            "timing_gap": timing_gap,
            "appium_mode": init.get("appium_mode"),
        },
        "evidence_paths": result.get("evidence_paths") or qa_result.get("evidence_paths") or [],
        "screenshot": gen.get("screenshot") or {},
        "scenarios_results": qa_result.get("scenarios_results"),
    }

    out_path = (
        ROOT
        / "agents"
        / "00-runtime"
        / "system"
        / "observability"
        / "qa_validate_evening_live_timing_T-P3-009.json"
    )
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    lines = [
        f"# Timing — {SCENARIO} (Boa noite)",
        "",
        f"- **ok:** {out['ok']}",
        f"- **wall_elapsed_sec:** {elapsed}",
        f"- **blocking_reason:** {out.get('blocking_reason')}",
        "",
        "## Cadeia até evidência",
        f"- init_ms: {out['timing'].get('init_ms')}",
        f"- pipeline_ms: {out['timing'].get('pipeline_ms')}",
        f"- generate_ms: {out['timing'].get('generate_ms')}",
        f"- pre_script_ms: {pre.get('total_ms')}",
        f"- post_init_to_app_open_estimate_ms: {timing_gap.get('post_init_to_app_open_estimate_ms')}",
        f"- boot_runtime_ms: {timing_gap.get('boot_runtime_ms')}",
        f"- chain_total_ms: {timing_gap.get('chain_total_ms')}",
        f"- appium_mode: {out['timing'].get('appium_mode')}",
        "",
        "## pre_script phases",
    ]
    for p in pre.get("phases") or []:
        lines.append(f"- {p.get('phase')}: {p.get('duration_ms')}ms ok={p.get('ok')}")
    md = out_path.with_suffix(".md")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({k: out[k] for k in out if k != "scenarios_results"}, ensure_ascii=False, indent=2, default=str))
    print("REPORT", out_path)
    print("MD", md)
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
