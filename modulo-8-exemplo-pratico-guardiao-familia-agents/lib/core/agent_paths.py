"""Paths canônicos por agent_role (agents/{role}/)."""

from __future__ import annotations

from pathlib import Path

from lib.paths import MODULE_ROOT, SKILLS_DIR
from board_automation.board.reviewer_pairs import normalize_creator_role, reviewer_for

_SHARED = MODULE_ROOT / "agents" / "_shared"


def agent_role_dir(role: str) -> Path:
    return MODULE_ROOT / "agents" / role.strip()


def agent_prompt_path(role: str) -> Path:
    """Prompt do agente — agents/{role}/agent.md."""
    role = role.strip()
    canonical = agent_role_dir(role) / "agent.md"
    if canonical.is_file():
        return canonical
    legacy = MODULE_ROOT / "agents" / f"{role}.agent.md"
    if legacy.is_file():
        return legacy
    legacy_rev = MODULE_ROOT / "agents" / "reviewers" / f"{role}.agent.md"
    return legacy_rev if legacy_rev.is_file() else canonical


def skill_path(role: str) -> Path:
    """Skill principal — agents/{role}/SKILL.md."""
    role = role.strip()
    canonical = agent_role_dir(role) / "SKILL.md"
    if canonical.is_file():
        return canonical
    legacy = SKILLS_DIR / role / "SKILL.md"
    if legacy.is_file():
        return legacy
    # qa-gate / qa-author compartilham pasta qa-author
    if role == "qa-gate":
        alt = agent_role_dir("qa-author") / "SKILL.md"
        if alt.is_file():
            return alt
        alt_legacy = SKILLS_DIR / "qa" / "SKILL.md"
        if alt_legacy.is_file():
            return alt_legacy
    return canonical


def shared_doc(name: str) -> Path:
    return _SHARED / name


def agent_scripts_dir(role: str) -> Path:
    return agent_role_dir(role) / "scripts"
