"""Resolve caminhos locais dos repos Guardião Família."""

from __future__ import annotations

import os
from pathlib import Path

REPO_ENV = {
    "guardiao-familia-api": "GUARDAO_API_PATH",
    "guardiao-familia-parent": "GUARDAO_PARENT_PATH",
    "guardiao-familia-child": "GUARDAO_CHILD_PATH",
    "guardiao-familia-backoffice": "GUARDAO_BACKOFFICE_PATH",
    "guardiao-familia-site": "GUARDAO_SITE_PATH",
}

DEFAULT_PATHS = {
    "guardiao-familia-api": Path(r"C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-api"),
    "guardiao-familia-parent": Path(r"C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-parent"),
    "guardiao-familia-child": Path(r"C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-child"),
    "guardiao-familia-backoffice": Path(r"C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-backoffice"),
    "guardiao-familia-site": Path(r"C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-site"),
}

GITHUB_ORG = os.environ.get("GUARDAO_GITHUB_ORG", "guardiaofamilia")


def resolve_repo_path(repo: str) -> Path | None:
    env = REPO_ENV.get(repo)
    if env and os.environ.get(env):
        p = Path(os.environ[env])
        return p if p.exists() else p
    p = DEFAULT_PATHS.get(repo)
    if p and p.exists():
        return p
    return None


def github_repo_url(repo: str) -> str:
    return f"https://github.com/{GITHUB_ORG}/{repo}"
