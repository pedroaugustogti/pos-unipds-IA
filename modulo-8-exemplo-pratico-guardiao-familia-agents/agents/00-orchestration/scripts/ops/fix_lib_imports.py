#!/usr/bin/env python3
"""Atualiza imports legados e remove shims na raiz de lib/."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_bs = Path(__file__).resolve().parents[2] / "bootstrap.py"
_spec = importlib.util.spec_from_file_location("orch_bootstrap", _bs)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
_mod.setup()

import re
from pathlib import Path

from lib.paths import MODULE_ROOT as ROOT  # noqa: E402
# ROOT
LIB = MODULE_ROOT / "lib"

KEEP_AT_ROOT = {"paths.py", "env_load.py", "__init__.py", "README.md"}

IMPORT_MAP: dict[str, str] = {
    "repo_paths": "lib.core.repo_paths",
    "agent_paths": "lib.core.agent_paths",
    "agent_registry": "lib.core.agent_registry",
    "dependencies": "lib.core.dependencies",
    "openrouter_client": "lib.core.openrouter_client",
    "model_tier": "lib.core.model_tier",
    "react_policy": "lib.core.react_policy",
    "local_board": "board_automation.board.local_board",
    "board_client": "board_automation.board.board_client",
    "task_router": "board_automation.board.task_router",
    "task_status_workflow": "board_automation.board.task_status_workflow",
    "task_action_history": "board_automation.board.task_action_history",
    "issue_task_body": "board_automation.board.issue_task_body",
    "project_status_sync": "board_automation.board.project_status_sync",
    "status_labels": "board_automation.board.status_labels",
    "reviewer_pairs": "board_automation.board.reviewer_pairs",
    "infra_policy": "board_automation.board.infra_policy",
    "hitl_gates": "lib.gateway.hitl_gates",
    "event_schema": "lib.gateway.event_schema",
    "event_contract": "lib.gateway.event_contract",
    "handoff": "lib.gateway.handoff",
    "event_orchestrator": "lib.orchestrator.event_orchestrator",
    "claim_lock": "lib.orchestrator.claim_lock",
    "outbox": "lib.orchestrator.outbox",
    "worker_jobs": "lib.orchestrator.worker_jobs",
    "dispatch_adapter": "lib.orchestrator.dispatch_adapter",
    "complete_dispatch": "lib.orchestrator.complete_dispatch",
    "pilot": "lib.orchestrator.pilot",
    "ci_signals": "lib.ci.ci_signals",
    "ci_state": "lib.ci.ci_state",
    "mobile_runtime_config": "lib.mobile.mobile_runtime_config",
    "mobile_build_paths": "lib.mobile.mobile_build_paths",
    "mobile_setup_client": "lib.mobile.mobile_setup_client",
    "mobile_flow_discovery": "lib.mobile.mobile_flow_discovery",
    "mobile_flow_rag": "lib.mobile.mobile_flow_rag",
    "mobile_user_flow_db": "lib.mobile.mobile_user_flow_db",
    "mobile_evidence_guide": "lib.mobile.mobile_evidence_guide",
    "mobile_golden_flow": "lib.mobile.mobile_golden_flow",
    "mobile_work": "lib.mobile.mobile_work",
    "mobile_e2e_seed": "lib.mobile.mobile_e2e_seed",
    "local_e2e": "lib.mobile.local_e2e",
    "qa_mobile": "lib.mobile.qa_mobile",
    "qa_mobile_setup_evidence": "lib.mobile.qa_mobile_setup_evidence",
    "qa_mobile_mcp": "lib.mobile.qa_mobile_mcp",
    "qa_playwright": "lib.mobile.qa_playwright",
    "site_hero_work": "lib.site.site_hero_work",
}

SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules"}


def _patterns() -> list[tuple[re.Pattern[str], str]]:
    out: list[tuple[re.Pattern[str], str]] = []
    for mod in sorted(IMPORT_MAP, key=len, reverse=True):
        new = IMPORT_MAP[mod]
        out.append((re.compile(rf"\bfrom lib\.{mod}\b"), f"from {new}"))
        out.append((re.compile(rf"\bimport lib\.{mod}\b"), f"import {new}"))
    return out


def rewrite_file(path: Path, patterns: list[tuple[re.Pattern[str], str]]) -> bool:
    text = path.read_text(encoding="utf-8")
    new = text
    for pat, repl in patterns:
        new = pat.sub(repl, new)
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main() -> int:
    patterns = _patterns()
    changed: list[str] = []

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix not in {".py", ".md"}:
            continue
        if path.parent == LIB and path.name in KEEP_AT_ROOT:
            continue
        if rewrite_file(path, patterns):
            changed.append(str(path.relative_to(ROOT)))

    removed: list[str] = []
    for path in LIB.glob("*.py"):
        if path.name in KEEP_AT_ROOT:
            continue
        path.unlink()
        removed.append(path.name)

    print(f"imports atualizados: {len(changed)} arquivos")
    for rel in sorted(changed)[:20]:
        print(f"  ~ {rel}")
    if len(changed) > 20:
        print(f"  ... +{len(changed) - 20}")

    print(f"shims removidos: {len(removed)}")
    for name in sorted(removed):
        print(f"  - {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
