"""Pareamento criador -> revisor de codigo."""

from __future__ import annotations

CREATOR_ROLES = (
    "backend",
    "frontend-mobile",
    "frontend-web",
    "cloud-infra",
    "database",
    "devops-cicd",
    "qa",
    "stores-release",
)


def reviewer_for(creator_role: str) -> str:
    return f"{creator_role}-reviewer"


REVIEWER_TO_CREATOR = {reviewer_for(r): r for r in CREATOR_ROLES}
CREATOR_TO_REVIEWER = {r: reviewer_for(r) for r in CREATOR_ROLES}
