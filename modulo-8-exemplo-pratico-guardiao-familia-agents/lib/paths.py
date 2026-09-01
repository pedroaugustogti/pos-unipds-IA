"""Paths canônicos do módulo 8 (board permanece no módulo 7)."""

from __future__ import annotations

import os
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = MODULE_ROOT.parent

_DEFAULT_BOARD = (
    REPO_ROOT
    / "modulo-7-exemplo-pratico-guardiao-familia"
    / "docs"
    / "02-criacao-board"
    / "08-board"
    / "github-project-2-import.json"
)

BOARD_AUTOMATION_DIR = MODULE_ROOT / "board_automation"
BOARD_MAPS_DIR = BOARD_AUTOMATION_DIR / "data" / "maps"
BOARD_IMPORTS_DIR = BOARD_AUTOMATION_DIR / "data" / "imports"
BOARD_BACKLOGS_DIR = BOARD_AUTOMATION_DIR / "data" / "backlogs"
BOARD_SCRIPTS_DIR = BOARD_AUTOMATION_DIR / "scripts"

_board_env = (os.environ.get("GUARDAO_BOARD_JSON") or str(_DEFAULT_BOARD)).strip()
_board_path = Path(_board_env)
if not _board_path.is_absolute():
    _board_path = MODULE_ROOT / _board_path
BOARD_JSON = _board_path


def _resolve_map_csv() -> Path:
    _map_csv_env = (os.environ.get("GUARDAO_TASK_MAP_CSV") or "TASK_AGENT_MAP.csv").strip()
    if Path(_map_csv_env).is_absolute():
        return Path(_map_csv_env)
    return BOARD_MAPS_DIR / _map_csv_env


MAP_CSV = _resolve_map_csv()


def refresh_canonical_paths() -> None:
    """Re-resolve paths que dependem de env (apos load_dotenv)."""
    global BOARD_JSON, MAP_CSV
    _board_env = (os.environ.get("GUARDAO_BOARD_JSON") or str(_DEFAULT_BOARD)).strip()
    _board_path = Path(_board_env)
    if not _board_path.is_absolute():
        _board_path = MODULE_ROOT / _board_path
    BOARD_JSON = _board_path
    MAP_CSV = _resolve_map_csv()

AGENTS_DIR = MODULE_ROOT / "agents"
SKILLS_DIR = AGENTS_DIR / "skills"
ORCHESTRATION_DIR = AGENTS_DIR / "00-orchestration"
ORCH_SCRIPTS_DIR = ORCHESTRATION_DIR / "scripts"
ORCH_SCHEMAS_DIR = ORCHESTRATION_DIR / "schemas"
QA_SCRIPTS_DIR = AGENTS_DIR / "qa-gate" / "scripts"
RUNTIME_DIR = AGENTS_DIR / "00-runtime"

# output/ = somente pastas de ticket (T-P{n}-{seq})
RUNTIME_OUTPUT_DIR = RUNTIME_DIR / "output"
# system/ = estado global (orquestrador, board, dispatch, logs, …)
RUNTIME_SYSTEM_DIR = RUNTIME_DIR / "system"

# --- Legado (aliases → system; não criar em output/) ---
HANDOFF_DIR = RUNTIME_SYSTEM_DIR / "handoffs"
OBSERVABILITY_DIR = RUNTIME_SYSTEM_DIR / "observability"
LANGGRAPH_DIR = RUNTIME_SYSTEM_DIR / "langgraph"
EVIDENCE_DIR = RUNTIME_SYSTEM_DIR / "evidence"
EVAL_DIR = RUNTIME_SYSTEM_DIR / "evals"
DISPUTES_DIR = RUNTIME_SYSTEM_DIR / "disputes"

ORCHESTRATOR_DIR = RUNTIME_SYSTEM_DIR / "orchestrator"
RUNTIME_PATH = ORCHESTRATOR_DIR / "agent_runtime.json"
CLAIM_LOCKS_PATH = ORCHESTRATOR_DIR / "claim_locks.json"
OUTBOX_PATH = ORCHESTRATOR_DIR / "outbox.jsonl"

AUDIT_DIR = RUNTIME_SYSTEM_DIR / "audit"
AUDIT_TRAIL = AUDIT_DIR / "audit-trail.jsonl"

DISPATCH_DIR = RUNTIME_SYSTEM_DIR / "dispatch"
DISPATCH_RESULTS_DIR = DISPATCH_DIR / "results"
PROMPTS_DIR = DISPATCH_DIR / "prompts"
WORKER_JOBS_PATH = DISPATCH_DIR / "worker_jobs.json"

BOARD_DIR = RUNTIME_SYSTEM_DIR / "board"
PROJECT_ITEM_CACHE_PATH = BOARD_DIR / "project_item_cache.json"
PROJECT3_ITEM_CACHE_PATH = BOARD_DIR / "project3_item_cache.json"

MOBILE_DIR = RUNTIME_SYSTEM_DIR / "mobile"
MOBILE_GUIDES_DIR = MOBILE_DIR / "guides"
MOBILE_PHASE2_DIR = MOBILE_DIR / "phase2_runtime"
MOBILE_DUMPS_DIR = MOBILE_DIR / "dumps"
QA_SEED_CACHE_DIR = MOBILE_DIR / "qa_seed_cache"
QA_EVIDENCE_DIR = MOBILE_DIR / "qa_evidence"

DEMO_DIR = RUNTIME_SYSTEM_DIR / "demo"
LOGS_DIR = RUNTIME_SYSTEM_DIR / "logs"
REPORTS_DIR = RUNTIME_SYSTEM_DIR / "reports"


def orch_script(*parts: str) -> Path:
    return ORCH_SCRIPTS_DIR.joinpath(*parts)


def qa_script(*parts: str) -> Path:
    return QA_SCRIPTS_DIR.joinpath(*parts)


def board_script(*parts: str) -> Path:
    return BOARD_SCRIPTS_DIR.joinpath(*parts)


def ensure_output_dirs() -> None:
    """Cria pastas de system/ (idempotente). output/ só recebe tickets."""
    RUNTIME_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in (
        HANDOFF_DIR,
        OBSERVABILITY_DIR,
        LANGGRAPH_DIR,
        EVIDENCE_DIR,
        EVAL_DIR,
        DISPUTES_DIR,
        ORCHESTRATOR_DIR,
        AUDIT_DIR,
        DISPATCH_DIR,
        DISPATCH_RESULTS_DIR,
        PROMPTS_DIR,
        BOARD_DIR,
        MOBILE_DIR,
        MOBILE_GUIDES_DIR,
        MOBILE_PHASE2_DIR,
        MOBILE_DUMPS_DIR,
        QA_SEED_CACHE_DIR,
        QA_EVIDENCE_DIR,
        DEMO_DIR,
        LOGS_DIR,
        REPORTS_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


def module_root_from(file: str | Path, *, up: int) -> Path:
    return Path(file).resolve().parents[up]
