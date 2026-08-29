"""Papéis: criadores, revisores, QA-author vs QA-gate."""

from __future__ import annotations

# Criadores de produto (claim em Todo do próprio agent_role)
CREATOR_ROLES = (
    "backend",
    "frontend-mobile",
    "frontend-web",
    "cloud-infra",
    "database",
    "devops-cicd",
    "qa-author",  # escreve harness/cenários (tasks agent_role=qa no mapa)
    "stores-release",
)

# Gate de qualidade na pipeline (Ready for Test / In Test) — não claima features
QA_GATE_ROLE = "qa-gate"

# Alias legado no CSV: agent_role=qa → qa-author no claim; fila de teste → qa-gate
LEGACY_QA_ROLE = "qa"

PIPELINE_ROLES = (
    QA_GATE_ROLE,
    "orchestrator",
)


def normalize_creator_role(role: str) -> str:
    if role == LEGACY_QA_ROLE:
        return "qa-author"
    return role


def reviewer_for(creator_role: str) -> str:
    role = normalize_creator_role(creator_role)
    if role == "qa-author":
        return "qa-author-reviewer"
    return f"{role}-reviewer"


REVIEWER_TO_CREATOR = {reviewer_for(r): r for r in CREATOR_ROLES}
CREATOR_TO_REVIEWER = {r: reviewer_for(r) for r in CREATOR_ROLES}
