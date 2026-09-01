"""Contexto de atuação do agente após um evento de board (role-based)."""

from __future__ import annotations

from typing import Any

from board_automation.board.board_task_loader import get_board_task
from board_automation.board.task_router import load_tasks as load_router_tasks
from board_automation.board.issue_task_body import (
    _enrich_refinement_from_db,
    _qa_appium_child_only,
    build_agent_payload,
)
from board_automation.board.reviewer_pairs import (
    CREATOR_ROLES,
    QA_GATE_ROLE,
    normalize_creator_role,
    reviewer_for,
)
from board_automation.board.task_status_workflow import (
    build_event,
    is_known_event,
    merge_owner_for_task,
    parse_event,
    resolve_event_target,
    resolve_status,
    start_hint_for_event,
    stages_for_role,
)
from lib.orchestrator.event_orchestrator import (
    acting_agent_for_event,
    resolve_agent_for_event,
)
from lib.ci.ci_state import load_ci_state
from lib.core.agent_paths import agent_prompt_path, skill_path
from lib.core.agent_registry import AGENT_PROFILES, resolve_agent_for_task
from lib.core.model_tier import select_model
from lib.core.react_policy import CREATOR_STEPS, QA_GATE_STEPS, REVIEWER_STEPS, max_iterations_for
from lib.gateway.handoff import load_handoff


def _load_task(task_id: str) -> dict[str, Any] | None:
    task = get_board_task(task_id)
    if task:
        return task
    return next((t for t in load_router_tasks() if t.get("id") == task_id), None)


def resolve_event_string(
    event: str = "",
    *,
    agent_role: str = "",
    board_status: str = "",
    return_event: bool = False,
) -> str:
    if agent_role and board_status:
        return build_event(agent_role, board_status, return_=return_event)
    resolved = (event or "").strip()
    if not resolved:
        raise ValueError("Informe event ou (agent_role + board_status)")
    if not is_known_event(resolved):
        raise ValueError(f"Evento desconhecido: {resolved}")
    return resolved


def _playbook_for_role(agent_role: str, event: str, target_status: str) -> dict[str, Any]:
    hint = start_hint_for_event(event, target_status)
    steps: tuple[str, ...] = ()
    if agent_role in CREATOR_ROLES:
        steps = CREATOR_STEPS
    elif agent_role.endswith("-reviewer"):
        steps = REVIEWER_STEPS
    elif agent_role == QA_GATE_ROLE:
        steps = QA_GATE_STEPS
    return {
        "start_hint": hint,
        "react_steps": list(steps),
        "max_iterations": max_iterations_for(agent_role),
        "stages": stages_for_role(agent_role),
        "agent_prompt": str(agent_prompt_path(agent_role)),
        "skill_path": str(skill_path(agent_role)),
    }


def _extract_ticket_slice(task: dict[str, Any], agent_role: str) -> dict[str, Any]:
    """Campos do ticket relevantes para o papel que vai atuar."""
    enriched = {**task, "refinement": _enrich_refinement_from_db(task)}
    payload = build_agent_payload(enriched)
    ref = enriched.get("refinement") or {}
    qa = enriched.get("qa") or {}
    repo = str(enriched.get("repo") or "")
    creator = normalize_creator_role(str(enriched.get("agent_role") or "backend"))
    responsibilities = enriched.get("agent_responsibilities") or {}

    common = {
        "task_id": enriched.get("id"),
        "title": enriched.get("title"),
        "creator_role": creator,
        "reviewer_role": reviewer_for(creator),
        "track": enriched.get("track") or "produto",
        "repo": repo,
        "repo_path": payload.get("repo_path"),
        "branch": payload.get("branch"),
        "base_branch": payload.get("base_branch"),
        "epic_id": enriched.get("epic_id") or "",
        "depends_on": payload.get("depends_on") or [],
        "release_blocker": bool(payload.get("release_blocker")),
        "issue_url": enriched.get("issue_url"),
        "issue_number": enriched.get("issue_number"),
        "acceptance_criteria": list(ref.get("acceptance_hints") or []),
        "ac_verification": list(ref.get("ac_verification") or []),
        "in_scope": list(ref.get("in_scope") or []),
        "out_of_scope": list(ref.get("out_of_scope") or []),
        "suggested_files": list(ref.get("suggested_files") or []),
        "do_not_touch": list(ref.get("do_not_touch") or []),
        "implementation_steps": list(ref.get("implementation_steps") or []),
        "context_summary": ref.get("context_summary") or "",
        "technical_notes": ref.get("technical_notes") or "",
        "user_story": ref.get("user_story") or "",
        "stop_and_redirect": list(ref.get("stop_and_redirect") or []),
        "agent_responsibilities": responsibilities.get(agent_role)
        or responsibilities.get(f"{creator}-reviewer")
        or responsibilities.get(QA_GATE_ROLE)
        or [],
    }

    if agent_role in CREATOR_ROLES:
        common["user_flow"] = ref.get("user_flow") if agent_role == "frontend-mobile" else None
        common["handoff_expectations"] = payload.get("handoff_expectations") or {}
        return common

    if agent_role.endswith("-reviewer"):
        return {
            **common,
            "review_focus": {
                "creator_role": creator,
                "suggested_files": common["suggested_files"],
                "acceptance_criteria": common["acceptance_criteria"],
                "state_before": ref.get("state_before"),
                "state_after": ref.get("state_after"),
            },
        }

    if agent_role == QA_GATE_ROLE:
        profile = "basic_parent"
        raw_seed = qa.get("db_seed")
        if isinstance(raw_seed, dict) and raw_seed.get("profile"):
            profile = str(raw_seed["profile"])
        child_only = _qa_appium_child_only(repo, qa)
        return {
            **common,
            "qa": {
                "test_suite": qa.get("test_suite"),
                "scenarios": list(qa.get("scenarios") or []),
                "evidence": dict(qa.get("evidence") or {}),
                "db_seed_profile": profile,
                "child_only": child_only,
                "appium_scope": qa.get("appium_scope"),
                "how_to_run": qa.get("how_to_run"),
                "mcp_sequence": [
                    "get_handoff",
                    "emit_status_event(qa-gate_in_test)",
                    "query_mobile_flow_rag",
                    f"qa_db_seed(profile={profile})",
                    "qa_appium_suite_child(child_only=true)" if child_only else "qa_appium_suite_*",
                    "qa_db_cleanup",
                    "emit_status_event(qa-gate_in_pull_request|qa-gate_return_in_progress)",
                ],
            },
            "user_flow": ref.get("user_flow") if repo in {"guardiao-familia-parent", "guardiao-familia-child"} else None,
        }

    if agent_role in ("devops-cicd", "stores-release"):
        return {
            **common,
            "merge": {
                "merge_owner": merge_owner_for_task(str(enriched.get("track") or "produto")),
                "requires_hitl": True,
                "role_event": build_event(agent_role, "Done"),
            },
        }

    if agent_role == "orchestrator":
        return {
            **common,
            "routing": {
                "creator_role": creator,
                "match_reason": enriched.get("match_reason"),
                "labels": list(enriched.get("labels") or []),
            },
        }

    return common


def prepare_actuation_for_event(
    task_id: str,
    event: str = "",
    *,
    agent_role: str = "",
    board_status: str = "",
    return_event: bool = False,
) -> dict[str, Any]:
    """
    Dado um evento emitido (ou montado), identifica o agente e extrai contexto do ticket.

    Retorna acting_agent (emissor), assigned_agent (quem atua no status alvo) e
    ticket_slice com campos filtrados por papel.
    """
    tid = str(task_id or "").strip()
    if not tid:
        return {"ok": False, "error": "task_id obrigatorio"}

    try:
        resolved_event = resolve_event_string(
            event,
            agent_role=agent_role,
            board_status=board_status,
            return_event=return_event,
        )
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}

    task = _load_task(tid)
    if not task:
        return {"ok": False, "error": f"Task {tid} nao encontrada no board"}

    try:
        target_status = resolve_status(resolve_event_target(resolved_event))
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}

    parsed = parse_event(resolved_event) or {}
    event_agent = parsed.get("agent_role")
    acting = acting_agent_for_event(task, resolved_event)
    assigned = resolve_agent_for_event(task, resolved_event)
    creator = normalize_creator_role(str(task.get("agent_role") or "backend"))
    resolved_agent = resolve_agent_for_task(task)

    handoff = load_handoff(tid) or {}
    ci = load_ci_state(tid)
    purpose = "review" if "Review" in target_status else "implement_low"
    tier = select_model(task, purpose=purpose, role=assigned)

    ticket_slice = _extract_ticket_slice(task, assigned)

    return {
        "ok": True,
        "task_id": tid,
        "event": resolved_event,
        "event_kind": parsed.get("kind") or "advance",
        "target_status": target_status,
        "event_agent": event_agent,
        "acting_agent": acting,
        "assigned_agent": assigned,
        "creator_role": creator,
        "board_task": {
            "id": task.get("id"),
            "title": task.get("title"),
            "board_status": task.get("board_status"),
            "board_source": task.get("board_source"),
            "agent_role": creator,
            "agent_role_secondary": task.get("agent_role_secondary") or resolved_agent.get("agent_role_secondary"),
            "repo": task.get("repo"),
            "track": task.get("track"),
            "issue_url": task.get("issue_url"),
            "issue_number": task.get("issue_number"),
        },
        "routing": {
            "resolved": resolved_agent,
            "match_reason": task.get("match_reason") or resolved_agent.get("match_reason"),
        },
        "handoff": handoff,
        "ci": ci,
        "model_tier": tier,
        "agent_profile": AGENT_PROFILES.get(assigned) or AGENT_PROFILES.get(normalize_creator_role(assigned)),
        "ticket": ticket_slice,
        "playbook": _playbook_for_role(assigned, resolved_event, target_status),
    }
