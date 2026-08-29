"""Avaliadores D5 — regressão Kanban (dataset estático)."""

from __future__ import annotations

from typing import Any

from board_automation.board.task_status_workflow import EVENT_TARGET


def extract_facts(run: dict[str, Any]) -> dict[str, Any]:
    """Normaliza saída do grafo / fixture / policy-replay para os avaliadores."""
    events = list(run.get("events") or [])
    status_seq = list(run.get("status_sequence") or [])
    if not events and run.get("messages"):
        events, status_seq = _parse_messages(list(run.get("messages") or []))
    if not events and run.get("react_trace"):
        ev2, st2 = _parse_react(list(run.get("react_trace") or []))
        if ev2:
            events = ev2
        if st2 and not status_seq:
            status_seq = st2

    board = run.get("board_status") or (status_seq[-1] if status_seq else None)
    tier = run.get("model_tier") or {}
    return {
        "events": events,
        "status_sequence": status_seq,
        "board_status": board,
        "steps": int(run.get("steps") or 0),
        "hitl_pending": bool(run.get("hitl_pending")),
        "model_tier": tier.get("tier") if isinstance(tier, dict) else tier,
        "mode": run.get("mode"),
        "error": run.get("error"),
    }


def _parse_messages(messages: list[str]) -> tuple[list[str], list[str]]:
    events: list[str] = []
    statuses: list[str] = ["Todo"]
    for msg in messages:
        if not msg.startswith("apply:"):
            continue
        # apply: claim -> In Progress dry=True | ...
        body = msg[len("apply:") :].strip()
        if body.startswith("noop"):
            continue
        parts = body.split("->")
        if len(parts) < 2:
            continue
        left = parts[0].strip()
        event = left.split()[0] if left else ""
        right = parts[1].strip()
        status = right.split("dry")[0].split("|")[0].strip()
        if event and event != "noop":
            events.append(event)
        if status:
            if not statuses or statuses[-1] != status:
                statuses.append(status)
    return events, statuses


def _parse_react(trace: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    events: list[str] = []
    for row in trace:
        action = str(row.get("action") or "")
        for prefix in ("simulate:", "emit:", "decide:"):
            if action.startswith(prefix):
                ev = action[len(prefix) :].strip()
                if ev and ev != "noop":
                    events.append(ev)
                break
    return events, []


def eval_invalid_event(facts: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    bad = [e for e in facts["events"] if e != "noop" and e not in EVENT_TARGET]
    ok = len(bad) == 0
    return {
        "name": "invalid_event",
        "ok": ok,
        "detail": {"invalid": bad} if bad else {"invalid": []},
    }


def eval_status_sequence(facts: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    expected = list(case.get("expected_status_sequence") or [])
    if not expected:
        return {"name": "status_sequence", "ok": True, "detail": {"skipped": True}}
    actual = list(facts.get("status_sequence") or [])
    ok = actual == expected
    return {
        "name": "status_sequence",
        "ok": ok,
        "detail": {"expected": expected, "actual": actual},
    }


def eval_events(facts: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    expected = list(case.get("expected_events") or [])
    if case.get("expected_events") is None:
        return {"name": "events", "ok": True, "detail": {"skipped": True}}
    actual = list(facts.get("events") or [])
    ok = actual == expected
    return {
        "name": "events",
        "ok": ok,
        "detail": {"expected": expected, "actual": actual},
    }


def eval_final_status(facts: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    expected = case.get("expected_final_status")
    if expected is None:
        return {"name": "final_status", "ok": True, "detail": {"skipped": True}}
    actual = facts.get("board_status")
    ok = actual == expected
    return {
        "name": "final_status",
        "ok": ok,
        "detail": {"expected": expected, "actual": actual},
    }


def eval_hitl(facts: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    if "expected_hitl" not in case:
        return {"name": "hitl", "ok": True, "detail": {"skipped": True}}
    expected = bool(case.get("expected_hitl"))
    actual = bool(facts.get("hitl_pending"))
    # Em live, merge sem pending quando esperado true = pulou HITL
    skipped_hitl = expected and not actual and (facts.get("mode") == "live")
    ok = actual == expected
    return {
        "name": "hitl",
        "ok": ok,
        "detail": {
            "expected": expected,
            "actual": actual,
            "skipped_hitl": skipped_hitl,
        },
    }


def eval_max_steps(facts: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    limit = int(case.get("max_steps") or 40)
    steps = int(facts.get("steps") or 0)
    ok = steps <= limit
    return {
        "name": "max_steps",
        "ok": ok,
        "detail": {"steps": steps, "max_steps": limit},
    }


def eval_model_tier(facts: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    expected = case.get("expected_model_tier")
    if not expected:
        return {"name": "model_tier", "ok": True, "detail": {"skipped": True}}
    actual = facts.get("model_tier")
    ok = actual == expected
    return {
        "name": "model_tier",
        "ok": ok,
        "detail": {"expected": expected, "actual": actual},
    }


DEFAULT_EVALUATORS = [
    eval_invalid_event,
    eval_events,
    eval_status_sequence,
    eval_final_status,
    eval_hitl,
    eval_max_steps,
    eval_model_tier,
]


def score_case(
    facts: dict[str, Any],
    case: dict[str, Any],
    *,
    evaluators: list | None = None,
) -> dict[str, Any]:
    name_map = {
        "eval_invalid_event": "invalid_event",
        "eval_events": "events",
        "eval_status_sequence": "status_sequence",
        "eval_final_status": "final_status",
        "eval_hitl": "hitl",
        "eval_max_steps": "max_steps",
        "eval_model_tier": "model_tier",
    }
    fns = list(evaluators or DEFAULT_EVALUATORS)
    only = case.get("only_evaluators")
    if only:
        allow = set(only)
        fns = [fn for fn in fns if name_map.get(fn.__name__, fn.__name__) in allow]

    results = [fn(facts, case) for fn in fns]
    expect_fail = set(case.get("expect_eval_fail") or [])
    adjusted = []
    for r in results:
        name = r["name"]
        if name in expect_fail:
            adjusted.append(
                {
                    **r,
                    "ok": not r["ok"],
                    "detail": {**(r.get("detail") or {}), "expect_fail": True, "raw_ok": r["ok"]},
                }
            )
        else:
            adjusted.append(r)
    passed = all(r["ok"] for r in adjusted) and len(adjusted) > 0
    return {
        "case_id": case.get("id"),
        "task_id": case.get("task_id"),
        "ok": passed,
        "evaluators": adjusted,
    }
