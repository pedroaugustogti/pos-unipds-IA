"""Orquestracao por eventos de status: idle agents, dispatch e blocker por bugs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lib.local_board import get_local_status, mark_local_blocker
from lib.paths import RUNTIME_PATH
from lib.reviewer_pairs import CREATOR_ROLES, QA_GATE_ROLE, normalize_creator_role, reviewer_for
from lib.task_router import load_tasks
from lib.task_status_workflow import (
    EVENT_TARGET,
    apply_event,
    merge_owner_for_task,
    resolve_status,
)

BUG_THRESHOLD = 3

SKILL_IMPACT: dict[str, dict[str, str]] = {
    "backend": {
        "skill": "backend",
        "path": "skills/backend/SKILL.md",
        "impact": "Implementacao NestJS/API, contratos e integracoes — falhas recorrentes em codigo de dominio.",
    },
    "frontend-mobile": {
        "skill": "frontend-mobile",
        "path": "skills/frontend-mobile/SKILL.md",
        "impact": "Apps parent/child (Expo/RN), push, SOS e geofence — regressao de UX/device.",
    },
    "frontend-web": {
        "skill": "frontend-web",
        "path": "skills/frontend-web/SKILL.md",
        "impact": "Backoffice/site Next.js — fluxos web e painel operacional.",
    },
    "cloud-infra": {
        "skill": "cloud-infra",
        "path": "skills/cloud-infra/SKILL.md",
        "impact": "Terraform/AWS ECS — ambiente ou rede inconsistente afeta deploy e testes.",
    },
    "database": {
        "skill": "database",
        "path": "skills/database/SKILL.md",
        "impact": "Migrations/PostgreSQL/Redis — schema ou dados corrompem cenarios E2E.",
    },
    "devops-cicd": {
        "skill": "devops-cicd",
        "path": "skills/devops-cicd/SKILL.md",
        "impact": "CI/CD e observabilidade — builds/artefatos instaveis geram falsos bugs.",
    },
    "qa": {
        "skill": "qa",
        "path": "skills/qa/SKILL.md",
        "impact": "Harness E2E/cenarios — se bugs forem flaky, a skill QA precisa estabilizar evidencias.",
    },
    "qa-author": {
        "skill": "qa",
        "path": "skills/qa/SKILL.md",
        "impact": "Harness/cenarios escritos pelo qa-author — estabilizar evidencias.",
    },
    "qa-gate": {
        "skill": "qa",
        "path": "skills/qa/SKILL.md",
        "impact": "Execucao do gate de testes — flaky ou harness instavel.",
    },
    "stores-release": {
        "skill": "stores-release",
        "path": "skills/stores-release/SKILL.md",
        "impact": "Release stores/compliance — bloqueio de submissao ou checklist release.",
    },
}

# Evento → acao esperada do agente chamado
EVENT_START_HINT: dict[str, str] = {
    "claim": "Iniciar implementacao (In Progress)",
    "start_work": "Retomar implementacao",
    "open_pr": "Aguardar/assumir fila de code review",
    "start_review": "Executar checklist de review",
    "request_changes": "Corrigir CR e reenviar",
    "resubmit_review": "Re-revisar PR apos correcoes",
    "approve_review": "Planejar testes (Ready for Test)",
    "start_test": "Executar suite QA (In Test)",
    "test_failed_bug": "Corrigir bug reportado pelo QA",
    "test_passed": "Preparar merge (In Pull Request)",
    "merge_pr": "Encerrar ciclo (Done)",
    "reopen": "Reabrir no backlog (Todo)",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_runtime() -> dict[str, Any]:
    agents = {}
    for role in CREATOR_ROLES:
        agents[role] = {"state": "idle", "task_id": None, "updated_at": _now()}
        agents[reviewer_for(role)] = {"state": "idle", "task_id": None, "updated_at": _now()}
    agents[QA_GATE_ROLE] = {"state": "idle", "task_id": None, "updated_at": _now()}
    agents["orchestrator"] = {"state": "idle", "task_id": None, "updated_at": _now()}
    agents["human"] = {"state": "idle", "task_id": None, "updated_at": _now()}
    return {
        "version": 2,
        "updated_at": _now(),
        "agents": agents,
        "bug_counts": {},
        "blockers": [],
        "event_log": [],
        "dispatch_queue": [],
        "hitl_queue": [],
        "idempotency": {},
    }


def load_runtime(path: Path | None = None) -> dict[str, Any]:
    p = path or RUNTIME_PATH
    if not p.exists():
        data = _default_runtime()
        save_runtime(data, p)
        return data
    data = json.loads(p.read_text(encoding="utf-8"))
    # garantir chaves de agentes novos
    base = _default_runtime()["agents"]
    agents = data.setdefault("agents", {})
    for k, v in base.items():
        agents.setdefault(k, v)
    data.setdefault("bug_counts", {})
    data.setdefault("blockers", [])
    data.setdefault("event_log", [])
    data.setdefault("dispatch_queue", [])
    data.setdefault("hitl_queue", [])
    data.setdefault("idempotency", {})
    return data


def save_runtime(data: dict[str, Any], path: Path | None = None) -> Path:
    p = path or RUNTIME_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = _now()
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p


def list_idle_agents(runtime: dict[str, Any] | None = None) -> list[str]:
    rt = runtime or load_runtime()
    return sorted(
        name for name, meta in rt.get("agents", {}).items() if meta.get("state") == "idle"
    )


def set_agent_state(
    agent: str,
    state: str,
    task_id: str | None = None,
    *,
    runtime: dict[str, Any] | None = None,
    persist: bool = True,
) -> dict[str, Any]:
    rt = runtime or load_runtime()
    meta = rt.setdefault("agents", {}).setdefault(
        agent, {"state": "idle", "task_id": None, "updated_at": _now()}
    )
    meta["state"] = state
    meta["task_id"] = task_id if state == "busy" else None
    meta["updated_at"] = _now()
    if persist:
        save_runtime(rt)
    return meta


def release_agent(agent: str, *, persist: bool = True) -> dict[str, Any]:
    return set_agent_state(agent, "idle", None, persist=persist)


def _task_by_id(task_id: str) -> dict | None:
    return next((t for t in load_tasks() if t["id"] == task_id), None)


def resolve_agent_for_status(task: dict, status: str) -> str:
    """Qual agente deve iniciar/continuar a task neste status."""
    st = resolve_status(status)
    creator = normalize_creator_role(task.get("agent_role") or "backend")
    track = task.get("track") or "produto"

    if st == "Todo":
        return "orchestrator"
    if st == "In Progress":
        return creator
    if st in ("Ready for Code Review", "In Code Review"):
        return reviewer_for(creator)
    if st in ("Ready for Test", "In Test"):
        return QA_GATE_ROLE
    if st == "In Pull Request":
        return merge_owner_for_task(track)
    if st == "Done":
        return "orchestrator"
    return creator


def resolve_agent_for_event(task: dict, event: str) -> str:
    target = EVENT_TARGET.get(event)
    if not target:
        raise ValueError(f"Evento desconhecido: {event}")
    return resolve_agent_for_status(task, target)


def skill_impact_for_task(task: dict, *, bug_kind: str | None = None) -> dict[str, str]:
    role = normalize_creator_role(task.get("agent_role") or "backend")
    if bug_kind == "flaky":
        info = dict(SKILL_IMPACT.get("qa-gate", SKILL_IMPACT["qa"]))
        info["agent_role"] = "qa-gate"
        info["bug_kind"] = "flaky"
        return info
    info = dict(SKILL_IMPACT.get(role, SKILL_IMPACT["backend"]))
    info["agent_role"] = role
    info["bug_kind"] = bug_kind or "regression"
    return info


def record_bug(
    task_id: str,
    summary: str = "",
    *,
    threshold: int = BUG_THRESHOLD,
    dry_run: bool = False,
    bug_kind: str | None = None,
) -> dict[str, Any]:
    """Incrementa contador de bugs da task. No 3o: blocker + skill impactada."""
    task = _task_by_id(task_id)
    if not task:
        return {"ok": False, "error": f"Task {task_id} nao encontrada"}

    # Inferir flaky vs regression a partir do summary se nao informado
    kind = bug_kind
    if not kind:
        low = (summary or "").lower()
        kind = "flaky" if "flaky" in low or "[flaky]" in low else "regression"

    rt = load_runtime()
    entry = rt.setdefault("bug_counts", {}).setdefault(
        task_id,
        {"count": 0, "history": [], "skill": task.get("agent_role"), "blocker": False},
    )
    entry["count"] = int(entry.get("count") or 0) + 1
    entry["history"].append({"at": _now(), "summary": (summary or "")[:500], "bug_kind": kind})
    entry["history"] = entry["history"][-10:]
    skill = skill_impact_for_task(task, bug_kind=kind)
    entry["skill"] = skill["skill"]
    entry["skill_path"] = skill["path"]
    entry["bug_kind"] = kind

    result: dict[str, Any] = {
        "ok": True,
        "task_id": task_id,
        "bug_count": entry["count"],
        "threshold": threshold,
        "blocker": False,
        "skill": skill,
        "bug_kind": kind,
        "dry_run": dry_run,
    }

    if entry["count"] >= threshold:
        reason = (
            f"BLOCKER automatico: {entry['count']} bugs na mesma task {task_id} "
            f"(ultimo tipo={kind}). "
            f"Skill impactada: `{skill['skill']}` ({skill['path']}). "
            f"Impacto: {skill['impact']} "
            f"Ultimo resumo: {(summary or 'n/d')[:300]}"
        )
        local = {"ok": True, "dry_run": True, "reason": reason}
        if not dry_run:
            local = mark_local_blocker(task_id, reason)
        entry["blocker"] = True
        entry["blocker_reason"] = reason
        blocker_row = {
            "task_id": task_id,
            "title": task.get("title"),
            "bug_count": entry["count"],
            "bug_kind": kind,
            "skill": skill["skill"],
            "skill_path": skill["path"],
            "skill_impact": skill["impact"],
            "reason": reason,
            "at": _now(),
            "local_board": local,
            "hitl_required": True,
        }
        blockers = rt.setdefault("blockers", [])
        blockers[:] = [b for b in blockers if b.get("task_id") != task_id]
        blockers.append(blocker_row)
        result["blocker"] = True
        result["blocker_notification"] = blocker_row

    if not dry_run:
        save_runtime(rt)
    else:
        save_runtime(rt)
    result["runtime_path"] = str(RUNTIME_PATH)
    return result


def notify_status_change(
    task_id: str,
    event: str | None,
    *,
    from_status: str | None = None,
    to_status: str | None = None,
    summary: str = "",
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Notifica mudanca de status como evento:
    - resolve agente destino
    - lista agentes ociosos
    - se ocioso: dispatch (busy); senao: enfileira
    - se event=test_failed_bug: conta bugs e pode virar blocker (3x)
    """
    task = _task_by_id(task_id)
    if not task:
        return {"ok": False, "error": f"Task {task_id} nao encontrada"}

    current = from_status or get_local_status(task_id) or task.get("board_status") or "Todo"
    current = resolve_status(current)

    if event:
        if event not in EVENT_TARGET:
            return {"ok": False, "error": f"Evento invalido: {event}"}
        target = to_status or apply_event(current, event)
    else:
        if not to_status:
            return {"ok": False, "error": "Informe event ou to_status"}
        target = resolve_status(to_status)
        event = event or "status_change"

    target = resolve_status(target)
    next_agent = resolve_agent_for_status(task, target)
    idle = list_idle_agents()
    agent_idle = next_agent in idle

    bug_info = None
    if event == "test_failed_bug":
        bug_info = record_bug(task_id, summary, dry_run=dry_run)

    notification = {
        "ok": True,
        "type": "status_change",
        "event": event,
        "task_id": task_id,
        "title": task.get("title"),
        "from": current,
        "to": target,
        "next_agent": next_agent,
        "start_hint": EVENT_START_HINT.get(str(event), f"Atuar em status {target}"),
        "idle_agents": idle,
        "agent_idle": agent_idle,
        "dispatch": None,
        "queued": False,
        "blocker": None,
        "skill_impact": skill_impact_for_task(task),
        "at": _now(),
    }

    if bug_info and bug_info.get("blocker"):
        notification["blocker"] = bug_info.get("blocker_notification")
        notification["type"] = "blocker"
        # libera agentes da task e nao despacha trabalho novo sem triagem
        rt = load_runtime()
        for name, meta in rt.get("agents", {}).items():
            if meta.get("task_id") == task_id:
                meta["state"] = "idle"
                meta["task_id"] = None
                meta["updated_at"] = _now()
        save_runtime(rt)
        notification["idle_agents"] = list_idle_agents()
        notification["dispatch"] = {
            "action": "blocked",
            "message": "Task bloqueada apos 3 bugs — triagem humana/orchestrator obrigatoria.",
            "call_agent": "orchestrator",
        }
    elif agent_idle and next_agent != "orchestrator":
        if not dry_run:
            set_agent_state(next_agent, "busy", task_id)
        job_info: dict[str, Any] | None = None
        if not dry_run:
            try:
                from lib.worker_jobs import enqueue_job
                job_info = enqueue_job(
                    task_id=task_id,
                    role=next_agent,
                    event=str(event),
                    mirror_runtime_queue=False,
                )
            except Exception as exc:  # noqa: BLE001
                job_info = {"ok": False, "error": str(exc)}
        notification["dispatch"] = {
            "action": "start_task",
            "call_agent": next_agent,
            "task_id": task_id,
            "status": target,
            "hint": notification["start_hint"],
            "job": job_info,
            "message": (
                f"Agente `{next_agent}` ocioso — job enfileirado. "
                f"Rode: python scripts/worker_run.py --next --role {next_agent}"
            ),
        }
    elif next_agent == "orchestrator":
        notification["dispatch"] = {
            "action": "orchestrator_only",
            "call_agent": "orchestrator",
            "message": f"Status {target} nao exige specialist — orchestrator fecha/planeja.",
        }
    else:
        if not dry_run:
            rt = load_runtime()
            q = rt.setdefault("dispatch_queue", [])
            q.append({
                "task_id": task_id,
                "agent": next_agent,
                "status": target,
                "event": event,
                "at": _now(),
            })
            save_runtime(rt)
        notification["queued"] = True
        notification["dispatch"] = {
            "action": "queue",
            "call_agent": next_agent,
            "message": (
                f"Agente `{next_agent}` ocupado — evento enfileirado. "
                f"Ociosos agora: {idle or '(nenhum)'}"
            ),
        }

    if bug_info:
        notification["bug"] = {
            "count": bug_info.get("bug_count"),
            "threshold": bug_info.get("threshold"),
            "blocker": bug_info.get("blocker"),
        }

    if not dry_run:
        rt = load_runtime()
        log = rt.setdefault("event_log", [])
        log.append({
            "at": notification["at"],
            "event": event,
            "task_id": task_id,
            "from": current,
            "to": target,
            "next_agent": next_agent,
            "dispatch": (notification.get("dispatch") or {}).get("action"),
            "blocker": bool(notification.get("blocker")),
        })
        rt["event_log"] = log[-100:]
        save_runtime(rt)

    # Observabilidade (JSONL + dashboard) — inclui dry_run
    try:
        from lib.observability import log_from_notification
        log_from_notification(notification, dry_run=dry_run)
    except Exception as _obs_exc:  # noqa: BLE001
        notification["observability_error"] = str(_obs_exc)

    return notification


def process_dispatch_queue(limit: int = 5) -> list[dict[str, Any]]:
    """Tenta despachar itens enfileirados quando o agente fica ocioso."""
    rt = load_runtime()
    queue = rt.get("dispatch_queue") or []
    remaining = []
    dispatched = []
    for item in queue:
        agent = item.get("agent")
        idle = list_idle_agents(rt)
        if agent in idle and len(dispatched) < limit:
            set_agent_state(agent, "busy", item.get("task_id"), runtime=rt, persist=False)
            dispatched.append({
                **item,
                "action": "start_task",
                "message": f"Fila: chamar `{agent}` para `{item.get('task_id')}`",
            })
        else:
            remaining.append(item)
    rt["dispatch_queue"] = remaining
    save_runtime(rt)
    try:
        from lib.observability import log_workflow_event
        for item in dispatched:
            log_workflow_event(
                "dispatch_queue",
                task_id=item.get("task_id"),
                agent=item.get("agent"),
                event=item.get("event"),
                to_status=item.get("status"),
                dispatch_action="start_task",
                summary=item.get("message") or "",
            )
    except Exception:
        pass
    return dispatched


def emit_board_event(
    task_id: str,
    event: str,
    *,
    title: str | None = None,
    summary: str = "",
    dry_run: bool = False,
    apply_board: bool = True,
) -> dict[str, Any]:
    """Aplica evento no board (JSON+gh) e notifica orchestracao (idle/dispatch/blocker)."""
    from lib.board_client import update_project_status

    task = _task_by_id(task_id)
    if not task:
        return {"ok": False, "error": f"Task {task_id} nao encontrada"}
    if event not in EVENT_TARGET:
        return {"ok": False, "error": f"Evento desconhecido: {event}"}

    current = get_local_status(task_id) or task.get("board_status") or "Todo"
    current = resolve_status(current)
    target = resolve_status(EVENT_TARGET[event])

    board_result = None
    if apply_board:
        # valida transicao so quando vamos gravar
        target = apply_event(current, event)
        board_result = update_project_status(
            task_id,
            title or task["title"],
            target,
            dry_run=dry_run,
        )

    if not dry_run:
        rt = load_runtime()
        for _name, meta in list(rt.get("agents", {}).items()):
            if meta.get("task_id") == task_id and meta.get("state") == "busy":
                meta["state"] = "idle"
                meta["task_id"] = None
                meta["updated_at"] = _now()
        save_runtime(rt)

    notification = notify_status_change(
        task_id,
        event,
        from_status=current if apply_board else None,
        to_status=target,
        summary=summary,
        dry_run=dry_run,
    )
    return {
        "ok": bool(notification.get("ok"))
        and (board_result is None or board_result.get("ok", True) or dry_run),
        "board": board_result,
        "notification": notification,
    }
