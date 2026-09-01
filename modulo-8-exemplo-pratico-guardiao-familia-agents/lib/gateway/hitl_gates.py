"""Approval Gates humanos — eventos role-based v2."""

from __future__ import annotations

from typing import Any

from lib.gateway.v2_events import (
    is_creator_ready_for_code_review,
    is_ops_done,
    is_qa_in_pull_request,
    is_qa_return_to_in_progress,
    is_reviewer_ready_for_test,
)

HIGH_RISK_KEYWORDS = (
    "sos",
    "pagamento",
    "payment",
    "stripe",
    "lgpd",
    "consent",
    "auth",
    "terraform",
    "prod",
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
        str(task.get("epic") or ""),
        str(task.get("track") or ""),
        str(task.get("agent_role") or ""),
    ]
    return " ".join(parts).lower()


def is_high_risk_task(task: dict[str, Any]) -> bool:
    role = (task.get("agent_role") or "").lower()
    if role in HIGH_RISK_ROLES:
        return True
    if task.get("release_blocker"):
        return True
    blob = _text_blob(task)
    if any(k in blob for k in HIGH_RISK_KEYWORDS):
        return True
    epic = str(task.get("epic") or "")
    return any(epic.startswith(p) for p in HIGH_RISK_EPIC_PREFIXES)


def evaluate_hitl(
    task: dict[str, Any],
    event: str,
    *,
    bug_count: int = 0,
    bug_threshold: int = 3,
    proposed_verdict: str | None = None,
) -> dict[str, Any]:
    """Decide se o evento role-based pode ser aplicado automaticamente ou exige humano."""
    reasons: list[str] = []
    mode = "auto"

    if is_ops_done(event):
        reasons.append("Merge é irreversível no fluxo do board — Approval Gate humano obrigatório.")
        mode = "block_until_human"

    if task.get("release_blocker") in (True, "yes", "true", "True", 1, "1"):
        if is_reviewer_ready_for_test(event) or is_qa_in_pull_request(event) or is_ops_done(event):
            reasons.append("Card com release_blocker=True — HITL obrigatório.")
            mode = "block_until_human" if is_ops_done(event) else "propose_only"

    if is_reviewer_ready_for_test(event) and is_high_risk_task(task):
        reasons.append(
            "Review aprovado por agente LLM em task de alto risco — veredito só como proposta."
        )
        if mode == "auto":
            mode = "propose_only"

    if is_qa_return_to_in_progress(event) and bug_count >= bug_threshold:
        reasons.append(
            f"Blocker automático após {bug_count} bugs — triagem humana obrigatória."
        )
        mode = "block_until_human"

    if is_creator_ready_for_code_review(event) and is_high_risk_task(task) and proposed_verdict == "skip_tests":
        reasons.append("PR de alto risco sem evidência de testes.")
        mode = "block_until_human"

    required = mode != "auto"
    human_action = {
        "auto": "Nenhuma — seguir automação.",
        "propose_only": (
            "Humano confirma ou rejeita o veredito proposto no PR/board "
            "(reemitir o mesmo evento role-based com hitl_approved ou hitl_rejected)."
        ),
        "block_until_human": (
            "Humano decide no board/PR; reemitir o evento role-based após hitl_approved."
        ),
    }[mode]

    return {
        "required": required,
        "mode": mode,
        "reasons": reasons,
        "reason": " | ".join(reasons) if reasons else "",
        "human_action": human_action,
        "task_id": task.get("id"),
        "event": event,
        "high_risk": is_high_risk_task(task),
    }
