"""Paths curtos para build Android (junction C:\\gf\\r\\* + env referencial GF_SOURCE_*)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
SHORT_PATHS_PS1 = MODULE_ROOT / "scripts" / "mobile" / "mobile_short_paths.ps1"

PATH_REGISTRY: dict[str, str] = {
    "guardiao-familia-parent": "GUARDAO_PARENT_PATH",
    "guardiao-familia-child": "GUARDAO_CHILD_PATH",
    "guardiao-familia-api": "GUARDAO_API_PATH",
}

SOURCE_REGISTRY: dict[str, str] = {
    "guardiao-familia-parent": "GF_SOURCE_PARENT",
    "guardiao-familia-child": "GF_SOURCE_CHILD",
    "guardiao-familia-api": "GF_SOURCE_API",
}


def ensure_short_paths(*, quiet: bool = True) -> dict[str, str]:
    """Executa mobile_short_paths.ps1 e retorna mapa envKey -> drive curto."""
    if not SHORT_PATHS_PS1.is_file():
        raise FileNotFoundError(f"Script ausente: {SHORT_PATHS_PS1}")
    args = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SHORT_PATHS_PS1)]
    if quiet:
        args.append("-Quiet")
    subprocess.run(args, check=True, cwd=str(MODULE_ROOT))
    out: dict[str, str] = {}
    for env_key in PATH_REGISTRY.values():
        val = os.environ.get(env_key)
        if val:
            out[env_key] = val
    return out


def resolve_build_repo(repo: str) -> Path:
    """Repo para Gradle — prefere GUARDAO_*_PATH (drive curto) se definido."""
    env_key = PATH_REGISTRY.get(repo)
    if env_key and os.environ.get(env_key):
        return Path(os.environ[env_key])
    from lib.core.repo_paths import resolve_repo_path

    path = resolve_repo_path(repo)
    if not path:
        raise FileNotFoundError(f"Repo {repo} não encontrado")
    return path


def gradle_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    merged = os.environ.copy()
    merged.setdefault("GRADLE_USER_HOME", os.environ.get("GF_GRADLE_HOME", r"C:\gf\.gradle"))
    merged.setdefault("GF_ANDROID_BUILD", r"C:\gf\android-build")
    if extra:
        merged.update(extra)
    return merged
