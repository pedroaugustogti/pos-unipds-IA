"""Sinais GitHub → gateway / filas (Fase 3)."""

from __future__ import annotations

import re
from typing import Any

from lib.gateway.gateway import emit_status_event
from lib.gateway.handoff import load_handoff
from lib.ci.ci_state import patch_ci_state
from board_automation.board.local_board import get_local_status
from lib.runtime_log import log_workflow_event

TASK_ID_RE = re.compile(r"\[([A-Z]-[A-Z0-9]+-\d+)\]")

# Status em que open_pr ja foi aplicado (idempotente)
ALREADY_OPEN_PR = frozenset({
    "Ready for Code Review",
    "In Code Review",
    "Ready for Test",
    "In Test",
    "In Pull Request",
    "Done",
})


def parse_task_id(*texts: str | None) -> str | None:
    for t in texts:
        if not t:
            continue
        m = TASK_ID_RE.search(t)
        if m:
            return m.group(1)
    return None


def _ci_react_trace(pr_url: str | None, summary: str) -> list[dict[str, str]]:
    return [{
        "thought": "Sinal GitHub Actions confirma PR da task",
        "action": "ci_signal.pr_opened",
        "observation": summary or (pr_url or "PR sem URL"),
    }]


def handle_pr_signal(
    *,
    task_id: str,
    pr_url: str | None = None,
    branch: str | None = None,
    summary: str = "",
    dry_run: bool = False,
) -> dict[str, Any]:
    """PR opened/synchronize → open_pr se ainda In Progress; no-op se ja avancado."""
    st = get_local_status(task_id) or "Todo"
    if st in ALREADY_OPEN_PR:
        out = {
            "ok": True,
            "signal": "pr",
            "task_id": task_id,
            "action": "idempotent_skip",
            "status": st,
            "message": f"Status `{st}` ja passou de open_pr",
        }
        log_workflow_event(
            "ci_signal",
            task_id=task_id,
            event="open_pr",
            to_status=st,
            summary="idempotent skip",
            extra=out,
            dry_run=dry_run,
        )
        return out

    if st != "In Progress":
        return {
            "ok": False,
            "signal": "pr",
            "task_id": task_id,
            "action": "skip_bad_status",
            "status": st,
            "error": f"Status `{st}` nao permite open_pr via CI (esperado In Progress)",
        }

    ho = load_handoff(task_id) or {}
    trace = ho.get("react_trace") or (ho.get("metrics") or {}).get("react_trace")
    if not trace:
        trace = _ci_react_trace(pr_url, summary)

    emit = emit_status_event(
        task_id,
        "open_pr",
        summary=summary or f"CI/PR signal: {pr_url or ''}".strip(),
        pr_url=pr_url or ho.get("pr_url"),
        branch=branch or ho.get("branch"),
        react_trace=trace,
        metrics={"source": "github_actions", **(ho.get("metrics") or {})},
        dry_run=dry_run,
    )
    if not dry_run and emit.get("ok"):
        patch_ci_state(
            task_id,
            status="pending",
            last_signal="pr_opened",
            pr_url=pr_url or ho.get("pr_url"),
            branch=branch or ho.get("branch"),
            summary=summary or "PR aberto — aguardando checks",
            event="pr_opened",
            board_status=st,
            from_agent="devops-cicd",
            to_agent=ho.get("from_agent") or "frontend-web",
        )
    out = {
        "ok": bool(emit.get("ok")),
        "signal": "pr",
        "task_id": task_id,
        "action": "open_pr",
        "status_before": st,
        "emit": {
            "status": emit.get("status"),
            "code": emit.get("code"),
            "error": emit.get("error"),
            "to": (emit.get("notification") or {}).get("to"),
            "duplicate": emit.get("duplicate"),
        },
        "dry_run": dry_run,
    }
    log_workflow_event(
        "ci_signal",
        task_id=task_id,
        event="open_pr",
        from_status=st,
        to_status=(emit.get("notification") or {}).get("to"),
        summary=summary,
        extra={"pr_url": pr_url, "emit_status": emit.get("status")},
        dry_run=dry_run,
    )
    return out


def handle_ci_green(*, task_id: str, dry_run: bool = False) -> dict[str, Any]:
    """CI verde → start_test via gateway (sem fila worker)."""
    st = get_local_status(task_id) or "Todo"
    if dry_run:
        out = {
            "ok": True,
            "signal": "ci_green",
            "task_id": task_id,
            "action": "would_start_test",
            "dry_run": True,
        }
    else:
        emit = emit_status_event(
            task_id,
            "start_test",
            summary="CI green — QA gate inicia testes",
            dry_run=False,
            from_agent="devops-cicd",
        )
        patch_ci_state(
            task_id,
            status="green",
            last_signal="ci_green",
            summary="CI green — start_test emitido",
            event="start_test",
            from_agent="devops-cicd",
            to_agent="qa-gate",
        )
        out = {
            "ok": bool(emit.get("ok")),
            "signal": "ci_green",
            "task_id": task_id,
            "action": "start_test",
            "emit": emit,
        }
    log_workflow_event(
        "ci_signal",
        task_id=task_id,
        agent="qa-gate",
        event="start_test",
        dispatch_action="enqueue_qa_gate",
        summary="CI green → qa-gate",
        extra={"emit_status": (out.get("emit") or {}).get("status")},
        dry_run=dry_run,
    )
    return out


def handle_ci_red(
    *,
    task_id: str,
    bug_kind: str = "regression",
    summary: str = "CI failed",
    dry_run: bool = False,
) -> dict[str, Any]:
    """CI vermelho → test_failed_bug no gateway."""
    try:
        emit = emit_status_event(
            task_id,
            "test_failed_bug",
            summary=summary,
            bug_kind=bug_kind,
            dry_run=dry_run,
        )
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "signal": "ci_red", "task_id": task_id, "error": str(exc)}

    if not dry_run and emit.get("ok"):
        patch_ci_state(
            task_id,
            status="red",
            last_signal="ci_red",
            summary=summary,
            event="test_failed_bug",
            from_agent="devops-cicd",
            to_agent="qa-gate",
        )

    out = {
        "ok": bool(emit.get("ok")),
        "signal": "ci_red",
        "task_id": task_id,
        "action": "test_failed_bug",
        "bug_kind": bug_kind,
        "emit": {
            "status": emit.get("status"),
            "code": emit.get("code"),
            "error": emit.get("error"),
            "to": (emit.get("notification") or {}).get("to"),
        },
        "dry_run": dry_run,
    }
    log_workflow_event(
        "ci_signal",
        task_id=task_id,
        event="test_failed_bug",
        summary=summary,
        extra={"bug_kind": bug_kind, "emit_status": emit.get("status")},
        dry_run=dry_run,
    )
    return out


def dispatch_signal(payload: dict[str, Any], *, dry_run: bool = False) -> dict[str, Any]:
    """Entrada unica para Actions / repository_dispatch."""
    signal = (payload.get("signal") or payload.get("event") or "").strip().lower()
    task_id = payload.get("task_id") or parse_task_id(
        payload.get("pr_title"),
        payload.get("title"),
        payload.get("head_ref"),
        payload.get("branch"),
    )
    if not task_id:
        return {"ok": False, "error": "task_id nao encontrado no payload"}

    if signal in ("pr_opened", "pr_synchronize", "pr", "open_pr"):
        return handle_pr_signal(
            task_id=task_id,
            pr_url=payload.get("pr_url"),
            branch=payload.get("branch") or payload.get("head_ref"),
            summary=payload.get("summary") or "",
            dry_run=dry_run,
        )
    if signal in ("ci_green", "green", "checks_success"):
        return handle_ci_green(task_id=task_id, dry_run=dry_run)
    if signal in ("ci_red", "red", "checks_failure"):
        return handle_ci_red(
            task_id=task_id,
            bug_kind=payload.get("bug_kind") or "regression",
            summary=payload.get("summary") or "CI failed",
            dry_run=dry_run,
        )
    return {"ok": False, "error": f"signal desconhecido: {signal!r}", "task_id": task_id}
