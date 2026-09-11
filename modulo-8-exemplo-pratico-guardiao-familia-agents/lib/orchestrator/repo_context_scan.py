"""Leitura leve do repo alvo — arquivos sugeridos e pontos chave para atuação."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from lib.core.repo_paths import resolve_repo_path

_SYMBOL_HINTS = (
    "dynamicGreeting",
    "ChildHomeV2",
    "export function",
    "export const",
    "describe(",
    "it(",
    "test(",
)


def _read_snippet(path: Path, *, max_lines: int = 45) -> list[str]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    return lines[:max_lines]


def _grep_hints(path: Path, hints: tuple[str, ...] = _SYMBOL_HINTS) -> list[str]:
    found: list[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return found
    for hint in hints:
        if hint in text:
            found.append(hint)
    return found


def scan_repo_context(
    repo: str,
    suggested_files: list[str],
    *,
    extra_paths: list[str] | None = None,
    max_snippet_lines: int = 45,
) -> dict[str, Any]:
    """Mapeia arquivos do ticket no disco local (sem alterar nada)."""
    root = resolve_repo_path(repo)
    paths = list(dict.fromkeys([*(suggested_files or []), *(extra_paths or [])]))
    files: list[dict[str, Any]] = []

    if not root or not root.exists():
        return {
            "repo": repo,
            "repo_path": str(root) if root else "",
            "repo_available": False,
            "files": files,
            "notes": ["Repo local não encontrado — configure GUARDAO_*_PATH ou clone o repositório."],
        }

    notes: list[str] = []
    for rel in paths:
        rel = str(rel or "").strip().lstrip("/\\")
        if not rel:
            continue
        full = root / rel
        entry: dict[str, Any] = {
            "path": rel,
            "exists": full.is_file(),
            "symbols": [],
            "snippet": [],
        }
        if full.is_file():
            entry["symbols"] = _grep_hints(full)
            entry["snippet"] = _read_snippet(full, max_lines=max_snippet_lines)
        files.append(entry)

    pkg = root / "package.json"
    if pkg.is_file():
        notes.append("package.json presente — validar scripts de teste antes do PR.")
    notes.append(f"Root: {root}")

    return {
        "repo": repo,
        "repo_path": str(root),
        "repo_available": True,
        "files": files,
        "notes": notes,
    }
