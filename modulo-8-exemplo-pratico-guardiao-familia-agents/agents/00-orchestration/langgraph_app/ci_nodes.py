"""Nós CI/CD do StateGraph — wait_ci e cicd_gate."""

from __future__ import annotations

import os
from typing import Any

from lib.ci.ci_state import load_ci_state, merge_gate_ready, patch_ci_state, test_gate_ready
from board_automation.board.task_action_history import build_agent_observation
from langgraph_app import tools_bridge as tools
from langgraph_app.tracing import pipeline_span


def _mode(state: dict[str, Any]) -> str:
    return (state.get("mode") or os.environ.get("GUARDIAO_LANGGRAPH_MODE") or "dry_run").strip()


def _dry(state: dict[str, Any]) -> bool:
    return _mode(state) == "dry_run"


def _reload_ci(state: dict[str, Any]) -> dict[str, Any]:
    tid = str(state.get("task_id") or "")
    ci = load_ci_state(tid)
    mode = _mode(state)
    return {
        "ci_status": ci["ci_status"],
        "pr_url": ci.get("pr_url") or state.get("pr_url"),
        "ci_checks": ci.get("checks") or [],
        "test_ci_ready": test_gate_ready(ci, mode=mode),
        "merge_checks_ok": merge_gate_ready(ci, mode=mode),
    }


def wait_ci_node(state: dict[str, Any]) -> dict[str, Any]:
    """Gate antes de start_test: aguarda ci_green (Actions) ou simula em dry_run."""
    with pipeline_span(
        "wait_ci",
        metadata={"task_id": state.get("task_id"), "board_status": state.get("board_status")},
    ):
        return _wait_ci_node(state)


def _wait_ci_node(state: dict[str, Any]) -> dict[str, Any]:
    tid = str(state.get("task_id") or "")
    mode = _mode(state)
    dry = _dry(state)
    status = state.get("board_status") or "Ready for Test"
    if dry or mode == "demo":
        patch_ci_state(
            tid,
            status="green",
            last_signal="ci_green_simulated",
            summary=f"CI simulado ({mode}) para liberar start_test",
            event="ci_green",
            board_status=status,
            from_agent="devops-cicd",
            to_agent="qa-gate",
        )
        ci = load_ci_state(tid)
    else:
        ci = load_ci_state(tid)

    ci_status = ci.get("ci_status") or "pending"
    msgs = list(state.get("messages") or [])
    steps = int(state.get("steps") or 0) + 1
    base = _reload_ci(state)

    if ci_status == "green" or base["test_ci_ready"]:
        msgs.append(f"wait_ci: green ok ({mode}) -> decide/start_test")
        tools.append_task_action(
            tid,
            agent="devops-cicd",
            event="ci_green",
            thought="Checks GitHub verdes — liberando fila de teste",
            action="Gate CI: ci_status=green",
            observation=build_agent_observation(
                "CI verde — qa-gate pode iniciar start_test",
                extra={"ci_status": "green", "mode": mode},
                ok=True,
            ),
            dry_run=dry,
            record_history=True,
            from_status=status,
            to_status=status,
            extra={"stage": "wait_ci", "ci_status": "green"},
            executed=["wait_ci", "gate_pass"],
            ok=True,
        )
        return {
            **base,
            "ci_status": "green",
            "test_ci_ready": True,
            "ci_waiting": False,
            "messages": msgs,
            "steps": steps,
            "react_trace": [
                {
                    "thought": "CI verde",
                    "action": "wait_ci:pass",
                    "observation": "start_test liberado",
                    "agent": "devops-cicd",
                }
            ],
        }

    if ci_status == "red":
        summary = ci.get("summary") or "CI failed — regressao"
        msgs.append("wait_ci: red -> test_failed_bug")
        tools.append_task_action(
            tid,
            agent="devops-cicd",
            event="ci_red",
            thought=summary,
            action="Gate CI: ci_status=red",
            observation=build_agent_observation(summary, extra={"ci_status": "red"}, ok=False),
            dry_run=dry,
            record_history=True,
            from_status=status,
            to_status=status,
            extra={"stage": "wait_ci", "ci_status": "red"},
            executed=["wait_ci", "gate_fail"],
            ok=False,
        )
        return {
            **base,
            "ci_status": "red",
            "ci_waiting": False,
            "decision": {
                "next_event": "test_failed_bug",
                "summary": summary,
                "rationale": "CI vermelho bloqueou start_test",
                "confidence": 1.0,
                "needs_human": False,
            },
            "messages": msgs,
            "steps": steps,
            "react_trace": [
                {
                    "thought": summary,
                    "action": "wait_ci:fail",
                    "observation": "test_failed_bug",
                    "agent": "devops-cicd",
                }
            ],
        }

    msgs.append("wait_ci: pending — aguardando sinal GitHub Actions (ci_green/ci_red)")
    tools.append_task_action(
        tid,
        agent="devops-cicd",
        event="wait_ci",
        thought="Pipeline aguardando conclusao dos checks no repo de produto",
        action="Pausar grafo ate repository_dispatch ci_green ou ci_red",
        observation=build_agent_observation(
            "ci_status=pending",
            extra={"pr_url": ci.get("pr_url"), "mode": mode},
            ok=True,
        ),
        dry_run=dry,
        record_history=True,
        from_status=status,
        to_status=status,
        extra={"stage": "wait_ci", "ci_status": "pending"},
        executed=["wait_ci", "pause"],
        ok=True,
    )
    return {
        **base,
        "ci_status": "pending",
        "ci_waiting": True,
        "done": True,
        "messages": msgs,
        "steps": steps,
        "react_trace": [
            {
                "thought": "Aguardando CI",
                "action": "wait_ci:pause",
                "observation": "pending",
                "agent": "devops-cicd",
            }
        ],
    }


def cicd_gate_node(state: dict[str, Any]) -> dict[str, Any]:
    """Gate antes de merge_pr: valida checks + pr_url (devops-cicd)."""
    with pipeline_span(
        "cicd_gate",
        metadata={"task_id": state.get("task_id"), "board_status": state.get("board_status")},
    ):
        return _cicd_gate_node(state)


def _cicd_gate_node(state: dict[str, Any]) -> dict[str, Any]:
    tid = str(state.get("task_id") or "")
    mode = _mode(state)
    dry = _dry(state)
    status = state.get("board_status") or "In Pull Request"
    ci = load_ci_state(tid)
    ready = merge_gate_ready(ci, mode=mode)
    msgs = list(state.get("messages") or [])
    steps = int(state.get("steps") or 0) + 1
    base = _reload_ci(state)

    if ready:
        pr = ci.get("pr_url") or "n/a"
        msgs.append(f"cicd_gate: ok pr={pr[:60]} -> hitl merge")
        tools.append_task_action(
            tid,
            agent="devops-cicd",
            event="cicd_gate",
            thought="Checks e PR validados — liberando HITL merge",
            action="Gate merge: ci_status=green + pr_url",
            observation=build_agent_observation(
                f"merge liberado ({mode})",
                extra={"pr_url": pr, "ci_status": ci.get("ci_status")},
                ok=True,
            ),
            dry_run=dry,
            record_history=True,
            from_status=status,
            to_status=status,
            extra={"stage": "cicd_gate", "merge_checks_ok": True},
            executed=["cicd_gate", "pass"],
            ok=True,
        )
        return {
            **base,
            "merge_checks_ok": True,
            "ci_waiting": False,
            "messages": msgs,
            "steps": steps,
            "react_trace": [
                {
                    "thought": "Merge gate OK",
                    "action": "cicd_gate:pass",
                    "observation": str(pr)[:120],
                    "agent": "devops-cicd",
                }
            ],
        }

    reason = (
        f"ci_status={ci.get('ci_status')} pr_url={bool(ci.get('pr_url'))}"
    )
    msgs.append(f"cicd_gate: blocked ({reason})")
    tools.append_task_action(
        tid,
        agent="devops-cicd",
        event="cicd_gate",
        thought="Merge bloqueado — CI ou PR incompletos",
        action="Aguardar ci_green + pr_url valida antes do HITL merge",
        observation=build_agent_observation(reason, extra={"mode": mode}, ok=False),
        dry_run=dry,
        record_history=True,
        from_status=status,
        to_status=status,
        extra={"stage": "cicd_gate", "merge_checks_ok": False},
        executed=["cicd_gate", "block"],
        ok=False,
    )
    return {
        **base,
        "merge_checks_ok": False,
        "ci_waiting": True,
        "done": True,
        "messages": msgs,
        "steps": steps,
        "react_trace": [
            {
                "thought": reason,
                "action": "cicd_gate:block",
                "observation": "awaiting_ci",
                "agent": "devops-cicd",
            }
        ],
    }
