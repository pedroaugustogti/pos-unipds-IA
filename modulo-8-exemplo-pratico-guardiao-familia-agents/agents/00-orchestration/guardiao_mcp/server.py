"""Fase B — MCP server Guardião Família (fachada sobre lib/*)."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Annotated, Any

# Pacote local + lib do módulo
_MODULE_ROOT = Path(__file__).resolve().parents[3]
if str(_MODULE_ROOT) not in sys.path:
    sys.path.insert(0, str(_MODULE_ROOT))

from lib.env_load import ensure_env  # noqa: E402

ensure_env()

from mcp.server.fastmcp import FastMCP  # noqa: E402

from guardiao_mcp.contract import fail, ok, wrap_call  # noqa: E402
from guardiao_mcp import tool_prompts as prompts  # noqa: E402
from lib.gateway import (  # noqa: E402
    approve_hitl as gateway_approve_hitl,
    emit_status_event as gateway_emit,
    list_hitl_queue as gateway_list_hitl,
)
from lib.orchestrator.event_orchestrator import (  # noqa: E402
    list_idle_agents,
    process_dispatch_queue,
    release_agent,
    resolve_agent_for_event,
)
from board_automation.board.task_router import load_tasks, pick_task  # noqa: E402
from lib.observability import build_snapshot, write_dashboard  # noqa: E402
from lib.gateway.handoff import load_handoff, write_handoff  # noqa: E402
from board_automation.board.task_action_history import append_task_action  # noqa: E402
from lib.core.model_tier import select_model  # noqa: E402
from lib.orchestrator.dispatch_adapter import dispatch_job  # noqa: E402
from lib.orchestrator.worker_jobs import load_jobs  # noqa: E402
from board_automation.board.task_status_workflow import EVENT_TARGET  # noqa: E402
from lib.mobile.qa_mobile_mcp import run_appium_suite, run_db_cleanup, run_db_seed  # noqa: E402

mcp = FastMCP(
    "guardiao-familia-agents",
    instructions=prompts.SERVER_INSTRUCTIONS,
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


@mcp.tool(description=prompts.EMIT_STATUS_EVENT)
def emit_status_event(
    task_id: Annotated[str, "ID da task no board (ex: T-P3-009)"],
    event: Annotated[str, "Evento de transição: claim, open_pr, start_review, approve_review, start_test, test_passed, test_failed_bug, merge_pr, …"],
    summary: Annotated[str, "Resumo curto do motivo da transição (recomendado em dry_run=false)"] = "",
    dry_run: Annotated[bool, "true (padrão) simula; false aplica no board"] = True,
    pr_url: Annotated[str, "URL do PR — use com event=open_pr"] = "",
    from_agent: Annotated[str, "Papel que dispara (ex: qa-gate, frontend-mobile)"] = "",
) -> str:
    """Porta única de Status do board Kanban."""
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


@mcp.tool(description=prompts.LIST_HITL_QUEUE)
def list_hitl_queue() -> str:
    """Lista fila HITL (aprovações humanas pendentes)."""
    return ok({"hitl_queue": gateway_list_hitl()})


@mcp.tool(description=prompts.APPROVE_HITL)
def approve_hitl(
    task_id: Annotated[str, "ID da task bloqueada"],
    event: Annotated[str, "Evento a liberar (ex: merge_pr)"],
    dry_run: Annotated[bool, "true (padrão) simula; false aplica"] = True,
) -> str:
    """Libera evento HITL após decisão humana."""
    return wrap_call(gateway_approve_hitl, task_id=task_id, event=event, dry_run=dry_run)


# --- Observability / model tier ---


@mcp.tool(description=prompts.SNAPSHOT_OBSERVABILITY)
def snapshot_observability(
    write_html: Annotated[bool, "true grava dashboard HTML em output/"] = False,
) -> str:
    """Snapshot de agentes, filas e Kanban."""
    try:
        snap = build_snapshot()
        path = None
        if write_html:
            path = str(write_dashboard(snap))
        return ok({"snapshot": snap, "dashboard": path})
    except Exception as exc:  # noqa: BLE001
        return fail(f"{type(exc).__name__}: {exc}")


@mcp.tool(description=prompts.SELECT_MODEL_TIER)
def select_model_tier(
    purpose: Annotated[str, "route | implement_low | implement_high | review | summarize | cursor"] = "implement_low",
    title: Annotated[str, "Título da task (contexto)"] = "",
    agent_role: Annotated[str, "Papel do agente (ex: frontend-mobile)"] = "",
    epic_id: Annotated[str, "ID do épico (opcional)"] = "",
) -> str:
    """Consulta tier de modelo recomendado."""
    task = {
        "title": title,
        "agent_role": agent_role,
        "epic_id": epic_id,
    }
    return ok(select_model(task, purpose=purpose, role=agent_role or None))


# --- Orchestrator idle / dispatch queue ---


@mcp.tool(description=prompts.LIST_IDLE_AGENTS)
def list_idle_agents_tool() -> str:
    """Lista agent_role ociosos."""
    return ok({"idle": list_idle_agents()})


@mcp.tool(description=prompts.RESOLVE_AGENT_FOR_BOARD_EVENT)
def resolve_agent_for_board_event(
    task_id: Annotated[str, "ID da task"],
    event: Annotated[str, "Evento de board (ex: approve_review, start_test)"],
) -> str:
    """Resolve agent_role responsável após evento."""
    task = _task_by_id(task_id)
    if not task:
        return fail(f"Task nao encontrada: {task_id}")
    role = resolve_agent_for_event(task, event)
    return ok({"task_id": task_id, "event": event, "agent_role": role})


@mcp.tool(description=prompts.DRAIN_DISPATCH_QUEUE)
def drain_dispatch_queue(
    limit: Annotated[int, "Máximo de jobs a despachar (padrão 5)"] = 5,
) -> str:
    """Despacha fila para agentes idle."""
    return ok({"dispatched": process_dispatch_queue(limit=limit)})


@mcp.tool(description=prompts.MARK_AGENT_IDLE)
def mark_agent_idle(
    agent_role: Annotated[str, "Papel a marcar idle (ex: frontend-mobile)"],
) -> str:
    """Marca agente idle e drena 1 job da fila."""
    release_agent(agent_role, persist=True)
    queued = process_dispatch_queue(limit=1)
    return ok({"agent_role": agent_role, "state": "idle", "drained": queued})


# --- Board / tasks ---


@mcp.tool(description=prompts.LOAD_TASKS_TOOL)
def load_tasks_tool(
    limit: Annotated[int, "Tasks retornadas (1–200, padrão 50)"] = 50,
) -> str:
    """Lista tasks do board com status."""
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


@mcp.tool(description=prompts.PICK_TASK_TOOL)
def pick_task_tool(
    agent_role: Annotated[str, "Papel do agente (ex: frontend-mobile, qa-gate)"],
    sprint: Annotated[int, "Sprint atual para filtro de elegibilidade"] = 1,
) -> str:
    """Próxima task elegível para o role."""
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


@mcp.tool(description=prompts.GET_HANDOFF)
def get_handoff(
    task_id: Annotated[str, "ID da task (ex: T-P3-009)"],
) -> str:
    """Lê handoff JSON da task."""
    data = load_handoff(task_id)
    if data is None:
        return fail(f"Handoff ausente: {task_id}", result={"task_id": task_id})
    return ok(data)


@mcp.tool(description=prompts.WRITE_HANDOFF_TOOL)
def write_handoff_tool(
    task_id: Annotated[str, "ID da task"],
    from_agent: Annotated[str, "Papel de origem"],
    to_agent: Annotated[str, "Papel de destino"],
    event: Annotated[str, "Evento de handoff (ex: open_pr)"],
    status: Annotated[str, "Status atual da task"],
    summary: Annotated[str, "Resumo da entrega"] = "",
    pr_url: Annotated[str, "URL do PR se aplicável"] = "",
    dry_run: Annotated[bool, "true (padrão) simula; false grava"] = True,
) -> str:
    """Grava handoff entre agentes."""
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


@mcp.tool(description=prompts.APPEND_TASK_ACTION_TOOL)
def append_task_action_tool(
    task_id: Annotated[str, "ID da task"],
    agent: Annotated[str, "Papel do agente (ex: qa-gate)"],
    event: Annotated[str, "Evento de board relacionado"],
    thought: Annotated[str, "Raciocínio: o que decidiu e por quê"],
    action: Annotated[str, "Tool/comando executado (nome + args resumidos)"],
    observation: Annotated[str, "Resultado lido da tool (ok/erro, paths)"] = "",
    from_status: Annotated[str, "Status antes da ação"] = "",
    to_status: Annotated[str, "Status após a ação"] = "",
    title: Annotated[str, "Título curto da ação"] = "",
    focus: Annotated[str, "Ponto específico da execução (AC, arquivo, tela)"] = "",
    model: Annotated[str, "Modelo LLM usado"] = "",
    purpose: Annotated[str, "Propósito do modelo (implement_low, review, …)"] = "",
    tokens_input: Annotated[int, "Tokens de entrada"] = 0,
    tokens_output: Annotated[int, "Tokens de saída"] = 0,
    tokens_total: Annotated[int, "Total de tokens (0 = input+output)"] = 0,
    dry_run: Annotated[bool, "true (padrão) simula; false persiste histórico"] = True,
) -> str:
    """Registra passo ReAct no histórico da task."""
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


@mcp.tool(description=prompts.DISPATCH_JOB_TOOL)
def dispatch_job_tool(
    job_id: Annotated[str, "ID do job na fila worker"],
    dry_run: Annotated[bool, "true (padrão) simula; false despacha"] = True,
) -> str:
    """Despacha job worker (requer GUARDIAO_MCP_ALLOW_DISPATCH=1)."""
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


# --- Mobile user flow RAG (Postgres pgvector) ---


@mcp.tool(description=prompts.QUERY_MOBILE_FLOW_RAG)
def query_mobile_flow_rag(
    query: Annotated[str, "Texto de busca: tela, task_id, ação, elemento (ex: ChildHomeV2 greeting T-P3-009)"],
    app_id: Annotated[str, "Filtrar app: parent | child | vazio=todos"] = "",
    chunk_type: Annotated[str, "Filtrar chunk: screen | step | vazio=todos"] = "",
    top_k: Annotated[int, "Hits retornados (1–15, padrão 5)"] = 5,
) -> str:
    """Busca semântica de fluxos mobile no pgvector."""
    try:
        from lib.mobile.mobile_flow_rag import search, search_to_user_flow

        hits = search(query, app_id=app_id or "", chunk_type=chunk_type or "", top_k=max(1, min(top_k, 15)))
        user_flow = search_to_user_flow(hits)
        return ok({"query": query, "hits": hits, "user_flow": user_flow})
    except Exception as exc:  # noqa: BLE001
        return fail(
            f"{type(exc).__name__}: {exc}",
            hint="Rode ingest_mobile_flow_rag e garanta Postgres+pgvector (DATABASE_URL)",
        )


@mcp.tool(description=prompts.INGEST_MOBILE_FLOW_RAG)
def ingest_mobile_flow_rag(
    discover_first: Annotated[bool, "true roda discovery antes de ingerir"] = False,
    fake_embed: Annotated[bool, "true usa embeddings fake (dev sem API)"] = False,
    dry_run: Annotated[bool, "true (padrão) mostra plano; false executa ingest"] = True,
) -> str:
    """Ingere fluxos mobile no índice pgvector (manutenção)."""
    if dry_run:
        return ok(
            {
                "would_run": {
                    "discover_first": discover_first,
                    "fake_embed": fake_embed,
                    "steps": [
                        "qa_discover_mobile_flows (opcional)",
                        "ingest SQLite → Postgres",
                        "embed openai/text-embedding-3-small (OpenRouter)",
                    ],
                }
            },
            dry_run=True,
        )
    try:
        from lib.mobile.mobile_flow_discovery import run_discovery
        from lib.mobile.mobile_flow_rag import ensure_schema, ingest_from_sqlite, stats_pg

        if discover_first:
            run_discovery(["parent", "child"])
        ensure_schema()
        result = ingest_from_sqlite(use_fake_embed=fake_embed)
        result["pgvector"] = stats_pg()
        return ok(result)
    except Exception as exc:  # noqa: BLE001
        return fail(f"{type(exc).__name__}: {exc}")


# --- QA mobile (seed, cleanup, Appium stack) ---


@mcp.tool(description=prompts.QA_DB_SEED)
def qa_db_seed(
    task_id: Annotated[str, "ID da task (ex: T-P3-009) — obrigatório"],
    profile: Annotated[str, "pairing_warm | child_home | permissions_resume — vazio=child_home"] = "",
    bootstrap_api: Annotated[bool, "true sobe stack API Docker se necessário"] = True,
    use_task_config: Annotated[bool, "true lê qa.db_seed da task no CSV/issue"] = True,
    dry_run: Annotated[bool, "true (padrão) simula; false executa seed Postgres + handoff"] = True,
) -> str:
    """Seed Postgres + stage-handoff para QA Appium."""
    return wrap_call(
        run_db_seed,
        pass_dry_run=False,
        dry_run=dry_run,
        task_id=task_id,
        profile=profile,
        bootstrap_api=bootstrap_api,
        use_task_config=use_task_config,
    )


@mcp.tool(description=prompts.QA_DB_CLEANUP)
def qa_db_cleanup(
    task_id: Annotated[str, "ID da task — usa cache do último qa_db_seed"] = "",
    handoff_path: Annotated[str, "Caminho explícito ao stage-handoff.json"] = "",
    parent_email: Annotated[str, "Email do parent de teste (fallback)"] = "",
    dry_run: Annotated[bool, "true (padrão) simula; false executa purge"] = True,
) -> str:
    """Cleanup pós-evidência: purge DB + reset handoff."""
    return wrap_call(
        run_db_cleanup,
        pass_dry_run=False,
        dry_run=dry_run,
        task_id=task_id,
        handoff_path=handoff_path,
        parent_email=parent_email,
    )


@mcp.tool(description=prompts.QA_APPIUM_SUITE_PARENT)
def qa_appium_suite_parent(
    skip_build: Annotated[bool, "true pula rebuild (mais rápido)"] = True,
    skip_appium: Annotated[bool, "true só sobe infra; false roda Appium"] = True,
    phase: Annotated[str, "Smoke (padrão) | Regression"] = "Smoke",
    feature: Annotated[str, "create_account | pairing | go_to_home_parent — vazio=auto com from_db_seed"] = "",
    from_db_seed: Annotated[bool, "true retoma handoff pós qa_db_seed"] = False,
    task_id: Annotated[str, "Mesmo task_id do qa_db_seed"] = "",
    timeout_sec: Annotated[int, "Timeout em segundos (padrão 1800)"] = 1800,
    dry_run: Annotated[bool, "true (padrão) simula; false executa fast-stack"] = True,
) -> str:
    """Stack Appium app parent (emulator-5554, Metro 8082)."""
    return wrap_call(
        run_appium_suite,
        pass_dry_run=False,
        dry_run=dry_run,
        app="parent",
        skip_build=skip_build,
        skip_appium=skip_appium,
        phase=phase,
        feature=feature,
        from_db_seed=from_db_seed,
        task_id=task_id,
        timeout_sec=timeout_sec,
    )


@mcp.tool(description=prompts.QA_APPIUM_SUITE_CHILD)
def qa_appium_suite_child(
    skip_build: Annotated[bool, "true pula rebuild (mais rápido)"] = True,
    skip_appium: Annotated[bool, "true só infra; false roda Appium (auto com from_db_seed)"] = True,
    phase: Annotated[str, "Smoke (padrão) | Regression"] = "Smoke",
    feature: Annotated[str, "pairing | go_to_home_child — vazio=auto com from_db_seed"] = "",
    resume_from_handoff: Annotated[bool, "legado — prefira from_db_seed=true"] = False,
    from_db_seed: Annotated[bool, "true após qa_db_seed — retoma handoff e abre ChildHome"] = False,
    task_id: Annotated[str, "Mesmo task_id do qa_db_seed (obrigatório com from_db_seed)"] = "",
    timeout_sec: Annotated[int, "Timeout em segundos (padrão 1800)"] = 1800,
    dry_run: Annotated[bool, "true (padrão) simula; false executa fast-stack dual emulator"] = True,
) -> str:
    """Stack Appium dual parent+child (5554+5556, Metro 9090)."""
    return wrap_call(
        run_appium_suite,
        pass_dry_run=False,
        dry_run=dry_run,
        app="child",
        skip_build=skip_build,
        skip_appium=skip_appium,
        phase=phase,
        feature=feature,
        resume_from_handoff=resume_from_handoff,
        from_db_seed=from_db_seed,
        task_id=task_id,
        timeout_sec=timeout_sec,
    )


@mcp.tool(description=prompts.LIST_MCP_TOOLS)
def list_mcp_tools() -> str:
    """Catálogo de tools deste servidor MCP."""
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
        {"name": "query_mobile_flow_rag", "group": "mobile_rag", "writes": False},
        {"name": "ingest_mobile_flow_rag", "group": "mobile_rag", "writes": True},
        {"name": "qa_db_seed", "group": "qa_mobile", "writes": True},
        {"name": "qa_db_cleanup", "group": "qa_mobile", "writes": True},
        {"name": "qa_appium_suite_parent", "group": "qa_mobile", "writes": True},
        {"name": "qa_appium_suite_child", "group": "qa_mobile", "writes": True},
        {"name": "list_mcp_tools", "group": "meta", "writes": False},
    ]
    return ok({"count": len(catalog), "tools": catalog})


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
