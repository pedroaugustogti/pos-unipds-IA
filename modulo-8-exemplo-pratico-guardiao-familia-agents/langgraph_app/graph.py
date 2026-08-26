"""StateGraph Fase C — ciclo Kanban com loop até Done/HITL/max_steps."""

from __future__ import annotations

import importlib.util
import os
from typing import Any, Literal

from langgraph.graph import END, StateGraph

from langgraph_app.nodes import (
    apply_decision,
    decide_next,
    implement_node,
    load_context,
    qa_node,
    review_node,
    route_task,
)
from langgraph_app.persist import save_run
from langgraph_app.state import AgentState
from langgraph_app.tracing import (
    build_invoke_config,
    enrich_run_metadata,
    ensure_tracing,
    pipeline_span,
)
from lib.paths import MODULE_ROOT


def _after_context(
    state: AgentState,
) -> Literal["implement", "review", "qa", "hitl", "decide", "end"]:
    if state.get("error") or state.get("done"):
        return "end"
    if int(state.get("steps") or 0) >= int(state.get("max_steps") or 20):
        return "end"
    status = str(state.get("board_status") or "")
    if status == "Done":
        return "end"
    if status == "In Progress":
        return "implement"
    # Transicoes reais do board exigem start_review antes de approve_review
    if status == "In Code Review":
        return "review"
    if status == "In Test":
        return "qa"
    if status == "In Pull Request":
        return "hitl"
    # Todo, Ready for Code Review, Ready for Test → decide (policy: claim/start_review/start_test)
    return "decide"


def _after_hitl(state: AgentState) -> Literal["apply", "end"]:
    if state.get("done"):
        return "end"
    # Sempre tenta apply do merge_pr (live pode ficar awaiting_human)
    if str(state.get("board_status") or "") == "In Pull Request":
        return "apply"
    return "end"


def _after_apply(state: AgentState) -> Literal["route", "end"]:
    if state.get("error") or state.get("done") or state.get("hitl_pending"):
        return "end"
    if int(state.get("steps") or 0) >= int(state.get("max_steps") or 20):
        return "end"
    if str(state.get("board_status") or "") == "Done":
        return "end"
    return "route"


def _hitl_merge(state: AgentState) -> dict[str, Any]:
    mode = state.get("mode") or "dry_run"
    with pipeline_span(
        "hitl",
        metadata={"task_id": state.get("task_id"), "mode": mode, "board_status": state.get("board_status")},
    ):
        msgs = list(state.get("messages") or []) + [f"hitl: prepare merge ({mode})"]
        return {
            "decision": {
                "next_event": "merge_pr",
                "summary": "Merge apos QA",
                "rationale": "pipeline Fase C — HITL no merge (agente devops-cicd)",
                "confidence": 1.0,
                "needs_human": mode == "live",
            },
            "messages": msgs,
            "steps": int(state.get("steps") or 0) + 1,
            "react_trace": [
                {
                    "thought": "HITL merge",
                    "action": "hitl_merge",
                    "observation": mode,
                    "agent": "devops-cicd",
                }
            ],
        }


def build_graph():
    g = StateGraph(AgentState)
    g.add_node("route", route_task)
    g.add_node("load_context", load_context)
    g.add_node("decide", decide_next)
    g.add_node("implement", implement_node)
    g.add_node("review", review_node)
    g.add_node("qa", qa_node)
    g.add_node("hitl", _hitl_merge)
    g.add_node("apply", apply_decision)

    g.set_entry_point("route")
    g.add_edge("route", "load_context")
    g.add_conditional_edges(
        "load_context",
        _after_context,
        {
            "implement": "implement",
            "review": "review",
            "qa": "qa",
            "hitl": "hitl",
            "decide": "decide",
            "end": END,
        },
    )
    g.add_edge("decide", "apply")
    g.add_edge("implement", "apply")
    g.add_edge("review", "apply")
    g.add_edge("qa", "apply")
    g.add_conditional_edges("hitl", _after_hitl, {"apply": "apply", "end": END})
    g.add_conditional_edges("apply", _after_apply, {"route": "route", "end": END})
    return g.compile()


def _reset_task(task_id: str) -> None:
    path = MODULE_ROOT / "scripts" / "demo_apresentacao.py"
    spec = importlib.util.spec_from_file_location("demo_apresentacao_reset", path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.reset_task(task_id)
    from lib.task_action_history import clear_task_history

    clear_task_history(task_id)


def run_once(
    task_id: str,
    *,
    mode: str | None = None,
    title: str = "",
    agent_role: str = "",
    from_zero: bool = False,
) -> dict[str, Any]:
    mode = (mode or os.environ.get("GUARDIAO_LANGGRAPH_MODE") or "dry_run").strip()
    max_steps = int(os.environ.get("GUARDIAO_LANGGRAPH_MAX_STEPS") or "40")
    tracing = ensure_tracing()

    if from_zero:
        _reset_task(task_id)

    graph = build_graph()
    initial: AgentState = {
        "task_id": task_id,
        "title": title,
        "agent_role": agent_role,
        "mode": mode,
        "board_status": "Todo" if from_zero else "",
        "messages": [],
        "last_tool_results": [],
        "react_trace": [],
        "hitl_pending": False,
        "done": False,
        "steps": 0,
        "max_steps": max_steps,
        "token_usage": {},
        "last_llm_usage": None,
        "error": None,
        "cycle": 0,
    }

    config = build_invoke_config(
        task_id=task_id,
        mode=mode,
        agent_role=agent_role,
        title=title,
    )

    with pipeline_span(
        f"pipeline:{task_id}",
        metadata=dict(config.get("metadata") or {}),
    ):
        final = graph.invoke(initial, config=config)
        enrich_run_metadata(
            {
                "token_usage": final.get("token_usage") or {},
                "board_status": final.get("board_status"),
                "done": bool(final.get("done")) or final.get("board_status") == "Done",
                "hitl_pending": bool(final.get("hitl_pending")),
                "model_tier": final.get("model_tier") or {},
                "steps": final.get("steps"),
            }
        )

    final["langsmith"] = tracing
    path = save_run(task_id, final)
    final["persist_path"] = str(path)
    return final
