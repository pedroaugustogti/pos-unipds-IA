"""Runner D4/D5 — dataset estático local (+ opcional LangGraph dry_run)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from evals.evaluators import extract_facts, score_case
from langgraph_app.policy import status_after_event
from lib.model_tier import select_model
from lib.paths import MODULE_ROOT

DEFAULT_DATASET = MODULE_ROOT / "evals" / "datasets" / "kanban_pipeline.json"


def load_dataset(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_DATASET
    return json.loads(p.read_text(encoding="utf-8"))


def policy_replay(case: dict[str, Any]) -> dict[str, Any]:
    """Simula a sequência expected_events sem LLM (regressão barata)."""
    events = list(case.get("expected_events") or [])
    status = "Todo"
    seq = [status]
    for ev in events:
        status = status_after_event(ev, status)
        if not seq or seq[-1] != status:
            seq.append(status)
    tier = select_model(
        {
            "id": case.get("task_id"),
            "title": case.get("title"),
            "agent_role": case.get("agent_role"),
        },
        purpose="implement_low",
        role=case.get("agent_role"),
    )
    return {
        "mode": case.get("mode") or "dry_run",
        "board_status": status,
        "events": events,
        "status_sequence": seq,
        "steps": max(2, len(events) * 4),
        "hitl_pending": bool(case.get("expected_hitl")),
        "model_tier": tier,
        "error": None,
    }


def model_tier_only(case: dict[str, Any]) -> dict[str, Any]:
    tier = select_model(
        {
            "id": case.get("task_id"),
            "title": case.get("title"),
            "agent_role": case.get("agent_role"),
        },
        purpose="implement_low",
        role=case.get("agent_role"),
    )
    return {
        "mode": case.get("mode") or "dry_run",
        "board_status": None,
        "events": [],
        "status_sequence": [],
        "steps": 0,
        "hitl_pending": False,
        "model_tier": tier,
        "error": None,
    }


def fixture_run(case: dict[str, Any]) -> dict[str, Any]:
    fx = dict(case.get("fixture") or {})
    fx["mode"] = case.get("mode") or fx.get("mode") or "dry_run"
    return fx


def run_graph_case(case: dict[str, Any]) -> dict[str, Any]:
    from langgraph_app import run_once

    out = run_once(
        str(case["task_id"]),
        mode=str(case.get("mode") or "dry_run"),
        title=str(case.get("title") or ""),
        agent_role=str(case.get("agent_role") or ""),
        from_zero=True,
    )
    events, status_seq = [], []
    facts = extract_facts(out)
    events = facts["events"]
    status_seq = facts["status_sequence"]
    return {
        "mode": out.get("mode"),
        "board_status": out.get("board_status"),
        "events": events,
        "status_sequence": status_seq,
        "steps": out.get("steps"),
        "hitl_pending": out.get("hitl_pending"),
        "model_tier": out.get("model_tier"),
        "token_usage": out.get("token_usage"),
        "langsmith": out.get("langsmith"),
        "error": out.get("error"),
        "messages": out.get("messages"),
    }


def execute_case(case: dict[str, Any], *, with_graph: bool = False) -> dict[str, Any]:
    engine = (case.get("engine") or "").strip()
    if engine == "fixture":
        return fixture_run(case)
    if engine == "model_tier_only":
        return model_tier_only(case)
    if with_graph and case.get("run_graph"):
        return run_graph_case(case)
    return policy_replay(case)


def run_dataset(
    path: Path | None = None,
    *,
    with_graph: bool = False,
    case_ids: list[str] | None = None,
) -> dict[str, Any]:
    ds = load_dataset(path)
    results = []
    for case in ds.get("cases") or []:
        cid = case.get("id")
        if case_ids and cid not in case_ids:
            continue
        run = execute_case(case, with_graph=with_graph)
        facts = extract_facts(run)
        scored = score_case(facts, case)
        scored["engine"] = case.get("engine") or (
            "langgraph" if with_graph and case.get("run_graph") else "policy_replay"
        )
        if case.get("engine") == "fixture":
            scored["engine"] = "fixture"
        if case.get("engine") == "model_tier_only":
            scored["engine"] = "model_tier_only"
        scored["facts"] = {
            "events": facts["events"],
            "status_sequence": facts["status_sequence"],
            "board_status": facts["board_status"],
            "steps": facts["steps"],
            "hitl_pending": facts["hitl_pending"],
            "model_tier": facts["model_tier"],
        }
        results.append(scored)

    passed = sum(1 for r in results if r["ok"])
    total = len(results)
    return {
        "dataset": ds.get("name"),
        "version": ds.get("version"),
        "with_graph": with_graph,
        "passed": passed,
        "total": total,
        "ok": passed == total and total > 0,
        "results": results,
    }
