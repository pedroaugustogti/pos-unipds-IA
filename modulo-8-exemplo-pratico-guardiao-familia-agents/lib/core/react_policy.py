"""Política ReAct: teto de iterações e trilha Pensamento/Ação/Observação."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

# Limite padrão por papel (voltas de Thought→Act→Observe)
MAX_ITERATIONS: dict[str, int] = {
    "backend": 4,
    "frontend-mobile": 4,
    "frontend-web": 4,
    "cloud-infra": 3,
    "database": 3,
    "devops-cicd": 3,
    "qa-author": 4,
    "qa-gate": 3,
    "stores-release": 2,
    "orchestrator": 6,
    "default": 4,
}

CREATOR_STEPS = (
    "claim_and_read",
    "implement",
    "module_tests",
    "open_pr",
)

REVIEWER_STEPS = (
    "load_handoff",
    "checklist",
    "propose_verdict",
)

QA_GATE_STEPS = (
    "load_handoff",
    "run_suite",
    "pass_or_bug",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def max_iterations_for(role: str) -> int:
    return MAX_ITERATIONS.get(role, MAX_ITERATIONS["default"])


def new_trace(role: str, task_id: str) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "role": role,
        "max_iterations": max_iterations_for(role),
        "iterations": [],
        "stopped_reason": None,
        "started_at": _now(),
    }


def append_iteration(
    trace: dict[str, Any],
    *,
    thought: str,
    action: str,
    observation: str,
    continue_loop: bool,
) -> dict[str, Any]:
    n = len(trace.get("iterations") or []) + 1
    cap = int(trace.get("max_iterations") or 4)
    row = {
        "n": n,
        "thought": thought[:500],
        "action": action[:300],
        "observation": observation[:800],
        "continue": continue_loop,
        "at": _now(),
    }
    trace.setdefault("iterations", []).append(row)
    if n >= cap and continue_loop:
        trace["stopped_reason"] = "max_iterations"
        row["continue"] = False
        row["observation"] = (
            (row["observation"] + " | ").lstrip(" |")
            + f"LIMITE {cap} atingido — escalar Approval Gate / orchestrator."
        )
    elif not continue_loop:
        trace["stopped_reason"] = "converged"
    return trace


def should_stop(trace: dict[str, Any]) -> bool:
    if trace.get("stopped_reason"):
        return True
    return len(trace.get("iterations") or []) >= int(trace.get("max_iterations") or 4)
