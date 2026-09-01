"""LangGraph v2 — orchestrator decide → 55 nós de evento (factory MCP)."""

from __future__ import annotations

import importlib.util
import os
from typing import Any, Literal

from langgraph.graph import END, StateGraph

from langgraph_app.event_nodes import (
    ALL_EVENT_NODES,
    orchestrator_decide_node,
    sync_board_node,
)
from langgraph_app.event_registry import EVENT_REGISTRY, event_node_id
from langgraph_app.persist import save_run
from langgraph_app.state import PipelineState
from langgraph_app.tracing import build_invoke_config, ensure_tracing, pipeline_span
from lib.paths import orch_script


def _should_end(state: PipelineState) -> bool:
    if state.get("error") or state.get("done") or state.get("hitl_pending"):
        return True
    if int(state.get("steps") or 0) >= int(state.get("max_steps") or 120):
        return True
    return str(state.get("board_status") or "") == "Done"


def _after_sync(state: PipelineState) -> Literal["orchestrator_decide", "end"]:
    return "end" if _should_end(state) else "orchestrator_decide"


def _after_decide(state: PipelineState) -> str:
    if _should_end(state):
        return "end"
    node_id = str(state.get("selected_node_id") or "")
    if node_id and node_id in ALL_EVENT_NODES:
        return node_id
    event = str(state.get("selected_event") or "")
    if event in EVENT_REGISTRY:
        return event_node_id(event)
    return "end"


def _after_event(state: PipelineState) -> Literal["sync_board", "end"]:
    return "end" if _should_end(state) else "sync_board"


def build_graph():
    g = StateGraph(PipelineState)
    g.add_node("sync_board", sync_board_node)
    g.add_node("orchestrator_decide", orchestrator_decide_node)

    route_map: dict[str, str] = {"end": END}
    for node_id, fn in ALL_EVENT_NODES.items():
        g.add_node(node_id, fn)
        route_map[node_id] = node_id

    g.set_entry_point("sync_board")
    g.add_conditional_edges(
        "sync_board",
        _after_sync,
        {"orchestrator_decide": "orchestrator_decide", "end": END},
    )
    g.add_conditional_edges("orchestrator_decide", _after_decide, route_map)
    for node_id in ALL_EVENT_NODES:
        g.add_conditional_edges(
            node_id,
            _after_event,
            {"sync_board": "sync_board", "end": END},
        )
    return g.compile()


def _reset_task(task_id: str) -> None:
    path = orch_script("demo", "demo_apresentacao.py")
    spec = importlib.util.spec_from_file_location("demo_reset", path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.reset_task(task_id)
    from board_automation.board.task_action_history import clear_task_history

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
    max_steps = int(os.environ.get("GUARDIAO_LANGGRAPH_MAX_STEPS") or "120")
    tracing = ensure_tracing()
    if from_zero:
        _reset_task(task_id)

    initial: PipelineState = {
        "task_id": task_id,
        "title": title,
        "agent_role": agent_role,
        "mode": mode,
        "board_status": "Todo" if from_zero else "",
        "messages": [],
        "react_trace": [],
        "done": False,
        "hitl_pending": False,
        "human_clearance": mode in ("demo", "dry_run"),
        "steps": 0,
        "max_steps": max_steps,
        "selected_event": "",
        "selected_node_id": "",
    }
    config = build_invoke_config(task_id=task_id, mode=mode, agent_role=agent_role, title=title)
    with pipeline_span(f"pipeline-v2:{task_id}", metadata=dict(config.get("metadata") or {})):
        final = build_graph().invoke(initial, config=config)
    final["langsmith"] = tracing
    final["persist_path"] = str(save_run(task_id, final))
    return final
