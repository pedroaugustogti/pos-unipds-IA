"""Workflow de status de task — feature e bug — GitHub Project #2."""

from __future__ import annotations

from typing import Any, Literal

from board_automation.board.reviewer_pairs import (
    CREATOR_ROLES,
    QA_GATE_ROLE,
    reviewer_for,
)

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

# Papéis que podem aparecer como prefixo de evento role-based
PIPELINE_EVENT_ROLES: tuple[str, ...] = (
    QA_GATE_ROLE,
    "orchestrator",
    "devops-cicd",
    "stores-release",
)
ALL_EVENT_ROLES: tuple[str, ...] = tuple(CREATOR_ROLES) + tuple(
    reviewer_for(r) for r in CREATOR_ROLES
) + PIPELINE_EVENT_ROLES


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


def status_to_slug(status: str) -> str:
    return resolve_status(status).lower().replace(" ", "_")


def slug_to_status(slug: str) -> str:
    key = slug.strip().lower()
    if key in STATUS_ALIASES:
        return STATUS_ALIASES[key]
    for s in STATUSES:
        if status_to_slug(s) == key:
            return s
    raise ValueError(f"Status slug desconhecido: {slug!r}")


def build_event(agent_role: str, status: str, *, return_: bool = False) -> str:
    """Monta evento `{agent_role}_{status_slug}` ou `{agent_role}_return_{status_slug}`."""
    slug = status_to_slug(status)
    if return_:
        return f"{agent_role}_return_{slug}"
    return f"{agent_role}_{slug}"


def parse_event(event: str) -> dict[str, Any] | None:
    """Extrai agent_role, status alvo e se é retrocesso. None se inválido."""
    if event == "orchestrator_enter_in_progress":
        return {
            "agent_role": "orchestrator",
            "status": "In Progress",
            "return": False,
            "kind": "advance",
        }
    if "_return_" in event:
        role, _, slug = event.partition("_return_")
        try:
            return {
                "agent_role": role,
                "status": slug_to_status(slug),
                "return": True,
                "kind": "return",
            }
        except ValueError:
            return None
    for role in sorted(ALL_EVENT_ROLES, key=len, reverse=True):
        prefix = f"{role}_"
        if event.startswith(prefix):
            slug = event[len(prefix) :]
            try:
                return {
                    "agent_role": role,
                    "status": slug_to_status(slug),
                    "return": False,
                    "kind": "advance",
                }
            except ValueError:
                return None
    return None


def resolve_event_target(event: str) -> str:
    if event in EVENT_TARGET:
        return EVENT_TARGET[event]
    parsed = parse_event(event)
    if parsed:
        return parsed["status"]
    raise ValueError(f"Evento desconhecido: {event}")


def is_known_event(event: str) -> bool:
    return event in EVENT_TARGET


def is_claim_event(event: str) -> bool:
    if event == "orchestrator_enter_in_progress":
        return True
    parsed = parse_event(event)
    return bool(
        parsed
        and not parsed.get("return")
        and parsed.get("status") == "In Progress"
        and parsed.get("agent_role") in CREATOR_ROLES
    )


def is_open_pr_event(event: str) -> bool:
    parsed = parse_event(event)
    return bool(
        parsed
        and not parsed.get("return")
        and parsed.get("status") == "Ready for Code Review"
        and parsed.get("agent_role") in CREATOR_ROLES
    )


def is_approve_review_event(event: str) -> bool:
    parsed = parse_event(event)
    return bool(
        parsed
        and not parsed.get("return")
        and parsed.get("status") == "Ready for Test"
        and parsed.get("agent_role", "").endswith("-reviewer")
    )


def is_test_failed_event(event: str) -> bool:
    parsed = parse_event(event)
    return bool(
        parsed
        and parsed.get("return")
        and parsed.get("status") == "In Progress"
        and parsed.get("agent_role") == QA_GATE_ROLE
    )


def is_merge_event(event: str) -> bool:
    parsed = parse_event(event)
    return bool(
        parsed
        and not parsed.get("return")
        and parsed.get("status") == "Done"
        and parsed.get("agent_role") in ("devops-cicd", "stores-release")
    )


def is_test_passed_event(event: str) -> bool:
    parsed = parse_event(event)
    return bool(
        parsed
        and not parsed.get("return")
        and parsed.get("status") == "In Pull Request"
        and parsed.get("agent_role") == QA_GATE_ROLE
    )


def start_hint_for_event(event: str, target_status: str = "") -> str:
    """Hint de atuação para notificações e playbook."""
    if event == "orchestrator_enter_in_progress":
        return "Orchestrator dispatch da task prioritária (Todo → In Progress)"
    parsed = parse_event(event) or {}
    status = str(parsed.get("status") or target_status or "")
    if parsed.get("return"):
        if status == "In Progress":
            return "Corrigir e retomar implementacao"
        return f"Retrocesso para {status}"
    hints = {
        "In Progress": "Iniciar ou retomar implementacao",
        "Ready for Code Review": "Aguardar/assumir fila de code review",
        "In Code Review": "Executar checklist de review",
        "Ready for Test": "Planejar testes (Ready for Test)",
        "In Test": "Executar suite QA (In Test)",
        "In Pull Request": "Preparar merge (In Pull Request)",
        "Done": "Encerrar ciclo (Done)",
        "Todo": "Reabrir no backlog (Todo)",
    }
    return hints.get(status, f"Atuar em status {status or 'desconhecido'}")


def role_event_catalog() -> list[dict[str, str]]:
    """Catálogo de eventos role-based (avanço e retrocesso) por agente."""
    rows: list[dict[str, str]] = []
    creator_statuses = (
        ("In Progress", "advance"),
        ("Ready for Code Review", "advance"),
        ("In Code Review", "advance"),
    )
    for role in CREATOR_ROLES:
        for status, kind in creator_statuses:
            rows.append({
                "event": build_event(role, status),
                "agent_role": role,
                "board_status": status,
                "kind": kind,
                "classification": "creator",
            })
    reviewer_advances = (
        "In Code Review",
        "Ready for Test",
    )
    for role in CREATOR_ROLES:
        rev = reviewer_for(role)
        for status in reviewer_advances:
            rows.append({
                "event": build_event(rev, status),
                "agent_role": rev,
                "board_status": status,
                "kind": "advance",
                "classification": "reviewer",
            })
        rows.append({
            "event": build_event(rev, "In Progress", return_=True),
            "agent_role": rev,
            "board_status": "In Progress",
            "kind": "return",
            "classification": "reviewer",
        })
    for status, kind in (
        ("In Test", "advance"),
        ("In Pull Request", "advance"),
    ):
        rows.append({
            "event": build_event(QA_GATE_ROLE, status),
            "agent_role": QA_GATE_ROLE,
            "board_status": status,
            "kind": kind,
            "classification": "qa-gate",
        })
    rows.append({
        "event": build_event(QA_GATE_ROLE, "In Progress", return_=True),
        "agent_role": QA_GATE_ROLE,
        "board_status": "In Progress",
        "kind": "return",
        "classification": "qa-gate",
    })
    for ops in ("devops-cicd", "stores-release"):
        rows.append({
            "event": build_event(ops, "Done"),
            "agent_role": ops,
            "board_status": "Done",
            "kind": "advance",
            "classification": "ops",
        })
    rows.append({
        "event": "orchestrator_enter_in_progress",
        "agent_role": "orchestrator",
        "board_status": "In Progress",
        "kind": "advance",
        "classification": "orchestrator",
    })
    rows.append({
        "event": build_event("orchestrator", "Todo"),
        "agent_role": "orchestrator",
        "board_status": "Todo",
        "kind": "advance",
        "classification": "orchestrator",
    })
    return rows


def _build_role_event_target() -> dict[str, str]:
    return {row["event"]: row["board_status"] for row in role_event_catalog()}


EVENT_TARGET: dict[str, str] = _build_role_event_target()

# Papel responsável por status (primary owner)
STAGE_OWNERS: dict[str, str] = {
    "Todo": "orchestrator",
    "In Progress": "creator",
    "Ready for Code Review": "reviewer",
    "In Code Review": "reviewer",
    "Ready for Test": "qa-gate",
    "In Test": "qa-gate",
    "In Pull Request": "devops-cicd",
    "Done": "orchestrator",
}

# Detalhe por etapa: quem entra, o que faz, como sai, evento v2
AGENT_STAGES: list[dict[str, str]] = [
    {
        "status": "Todo",
        "owner": "orchestrator",
        "enters": "Backlog priorizado; nenhum agente criador ativo",
        "does": "Planeja sprint, roteia via TASK_AGENT_MAP, dispatch prioritário",
        "exits": "orchestrator_enter_in_progress → In Progress",
        "event_in": "-",
        "event_out": "orchestrator_enter_in_progress",
        "label": "agent:todo",
    },
    {
        "status": "In Progress",
        "owner": "creator",
        "enters": "orchestrator_enter_in_progress | {reviewer}_return_in_progress | qa-gate_return_in_progress",
        "does": "Implementa/corrige na branch; commit T-XXX; prepara PR",
        "exits": "{creator}_ready_for_code_review | {creator}_in_code_review (resubmit)",
        "event_in": "orchestrator_enter_in_progress / *_return_in_progress",
        "event_out": "{creator}_ready_for_code_review / {creator}_in_code_review",
        "label": "agent:in-progress",
    },
    {
        "status": "Ready for Code Review",
        "owner": "reviewer",
        "enters": "{creator}_ready_for_code_review (PR aberto)",
        "does": "Revisor pareado (1:1) assume fila; busca PR por task_id",
        "exits": "{reviewer}_in_code_review",
        "event_in": "{creator}_ready_for_code_review",
        "event_out": "{reviewer}_in_code_review",
        "label": "agent:ready-for-code-review",
    },
    {
        "status": "In Code Review",
        "owner": "reviewer",
        "enters": "{reviewer}_in_code_review | {creator}_in_code_review (correção)",
        "does": "Checklist skill revisor; comenta PR; emite veredito",
        "exits": "{reviewer}_ready_for_test | {reviewer}_return_in_progress",
        "event_in": "{reviewer}_in_code_review / {creator}_in_code_review",
        "event_out": "{reviewer}_ready_for_test / {reviewer}_return_in_progress",
        "label": "agent:in-code-review",
    },
    {
        "status": "Ready for Test",
        "owner": "qa-gate",
        "enters": "{reviewer}_ready_for_test (CR aprovado)",
        "does": "QA planeja cenários; prepara ambiente/dispositivos",
        "exits": "qa-gate_in_test",
        "event_in": "{reviewer}_ready_for_test",
        "event_out": "qa-gate_in_test",
        "label": "agent:ready-for-test",
    },
    {
        "status": "In Test",
        "owner": "qa-gate",
        "enters": "qa-gate_in_test",
        "does": "E2E, regressao, evidencias; label type:bug se falhar",
        "exits": "qa-gate_in_pull_request | qa-gate_return_in_progress",
        "event_in": "qa-gate_in_test",
        "event_out": "qa-gate_in_pull_request / qa-gate_return_in_progress",
        "label": "agent:in-test",
    },
    {
        "status": "In Pull Request",
        "owner": "devops-cicd",
        "enters": "qa-gate_in_pull_request (stores-release se track=stores)",
        "does": "Merge queue, CI green, deploy staging/prod conforme task",
        "exits": "{ops}_done",
        "event_in": "qa-gate_in_pull_request",
        "event_out": "devops-cicd_done / stores-release_done",
        "label": "agent:in-pull-request",
    },
    {
        "status": "Done",
        "owner": "orchestrator",
        "enters": "{ops}_done",
        "does": "Fecha ciclo; metricas; retrospectiva opcional",
        "exits": "-",
        "event_in": "devops-cicd_done / stores-release_done",
        "event_out": "-",
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
    if role == "qa-gate":
        return [s for s in AGENT_STAGES if s["owner"] == "qa-gate"]
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
        "enters": "Após {creator}_ready_for_code_review (aguarda revisor)",
        "does": "Monitora PR; responde duvidas do revisor",
        "exits": "Revisor assume ({reviewer}_in_code_review)",
        "event_in": "{creator}_ready_for_code_review",
        "event_out": "{reviewer}_in_code_review",
        "label": "agent:ready-for-code-review",
    })
    return creator_stages


def mermaid_agent_swimlane() -> str:
    return """```mermaid
flowchart TB
  subgraph ORCH["🎯 Orchestrator"]
    T[Todo] -->|orchestrator_enter_in_progress| IP
  end
  subgraph CRE["👨‍💻 Creator (agent_role da task)"]
    IP[In Progress] -->|{creator}_ready_for_code_review| RFC
    IP -->|{creator}_in_code_review| ICR
  end
  subgraph REV["🔍 Reviewer (par 1:1)"]
    RFC[Ready for Code Review] -->|{reviewer}_in_code_review| ICR[In Code Review]
    ICR -->|{reviewer}_ready_for_test| RFT[Ready for Test]
    ICR -->|{reviewer}_return_in_progress| IP
  end
  subgraph QA["🧪 QA-gate"]
    RFT -->|qa-gate_in_test| IT[In Test]
    IT -->|qa-gate_in_pull_request| IPR[In Pull Request]
    IT -->|qa-gate_return_in_progress| IP
  end
  subgraph OPS["⚙️ DevOps / Stores-release"]
    IPR -->|{ops}_done| D[Done]
  end
  D --> ORCH2[Orchestrator fecha ciclo]
```"""


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
    if not is_known_event(event):
        raise ValueError(f"Evento desconhecido: {event}. Eventos: {sorted(EVENT_TARGET)}")
    target = resolve_event_target(event)
    return transition(current, target, kind)


def validate_role_event_for_task(
    event: str,
    *,
    from_agent: str,
    task_agent_role: str | None = None,
) -> str | None:
    """Retorna mensagem de erro ou None se válido."""
    if not is_known_event(event):
        return f"Evento invalido: {event}"
    parsed = parse_event(event)
    if not parsed or not parsed.get("agent_role"):
        return None
    role = parsed["agent_role"]
    if not from_agent:
        return "from_agent obrigatorio para eventos role-based"
    from board_automation.board.reviewer_pairs import normalize_creator_role

    creator = normalize_creator_role(task_agent_role or "")
    if from_agent == "orchestrator" and role == creator:
        return None
    if from_agent != role:
        return f"from_agent={from_agent!r} nao corresponde ao evento (esperado {role!r})"
    return None


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
  Todo --> InProgress: orchestrator_enter_in_progress
  InProgress --> ReadyForCodeReview: creator_ready_for_code_review
  ReadyForCodeReview --> InCodeReview: reviewer_in_code_review
  InCodeReview --> ReadyForTest: reviewer_ready_for_test
  InCodeReview --> InProgress: reviewer_return_in_progress
  InProgress --> InCodeReview: creator_in_code_review
  ReadyForTest --> InTest: qa_gate_in_test
  InTest --> InPullRequest: qa_gate_in_pull_request
  InTest --> InProgress: qa_gate_return_in_progress
  InPullRequest --> Done: ops_done
  Done --> [*]
```"""


def mermaid_bug_flow() -> str:
    return """```mermaid
stateDiagram-v2
  [*] --> Todo
  Todo --> InProgress: orchestrator_enter_in_progress
  InProgress --> InCodeReview: creator_in_code_review
  InProgress --> ReadyForCodeReview: creator_ready_for_code_review
  ReadyForCodeReview --> InCodeReview: reviewer_in_code_review
  InCodeReview --> InProgress: reviewer_return_in_progress
  InProgress --> InCodeReview: creator_in_code_review
  InCodeReview --> InTest: qa_gate_in_test
  InTest --> InProgress: qa_gate_return_in_progress
  InTest --> InPullRequest: qa_gate_in_pull_request
  InPullRequest --> Done: ops_done
```"""
