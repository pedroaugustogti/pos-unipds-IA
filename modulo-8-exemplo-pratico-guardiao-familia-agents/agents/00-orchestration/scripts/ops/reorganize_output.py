
from lib.paths import MODULE_ROOT, REPO_ROOT  # noqa: E402
from lib.env_load import ensure_env  # noqa: E402

ensure_env()
#!/usr/bin/env python3
"""Move artefatos legados da raiz de output/ para subpastas canônicas."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_bs = Path(__file__).resolve().parents[2] / "bootstrap.py"
_spec = importlib.util.spec_from_file_location("orch_bootstrap", _bs)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
_mod.setup()

import shutil
import sys
from pathlib import Path

from lib.paths import (  # noqa: E402
    AUDIT_DIR,
    BOARD_DIR,
    CLAIM_LOCKS_PATH,
    DEMO_DIR,
    DISPATCH_DIR,
    DISPATCH_RESULTS_DIR,
    EVAL_DIR,
    LANGGRAPH_DIR,
    LOGS_DIR,
    MOBILE_GUIDES_DIR,
    MOBILE_PHASE2_DIR,
    ORCHESTRATOR_DIR,
    OUTBOX_PATH,
    PROMPTS_DIR,
    REPORTS_DIR,
    RUNTIME_OUTPUT_DIR,
    RUNTIME_PATH,
    WORKER_JOBS_PATH,
    ensure_output_dirs,
)

# arquivo/dir na raiz de output -> destino relativo à subpasta alvo
MOVES: list[tuple[str, Path]] = [
    ("agent_runtime.json", RUNTIME_PATH),
    ("claim_locks.json", CLAIM_LOCKS_PATH),
    ("outbox.jsonl", OUTBOX_PATH),
    ("audit-trail.jsonl", AUDIT_DIR / "audit-trail.jsonl"),
    ("worker_jobs.json", WORKER_JOBS_PATH),
    ("project_item_cache.json", BOARD_DIR / "project_item_cache.json"),
    ("project3_item_cache.json", BOARD_DIR / "project3_item_cache.json"),
    ("convert_drafts_log.jsonl", BOARD_DIR / "convert_drafts_log.jsonl"),
    ("seed_project3_log.jsonl", BOARD_DIR / "seed_project3_log.jsonl"),
    ("seed_infra_fargate_log.jsonl", BOARD_DIR / "seed_infra_fargate_log.jsonl"),
    ("mobile_evidence_guide_parent.json", MOBILE_GUIDES_DIR / "mobile_evidence_guide_parent.json"),
    ("mobile_evidence_guide_child.json", MOBILE_GUIDES_DIR / "mobile_evidence_guide_child.json"),
    ("mobile_evidence_guide_app_gates.json", MOBILE_GUIDES_DIR / "mobile_evidence_guide_app_gates.json"),
    ("mobile_evidence_guide_merged.json", MOBILE_GUIDES_DIR / "mobile_evidence_guide_merged.json"),
    ("MOBILE_EVIDENCE_MAP_REPORT.md", MOBILE_GUIDES_DIR / "MOBILE_EVIDENCE_MAP_REPORT.md"),
    ("PHASE2_RUNTIME_REPORT.md", REPORTS_DIR / "PHASE2_RUNTIME_REPORT.md"),
    ("demo_apresentacao_report.json", DEMO_DIR / "demo_apresentacao_report.json"),
    ("pilot_session_report.json", DEMO_DIR / "pilot_session_report.json"),
]

DIR_MOVES: list[tuple[str, Path]] = [
    ("dispatch_results", DISPATCH_RESULTS_DIR),
    ("prompts", PROMPTS_DIR),
    ("phase2_runtime", MOBILE_PHASE2_DIR),
    ("demo_workspace", DEMO_DIR / "workspace"),
    ("qa_evidence", RUNTIME_OUTPUT_DIR / "mobile" / "qa_evidence"),
    ("qa_seed_cache", RUNTIME_OUTPUT_DIR / "mobile" / "qa_seed_cache"),
]


def _move_file(src: Path, dest: Path) -> bool:
    if not src.is_file() or dest.is_file():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest))
    return True


def _move_dir(src: Path, dest: Path) -> bool:
    if not src.is_dir():
        return False
    if dest.exists():
        for child in src.iterdir():
            target = dest / child.name
            if child.is_dir():
                _move_dir(child, target)
            elif child.is_file() and not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(child), str(target))
        try:
            src.rmdir()
        except OSError:
            pass
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest))
    return True


def main() -> int:
    ensure_output_dirs()
    moved: list[str] = []
    out = RUNTIME_OUTPUT_DIR

    for name, dest in MOVES:
        src = out / name
        if _move_file(src, dest):
            moved.append(f"{name} -> {dest.relative_to(out)}")

    for name, dest in DIR_MOVES:
        src = out / name
        if _move_dir(src, dest):
            moved.append(f"{name}/ -> {dest.relative_to(out)}/")

    for log in sorted(out.glob("*.log")):
        target = LOGS_DIR / log.name
        if _move_file(log, target):
            moved.append(f"{log.name} -> logs/{log.name}")

    for dump in sorted(out.glob("ui_dump_*.xml")):
        target = RUNTIME_OUTPUT_DIR / "mobile" / "dumps" / dump.name
        if _move_file(dump, target):
            moved.append(f"{dump.name} -> mobile/dumps/{dump.name}")

    print(f"Reorganize output: {len(moved)} itens movidos")
    for line in moved:
        print(f"  - {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
