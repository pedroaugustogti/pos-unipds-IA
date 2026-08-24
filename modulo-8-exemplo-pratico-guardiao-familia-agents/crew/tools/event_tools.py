"""CrewAI tools — orquestracao por eventos de status do board."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_LIB = Path(__file__).resolve().parents[2]
if str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))

from lib.event_orchestrator import (  # noqa: E402
    BUG_THRESHOLD,
    emit_board_event,
    list_idle_agents,
    load_runtime,
    notify_status_change,
    process_dispatch_queue,
    record_bug,
    release_agent,
    resolve_agent_for_event,
    skill_impact_for_task,
)
from lib.gateway import approve_hitl, emit_status_event as gateway_emit, list_hitl_queue  # noqa: E402
from lib.task_router import load_tasks  # noqa: E402
from lib.task_status_workflow import EVENT_TARGET  # noqa: E402
from lib.observability import build_snapshot, write_dashboard  # noqa: E402

_DRY_RUN = False


def set_dry_run(value: bool) -> None:
    global _DRY_RUN
    _DRY_RUN = value


try:
    from crewai.tools import tool
except ImportError:
    def tool(name: str):  # type: ignore[misc]
        def deco(fn):
            fn.name = name  # type: ignore[attr-defined]
            return fn
        return deco


@tool("Emitir evento de status no board")
def emit_status_event(task_id: str, event: str, summary: str = "") -> str:
    """Porta unica (gateway): contrato + HITL + handoff + board.

    Eventos: claim, open_pr, start_review, request_changes, resubmit_review,
    approve_review, start_test, test_failed_bug, test_passed, merge_pr, reopen.
    merge_pr e blocker(3 bugs) exigem HITL humano.
    """
    if event not in EVENT_TARGET and event not in ("hitl_approved", "hitl_rejected"):
        return json.dumps({
            "ok": False,
            "error": f"Evento invalido: {event}",
            "allowed": sorted(EVENT_TARGET),
        }, ensure_ascii=False)
    result = gateway_emit(
        task_id, event, summary=summary, dry_run=_DRY_RUN, apply_board=True,
    )
    return json.dumps(result, ensure_ascii=False, indent=2)


@tool("Listar fila HITL")
def list_pending_hitl() -> str:
    """Lista eventos aguardando aprovacao humana (merge, blocker, review alto risco)."""
    return json.dumps({"hitl_queue": list_hitl_queue()}, ensure_ascii=False, indent=2)


@tool("Aprovar HITL humano")
def approve_pending_hitl(task_id: str, event: str) -> str:
    """Libera evento bloqueado apos decisao humana (ex.: merge_pr)."""
    result = approve_hitl(task_id, event, dry_run=_DRY_RUN)
    return json.dumps(result, ensure_ascii=False, indent=2)


@tool("Notificar mudanca de status")
def notify_board_status_change(
    task_id: str,
    event: str,
    from_status: str = "",
    to_status: str = "",
    summary: str = "",
) -> str:
    """Somente notificacao: verifica agentes ociosos e quem chamar (sem gravar board)."""
    result = notify_status_change(
        task_id,
        event if event else None,
        from_status=from_status or None,
        to_status=to_status or None,
        summary=summary,
        dry_run=_DRY_RUN,
    )
    return json.dumps(result, ensure_ascii=False, indent=2)


@tool("Listar agentes ociosos")
def list_idle_crew_agents() -> str:
    """Lista agentes com state=idle no runtime do crew."""
    idle = list_idle_agents()
    rt = load_runtime()
    busy = {
        k: v for k, v in rt.get("agents", {}).items() if v.get("state") == "busy"
    }
    return json.dumps({
        "idle": idle,
        "busy": busy,
        "queue_len": len(rt.get("dispatch_queue") or []),
        "blockers": rt.get("blockers") or [],
    }, ensure_ascii=False, indent=2)


@tool("Resolver agente para evento")
def resolve_agent_for_board_event(task_id: str, event: str) -> str:
    """Retorna qual agente chamar apos o evento, com skill impactada."""
    task = next((t for t in load_tasks() if t["id"] == task_id), None)
    if not task:
        return json.dumps({"ok": False, "error": f"Task {task_id} nao encontrada"})
    if event not in EVENT_TARGET:
        return json.dumps({"ok": False, "error": f"Evento invalido: {event}"})
    agent = resolve_agent_for_event(task, event)
    idle = list_idle_agents()
    return json.dumps({
        "ok": True,
        "task_id": task_id,
        "event": event,
        "target_status": EVENT_TARGET[event],
        "call_agent": agent,
        "agent_idle": agent in idle,
        "idle_agents": idle,
        "skill": skill_impact_for_task(task),
    }, ensure_ascii=False, indent=2)


@tool("Registrar bug e checar blocker")
def register_task_bug(task_id: str, summary: str) -> str:
    """Incrementa bugs da task. No 3o bug: blocker + motivo + skill impactada."""
    result = record_bug(task_id, summary, threshold=BUG_THRESHOLD, dry_run=_DRY_RUN)
    if result.get("blocker"):
        # Notifica como se fosse test_failed_bug ja no limite
        note = notify_status_change(
            task_id,
            "test_failed_bug",
            from_status="In Test",
            to_status="In Progress",
            summary=summary,
            dry_run=_DRY_RUN,
        )
        result["notification"] = note
    return json.dumps(result, ensure_ascii=False, indent=2)


@tool("Processar fila de dispatch")
def drain_dispatch_queue(limit: int = 5) -> str:
    """Despacha eventos enfileirados quando agentes ficam ociosos."""
    dispatched = process_dispatch_queue(limit=limit)
    return json.dumps({
        "dispatched": dispatched,
        "idle": list_idle_agents(),
    }, ensure_ascii=False, indent=2)


@tool("Liberar agente")
def mark_agent_idle(agent_role: str) -> str:
    """Marca agente como idle apos concluir etapa."""
    meta = release_agent(agent_role)
    queued = process_dispatch_queue(limit=1)
    return json.dumps({
        "agent": agent_role,
        "state": meta,
        "followed_up": queued,
    }, ensure_ascii=False, indent=2)


@tool("Resumo de observabilidade")
def observability_summary() -> str:
    """Snapshot do fluxo: idle/busy, fila, blockers, eventos recentes. Regenera dashboard."""
    snap = build_snapshot()
    write_dashboard(snap)
    return json.dumps({
        "totals": snap.get("totals"),
        "busy_agents": snap.get("busy_agents"),
        "idle_agents": snap.get("idle_agents"),
        "blockers": snap.get("blockers"),
        "recent_tasks": snap.get("recent_tasks"),
        "timeline": (snap.get("timeline") or [])[-15:],
        "paths": snap.get("paths"),
    }, ensure_ascii=False, indent=2)


EVENT_TOOLS = [
    emit_status_event,
    list_pending_hitl,
    approve_pending_hitl,
    notify_board_status_change,
    list_idle_crew_agents,
    resolve_agent_for_board_event,
    register_task_bug,
    drain_dispatch_queue,
    mark_agent_idle,
    observability_summary,
]
