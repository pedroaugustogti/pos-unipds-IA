"""Validação do contrato de eventos v2 (role-based)."""

from __future__ import annotations

from typing import Any

from lib.gateway.v2_events import (
    is_creator_ready_for_code_review,
    is_valid_gateway_event,
    legacy_event_error,
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
    legacy = legacy_event_error(event)
    if legacy:
        errors.append(legacy)
    elif not is_valid_gateway_event(event):
        errors.append(f"evento invalido (v2): {event}")
    if is_creator_ready_for_code_review(event):
        if not pr_url or len(str(pr_url)) < 8:
            errors.append("{creator}_ready_for_code_review exige pr_url")
        if not react_trace:
            errors.append("{creator}_ready_for_code_review exige react_trace com >=1 iteracao")
    if bug_kind and bug_kind not in ("regression", "flaky"):
        errors.append("bug_kind deve ser regression|flaky")
    return {"ok": not errors, "errors": errors}
