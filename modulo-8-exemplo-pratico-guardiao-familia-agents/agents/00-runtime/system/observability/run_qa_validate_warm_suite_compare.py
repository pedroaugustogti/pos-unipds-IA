"""qa_validate live/local — 3 greetings com suite já up; gera comparativo de timing."""

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
    ("greeting-morning-08h", "Bom dia"),
    ("greeting-afternoon-15h", "Boa tarde"),
    ("greeting-evening-21h", "Boa noite"),
]

# 1 emulator: serializar workers
os.environ["GF_QA_SCENARIO_MAX_PARALLEL"] = "1"


def _run_one(scenario_id: str, label: str) -> dict:
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
    qa["scenarios"] = [scenario_id]
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
    steps = sr.get("mcp_steps") or []
    init = next((s for s in steps if s.get("tool") == "qa_init_suite_mobile"), {}) or {}
    pipe = next((s for s in steps if s.get("tool") == "qa_pipeline_evidence"), {}) or {}
    gen = next((s for s in steps if s.get("tool") == "qa_generate_evidence"), {}) or {}
    pre = gen.get("pre_script") if isinstance(gen.get("pre_script"), dict) else {}
    gap = sr.get("timing_gap") or qa_result.get("timing_gap") or {}

    # runtime-result timing se existir
    boot_ms = gap.get("boot_runtime_ms")
    pkg = str(sr.get("package_dir") or "")
    if not boot_ms and pkg:
        rr = Path(pkg) / "runtime-result.json"
        if rr.is_file():
            try:
                rt = json.loads(rr.read_text(encoding="utf-8"))
                boot_ms = (rt.get("timing") or {}).get("boot_total_ms")
                steps_ms = (rt.get("timing") or {}).get("steps_total_ms")
            except json.JSONDecodeError:
                steps_ms = None
        else:
            steps_ms = None
    else:
        steps_ms = None
        if pkg:
            rr = Path(pkg) / "runtime-result.json"
            if rr.is_file():
                try:
                    rt = json.loads(rr.read_text(encoding="utf-8"))
                    steps_ms = (rt.get("timing") or {}).get("steps_total_ms")
                    if boot_ms is None:
                        boot_ms = (rt.get("timing") or {}).get("boot_total_ms")
                except json.JSONDecodeError:
                    pass

    seed_ms = None
    for p in pre.get("phases") or []:
        if p.get("phase") == "qa_db_seed":
            seed_ms = p.get("duration_ms")

    return {
        "scenario_id": scenario_id,
        "label": label,
        "ok": bool(result.get("ok")),
        "wall_elapsed_sec": elapsed,
        "blocking_reason": qa_result.get("blocking_reason") or sr.get("blocking_reason"),
        "appium_mode": init.get("appium_mode"),
        "init_ms": init.get("duration_ms"),
        "pipeline_ms": pipe.get("duration_ms"),
        "generate_ms": gen.get("duration_ms"),
        "pre_script_ms": pre.get("total_ms"),
        "seed_ms": seed_ms,
        "boot_runtime_ms": boot_ms,
        "steps_total_ms": steps_ms,
        "timing_gap": gap,
        "pre_script": pre,
        "evidence_paths": result.get("evidence_paths") or sr.get("evidence_paths") or [],
    }


def main() -> int:
    # baseline: warm suite ANTES do skip bootstrap (~90s wall)
    baseline = {
        "greeting-morning-08h": {
            "source": "qa_validate_warm_suite_timing_compare_T-P3-009 (pré seed-opt)",
            "wall_elapsed_sec": 90.1,
            "ok": True,
            "init_ms": 382,
            "seed_ms": 18033,
            "note": "suite warm; seed ainda com bootstrap ~18s",
        },
        "greeting-afternoon-15h": {
            "source": "qa_validate_warm_suite_timing_compare_T-P3-009 (pré seed-opt)",
            "wall_elapsed_sec": 88.0,
            "ok": False,
            "init_ms": 351,
            "seed_ms": 17690,
            "note": "suite warm; set_clock assert",
        },
        "greeting-evening-21h": {
            "source": "qa_validate_warm_suite_timing_compare_T-P3-009 (pré seed-opt)",
            "wall_elapsed_sec": 90.0,
            "ok": False,
            "init_ms": 362,
            "seed_ms": 18795,
            "note": "suite warm; set_clock assert",
        },
        "_cold_partial": {
            "greeting-afternoon-15h": 228.3,
            "greeting-evening-21h": 210.2,
        },
    }

    runs: list[dict] = []
    for sid, label in SCENARIOS:
        print(f"=== RUN {sid} ({label}) suite=warm parallel=1 ===", flush=True)
        row = _run_one(sid, label)
        runs.append(row)
        print(
            json.dumps(
                {
                    "scenario_id": sid,
                    "ok": row["ok"],
                    "wall_sec": row["wall_elapsed_sec"],
                    "init_ms": row["init_ms"],
                    "pre_script_ms": row["pre_script_ms"],
                    "seed_ms": row["seed_ms"],
                    "boot_ms": row["boot_runtime_ms"],
                    "steps_ms": row["steps_total_ms"],
                    "blocking": row["blocking_reason"],
                },
                ensure_ascii=False,
            ),
            flush=True,
        )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "task_id": "T-P3-009",
        "mode": "live",
        "worker_mode": "local",
        "suite_assumption": "already_up_warm",
        "max_parallel": 1,
        "baseline_previous": baseline,
        "runs_warm": runs,
    }

    out = (
        ROOT
        / "agents"
        / "00-runtime"
        / "system"
        / "observability"
        / "qa_validate_live_timing_post_seed_opt_T-P3-009.json"
    )
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    lines = [
        "# Timing qa_validate live/local — pós seed-opt (suite warm)",
        "",
        f"- **mode:** live | **worker:** local | **parallel:** 1",
        f"- **generated_at:** {report['generated_at']}",
        f"- **suite:** already up (appium warm)",
        "",
        "## Runs desta sessão",
        "",
        "| cenário | ok | wall_s | init_s | seed_s | boot_s | steps_s |",
        "|---------|----|--------|--------|--------|--------|---------|",
    ]
    for r in runs:
        lines.append(
            "| {sid} | {ok} | {wall} | {init} | {seed} | {boot} | {steps} |".format(
                sid=r["scenario_id"],
                ok=r["ok"],
                wall=r["wall_elapsed_sec"],
                init=round((r.get("init_ms") or 0) / 1000, 1),
                seed=round((r.get("seed_ms") or 0) / 1000, 1),
                boot=round((r.get("boot_runtime_ms") or 0) / 1000, 1),
                steps=round((r.get("steps_total_ms") or 0) / 1000, 1),
            )
        )

    lines.extend(
        [
            "",
            "## vs warm anterior (pré seed-opt, ~90s)",
            "",
            "| cenário | wall antes | wall agora | delta |",
            "|---------|------------|------------|-------|",
        ]
    )
    for r in runs:
        b = baseline.get(r["scenario_id"]) or {}
        before = b.get("wall_elapsed_sec")
        if before is None:
            lines.append(f"| {r['scenario_id']} | — | {r['wall_elapsed_sec']} | — |")
        else:
            delta = round(r["wall_elapsed_sec"] - float(before), 1)
            sign = f"+{delta}" if delta > 0 else str(delta)
            lines.append(
                f"| {r['scenario_id']} | {before} | {r['wall_elapsed_sec']} | {sign}s |"
            )

    cold = baseline.get("_cold_partial") or {}
    lines.extend(
        [
            "",
            "## vs cold/parcial (histórico)",
            "",
            "| cenário | cold | agora |",
            "|---------|------|-------|",
        ]
    )
    for r in runs:
        c = cold.get(r["scenario_id"])
        if c is not None:
            lines.append(f"| {r['scenario_id']} | {c}s | {r['wall_elapsed_sec']}s |")

    lines.extend(["", "## Blocking / notes"])
    for r in runs:
        lines.append(
            f"- **{r['scenario_id']}:** ok={r['ok']} appium={r.get('appium_mode')} — {r.get('blocking_reason') or 'PASS'}"
        )

    lines.extend(
        [
            "",
            "## Notas",
            "- Seed-opt: skip bootstrap se API healthy (T3 ~0.9s vs ~18s).",
            "- set_clock no emulador pode ainda falhar assert de saudação.",
            "",
            f"JSON: `{out.name}`",
        ]
    )
    md = out.with_suffix(".md")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("REPORT", out)
    print("MD", md)
    return 0 if all(r["ok"] for r in runs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
