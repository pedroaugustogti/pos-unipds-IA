"""Resolve e sincroniza scripts de seed do guardiao-familia-mobile-setup/seed_db."""

from __future__ import annotations

import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from lib.core.repo_paths import GITHUB_ORG, github_repo_url

MOBILE_SETUP_REPO = "guardiao-familia-mobile-setup"
SEED_DB_DIRNAME = "seed_db"
SEED_DB_REF = "main"
SEED_DB_FILES = (
    "README.md",
    "api.mjs",
    "cleanup.mjs",
    "config.mjs",
    "seed.mjs",
    "validate.mjs",
    "validate_db.py",
)


def seed_db_github_tree() -> str:
    return f"{github_repo_url(MOBILE_SETUP_REPO)}/tree/{SEED_DB_REF}/{SEED_DB_DIRNAME}"


def seed_db_dir(setup: Path) -> Path:
    return setup / SEED_DB_DIRNAME


def seed_db_script_path(setup: Path) -> Path:
    return seed_db_dir(setup) / "seed.mjs"


def _github_raw_url(filename: str, *, ref: str = SEED_DB_REF) -> str:
    return (
        f"https://raw.githubusercontent.com/{GITHUB_ORG}/{MOBILE_SETUP_REPO}"
        f"/{ref}/{SEED_DB_DIRNAME}/{filename}"
    )


def _git_pull_seed_db(setup: Path, *, ref: str = SEED_DB_REF) -> bool:
    if not (setup / ".git").is_dir():
        return False
    try:
        proc = subprocess.run(
            ["git", "-C", str(setup), "pull", "--ff-only", "origin", ref],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return proc.returncode == 0 and seed_db_script_path(setup).is_file()


def _download_seed_db_files(setup: Path, *, ref: str = SEED_DB_REF) -> list[str]:
    target = seed_db_dir(setup)
    target.mkdir(parents=True, exist_ok=True)
    fetched: list[str] = []
    for name in SEED_DB_FILES:
        url = _github_raw_url(name, ref=ref)
        try:
            with urllib.request.urlopen(url, timeout=20) as resp:
                data = resp.read()
        except (urllib.error.URLError, TimeoutError, OSError):
            continue
        (target / name).write_bytes(data)
        fetched.append(name)
    return fetched


def ensure_seed_db_scripts(setup: Path, *, ref: str = SEED_DB_REF) -> dict[str, Any]:
    """Garante seed_db/seed.mjs no mobile-setup — local, git pull ou GitHub raw."""
    script = seed_db_script_path(setup)
    github = seed_db_github_tree()
    if script.is_file():
        return {
            "ok": True,
            "source": "local",
            "path": str(script),
            "github": github,
        }

    if _git_pull_seed_db(setup, ref=ref):
        return {
            "ok": True,
            "source": "git_pull",
            "path": str(script),
            "github": github,
        }

    fetched = _download_seed_db_files(setup, ref=ref)
    if script.is_file():
        return {
            "ok": True,
            "source": "github_raw",
            "path": str(script),
            "github": github,
            "fetched": fetched,
        }

    return {
        "ok": False,
        "error": (
            f"seed_db ausente em {setup} — clone {github_repo_url(MOBILE_SETUP_REPO)} "
            f"ou defina GUARDAO_MOBILE_SETUP_PATH"
        ),
        "github": github,
        "fetched": fetched,
    }
