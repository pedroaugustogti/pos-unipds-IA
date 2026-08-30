#!/usr/bin/env python3
"""Mescla enrichment + re-publica corpo das issues T-P3-* no GitHub."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import time
from pathlib import Path

_bs = Path(__file__).resolve().parents[2] / "bootstrap.py"
_spec = importlib.util.spec_from_file_location("ba_bootstrap", _bs)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
_mod.setup()

from board_automation.board.board_client import ORG  # noqa: E402
from board_automation.board.issue_task_body import build_issue_body  # noqa: E402
from lib.paths import BOARD_IMPORTS_DIR, PROJECT3_ITEM_CACHE_PATH  # noqa: E402

BACKLOG = BOARD_IMPORTS_DIR / "BACKLOG_PROJECT3.json"
EXTRA = BOARD_IMPORTS_DIR / "PROJECT3_REFINEMENT_EXTRA.json"
CACHE = PROJECT3_ITEM_CACHE_PATH


def _deep_merge(base: dict, extra: dict) -> dict:
    out = dict(base)
    for k, v in extra.items():
        if k == "refinement" and isinstance(v, dict):
            ref = dict(out.get("refinement") or {})
            ref.update(v)
            out["refinement"] = ref
        else:
            out[k] = v
    return out


def load_tasks() -> tuple[dict, list[dict]]:
    backlog = json.loads(BACKLOG.read_text(encoding="utf-8"))
    extra_all = json.loads(EXTRA.read_text(encoding="utf-8")) if EXTRA.is_file() else {}
    tasks = []
    for t in backlog["tasks"]:
        tid = t["id"]
        merged = _deep_merge(t, extra_all.get(tid, {}))
        tasks.append(merged)
    return backlog, tasks


def update_issue(repo: str, number: str, body: str, *, dry_run: bool) -> None:
    if dry_run:
        print(f"  dry-run issue #{number} ({len(body)} chars)")
        return
    payload = json.dumps({"body": body}, ensure_ascii=False).encode("utf-8")
    r = subprocess.run(
        ["gh", "api", "-X", "PATCH", f"repos/{ORG}/{repo}/issues/{number}", "--input", "-"],
        input=payload,
        capture_output=True,
        check=False,
    )
    if r.returncode != 0:
        err = (r.stderr or r.stdout or b"").decode("utf-8", errors="replace")
        raise RuntimeError(err[:500])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--task", default="", help="Só um task_id ex: T-P3-001")
    args = parser.parse_args()

    backlog, tasks = load_tasks()
    conv = backlog.get("comment_conventions") or {}
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}

    for task in tasks:
        tid = task["id"]
        if args.task and tid != args.task:
            continue
        entry = cache.get(tid)
        if not entry or not entry.get("issue_number"):
            print(f"skip {tid}: sem cache/issue_number")
            continue
        num = str(entry["issue_number"])
        repo = task["repo"]
        body = build_issue_body(task, conv)
        print(f"patch {tid} {ORG}/{repo}#{num}...")
        update_issue(repo, num, body, dry_run=args.dry_run)
        time.sleep(1.2)

    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
