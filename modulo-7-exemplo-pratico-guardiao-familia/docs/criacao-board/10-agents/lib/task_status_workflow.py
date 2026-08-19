"""Workflow de status de task — feature e bug — GitHub Project #2."""

from __future__ import annotations

from typing import Literal

TaskKind = Literal["feature", "bug"]

# Ordem canônica no board (single select GitHub Project)
STATUSES: tuple[str, ...] = (
    "Todo",
    "In Progress",
    "Ready for Code Review",
    "In Code Review",
    "Ready for Test",
    "In Test",
    "In Pull Request",
    "Done",
)

STATUS_ALIASES: dict[str, str] = {
    "todo": "Todo",
    "in_progress": "In Progress",
    "in-progress": "In Progress",
    "ready_for_code_review": "Ready for Code Review",
    "ready-for-code-review": "Ready for Code Review",
    "in_code_review": "In Code Review",
    "in-code-review": "In Code Review",
    "in_review": "In Code Review",
    "in-review": "In Code Review",
    "ready_for_test": "Ready for Test",
    "ready-for-test": "Ready for Test",
    "in_test": "In Test",
    "in-test": "In Test",
    "in_pull_request": "In Pull Request",
    "in-pull-request": "In Pull Request",
    "in_pr": "In Pull Request",
    "in-pr": "In Pull Request",
    "done": "Done",
}

# Fluxo principal (feature)
FEATURE_TRANSITIONS: dict[str, set[str]] = {
    "Todo": {"In Progress"},
    "In Progress": {"Ready for Code Review", "In Code Review", "Todo"},
    "Ready for Code Review": {"In Code Review", "In Progress"},
    "In Code Review": {"Ready for Test", "In Progress"},
    "Ready for Test": {"In Test", "In Code Review"},
    "In Test": {"In Pull Request", "In Progress"},
    "In Pull Request": {"Done", "In Progress"},
    "Done": set(),
}

# Bug: atalho Todo → In Progress; retestos após fix
BUG_TRANSITIONS: dict[str, set[str]] = {
    **{k: set(v) for k, v in FEATURE_TRANSITIONS.items()},
    "Todo": {"In Progress"},
    "In Test": {"In Progress", "In Pull Request", "In Code Review"},
    "In Code Review": {"Ready for Test", "In Progress", "In Test"},
    "In Progress": {"Ready for Code Review", "In Code Review", "Todo"},
}

# Eventos de automação (agentes / orquestrador)
EVENT_TARGET: dict[str, str] = {
    "claim": "In Progress",
    "start_work": "In Progress",
    "open_pr": "Ready for Code Review",
    "start_review": "In Code Review",
    "request_changes": "In Progress",
    "resubmit_review": "In Code Review",
    "approve_review": "Ready for Test",
    "start_test": "In Test",
    "test_failed_bug": "In Progress",
    "test_passed": "In Pull Request",
    "merge_pr": "Done",
    "reopen": "Todo",
}

EVENT_AFTER_CHANGES_REQUESTED = "resubmit_review"  # volta para In Code Review


def resolve_status(name: str) -> str:
    key = name.strip().lower().replace(" ", "_")
    if name in STATUSES:
        return name
    if key in STATUS_ALIASES:
        return STATUS_ALIASES[key]
    normalized = name.strip()
    for s in STATUSES:
        if s.lower() == normalized.lower():
            return s
    raise ValueError(f"Status desconhecido: {name!r}")


def transitions_for(kind: TaskKind = "feature") -> dict[str, set[str]]:
    return BUG_TRANSITIONS if kind == "bug" else FEATURE_TRANSITIONS


def can_transition(current: str, target: str, kind: TaskKind = "feature") -> bool:
    cur = resolve_status(current)
    tgt = resolve_status(target)
    return tgt in transitions_for(kind).get(cur, set())


def transition(current: str, target: str, kind: TaskKind = "feature") -> str:
    cur = resolve_status(current)
    tgt = resolve_status(target)
    if not can_transition(cur, tgt, kind):
        allowed = sorted(transitions_for(kind).get(cur, set()))
        raise ValueError(
            f"Transicao invalida ({kind}): {cur} -> {tgt}. Permitido: {allowed or '(nenhum)'}"
        )
    return tgt


def apply_event(current: str, event: str, kind: TaskKind = "feature") -> str:
    if event not in EVENT_TARGET:
        raise ValueError(f"Evento desconhecido: {event}. Eventos: {sorted(EVENT_TARGET)}")
    target = EVENT_TARGET[event]
    return transition(current, target, kind)


def status_after_review_verdict(verdict: str, *, resubmit: bool = False) -> str:
    v = verdict.lower().replace(" ", "_")
    if v == "approved":
        return "Ready for Test"
    if resubmit:
        return "In Code Review"
    return "In Progress"


def label_for_status(status: str) -> str | None:
    """Label agent:* sugerida (opcional) para o status."""
    s = resolve_status(status)
    mapping = {
        "Todo": "agent:ready",
        "In Progress": "agent:in-progress",
        "Ready for Code Review": "agent:ready-for-review",
        "In Code Review": "agent:in-review",
        "Ready for Test": "agent:ready-for-test",
        "In Test": "agent:in-test",
        "In Pull Request": "agent:in-pr",
        "Done": "agent:done",
    }
    return mapping.get(s)


def mermaid_feature_flow() -> str:
    return """```mermaid
stateDiagram-v2
  [*] --> Todo
  Todo --> InProgress: claim
  InProgress --> ReadyForCodeReview: open PR
  ReadyForCodeReview --> InCodeReview: start review
  InCodeReview --> ReadyForTest: approved
  InCodeReview --> InProgress: changes requested
  InProgress --> InCodeReview: resubmit (correcao CR)
  ReadyForTest --> InTest: QA start
  InTest --> InPullRequest: tests pass
  InTest --> InProgress: bug found
  InPullRequest --> Done: merge
  Done --> [*]
```"""


def mermaid_bug_flow() -> str:
    return """```mermaid
stateDiagram-v2
  [*] --> Todo
  Todo --> InProgress: claim bug
  InProgress --> InCodeReview: hotfix direto (opcional)
  InProgress --> ReadyForCodeReview: open PR
  ReadyForCodeReview --> InCodeReview: start review
  InCodeReview --> InProgress: changes requested
  InProgress --> InCodeReview: resubmit correcao
  InCodeReview --> InTest: approved (pular fila QA opcional)
  InTest --> InProgress: regressao / bug
  InTest --> InPullRequest: OK
  InPullRequest --> Done: merge
```"""
