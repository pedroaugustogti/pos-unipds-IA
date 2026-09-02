"""Papéis: criadores, revisores, QA-author vs QA-gate."""

from __future__ import annotations

# Criadores de produto (dispatch em Todo do próprio agent_role)
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

# Gate de qualidade na pipeline (Ready for Test / In Test) — não dispatcha features
QA_GATE_ROLE = "qa-gate"

# Alias no CSV de classificação: agent_role=qa → qa-author
CSV_QA_ROLE_ALIAS = "qa"

PIPELINE_ROLES = (
    QA_GATE_ROLE,
    "orchestrator",
)


def normalize_creator_role(role: str) -> str:
    if role == CSV_QA_ROLE_ALIAS:
        return "qa-author"
    return role


# Retrocompat imports (CSV classifica como "qa")
LEGACY_QA_ROLE = CSV_QA_ROLE_ALIAS


def reviewer_for(creator_role: str) -> str:
    role = normalize_creator_role(creator_role)
    if role == "qa-author":
        return "qa-author-reviewer"
    return f"{role}-reviewer"


REVIEWER_TO_CREATOR = {reviewer_for(r): r for r in CREATOR_ROLES}
CREATOR_TO_REVIEWER = {r: reviewer_for(r) for r in CREATOR_ROLES}
