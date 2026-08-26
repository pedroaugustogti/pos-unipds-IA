"""Fase B — MCP server Guardião Família (fachada sobre lib/*)."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

# Pacote local + lib do módulo
_MODULE_ROOT = Path(__file__).resolve().parents[1]
if str(_MODULE_ROOT) not in sys.path:
    sys.path.insert(0, str(_MODULE_ROOT))

from lib.env_load import ensure_env  # noqa: E402

ensure_env()

from mcp.server.fastmcp import FastMCP  # noqa: E402

from guardiao_mcp.contract import fail, ok, wrap_call  # noqa: E402
from lib.gateway import (  # noqa: E402
    approve_hitl as gateway_approve_hitl,
    emit_status_event as gateway_emit,
    list_hitl_queue as gateway_list_hitl,
)
from lib.event_orchestrator import (  # noqa: E402
    list_idle_agents,
    process_dispatch_queue,
    release_agent,
    resolve_agent_for_event,
)
from lib.task_router import load_tasks, pick_task  # noqa: E402
from lib.observability import build_snapshot, write_dashboard  # noqa: E402
from lib.handoff import load_handoff, write_handoff  # noqa: E402
from lib.task_action_history import append_task_action  # noqa: E402
from lib.model_tier import select_model  # noqa: E402
from lib.dispatch_adapter import dispatch_job  # noqa: E402
from lib.worker_jobs import load_jobs  # noqa: E402
from lib.task_status_workflow import EVENT_TARGET  # noqa: E402

mcp = FastMCP(
    "guardiao-familia-agents",
    instructions=(
        "Tools do Guardião Família (módulo 8). "
        "Status só via emit_status_event (gateway). "
        "Nunca mergeie sem approve_hitl. Prefira dry_run=true em exploração."
    ),
)


def _dispatch_allowed() -> bool:
    return (os.environ.get("GUARDIAO_MCP_ALLOW_DISPATCH") or "").strip() in (
        "1",
        "true",
        "True",
        "yes",
    )


def _task_by_id(task_id: str) -> dict[str, Any] | None:
    return next((t for t in load_tasks() if t.get("id") == task_id), None)


# --- Gateway / HITL ---


@mcp.tool()
def emit_status_event(
    task_id: str,
    event: str,
    summary: str = "",
    dry_run: bool = True,
    pr_url: str = "",
    from_agent: str = "",
) -> str:
    """Porta única de Status (gateway). Eventos: claim, open_pr, start_review, …

    dry_run default True por segurança no MCP.
    """
    if event not in EVENT_TARGET and event not in ("hitl_approved", "hitl_rejected"):
        return fail(
            f"Evento invalido: {event}",
            dry_run=dry_run,
            allowed=sorted(EVENT_TARGET),
        )
    return wrap_call(
        gateway_emit,
        task_id=task_id,
        event=event,
        summary=summary,
        dry_run=dry_run,
        apply_board=True,
        pr_url=pr_url or None,
        from_agent=from_agent or None,
    )


@mcp.tool()
def list_hitl_queue() -> str:
    """Lista eventos aguardando aprovação humana (merge, blocker, review alto risco)."""
    return ok({"hitl_queue": gateway_list_hitl()})


@mcp.tool()
def approve_hitl(task_id: str, event: str, dry_run: bool = True) -> str:
    """Libera evento bloqueado após decisão humana (ex.: merge_pr). dry_run default True."""
    return wrap_call(gateway_approve_hitl, task_id=task_id, event=event, dry_run=dry_run)


# --- Observability / model tier ---


@mcp.tool()
def snapshot_observability(write_html: bool = False) -> str:
    """Snapshot de agentes idle/busy, filas e Kanban piloto."""
    try:
        snap = build_snapshot()
        path = None
        if write_html:
            path = str(write_dashboard(snap))
        return ok({"snapshot": snap, "dashboard": path})
    except Exception as exc:  # noqa: BLE001
        return fail(f"{type(exc).__name__}: {exc}")


@mcp.tool()
def select_model_tier(
    purpose: str = "implement_low",
    title: str = "",
    agent_role: str = "",
    epic_id: str = "",
) -> str:
    """Consulta select_model (Fase A): route | implement_low | implement_high | review | summarize | cursor."""
    task = {
        "title": title,
        "agent_role": agent_role,
        "epic_id": epic_id,
    }
    return ok(select_model(task, purpose=purpose, role=agent_role or None))


# --- Orchestrator idle / dispatch queue ---


@mcp.tool()
def list_idle_agents_tool() -> str:
    """Lista papéis ociosos no agent_runtime."""
    return ok({"idle": list_idle_agents()})


@mcp.tool()
def resolve_agent_for_board_event(task_id: str, event: str) -> str:
    """Resolve qual agent_role deve atuar após o evento."""
    task = _task_by_id(task_id)
    if not task:
        return fail(f"Task nao encontrada: {task_id}")
    role = resolve_agent_for_event(task, event)
    return ok({"task_id": task_id, "event": event, "agent_role": role})


@mcp.tool()
def drain_dispatch_queue(limit: int = 5) -> str:
    """Despacha itens da dispatch_queue quando o agente está idle."""
    return ok({"dispatched": process_dispatch_queue(limit=limit)})


@mcp.tool()
def mark_agent_idle(agent_role: str) -> str:
    """Marca agente idle e processa um item da fila se houver."""
    release_agent(agent_role, persist=True)
    queued = process_dispatch_queue(limit=1)
    return ok({"agent_role": agent_role, "state": "idle", "drained": queued})


# --- Board / tasks ---


@mcp.tool()
def load_tasks_tool(limit: int = 50) -> str:
    """Carrega tasks do CSV + status do board (limitado)."""
    tasks = load_tasks()
    slim = [
        {
            "id": t.get("id"),
            "title": t.get("title"),
            "agent_role": t.get("agent_role"),
            "board_status": t.get("board_status"),
            "sprint": t.get("sprint"),
            "depends_on": t.get("depends_on"),
        }
        for t in tasks[: max(1, min(limit, 200))]
    ]
    return ok({"count": len(tasks), "returned": len(slim), "tasks": slim})


@mcp.tool()
def pick_task_tool(agent_role: str, sprint: int = 1) -> str:
    """Seleciona a próxima task elegível para o role (scoring do task_router)."""
    task = pick_task(agent_role, sprint_atual=sprint)
    if not task:
        return ok({"task": None, "message": f"Nenhuma task elegivel para {agent_role}"})
    return ok(
        {
            "task": {
                "id": task.get("id"),
                "title": task.get("title"),
                "agent_role": task.get("agent_role"),
                "board_status": task.get("board_status"),
            }
        }
    )


# --- Handoff / ReAct history ---


@mcp.tool()
def get_handoff(task_id: str) -> str:
    """Lê handoff JSON da task."""
    data = load_handoff(task_id)
    if data is None:
        return fail(f"Handoff ausente: {task_id}", result={"task_id": task_id})
    return ok(data)


@mcp.tool()
def write_handoff_tool(
    task_id: str,
    from_agent: str,
    to_agent: str,
    event: str,
    status: str,
    summary: str = "",
    pr_url: str = "",
    dry_run: bool = True,
) -> str:
    """Grava/atualiza handoff. dry_run default True."""
    if dry_run:
        return ok(
            {
                "would_write": {
                    "task_id": task_id,
                    "from_agent": from_agent,
                    "to_agent": to_agent,
                    "event": event,
                    "status": status,
                    "summary": summary,
                    "pr_url": pr_url or None,
                }
            },
            dry_run=True,
        )
    return wrap_call(
        write_handoff,
        pass_dry_run=False,
        dry_run=False,
        task_id=task_id,
        from_agent=from_agent,
        to_agent=to_agent,
        event=event,
        status=status,
        summary=summary,
        pr_url=pr_url or None,
    )


@mcp.tool()
def append_task_action_tool(
    task_id: str,
    agent: str,
    event: str,
    thought: str,
    action: str,
    observation: str = "",
    from_status: str = "",
    to_status: str = "",
    title: str = "",
    focus: str = "",
    model: str = "",
    purpose: str = "",
    tokens_input: int = 0,
    tokens_output: int = 0,
    tokens_total: int = 0,
    dry_run: bool = True,
) -> str:
    """Append thought/action no histórico. Informe thought (o que pensou), action (o que
    executou) e focus (ponto específico da execução). Modelo/tokens entram na observação.
    dry_run default True."""
    if dry_run:
        return ok(
            {
                "would_append": {
                    "task_id": task_id,
                    "agent": agent,
                    "event": event,
                    "thought": thought[:200],
                    "action": action[:200],
                    "focus": focus[:200],
                    "model": model or None,
                    "tokens_total": tokens_total or (tokens_input + tokens_output) or None,
                }
            },
            dry_run=True,
        )
    extra: dict = {}
    if focus:
        extra["focus"] = focus
    if model:
        extra["model"] = model
    if purpose:
        extra["purpose"] = purpose
    if tokens_input or tokens_output or tokens_total:
        extra["tokens"] = {
            "input": tokens_input,
            "output": tokens_output,
            "total": tokens_total or (tokens_input + tokens_output),
        }
    return wrap_call(
        append_task_action,
        pass_dry_run=False,
        dry_run=False,
        task_id=task_id,
        agent=agent,
        event=event,
        thought=thought,
        action=action,
        observation=observation,
        from_status=from_status or None,
        to_status=to_status or None,
        title=title or None,
        extra=extra or None,
    )


# --- Dispatch (feature-flag) ---


@mcp.tool()
def dispatch_job_tool(job_id: str, dry_run: bool = True) -> str:
    """Despacha job da fila worker (Cursor SDK ou fallback). Requer GUARDIAO_MCP_ALLOW_DISPATCH=1."""
    if not _dispatch_allowed():
        return fail(
            "Dispatch desabilitado. Defina GUARDIAO_MCP_ALLOW_DISPATCH=1 para habilitar.",
            dry_run=dry_run,
        )
    jobs = load_jobs().get("jobs") or []
    job = next((j for j in jobs if j.get("job_id") == job_id), None)
    if not job:
        return fail(f"Job nao encontrado: {job_id}", dry_run=dry_run)
    return wrap_call(dispatch_job, job=job, dry_run=dry_run)


@mcp.tool()
def list_mcp_tools() -> str:
    """Lista as tools expostas por este servidor MCP (catálogo)."""
    catalog = [
        {"name": "emit_status_event", "group": "gateway", "writes": True},
        {"name": "list_hitl_queue", "group": "gateway", "writes": False},
        {"name": "approve_hitl", "group": "gateway", "writes": True},
        {"name": "snapshot_observability", "group": "observability", "writes": False},
        {"name": "select_model_tier", "group": "model", "writes": False},
        {"name": "list_idle_agents_tool", "group": "orchestrator", "writes": False},
        {"name": "resolve_agent_for_board_event", "group": "orchestrator", "writes": False},
        {"name": "drain_dispatch_queue", "group": "orchestrator", "writes": True},
        {"name": "mark_agent_idle", "group": "orchestrator", "writes": True},
        {"name": "load_tasks_tool", "group": "board", "writes": False},
        {"name": "pick_task_tool", "group": "board", "writes": False},
        {"name": "get_handoff", "group": "handoff", "writes": False},
        {"name": "write_handoff_tool", "group": "handoff", "writes": True},
        {"name": "append_task_action_tool", "group": "history", "writes": True},
        {"name": "dispatch_job_tool", "group": "dispatch", "writes": True, "flag": "GUARDIAO_MCP_ALLOW_DISPATCH"},
        {"name": "list_mcp_tools", "group": "meta", "writes": False},
    ]
    return ok({"count": len(catalog), "tools": catalog})


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
