#!/usr/bin/env python3
"""Atualiza referências de paths legados (skills, _shared, agents/{role})."""

from __future__ import annotations

from pathlib import Path

MODULE = Path(__file__).resolve().parents[4]
ROLES = (
    "backend-reviewer",
    "frontend-mobile-reviewer",
    "frontend-web-reviewer",
    "cloud-infra-reviewer",
    "database-reviewer",
    "devops-cicd-reviewer",
    "qa-author-reviewer",
    "stores-release-reviewer",
    "qa-reviewer",
    "frontend-mobile",
    "frontend-web",
    "cloud-infra",
    "devops-cicd",
    "stores-release",
    "qa-author",
    "backend",
    "database",
    "qa-gate",
    "qa",
)

TEXT_SUFFIXES = {".md", ".py", ".json", ".jsonl", ".csv", ".yml", ".yaml", ".ps1", ".txt", ".html"}
SKIP_PARTS = {"__pycache__", "node_modules", ".git"}
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".pyc", ".xml"}

GLOBAL_REPLACEMENTS = [
    ("(exceto `output/`)", "(exceto `output/`)"),
    ("../../00-orchestration/docs/routing/REPOS_AND_ROUTING.md", "../../00-orchestration/docs/routing/REPOS_AND_ROUTING.md"),
    ("../../00-orchestration/docs/graph/STATEGRAPH_FLOW.md", "../../00-orchestration/docs/graph/STATEGRAPH_FLOW.md"),
    ("../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md", "../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md"),
    ("../../00-orchestration/docs/routing/REPOS_AND_ROUTING.md", "../../00-orchestration/docs/routing/REPOS_AND_ROUTING.md"),
    ("../../00-orchestration/docs/graph/STATEGRAPH_FLOW.md", "../../00-orchestration/docs/graph/STATEGRAPH_FLOW.md"),
    ("../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md", "../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md"),
    ("../../00-orchestration/", "../../00-orchestration/"),
    ("[`01-role-based/README.md`](../01-role-based/README.md)", "[`01-role-based/README.md`](../01-role-based/README.md)"),
    ("### `agents/01-role-based/`", "### `agents/01-role-based/`"),
    ("agents/01-role-based/README.md", "agents/01-role-based/README.md"),
    ("../01-role-based/README.md", "../01-role-based/README.md"),
    ("par de `agents/01-role-based/", "par de `agents/01-role-based/"),
    ("par de `agents/01-role-based/", "par de `agents/01-role-based/"),
]

# skills/02-skills/{role} → 01-role-based/{role}
for _role in ROLES:
    GLOBAL_REPLACEMENTS.extend([
        (f"agents/01-role-based/{_role}/", f"agents/01-role-based/{_role}/"),
        (f"agents/01-role-based/{_role}/", f"agents/01-role-based/{_role}/"),
        (f"`agents/01-role-based/{_role}/", f"`agents/01-role-based/{_role}/"),
        (f"`agents/01-role-based/{_role}/", f"`agents/01-role-based/{_role}/"),
        (f"agents/01-role-based/{_role}", f"agents/01-role-based/{_role}"),
        (f"agents/01-role-based/{_role}", f"agents/01-role-based/{_role}"),
        (f"modulo-8-exemplo-pratico-guardiao-familia-agents/01-role-based/{_role}", f"agents/01-role-based/{_role}"),
        (f"modulo-8-exemplo-pratico-guardiao-familia-agents/01-role-based/{_role}", f"agents/01-role-based/{_role}"),
    ])

GLOBAL_REPLACEMENTS.extend([
    ("agents/01-role-based/", "agents/01-role-based/"),
    ("agents/01-role-based/", "agents/01-role-based/"),
    ("../01-role-based/", "../01-role-based/"),
    ("../../01-role-based/", "../../01-role-based/"),
    ("modulo-8-exemplo-pratico-guardiao-familia-agents/01-role-based/", "agents/01-role-based/"),
    ("modulo-8-exemplo-pratico-guardiao-familia-agents/01-role-based/", "agents/01-role-based/"),
])


def should_process(path: Path) -> bool:
    if any(p in SKIP_PARTS for p in path.parts):
        return False
    if path.suffix.lower() in SKIP_SUFFIXES:
        return False
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in {"README", "SKILL"}


def patch_text(text: str, in_role_based: bool) -> str:
    for old, new in GLOBAL_REPLACEMENTS:
        text = text.replace(old, new)
    for role in ROLES:
        old = f"agents/{role}/"
        new = f"agents/01-role-based/{role}/"
        if old in text and new not in text.replace(new, ""):
            text = text.replace(old, new)
    if in_role_based:
        text = text.replace("../../00-orchestration/", "../../00-orchestration/")
        if "../00-orchestration/" in text and "../../00-orchestration/" not in text:
            text = text.replace("../00-orchestration/", "../../00-orchestration/")
    return text


def main() -> None:
    changed = 0
    for path in MODULE.rglob("*"):
        if not path.is_file() or not should_process(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        in_rb = "01-role-based" in path.parts
        new = patch_text(text, in_rb)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed += 1
    print(f"Updated {changed} files")


if __name__ == "__main__":
    main()
