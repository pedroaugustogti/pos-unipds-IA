"""Regenera relatório de timing a partir dos status do último fan-out qa_validate."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
STATUS_DIR = ROOT / "agents/00-runtime/output/T-P3-009/qa-gate-(20)/status"
WALL = 175.151  # wall medido no fan-out live

LABELS = {
    "greeting-morning-08h": "Bom dia",
    "greeting-afternoon-15h": "Boa tarde",
    "greeting-evening-21h": "Boa noite",
}


def main() -> int:
    rows: list[dict] = []
    for sid, label in LABELS.items():
        st = json.loads((STATUS_DIR / f"{sid}.json").read_text(encoding="utf-8"))
        steps = st.get("mcp_steps") or []
        init = next((s for s in steps if s.get("tool") == "qa_init_suite_mobile"), {}) or {}
        pipe = next((s for s in steps if s.get("tool") == "qa_pipeline_evidence"), {}) or {}
        gen = next((s for s in steps if s.get("tool") == "qa_generate_evidence"), {}) or {}
        pre = gen.get("pre_script") if isinstance(gen.get("pre_script"), dict) else {}
        seed = next(
            (p.get("duration_ms") for p in (pre.get("phases") or []) if p.get("phase") == "qa_db_seed"),
            None,
        )
        gap = st.get("timing_gap") or {}
        shot = (gen.get("screenshot") or {}).get("evidence") or ""
        vid = (gen.get("video_record") or {}).get("evidence") or ""
        rows.append(
            {
                "scenario_id": sid,
                "label": label,
                "ok": bool(st.get("ok", gen.get("ok"))),
                "blocking_reason": st.get("blocking_reason"),
                "init_ms": init.get("duration_ms") or gap.get("init_ms"),
                "pipeline_ms": pipe.get("duration_ms") or gap.get("pipeline_ms"),
                "generate_ms": gen.get("duration_ms") or gap.get("generate_total_ms"),
                "pre_script_ms": pre.get("total_ms") or gap.get("pre_script_ms"),
                "seed_ms": seed,
                "boot_runtime_ms": gap.get("boot_runtime_ms"),
                "chain_total_ms": gap.get("chain_total_ms"),
                "post_init_to_app_open_estimate_ms": gap.get("post_init_to_app_open_estimate_ms"),
                "screenshot": shot,
                "video": vid,
                "timing_gap": gap,
                "finished_at": st.get("finished_at"),
            }
        )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "task_id": "T-P3-009",
        "mode": "live",
        "worker_mode": "local",
        "max_parallel": 1,
        "source_status_dir": str(STATUS_DIR),
        "flow": "clock→launch→pair→capture (sem forceStop no caminho feliz)",
        "wall_elapsed_sec": WALL,
        "qa_validate_ok": all(r["ok"] for r in rows),
        "scenarios": list(LABELS),
        "runs": rows,
        "note": (
            "Métricas por cenário via status/timing_gap. "
            "runtime-result.json é compartilhado e fica com o último cenário."
        ),
    }

    out = (
        ROOT
        / "agents/00-runtime/system/observability/qa_validate_suite_timing_report_T-P3-009.json"
    )
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Timing — qa_validate suite T-P3-009 (3 greetings)",
        "",
        f"- **ok:** {report['qa_validate_ok']}",
        "- **mode:** live | **worker:** local | **parallel:** 1",
        f"- **wall_elapsed_sec:** {WALL}",
        f"- **flow:** {report['flow']}",
        f"- **source:** `{STATUS_DIR.parent.name}/status`",
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
            f"- **soma chain:** {round(tot_chain, 1)}s | **wall qa_validate:** {WALL}s",
            "",
            "## Evidências",
            "",
        ]
    )
    for r in rows:
        shot_name = Path(r["screenshot"]).name if r.get("screenshot") else "—"
        vid_name = Path(r["video"]).name if r.get("video") else "—"
        lines.append(f"### {r['scenario_id']} ({r['label']})")
        lines.append(f"- ok={r['ok']} finished={r.get('finished_at')}")
        lines.append(f"- screenshot: `{shot_name}`")
        lines.append(f"- video: `{vid_name}`")
        lines.append("")

    lines.extend(
        [
            "## Notas",
            "- Fluxo único: `set_clock pre_launch` → `launch opened_after_clock` → pairing → capture.",
            "- Sem forceStop/hard_retry no caminho feliz.",
            "- Timing por cenário vem do `status/*.json` (timing_gap + mcp_steps).",
            "",
            f"JSON: `{out.name}`",
        ]
    )
    md = out.with_suffix(".md")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": report["qa_validate_ok"], "md": str(md), "json": str(out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
