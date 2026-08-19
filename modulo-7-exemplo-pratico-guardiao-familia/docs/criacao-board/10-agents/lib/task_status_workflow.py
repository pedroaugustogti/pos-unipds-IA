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

# Papel responsável por status (primary owner)
STAGE_OWNERS: dict[str, str] = {
    "Todo": "orchestrator",
    "In Progress": "creator",
    "Ready for Code Review": "reviewer",
    "In Code Review": "reviewer",
    "Ready for Test": "qa",
    "In Test": "qa",
    "In Pull Request": "devops-cicd",
    "Done": "orchestrator",
}

# Detalhe por etapa: quem entra, o que faz, como sai, evento
AGENT_STAGES: list[dict[str, str]] = [
    {
        "status": "Todo",
        "owner": "orchestrator",
        "enters": "Backlog priorizado; nenhum agente criador ativo",
        "does": "Planeja sprint, roteia via TASK_AGENT_MAP, executa claim",
        "exits": "claim → assign creator + In Progress",
        "event_in": "—",
        "event_out": "claim",
        "label": "agent:ready",
    },
    {
        "status": "In Progress",
        "owner": "creator",
        "enters": "claim | request_changes (CR) | test_failed_bug (QA)",
        "does": "Implementa/corrige na branch; commit T-XXX; prepara PR",
        "exits": "open_pr → Ready for Code Review | resubmit_review → In Code Review",
        "event_in": "claim / request_changes / test_failed_bug",
        "event_out": "open_pr / resubmit_review",
        "label": "agent:in-progress",
    },
    {
        "status": "Ready for Code Review",
        "owner": "reviewer",
        "enters": "open_pr (criador abriu PR)",
        "does": "Revisor pareado (1:1) assume fila; busca PR por task_id",
        "exits": "start_review → In Code Review",
        "event_in": "open_pr",
        "event_out": "start_review",
        "label": "agent:ready-for-review",
    },
    {
        "status": "In Code Review",
        "owner": "reviewer",
        "enters": "start_review | resubmit_review (correcao CR)",
        "does": "Checklist skill revisor; comenta PR; emite veredito",
        "exits": "approve_review → Ready for Test | request_changes → In Progress",
        "event_in": "start_review / resubmit_review",
        "event_out": "approve_review / request_changes",
        "label": "agent:in-review",
    },
    {
        "status": "Ready for Test",
        "owner": "qa",
        "enters": "approve_review (CR aprovado)",
        "does": "QA planeja cenarios; prepara ambiente/dispositivos",
        "exits": "start_test → In Test",
        "event_in": "approve_review",
        "event_out": "start_test",
        "label": "agent:ready-for-test",
    },
    {
        "status": "In Test",
        "owner": "qa",
        "enters": "start_test",
        "does": "E2E, regressao, evidencias; label type:bug se falhar",
        "exits": "test_passed → In Pull Request | test_failed_bug → In Progress",
        "event_in": "start_test",
        "event_out": "test_passed / test_failed_bug",
        "label": "agent:in-test",
    },
    {
        "status": "In Pull Request",
        "owner": "devops-cicd",
        "enters": "test_passed (stores-release se track=stores)",
        "does": "Merge queue, CI green, deploy staging/prod conforme task",
        "exits": "merge_pr → Done",
        "event_in": "test_passed",
        "event_out": "merge_pr",
        "label": "agent:in-pr",
    },
    {
        "status": "Done",
        "owner": "orchestrator",
        "enters": "merge_pr",
        "does": "Fecha ciclo; metricas; retrospectiva opcional",
        "exits": "—",
        "event_in": "merge_pr",
        "event_out": "—",
        "label": "agent:done",
    },
]

# Criador: status em que atua
CREATOR_ACTIVE_STATUSES = frozenset({"In Progress"})
REVIEWER_ACTIVE_STATUSES = frozenset({"Ready for Code Review", "In Code Review"})
QA_ACTIVE_STATUSES = frozenset({"Ready for Test", "In Test"})
MERGE_OWNER_BY_TRACK = {
    "stores": "stores-release",
    "infraestrutura": "devops-cicd",
    "produto": "devops-cicd",
}


def merge_owner_for_task(track: str = "produto") -> str:
    return MERGE_OWNER_BY_TRACK.get(track, "devops-cicd")


def stages_for_role(role: str) -> list[dict[str, str]]:
    """Etapas onde o agente e owner ou participa."""
    if role == "orchestrator":
        return [s for s in AGENT_STAGES if s["owner"] == "orchestrator"]
    if role == "qa":
        return [s for s in AGENT_STAGES if s["owner"] == "qa"]
    if role == "devops-cicd" or role == "stores-release":
        track = "stores" if role == "stores-release" else "produto"
        return [s for s in AGENT_STAGES if s["status"] == "In Pull Request"]
    if role.endswith("-reviewer"):
        return [s for s in AGENT_STAGES if s["owner"] == "reviewer"]
    # creator roles
    creator_stages = [s for s in AGENT_STAGES if s["status"] in CREATOR_ACTIVE_STATUSES]
    creator_stages.append({
        "status": "Ready for Code Review",
        "owner": "creator",
        "enters": "Apos open_pr (aguarda revisor)",
        "does": "Monitora PR; responde duvidas do revisor",
        "exits": "Revisor assume (start_review)",
        "event_in": "open_pr",
        "event_out": "start_review",
        "label": "agent:ready-for-review",
    })
    return creator_stages


def mermaid_agent_swimlane() -> str:
    return """```mermaid
flowchart TB
  subgraph ORCH["🎯 Orchestrator"]
    T[Todo] -->|claim| IP
  end
  subgraph CRE["👨‍💻 Creator (agent_role da task)"]
    IP[In Progress] -->|open_pr| RFC
    IP -->|resubmit_review| ICR
  end
  subgraph REV["🔍 Reviewer (par 1:1)"]
    RFC[Ready for Code Review] -->|start_review| ICR[In Code Review]
    ICR -->|approve_review| RFT[Ready for Test]
    ICR -->|request_changes| IP
  end
  subgraph QA["🧪 QA"]
    RFT -->|start_test| IT[In Test]
    IT -->|test_passed| IPR[In Pull Request]
    IT -->|test_failed_bug| IP
  end
  subgraph OPS["⚙️ DevOps / Stores-release"]
    IPR -->|merge_pr| D[Done]
  end
  D --> ORCH2[Orchestrator fecha ciclo]
```"""


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
