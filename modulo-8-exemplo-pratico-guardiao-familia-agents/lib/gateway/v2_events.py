"""Gateway v2 — validação e semântica de eventos role-based exclusivamente."""

from __future__ import annotations

from board_automation.board.task_status_workflow import (
    is_approve_review_event,
    is_claim_event,
    is_known_event,
    is_merge_event,
    is_open_pr_event,
    is_test_failed_event,
    is_test_passed_event,
)

# Eventos v1 rejeitados na porta do gateway
LEGACY_EVENT_NAMES = frozenset({
    "claim",
    "start_work",
    "open_pr",
    "start_review",
    "request_changes",
    "resubmit_review",
    "approve_review",
    "propose_review",
    "confirm_approve_review",
    "start_test",
    "test_failed_bug",
    "test_passed",
    "merge_pr",
    "reopen",
})

HITL_CONTROL_EVENTS = frozenset({"hitl_approved", "hitl_rejected", "dispute"})

# Aliases semânticos v2 (predicados operam só em eventos role-based)
is_orchestrator_claim = is_claim_event  # orchestrator_enter_in_progress | {creator}_in_progress
is_creator_ready_for_code_review = is_open_pr_event  # {creator}_ready_for_code_review
is_reviewer_ready_for_test = is_approve_review_event  # {reviewer}_ready_for_test
is_qa_return_to_in_progress = is_test_failed_event  # qa-gate_return_in_progress
is_qa_in_pull_request = is_test_passed_event  # qa-gate_in_pull_request
is_ops_done = is_merge_event  # {ops}_done


def legacy_event_error(event: str) -> str | None:
    """Retorna mensagem de erro se o evento for legado v1."""
    name = (event or "").strip()
    if name in LEGACY_EVENT_NAMES:
        return (
            f"evento legado '{name}' rejeitado — use role-based "
            f"(ex: frontend-mobile_ready_for_code_review). "
            "Catálogo: MCP list_status_events"
        )
    return None


def is_valid_gateway_event(event: str) -> bool:
    name = (event or "").strip()
    if legacy_event_error(name):
        return False
    return name in HITL_CONTROL_EVENTS or is_known_event(name)
