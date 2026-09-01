#!/usr/bin/env python3
"""Atualiza paths legados output/ -> output/{ticket}/ + system/ em markdown."""

from __future__ import annotations

from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[4]

REPLACEMENTS: list[tuple[str, str]] = [
    (
        "agents/00-runtime/output/handoffs/{task_id}.json",
        "agents/00-runtime/output/{task_id}/handoff.json",
    ),
    (
        "agents/00-runtime/output/handoffs/{task}.json",
        "agents/00-runtime/output/{task}/handoff.json",
    ),
    (
        "agents/00-runtime/output/evidence/{task_id}/manifest.json",
        "agents/00-runtime/output/{task_id}/qa-gate-({N})/evidence/manifest.json",
    ),
    (
        "agents/00-runtime/output/mobile/qa_evidence/T-P3-009/",
        "agents/00-runtime/output/T-P3-009/qa-gate-(1)/evidence/",
    ),
    (
        "agents/00-runtime/output/mobile/qa_evidence/{task_id}/",
        "agents/00-runtime/output/{task_id}/qa-gate-({N})/evidence/",
    ),
    (
        "agents/00-runtime/output/mobile/qa_evidence/{tid}/",
        "agents/00-runtime/output/{tid}/qa-gate-({N})/evidence/",
    ),
    (
        "agents/00-runtime/output/mobile/qa_seed_cache/{task_id}.json",
        "agents/00-runtime/output/{task_id}/seed-cache.json",
    ),
    (
        "agents/00-runtime/output/mobile/guides/",
        "agents/00-runtime/system/mobile/guides/",
    ),
    (
        "agents/00-runtime/output/dispatch/",
        "agents/00-runtime/system/dispatch/",
    ),
    (
        "agents/00-runtime/output/orchestrator/",
        "agents/00-runtime/system/orchestrator/",
    ),
    (
        "agents/00-runtime/output/board/",
        "agents/00-runtime/system/board/",
    ),
    (
        "agents/00-runtime/output/observability/",
        "agents/00-runtime/system/observability/",
    ),
    (
        "agents/00-runtime/output/audit-trail.jsonl",
        "agents/00-runtime/system/audit/audit-trail.jsonl",
    ),
    (
        "agents/00-runtime/output/handoffs/",
        "agents/00-runtime/system/handoffs/",
    ),
]

SKIP_NAMES = {"KNOWLEDGE.md", "REPO_KNOWLEDGE.md"}


def main() -> int:
    changed: list[str] = []
    for path in sorted(MODULE_ROOT.rglob("*.md")):
        if path.name in SKIP_NAMES:
            continue
        text = path.read_text(encoding="utf-8")
        original = text
        for old, new in REPLACEMENTS:
            text = text.replace(old, new)
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed.append(path.relative_to(MODULE_ROOT).as_posix())
    print(f"Atualizados {len(changed)} arquivos .md")
    for name in changed[:30]:
        print(f"  - {name}")
    if len(changed) > 30:
        print(f"  ... +{len(changed) - 30} mais")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
