"""Estado do grafo Guardião (Fase C)."""

from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict


class AgentState(TypedDict, total=False):
    task_id: str
    title: str
    board_status: str
    agent_role: str
    agent_role_secondary: str
    scope_redirect: dict[str, Any]
    mode: str  # dry_run | demo | live
    model_tier: dict[str, Any]
    handoff: dict[str, Any]
    decision: dict[str, Any]
    review: dict[str, Any]
    hitl_pending: bool
    messages: list[str]
    last_tool_results: list[dict[str, Any]]
    react_trace: Annotated[list[dict[str, Any]], operator.add]
    error: str | None
    steps: int
    max_steps: int
    token_usage: dict[str, Any]
    last_llm_usage: dict[str, Any] | None
    implement_path: str | None
    cycle: int
    persist_path: str | None
    # CI/CD (handoff metrics.ci + gates do grafo)
    ci_status: str  # pending | green | red
    ci_waiting: bool
    pr_url: str | None
    ci_checks: list[dict[str, Any]]
    test_ci_ready: bool
    merge_checks_ok: bool
