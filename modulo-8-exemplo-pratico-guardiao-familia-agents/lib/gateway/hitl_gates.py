"""Approval Gates humanos — somente quando policy é violada (v2)."""

from __future__ import annotations

import re
from typing import Any

from lib.gateway.policy_violations import hitl_from_policy_findings, scan_policy_violations

# Mantido para roteamento de modelo / telemetria — não dispara HITL.
HIGH_RISK_KEYWORDS = (
    "sos",
    "pagamento",
    "payment",
    "stripe",
    "lgpd",
    "consent",
    "auth",
    "terraform",
    "production",
    "release",
    "store",
)

HIGH_RISK_ROLES = frozenset({
    "cloud-infra",
    "stores-release",
    "devops-cicd",
})

HIGH_RISK_EPIC_PREFIXES = ("E-P01", "E-P07", "E-P09", "E-P11")


def _text_blob(task: dict[str, Any]) -> str:
    parts = [
        str(task.get("title") or ""),
        str(task.get("id") or ""),
        str(task.get("epic") or task.get("epic_id") or ""),
        str(task.get("track") or ""),
        str(task.get("agent_role") or ""),
    ]
    return " ".join(parts).lower()


def is_high_risk_task(task: dict[str, Any]) -> bool:
    """Classificação operacional (model tier) — não determina HITL."""
    role = (task.get("agent_role") or "").lower()
    if role in HIGH_RISK_ROLES:
        return True
    if task.get("release_blocker"):
        return True
    blob = _text_blob(task)
    if any(re.search(rf"\b{re.escape(k)}\b", blob) for k in HIGH_RISK_KEYWORDS):
        return True
    epic = str(task.get("epic") or task.get("epic_id") or "")
    return any(epic.startswith(p) for p in HIGH_RISK_EPIC_PREFIXES)


def _context_blob(
    task: dict[str, Any],
    event: str,
    *,
    summary: str = "",
    context_text: str = "",
    metrics: dict[str, Any] | None = None,
) -> str:
    parts = [
        str(task.get("title") or ""),
        str(task.get("id") or ""),
        str(event or ""),
        str(summary or ""),
        str(context_text or ""),
        " ".join(str(x) for x in (task.get("acceptance_criteria") or [])),
        " ".join(str(x) for x in (task.get("in_scope") or [])),
        " ".join(str(x) for x in (task.get("out_of_scope") or [])),
        " ".join(str(x) for x in (task.get("do_not_touch") or [])),
    ]
    for step in (metrics or {}).get("react_trace") or []:
        if isinstance(step, dict):
            parts.append(str(step.get("thought") or ""))
            parts.append(str(step.get("action") or ""))
            parts.append(str(step.get("observation") or ""))
        else:
            parts.append(str(step))
    return "\n".join(parts)


def evaluate_hitl(
    task: dict[str, Any],
    event: str,
    *,
    bug_count: int = 0,
    bug_threshold: int = 3,
    proposed_verdict: str | None = None,
    summary: str = "",
    context_text: str = "",
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    HITL somente quando scan de policy encontra violação no contexto do evento.

    Metadados (high_risk, release_blocker, tipo de evento, bug_count) não disparam HITL.
    """
    del bug_count, bug_threshold, proposed_verdict  # legado — ignorado

    blob = _context_blob(
        task,
        event,
        summary=summary,
        context_text=context_text,
        metrics=metrics,
    )
    findings = scan_policy_violations(blob)
    return hitl_from_policy_findings(
        findings,
        task_id=str(task.get("id") or ""),
        event=event,
    )
