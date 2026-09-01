"""Fase B — MCP server Guardião Família (fachada sobre lib/*)."""

from __future__ import annotations

import json
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
from lib.gateway import emit_status_event as gateway_emit  # noqa: E402
from lib.gateway.actuation_guardrail import evaluate_actuation_guard  # noqa: E402
from board_automation.board.task_router import load_tasks  # noqa: E402
from lib.mobile.qa_mobile_mcp import run_appium_suite, run_db_cleanup, run_db_seed  # noqa: E402
from board_automation.board.task_status_workflow import (  # noqa: E402
    build_event,
    is_known_event,
    role_event_catalog,
    validate_role_event_for_task,
)
from lib.orchestrator.event_actuation_context import prepare_actuation_for_event  # noqa: E402

mcp = FastMCP(
    "guardiao-familia-agents",
    instructions=prompts.SERVER_INSTRUCTIONS,
)


def _task_by_id(task_id: str) -> dict[str, Any] | None:
    return next((t for t in load_tasks() if t.get("id") == task_id), None)


# --- Gateway / HITL ---


@mcp.tool(description=prompts.EMIT_STATUS_EVENT)
def emit_status_event(
    task_id: Annotated[str, "ID da task no board (ex: T-P3-009)"],
    event: Annotated[
        str,
        "Evento role-based ({agent_role}_{status_slug}). "
        "Alternativa: deixe vazio e use agent_role + board_status.",
    ] = "",
    agent_role: Annotated[
        str,
        "Papel que emite (ex: frontend-mobile, frontend-mobile-reviewer, qa-gate). "
        "Com board_status monta o evento automaticamente.",
    ] = "",
    board_status: Annotated[
        str,
        "Status alvo no board (ex: In Progress, Ready for Code Review). "
        "Usado com agent_role para montar o evento.",
    ] = "",
    return_event: Annotated[
        bool,
        "true → evento de retrocesso ({agent_role}_return_{status_slug}), ex: request_changes",
    ] = False,
    summary: Annotated[str, "Resumo curto do motivo da transição (recomendado em dry_run=false)"] = "",
    dry_run: Annotated[bool, "true (padrão) simula; false aplica no board"] = True,
    pr_url: Annotated[str, "URL do PR — use em {creator}_ready_for_code_review"] = "",
    from_agent: Annotated[str, "Papel que dispara (deve bater com o prefixo do evento role-based)"] = "",
) -> str:
    """Porta única de Status do board Kanban."""
    task = _task_by_id(task_id)
    if not task:
        return fail(f"Task nao encontrada: {task_id}", dry_run=dry_run)

    resolved_event = (event or "").strip()
    if agent_role and board_status:
        resolved_event = build_event(agent_role, board_status, return_=return_event)
    elif not resolved_event:
        return fail(
            "Informe event OU (agent_role + board_status)",
            dry_run=dry_run,
            hint="Ex: event=frontend-mobile_in_progress ou agent_role=frontend-mobile, board_status=In Progress",
        )

    if not is_known_event(resolved_event) and resolved_event not in (
        "hitl_approved",
        "hitl_rejected",
    ):
        return fail(
            f"Evento invalido: {resolved_event}",
            dry_run=dry_run,
            catalog_tool="list_status_events",
        )

    role_err = validate_role_event_for_task(
        resolved_event,
        from_agent=from_agent,
        task_agent_role=task.get("agent_role"),
    )
    if role_err:
        return fail(role_err, dry_run=dry_run, event=resolved_event, from_agent=from_agent)

    return wrap_call(
        gateway_emit,
        task_id=task_id,
        event=resolved_event,
        summary=summary,
        dry_run=dry_run,
        apply_board=True,
        pr_url=pr_url or None,
        from_agent=from_agent or None,
    )


@mcp.tool(description=prompts.LIST_STATUS_EVENTS)
def list_status_events(
    agent_role: Annotated[str, "Filtrar por papel (ex: frontend-mobile). Vazio = todos."] = "",
    classification: Annotated[
        str,
        "Filtrar por classificação: creator, reviewer, qa-gate, ops, orchestrator",
    ] = "",
) -> str:
    """Catálogo de eventos role-based alinhados a agent_role e board status."""
    rows = role_event_catalog()
    if agent_role:
        rows = [r for r in rows if r["agent_role"] == agent_role]
    if classification:
        rows = [r for r in rows if r["classification"] == classification]
    return ok({
        "pattern_advance": "{agent_role}_{status_slug}",
        "pattern_return": "{agent_role}_return_{status_slug}",
        "events": rows,
        "count": len(rows),
    })


@mcp.tool(description=prompts.ON_STATUS_EVENT)
def on_status_event(
    task_id: Annotated[str, "ID da task (ex: T-P3-009)"],
    event: Annotated[
        str,
        "Evento emitido (role-based). Opcional se usar agent_role + board_status.",
    ] = "",
    agent_role: Annotated[str, "Monta evento com board_status (mesma regra de emit_status_event)"] = "",
    board_status: Annotated[str, "Status alvo do evento (ex: In Progress, In Test)"] = "",
    return_event: Annotated[bool, "true se o evento foi retrocesso (_return_)"] = False,
) -> str:
    """Após emit_status_event: identifica agente, lê ticket e extrai contexto de atuação."""
    try:
        result = prepare_actuation_for_event(
            task_id,
            event,
            agent_role=agent_role,
            board_status=board_status,
            return_event=return_event,
        )
    except Exception as exc:  # noqa: BLE001
        return fail(f"{type(exc).__name__}: {exc}")
    if not result.get("ok"):
        return fail(str(result.get("error") or "falha ao preparar contexto"), **result)
    return ok(result)


@mcp.tool(description=prompts.HITL_GUARD_ACTUATION)
def hitl_guard_actuation(
    actuation_context: Annotated[
        str,
        "JSON retornado por on_status_event (objeto completo ou campo result)",
    ],
    mode: Annotated[
        str,
        "dry_run | live — influencia score de merge/release (padrão: GUARDIAO_LANGGRAPH_MODE)",
    ] = "",
    human_clearance: Annotated[
        bool,
        "true após triagem humana no board libera contexto bloqueado",
    ] = False,
    clearance_note: Annotated[str, "Motivo da liberação humana (obrigatório se human_clearance=true)"] = "",
    dry_run: Annotated[bool, "true (padrão) não comenta na issue; false notifica board em bloqueio"] = True,
) -> str:
    """Valida contexto contra policy antes de execute_agent_actuation_tool."""
    run_mode = (mode or os.environ.get("GUARDIAO_LANGGRAPH_MODE") or "dry_run").strip()
    if human_clearance and not clearance_note.strip():
        return fail("clearance_note obrigatório quando human_clearance=true")
    try:
        result = evaluate_actuation_guard(
            actuation_context,
            mode=run_mode,
            human_clearance=human_clearance,
            clearance_note=clearance_note,
            dry_run=dry_run,
        )
    except Exception as exc:  # noqa: BLE001
        return fail(f"{type(exc).__name__}: {exc}")
    if result.get("blocked"):
        return fail(result.get("message") or "contexto bloqueado pelo guardrail", **result)
    return ok(result)


@mcp.tool(description=prompts.EXECUTE_AGENT_ACTUATION)
def execute_agent_actuation_tool(
    actuation_context: Annotated[
        str,
        "JSON retornado por on_status_event (objeto completo ou campo result)",
    ],
    guard_pass_id: Annotated[
        str,
        "Token de uso único retornado por hitl_guard_actuation (obrigatório)",
    ],
    mode: Annotated[
        str,
        "dry_run (padrão) simula trabalho+emit; live aplica no board",
    ] = "",
    use_role_events: Annotated[
        bool,
        "true (padrão) emite evento role-based no final (ex: frontend-mobile_ready_for_code_review)",
    ] = True,
    phase_work: Annotated[
        str,
        "JSON opcional — resultado de developer_implement/review/qa_validate; evita reexecutar fase",
    ] = "",
) -> str:
    """Executa fase do agente a partir do contexto on_status_event e emite próximo evento."""
    from lib.orchestrator.event_actuation_runner import execute_agent_actuation

    pw: dict[str, Any] | None = None
    if phase_work.strip():
        try:
            pw = json.loads(phase_work)
        except json.JSONDecodeError:
            return fail("phase_work JSON invalido")

    try:
        result = execute_agent_actuation(
            actuation_context,
            guard_pass_id=guard_pass_id,
            mode=mode or None,
            use_role_events=use_role_events,
            phase_work=pw,
        )
    except Exception as exc:  # noqa: BLE001
        return fail(f"{type(exc).__name__}: {exc}")
    if not result.get("ok"):
        return fail(str(result.get("error") or "falha na execucao"), result=result)
    return ok(result)


# --- Orchestrator ---


@mcp.tool(description=prompts.ORCHESTRATOR_ENTER_IN_PROGRESS)
def orchestrator_enter_in_progress(
    sprint: Annotated[int, "Sprint para priorização (bonus se task do sprint atual)"] = 1,
    sprint_only: Annotated[bool, "true limita a tasks do sprint informado"] = False,
    task_id: Annotated[str, "ID fixo (opcional); se vazio, escolhe Todo de maior prioridade"] = "",
    summary: Annotated[str, "Resumo do claim (recomendado em dry_run=false)"] = "",
    dry_run: Annotated[bool, "true (padrão) simula; false aplica no board"] = True,
) -> str:
    """Seleciona task Todo prioritária e emite orchestrator_enter_in_progress."""
    from lib.orchestrator.orchestrator_claim import orchestrator_enter_priority_todo

    result = orchestrator_enter_priority_todo(
        task_id=task_id.strip(),
        sprint=sprint,
        sprint_only=sprint_only,
        summary=summary,
        dry_run=dry_run,
    )
    if not result.get("ok"):
        return fail(str(result.get("error") or "falha no claim"), result=result)
    return ok(result, dry_run=dry_run)


# --- Fases de trabalho (implement / review / qa) ---


@mcp.tool(description=prompts.DEVELOPER_IMPLEMENT)
def developer_implement(
    actuation_context: Annotated[
        str,
        "JSON retornado por on_status_event (objeto completo ou campo result)",
    ],
    mode: Annotated[str, "dry_run | live"] = "",
) -> str:
    """Codificação + testes unitários a partir do contexto e skill do agente."""
    from lib.orchestrator.phase_developer_implement import run_developer_implement

    try:
        result = run_developer_implement(actuation_context, mode=mode or None)
    except Exception as exc:  # noqa: BLE001
        return fail(f"{type(exc).__name__}: {exc}")
    if not result.get("ok"):
        return fail(str(result.get("error") or "falha implement"), result=result)
    return ok(result)


@mcp.tool(description=prompts.DEVELOPER_REVIEW)
def developer_review(
    actuation_context: Annotated[str, "JSON de on_status_event"],
    mode: Annotated[str, "dry_run | live"] = "",
) -> str:
    """Review de código: arquitetura, manutenibilidade, testes, boas práticas."""
    from lib.orchestrator.phase_developer_review import run_developer_review

    try:
        result = run_developer_review(actuation_context, mode=mode or None)
    except Exception as exc:  # noqa: BLE001
        return fail(f"{type(exc).__name__}: {exc}")
    if not result.get("ok"):
        return fail(str(result.get("error") or "falha review"), result=result)
    return ok(result)


@mcp.tool(description=prompts.QA_VALIDATE)
def qa_validate(
    actuation_context: Annotated[str, "JSON de on_status_event"],
    mode: Annotated[str, "dry_run | live"] = "",
) -> str:
    """QA gate: ambiente mobile MCP + evidências + validação de AC."""
    from lib.orchestrator.phase_qa_validate import run_qa_validate

    try:
        result = run_qa_validate(actuation_context, mode=mode or None)
    except Exception as exc:  # noqa: BLE001
        return fail(f"{type(exc).__name__}: {exc}")
    if not result.get("ok") and result.get("decision", {}).get("next_event") != "test_failed_bug":
        return fail(str(result.get("error") or "falha qa"), result=result)
    return ok(result)


# --- QA mobile (seed, cleanup, Appium stack) ---


@mcp.tool(description=prompts.QA_DB_SEED)
def qa_db_seed(
    task_id: Annotated[str, "ID da task (ex: T-P3-009) — obrigatório"],
    profile: Annotated[str, "pairing_warm | basic_parent | parent_home | child_home | permissions_resume — vazio=child_home"] = "",
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
    phase: Annotated[str, "All (padrão) | Api | Boot | Metro | Build | Smoke"] = "All",
    feature: Annotated[str, "create_account | config_family | login | pairing | go_to_home_parent — vazio=auto"] = "",
    from_db_seed: Annotated[bool, "true retoma handoff pós qa_db_seed"] = False,
    task_id: Annotated[str, "Mesmo task_id do qa_db_seed"] = "",
    parent_only: Annotated[
        bool,
        "true só parent 5554 — auto com from_db_seed (parent_home); evita boot child",
    ] = False,
    reset_handoff_after: Annotated[
        bool,
        "true (padrão com from_db_seed/task_id) zera stage-handoff ao final",
    ] = True,
    timeout_sec: Annotated[int, "Timeout em segundos (padrão 1800)"] = 1800,
    dry_run: Annotated[bool, "true (padrão) simula; false executa fast-stack"] = True,
) -> str:
    """Stack Appium app parent (emulator-5554, Metro 8082)."""
    effective_skip_appium = skip_appium if not from_db_seed else False
    return wrap_call(
        run_appium_suite,
        pass_dry_run=False,
        dry_run=dry_run,
        app="parent",
        skip_build=skip_build,
        skip_appium=effective_skip_appium,
        phase=phase,
        feature=feature,
        from_db_seed=from_db_seed,
        task_id=task_id,
        parent_only=parent_only,
        reset_handoff_after=reset_handoff_after,
        timeout_sec=timeout_sec,
    )


@mcp.tool(description=prompts.QA_APPIUM_SUITE_CHILD)
def qa_appium_suite_child(
    skip_build: Annotated[bool, "true pula rebuild (mais rápido)"] = True,
    skip_appium: Annotated[bool, "true só infra; false roda Appium (auto com from_db_seed)"] = True,
    phase: Annotated[str, "All (padrão) | Api | Boot | Metro | Build | Smoke"] = "All",
    feature: Annotated[str, "pairing | go_to_home_child — vazio=auto com from_db_seed"] = "",
    resume_from_handoff: Annotated[bool, "legado — prefira from_db_seed=true"] = False,
    child_only: Annotated[bool, "true: QA child sem exigir parent home — auto com seed child"] = False,
    from_db_seed: Annotated[bool, "true após qa_db_seed — retoma handoff e abre ChildHome"] = False,
    task_id: Annotated[str, "Mesmo task_id do qa_db_seed (obrigatório com from_db_seed)"] = "",
    reset_handoff_after: Annotated[
        bool,
        "true (padrão com from_db_seed/task_id) zera stage-handoff ao final",
    ] = True,
    timeout_sec: Annotated[int, "Timeout em segundos (padrão 1800)"] = 1800,
    dry_run: Annotated[bool, "true (padrão) simula; false executa fast-stack dual emulator"] = True,
) -> str:
    """Stack Appium dual parent+child (5554+5556, Metro 9090)."""
    effective_skip_appium = skip_appium if not (from_db_seed or child_only) else False
    return wrap_call(
        run_appium_suite,
        pass_dry_run=False,
        dry_run=dry_run,
        app="child",
        skip_build=skip_build,
        skip_appium=effective_skip_appium,
        phase=phase,
        feature=feature,
        resume_from_handoff=resume_from_handoff,
        from_db_seed=from_db_seed,
        task_id=task_id,
        timeout_sec=timeout_sec,
        child_only=child_only,
        reset_handoff_after=reset_handoff_after,
    )


@mcp.tool(description=prompts.LIST_MCP_TOOLS)
def list_mcp_tools() -> str:
    """Catálogo de tools deste servidor MCP."""
    catalog = [
        {"name": "emit_status_event", "group": "gateway", "writes": True},
        {"name": "list_status_events", "group": "gateway", "writes": False},
        {"name": "on_status_event", "group": "gateway", "writes": False},
        {"name": "hitl_guard_actuation", "group": "gateway", "writes": True},
        {"name": "developer_implement", "group": "phase", "writes": True},
        {"name": "developer_review", "group": "phase", "writes": True},
        {"name": "qa_validate", "group": "phase", "writes": True},
        {"name": "execute_agent_actuation_tool", "group": "gateway", "writes": True},
        {"name": "orchestrator_enter_in_progress", "group": "orchestrator", "writes": True},
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
