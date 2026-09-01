"""Validacao leve do contrato de eventos (sem dependencia jsonschema)."""

from __future__ import annotations

from typing import Any

from board_automation.board.task_status_workflow import (
    is_known_event,
    is_open_pr_event,
)


def validate_event_payload(
    *,
    task_id: str,
    event: str,
    pr_url: str | None = None,
    react_trace: list | None = None,
    bug_kind: str | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    if not task_id or not str(task_id).startswith("T-"):
        errors.append("task_id invalido")
    if event not in ("hitl_approved", "hitl_rejected", "dispute") and not is_known_event(event):
        errors.append(f"event desconhecido: {event}")
    if is_open_pr_event(event):
        if not pr_url or len(str(pr_url)) < 8:
            errors.append("ready_for_code_review exige pr_url")
        if not react_trace:
            errors.append("ready_for_code_review exige react_trace com >=1 iteracao")
    if bug_kind and bug_kind not in ("regression", "flaky"):
        errors.append("bug_kind deve ser regression|flaky")
    return {"ok": not errors, "errors": errors}
