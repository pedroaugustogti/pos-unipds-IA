"""Estado CI/CD persistido no handoff (metrics.ci)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from lib.gateway.handoff import load_handoff, write_handoff

CI_KEY = "ci"
VALID_STATUS = frozenset({"pending", "green", "red"})


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_ci_state(task_id: str) -> dict[str, Any]:
    ho = load_handoff(task_id) or {}
    metrics = ho.get("metrics") or {}
    ci = metrics.get(CI_KEY) or {}
    status = str(ci.get("status") or "pending")
    if status not in VALID_STATUS:
        status = "pending"
    return {
        "ci_status": status,
        "pr_url": ho.get("pr_url"),
        "branch": ho.get("branch"),
        "checks": list(ci.get("checks") or []),
        "workflow_run_id": ci.get("workflow_run_id"),
        "check_suite_id": ci.get("check_suite_id"),
        "last_signal": ci.get("last_signal"),
        "updated_at": ci.get("updated_at"),
        "summary": ci.get("summary") or "",
    }


def patch_ci_state(
    task_id: str,
    *,
    status: str | None = None,
    last_signal: str | None = None,
    pr_url: str | None = None,
    branch: str | None = None,
    checks: list[dict[str, Any]] | None = None,
    workflow_run_id: str | None = None,
    check_suite_id: str | None = None,
    summary: str | None = None,
    from_agent: str = "ci",
    to_agent: str = "orchestrator",
    event: str = "ci_update",
    board_status: str = "",
) -> dict[str, Any]:
    prev = load_handoff(task_id) or {}
    metrics = dict(prev.get("metrics") or {})
    ci = dict(metrics.get(CI_KEY) or {})
    if status is not None:
        ci["status"] = status if status in VALID_STATUS else "pending"
    if last_signal is not None:
        ci["last_signal"] = last_signal
    if checks is not None:
        ci["checks"] = checks
    if workflow_run_id is not None:
        ci["workflow_run_id"] = workflow_run_id
    if check_suite_id is not None:
        ci["check_suite_id"] = check_suite_id
    if summary is not None:
        ci["summary"] = summary
    ci["updated_at"] = _now()
    metrics[CI_KEY] = ci
    return write_handoff(
        task_id,
        from_agent=from_agent,
        to_agent=to_agent,
        event=event,
        status=board_status or prev.get("status") or "",
        repo=prev.get("repo"),
        branch=branch or prev.get("branch"),
        pr_url=pr_url or prev.get("pr_url"),
        summary=summary or prev.get("summary") or "",
        metrics=metrics,
    )


def merge_gate_ready(ci: dict[str, Any], *, mode: str = "dry_run") -> bool:
    """PR merge só após CI verde + pr_url válida (live exige URL real)."""
    if mode in ("dry_run", "demo"):
        return True
    if ci.get("ci_status") != "green":
        return False
    pr = str(ci.get("pr_url") or "")
    if len(pr) < 8:
        return False
    if "example.com" in pr:
        return mode == "demo"
    return True


def test_gate_ready(ci: dict[str, Any], *, mode: str = "dry_run") -> bool:
    """start_test só após ci_green (dry_run/demo simulam)."""
    if mode in ("dry_run", "demo"):
        return True
    return ci.get("ci_status") == "green"


def ci_fields_for_state(task_id: str, *, mode: str = "dry_run") -> dict[str, Any]:
    ci = load_ci_state(task_id)
    return {
        "ci_status": ci["ci_status"],
        "pr_url": ci.get("pr_url"),
        "ci_checks": ci.get("checks") or [],
        "merge_checks_ok": merge_gate_ready(ci, mode=mode),
        "test_ci_ready": test_gate_ready(ci, mode=mode),
    }
