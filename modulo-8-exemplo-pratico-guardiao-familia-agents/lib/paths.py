"""Paths canônicos do módulo 8 (board permanece no módulo 7)."""

from __future__ import annotations

import os
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = MODULE_ROOT.parent

# Board oficial do exemplo prático (módulo 7) — evita duplicar o JSON grande
_DEFAULT_BOARD = (
    REPO_ROOT
    / "modulo-7-exemplo-pratico-guardiao-familia"
    / "docs"
    / "02-criacao-board"
    / "08-board"
    / "github-project-2-import.json"
)

BOARD_JSON = Path(os.environ.get("GUARDAO_BOARD_JSON", str(_DEFAULT_BOARD)))
MAP_CSV = MODULE_ROOT / "TASK_AGENT_MAP.csv"
RUNTIME_PATH = MODULE_ROOT / "crew" / "output" / "agent_runtime.json"
HANDOFF_DIR = MODULE_ROOT / "crew" / "output" / "handoffs"
AUDIT_TRAIL = MODULE_ROOT / "crew" / "output" / "audit-trail.jsonl"
OBSERVABILITY_DIR = MODULE_ROOT / "crew" / "output" / "observability"
