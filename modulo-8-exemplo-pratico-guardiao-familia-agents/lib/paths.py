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

BOARD_AUTOMATION_DIR = MODULE_ROOT / "board_automation"
BOARD_MAPS_DIR = BOARD_AUTOMATION_DIR / "data" / "maps"
BOARD_IMPORTS_DIR = BOARD_AUTOMATION_DIR / "data" / "imports"
BOARD_BACKLOGS_DIR = BOARD_AUTOMATION_DIR / "data" / "backlogs"
BOARD_SCRIPTS_DIR = BOARD_AUTOMATION_DIR / "scripts"

BOARD_JSON = Path(os.environ.get("GUARDAO_BOARD_JSON", str(_DEFAULT_BOARD)))
_map_csv_env = (os.environ.get("GUARDAO_TASK_MAP_CSV") or "TASK_AGENT_MAP.csv").strip()
if Path(_map_csv_env).is_absolute():
    MAP_CSV = Path(_map_csv_env)
else:
    MAP_CSV = BOARD_MAPS_DIR / _map_csv_env

AGENTS_DIR = MODULE_ROOT / "agents"
SKILLS_DIR = AGENTS_DIR / "skills"
ORCHESTRATION_DIR = AGENTS_DIR / "00-orchestration"
ORCH_SCRIPTS_DIR = ORCHESTRATION_DIR / "scripts"
ORCH_SCHEMAS_DIR = ORCHESTRATION_DIR / "schemas"
QA_SCRIPTS_DIR = AGENTS_DIR / "qa-gate" / "scripts"
RUNTIME_DIR = AGENTS_DIR / "00-runtime"
RUNTIME_OUTPUT_DIR = RUNTIME_DIR / "output"

# --- Pipeline / agentes ---
HANDOFF_DIR = RUNTIME_OUTPUT_DIR / "handoffs"
OBSERVABILITY_DIR = RUNTIME_OUTPUT_DIR / "observability"
LANGGRAPH_DIR = RUNTIME_OUTPUT_DIR / "langgraph"
EVIDENCE_DIR = RUNTIME_OUTPUT_DIR / "evidence"
EVAL_DIR = RUNTIME_OUTPUT_DIR / "evals"
DISPUTES_DIR = RUNTIME_OUTPUT_DIR / "disputes"

# --- Orquestrador (gateway, locks, fila GitHub) ---
ORCHESTRATOR_DIR = RUNTIME_OUTPUT_DIR / "orchestrator"
RUNTIME_PATH = ORCHESTRATOR_DIR / "agent_runtime.json"
CLAIM_LOCKS_PATH = ORCHESTRATOR_DIR / "claim_locks.json"
OUTBOX_PATH = ORCHESTRATOR_DIR / "outbox.jsonl"

# --- Auditoria ---
AUDIT_DIR = RUNTIME_OUTPUT_DIR / "audit"
AUDIT_TRAIL = AUDIT_DIR / "audit-trail.jsonl"

# --- Dispatch / worker Cursor ---
DISPATCH_DIR = RUNTIME_OUTPUT_DIR / "dispatch"
DISPATCH_RESULTS_DIR = DISPATCH_DIR / "results"
PROMPTS_DIR = DISPATCH_DIR / "prompts"
WORKER_JOBS_PATH = DISPATCH_DIR / "worker_jobs.json"

# --- Board GitHub (cache, seeds de issues) ---
BOARD_DIR = RUNTIME_OUTPUT_DIR / "board"
PROJECT_ITEM_CACHE_PATH = BOARD_DIR / "project_item_cache.json"
PROJECT3_ITEM_CACHE_PATH = BOARD_DIR / "project3_item_cache.json"

# --- Mobile QA / RAG / Appium ---
MOBILE_DIR = RUNTIME_OUTPUT_DIR / "mobile"
MOBILE_GUIDES_DIR = MOBILE_DIR / "guides"
MOBILE_PHASE2_DIR = MOBILE_DIR / "phase2_runtime"
MOBILE_DUMPS_DIR = MOBILE_DIR / "dumps"
QA_SEED_CACHE_DIR = MOBILE_DIR / "qa_seed_cache"
QA_EVIDENCE_DIR = MOBILE_DIR / "qa_evidence"

# --- Demo, logs, relatórios avulsos ---
DEMO_DIR = RUNTIME_OUTPUT_DIR / "demo"
LOGS_DIR = RUNTIME_OUTPUT_DIR / "logs"
REPORTS_DIR = RUNTIME_OUTPUT_DIR / "reports"


def orch_script(*parts: str) -> Path:
    """Path de script em agents/00-orchestration/scripts/."""
    return ORCH_SCRIPTS_DIR.joinpath(*parts)


def qa_script(*parts: str) -> Path:
    """Path de script em agents/qa-gate/scripts/."""
    return QA_SCRIPTS_DIR.joinpath(*parts)


def board_script(*parts: str) -> Path:
    """Path de script em board_automation/scripts/."""
    return BOARD_SCRIPTS_DIR.joinpath(*parts)


def ensure_output_dirs() -> None:
    """Cria subpastas canônicas de output (idempotente)."""
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
    """Sobe `up` níveis a partir do arquivo até a raiz do módulo 8."""
    return Path(file).resolve().parents[up]
