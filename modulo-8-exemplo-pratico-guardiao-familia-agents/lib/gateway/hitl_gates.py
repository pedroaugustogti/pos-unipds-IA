"""Approval Gates humanos — onde a automação para (módulo 8 / P2)."""

from __future__ import annotations

from typing import Any

# Papéis / eventos que exigem humano antes de efeito irreversível
HITL_EVENTS = frozenset({
    "merge_pr",
    "hitl_required",
})

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

HIGH_RISK_EPIC_PREFIXES = ("E-P01", "E-P07", "E-P09", "E-P11")  # auth/safety/payments/release (exemplo)


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
    """
    Decide se o evento pode ser aplicado automaticamente ou exige humano.

    Retorno:
      required: bool
      reason: str
      mode: auto | propose_only | block_until_human
      human_action: str
    """
    reasons: list[str] = []
    mode = "auto"

    if event == "merge_pr":
        reasons.append("Merge é irreversível no fluxo do board — Approval Gate humano obrigatório.")
        mode = "block_until_human"

    if task.get("release_blocker") in (True, "yes", "true", "True", 1, "1"):
        if event in ("approve_review", "test_passed", "merge_pr"):
            reasons.append("Card com release_blocker=True — HITL obrigatório.")
            mode = "block_until_human" if event == "merge_pr" else "propose_only"

    if event == "approve_review" and is_high_risk_task(task):
        reasons.append(
            "Review aprovado por agente LLM em task de alto risco — veredito só como proposta."
        )
        if mode == "auto":
            mode = "propose_only"

    if event == "test_failed_bug" and bug_count >= bug_threshold:
        reasons.append(
            f"Blocker automático após {bug_count} bugs — triagem humana obrigatória."
        )
        mode = "block_until_human"

    if event in ("open_pr",) and is_high_risk_task(task) and proposed_verdict == "skip_tests":
        reasons.append("PR de alto risco sem evidência de testes.")
        mode = "block_until_human"

    required = mode != "auto"
    human_action = {
        "auto": "Nenhuma — seguir automação.",
        "propose_only": (
            "Humano confirma ou rejeita o veredito proposto no PR/board "
            "(evento hitl_approved | hitl_rejected)."
        ),
        "block_until_human": (
            "Humano decide no board/PR; só então emitir hitl_approved + evento liberado."
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
