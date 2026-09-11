"""Agrega timing de boot (init) + views/steps (runtime) para decisão de aceleração."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _sec(ms: float | int | None) -> float:
    return round(float(ms or 0) / 1000.0, 3)


def _parse_time_exec(raw: str | None) -> float | None:
    """Converte '12.3s' / '1m2s' simples em segundos."""
    if not raw:
        return None
    s = str(raw).strip().lower()
    try:
        if s.endswith("ms"):
            return float(s[:-2]) / 1000.0
        if s.endswith("s") and "m" not in s:
            return float(s[:-1])
        if "m" in s and s.endswith("s"):
            parts = s[:-1].split("m")
            return float(parts[0] or 0) * 60 + float(parts[1] or 0)
    except ValueError:
        return None
    return None


def extract_init_boot(init: dict[str, Any] | None) -> dict[str, Any]:
    init = init or {}
    checks = init.get("checks_child") or init.get("checks_parent") or {}
    rows: list[dict[str, Any]] = []
    total = 0.0
    for name, payload in (checks.items() if isinstance(checks, dict) else []):
        if name == "error_runtime" or not isinstance(payload, dict):
            continue
        sec = _parse_time_exec(str(payload.get("time_exec") or ""))
        if sec is None:
            sec = float(payload.get("elapsed_sec") or 0)
        total += sec
        rows.append(
            {
                "check": name,
                "ok": bool(payload.get("ok")),
                "attempts": payload.get("attempts"),
                "duration_sec": round(sec, 3),
                "detail": str(payload.get("detail") or "")[:200],
                "mode": payload.get("mode"),
            }
        )
    rows.sort(key=lambda r: r["duration_sec"], reverse=True)
    return {
        "total_sec": round(total, 3),
        "checks": rows,
        "top_slow": rows[:5],
        "timeline": init.get("timeline") or [],
    }


def extract_runtime_timing(runtime_result: dict[str, Any] | None) -> dict[str, Any]:
    runtime_result = runtime_result or {}
    boot = list(runtime_result.get("boot") or [])
    timeline = list(runtime_result.get("timeline") or [])
    timing = runtime_result.get("timing") if isinstance(runtime_result.get("timing"), dict) else {}

    by_view: dict[str, float] = {}
    steps_out: list[dict[str, Any]] = []
    for st in timeline:
        if not isinstance(st, dict):
            continue
        ms = float(st.get("duration_ms") or 0)
        view = str(st.get("view") or st.get("view_testid") or st.get("step_id") or "unknown")
        by_view[view] = by_view.get(view, 0.0) + ms
        steps_out.append(
            {
                "step_id": st.get("step_id"),
                "order": st.get("order"),
                "action": st.get("action"),
                "view": st.get("view"),
                "view_testid": st.get("view_testid"),
                "duration_sec": _sec(ms),
                "skipped": bool(st.get("skipped")),
                "hooks": st.get("hooks") or [],
            }
        )
    steps_out_sorted = sorted(steps_out, key=lambda s: s["duration_sec"], reverse=True)
    views = [
        {"view": v, "duration_sec": _sec(ms)}
        for v, ms in sorted(by_view.items(), key=lambda kv: kv[1], reverse=True)
    ]
    boot_rows = [
        {
            "phase": b.get("phase"),
            "ok": b.get("ok"),
            "duration_sec": _sec(b.get("duration_ms")),
            "error": b.get("error"),
        }
        for b in boot
        if isinstance(b, dict)
    ]
    boot_rows_sorted = sorted(boot_rows, key=lambda b: b["duration_sec"], reverse=True)
    return {
        "total_runtime_sec": _sec(timing.get("total_runtime_ms")),
        "boot_total_sec": _sec(timing.get("boot_total_ms")) or sum(b["duration_sec"] for b in boot_rows),
        "steps_total_sec": _sec(timing.get("steps_total_ms")) or sum(s["duration_sec"] for s in steps_out),
        "boot_phases": boot_rows_sorted,
        "steps_by_duration": steps_out_sorted,
        "views_by_duration": views,
        "top_slow_steps": steps_out_sorted[:8],
        "top_slow_views": views[:8],
    }


def build_acceleration_insights(
    *,
    init_boot: dict[str, Any],
    runtime: dict[str, Any],
) -> list[dict[str, Any]]:
    insights: list[dict[str, Any]] = []
    for chk in (init_boot.get("top_slow") or [])[:3]:
        if chk["duration_sec"] >= 5:
            insights.append(
                {
                    "area": "boot_init",
                    "item": chk["check"],
                    "duration_sec": chk["duration_sec"],
                    "impact": "high" if chk["duration_sec"] >= 20 else "medium",
                    "recommendation": (
                        "Reusar stack já pronta (skip_build / cold→warm Appium) e evitar rebuild/reinstall neste check."
                        if chk["check"] in ("apk", "metro", "emulator", "appium")
                        else "Investigar retries/timeouts neste check de init."
                    ),
                }
            )
    for ph in (runtime.get("boot_phases") or [])[:3]:
        if ph["duration_sec"] >= 3:
            insights.append(
                {
                    "area": "boot_runtime",
                    "item": ph["phase"],
                    "duration_sec": ph["duration_sec"],
                    "impact": "high" if ph["duration_sec"] >= 15 else "medium",
                    "recommendation": (
                        "Sessão Appium: manter server warm e evitar pm_clear a cada cenário se o estado for reutilizável."
                        if ph["phase"] == "create_appium_session"
                        else "Reduzir grant/pm_clear/reload quando o app já está estável."
                    ),
                }
            )
    for st in (runtime.get("top_slow_steps") or [])[:5]:
        if st["duration_sec"] < 3:
            continue
        action = str(st.get("action") or "")
        if st.get("skipped"):
            insights.append(
                {
                    "area": "pipeline_view",
                    "item": f"{st.get('step_id')} ({st.get('view') or st.get('view_testid')})",
                    "action": action,
                    "duration_sec": st["duration_sec"],
                    "impact": "high" if st["duration_sec"] >= 10 else "medium",
                    "recommendation": (
                        "Step optional skipped ainda consumiu settle/timeout — reduzir "
                        "optional settle e short-circuit quando o fluxo já avançou (ex.: auto-submit OTP)."
                    ),
                }
            )
            continue
        rec = "Reduzir delay_ms_after / settle e apertar view_gate timeout quando a view e estavel."
        if action == "set_clock":
            rec = "set_clock+force_reload e caro: avaliar clock via mock/seed ou reload parcial sem re-pair."
        elif action == "fill":
            rec = "Fill OTP: EditText direto, expected_length=6, sem retries no Pressable."
        elif action == "capture":
            rec = "Capture: estabilizar home mais cedo; assert via text+contentDescription."
        elif action in ("wait", "navigate", "launch"):
            rec = "Launch/wait: cortar dismiss_expo duplicado e delays fixos quando gate ja passou."
        elif action == "tap":
            rec = "Tap: se auto-submit existir, nao esperar exit_condition longo em tela antiga."
        insights.append(
            {
                "area": "pipeline_view",
                "item": f"{st.get('step_id')} ({st.get('view') or st.get('view_testid')})",
                "action": action,
                "duration_sec": st["duration_sec"],
                "impact": "high" if st["duration_sec"] >= 15 else "medium",
                "recommendation": rec,
            }
        )
    if not insights:
        insights.append(
            {
                "area": "general",
                "item": "no_hotspots",
                "duration_sec": 0,
                "impact": "low",
                "recommendation": "Sem hotspots >3s; foque em paralelizar cenários e reuso de init entre saudações.",
            }
        )
    return insights


def build_timing_report(
    *,
    scenario_id: str,
    qa_result: dict[str, Any],
    runtime_result_path: Path | None = None,
) -> dict[str, Any]:
    init = {}
    # multi-scenario: first scenario result may nest init in mcp_steps / scenarios_results
    for sc in qa_result.get("scenarios_results") or []:
        if isinstance(sc, dict) and sc.get("scenario_id") == scenario_id:
            # status may have mcp_steps only
            break
    # chain result from worker status files may not embed init; look at mcp_steps packages
    # Prefer explicit init on orchestrator aggregate if present
    init = qa_result.get("init") if isinstance(qa_result.get("init"), dict) else {}

    runtime: dict[str, Any] = {}
    if runtime_result_path and runtime_result_path.is_file():
        try:
            runtime = json.loads(runtime_result_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            runtime = {}

    if not runtime:
        # procura runtime-result sob package_dir / evidence
        candidates: list[Path] = []
        for p in qa_result.get("evidence_paths") or []:
            root = Path(str(p))
            if root.is_file():
                root = root.parent
            if root.is_dir():
                candidates.extend(root.rglob("runtime-result.json"))
        pkg = qa_result.get("package_dir")
        if pkg:
            candidates.extend(Path(str(pkg)).rglob("runtime-result.json"))
        for c in sorted(candidates, key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                data = json.loads(c.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if str(data.get("scenario_id") or "") in ("", scenario_id):
                runtime = data
                runtime_result_path = c
                break

    # init from nested scenario chain if available in status mcp
    for step in qa_result.get("mcp_steps") or []:
        if isinstance(step, dict) and step.get("tool") == "qa_init_suite_mobile" and not init:
            # init details may not be fully in mcp_steps
            pass

    init_boot = extract_init_boot(init)
    # also scan scenarios_results status for nested result files already handled

    rt = extract_runtime_timing(runtime)
    wall = float(init_boot.get("total_sec") or 0) + float(rt.get("total_runtime_sec") or 0)
    insights = build_acceleration_insights(init_boot=init_boot, runtime=rt)

    return {
        "scenario_id": scenario_id,
        "ok": bool(qa_result.get("ok")),
        "worker_mode": qa_result.get("worker_mode") or "local",
        "wall_clock_sec_approx": round(wall, 3),
        "boot_init": init_boot,
        "boot_runtime": {
            "total_sec": rt.get("boot_total_sec"),
            "phases": rt.get("boot_phases"),
        },
        "pipeline_views": {
            "steps_total_sec": rt.get("steps_total_sec"),
            "views_by_duration": rt.get("views_by_duration"),
            "steps_by_duration": rt.get("steps_by_duration"),
            "top_slow_steps": rt.get("top_slow_steps"),
            "top_slow_views": rt.get("top_slow_views"),
        },
        "runtime_result_path": str(runtime_result_path) if runtime_result_path else None,
        "acceleration_insights": insights,
        "decision_summary": {
            "biggest_costs": [
                *(
                    [{"area": "init", "item": c["check"], "sec": c["duration_sec"]} for c in (init_boot.get("top_slow") or [])[:2]]
                ),
                *(
                    [{"area": "runtime_boot", "item": p["phase"], "sec": p["duration_sec"]} for p in (rt.get("boot_phases") or [])[:2]]
                ),
                *(
                    [
                        {
                            "area": "view",
                            "item": s.get("step_id"),
                            "sec": s["duration_sec"],
                        }
                        for s in (rt.get("top_slow_steps") or [])[:3]
                        if not s.get("skipped")
                    ]
                ),
            ],
            "priority_actions": [i["recommendation"] for i in insights[:5]],
        },
    }
