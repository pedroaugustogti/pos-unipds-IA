"""Paths canônicos por agent_role (agents/01-role-based/{role}/)."""

from __future__ import annotations

from pathlib import Path

from lib.paths import MODULE_ROOT, ROLE_BASED_DIR

_SHARED = MODULE_ROOT / "agents" / "_shared"

_QA_ALIASES = {"qa": "qa-author", "qa-reviewer": "qa-author-reviewer"}


def agent_role_dir(role: str) -> Path:
    return ROLE_BASED_DIR / role.strip()


def agent_prompt_path(role: str) -> Path:
    """Prompt do agente — agents/01-role-based/{role}/agent.md."""
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
    """Skill principal — agents/01-role-based/{role}/SKILL.md."""
    role = role.strip()
    alias = _QA_ALIASES.get(role, role)
    return agent_role_dir(alias) / "SKILL.md"


def shared_doc(name: str) -> Path:
    return _SHARED / name


def agent_scripts_dir(role: str) -> Path:
    return agent_role_dir(role) / "scripts"
