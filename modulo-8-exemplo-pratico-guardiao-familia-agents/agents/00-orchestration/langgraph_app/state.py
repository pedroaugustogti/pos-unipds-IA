"""Estado mínimo do grafo — espelha ciclo MCP."""

from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict


class PipelineState(TypedDict, total=False):
    task_id: str
    title: str
    agent_role: str
    board_status: str
    mode: str
    done: bool
    error: str | None
    hitl_pending: bool
    human_clearance: bool
    steps: int
    max_steps: int
    messages: list[str]
    react_trace: Annotated[list[dict[str, Any]], operator.add]
    actuation_context: dict[str, Any]
    guard_pass_id: str | None
    guard_result: dict[str, Any]
    phase_work: dict[str, Any]
    pending_emit_event: str
    pending_emit_summary: str
    selected_event: str
    selected_node_id: str
