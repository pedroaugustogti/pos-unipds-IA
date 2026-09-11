"""qa_validate live/local — 3 greetings de uma vez + relatório de timing."""

from __future__ import annotations

import json
import os
import sys
import time
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from lib.orchestrator.phase_qa_validate import run_qa_validate

SCENARIOS = [
    "greeting-morning-08h",
    "greeting-afternoon-15h",
    "greeting-evening-21h",
]
LABELS = {
    "greeting-morning-08h": "Bom dia",
    "greeting-afternoon-15h": "Boa tarde",
    "greeting-evening-21h": "Boa noite",
}

os.environ["GF_QA_SCENARIO_MAX_PARALLEL"] = "1"


def _row_from_scenario(sr: dict) -> dict:
    sid = str(sr.get("scenario_id") or "")
    steps = sr.get("mcp_steps") or []
    init = next((s for s in steps if s.get("tool") == "qa_init_suite_mobile"), {}) or {}
    pipe = next((s for s in steps if s.get("tool") == "qa_pipeline_evidence"), {}) or {}
    gen = next((s for s in steps if s.get("tool") == "qa_generate_evidence"), {}) or {}
    pre = gen.get("pre_script") if isinstance(gen.get("pre_script"), dict) else {}
    seed = next(
        (p.get("duration_ms") for p in (pre.get("phases") or []) if p.get("phase") == "qa_db_seed"),
        None,
    )
    gap = sr.get("timing_gap") if isinstance(sr.get("timing_gap"), dict) else {}
    shot = (gen.get("screenshot") or {}).get("evidence") or ""
    vid = (gen.get("video_record") or {}).get("evidence") or ""
    return {
        "scenario_id": sid,
        "label": LABELS.get(sid, sid),
        "ok": bool(sr.get("ok", gen.get("ok"))),
        "blocking_reason": sr.get("blocking_reason"),
        "package_dir": str(sr.get("package_dir") or ""),
        "init_ms": init.get("duration_ms") or gap.get("init_ms"),
        "pipeline_ms": pipe.get("duration_ms") or gap.get("pipeline_ms"),
        "generate_ms": gen.get("duration_ms") or gap.get("generate_total_ms"),
        "pre_script_ms": pre.get("total_ms") or gap.get("pre_script_ms"),
        "seed_ms": seed,
        "boot_runtime_ms": gap.get("boot_runtime_ms"),
        "chain_total_ms": gap.get("chain_total_ms"),
        "post_init_to_app_open_estimate_ms": gap.get("post_init_to_app_open_estimate_ms"),
        "timing_gap": gap,
        "screenshot": shot,
        "video": vid,
        "evidence_paths": sr.get("evidence_paths") or [],
    }


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
    qa["scenarios"] = list(SCENARIOS)
    if isinstance(qa.get("evidence"), dict):
        qa["evidence"]["scenarios_count"] = len(SCENARIOS)
    actuation = deepcopy(actuation)
    if "ticket" in actuation and isinstance(actuation["ticket"], dict):
        actuation["ticket"]["qa"] = qa
    else:
        actuation["qa"] = qa

    print(
        f"=== qa_validate live/local scenarios={SCENARIOS} parallel=1 ===",
        flush=True,
    )
    t0 = time.perf_counter()
    result = run_qa_validate(actuation, mode="live", worker_mode="local")
    wall = round(time.perf_counter() - t0, 3)
    qa_result = result.get("qa_result") if isinstance(result.get("qa_result"), dict) else {}
    scenarios_results = qa_result.get("scenarios_results") or []

    rows = [_row_from_scenario(sr) for sr in scenarios_results if isinstance(sr, dict)]
    # ordenar na ordem canônica
    by_id = {r["scenario_id"]: r for r in rows}
    rows = [by_id[s] for s in SCENARIOS if s in by_id] + [r for r in rows if r["scenario_id"] not in SCENARIOS]

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "task_id": "T-P3-009",
        "mode": "live",
        "worker_mode": "local",
        "max_parallel": 1,
        "flow": "clock→launch→pair→capture (sem forceStop no caminho feliz)",
        "wall_elapsed_sec": wall,
        "qa_validate_ok": bool(result.get("ok")),
        "blocking_reason": qa_result.get("blocking_reason"),
        "scenarios": list(SCENARIOS),
        "scenarios_count": len(rows),
        "runs": rows,
        "evidence_paths": result.get("evidence_paths") or qa_result.get("evidence_paths") or [],
    }

    out = (
        ROOT
        / "agents"
        / "00-runtime"
        / "system"
        / "observability"
        / "qa_validate_suite_timing_report_T-P3-009.json"
    )
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    lines = [
        "# Timing — qa_validate suite T-P3-009 (3 greetings)",
        "",
        f"- **ok:** {report['qa_validate_ok']}",
        "- **mode:** live | **worker:** local | **parallel:** 1",
        f"- **wall_elapsed_sec:** {wall}",
        f"- **blocking_reason:** {report.get('blocking_reason')}",
        f"- **flow:** {report['flow']}",
        f"- **generated_at:** {report['generated_at']}",
        "",
        "## Resumo por cenário",
        "",
        "| cenário | label | ok | chain_s | init_s | seed_s | pre_s | boot_s | generate_s |",
        "|---------|-------|----|---------|--------|--------|-------|--------|------------|",
    ]
    for r in rows:
        lines.append(
            "| {sid} | {lab} | {ok} | {ch} | {ini} | {seed} | {pre} | {boot} | {gen} |".format(
                sid=r["scenario_id"],
                lab=r["label"],
                ok=r["ok"],
                ch=round((r.get("chain_total_ms") or 0) / 1000, 1),
                ini=round((r.get("init_ms") or 0) / 1000, 1),
                seed=round((r.get("seed_ms") or 0) / 1000, 1),
                pre=round((r.get("pre_script_ms") or 0) / 1000, 1),
                boot=round((r.get("boot_runtime_ms") or 0) / 1000, 1),
                gen=round((r.get("generate_ms") or 0) / 1000, 1),
            )
        )

    tot_chain = sum((r.get("chain_total_ms") or 0) for r in rows) / 1000
    lines.extend(
        [
            "",
            f"- **soma chain:** {round(tot_chain, 1)}s | **wall qa_validate:** {wall}s",
            "",
            "## Evidências",
            "",
        ]
    )
    for r in rows:
        shot_name = Path(r["screenshot"]).name if r.get("screenshot") else "—"
        vid_name = Path(r["video"]).name if r.get("video") else "—"
        lines.append(f"### {r['scenario_id']} ({r['label']})")
        lines.append(f"- ok={r['ok']}")
        if r.get("blocking_reason"):
            lines.append(f"- blocking: `{r['blocking_reason']}`")
        lines.append(f"- screenshot: `{shot_name}`")
        lines.append(f"- video: `{vid_name}`")
        lines.append("")

    lines.extend(
        [
            "## Artefatos",
            f"- JSON: `{out.name}`",
            f"- MD: `{out.with_suffix('.md').name}`",
        ]
    )
    md = out.with_suffix(".md")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "ok": report["qa_validate_ok"],
        "wall_elapsed_sec": wall,
        "report_json": str(out),
        "report_md": str(md),
        "scenarios": [
            {
                "id": r["scenario_id"],
                "ok": r["ok"],
                "chain_s": round((r.get("chain_total_ms") or 0) / 1000, 1),
                "generate_s": round((r.get("generate_ms") or 0) / 1000, 1),
            }
            for r in rows
        ],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if report["qa_validate_ok"] and all(r["ok"] for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
