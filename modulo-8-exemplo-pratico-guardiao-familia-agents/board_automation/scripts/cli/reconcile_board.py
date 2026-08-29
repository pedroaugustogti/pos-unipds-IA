#!/usr/bin/env python3
"""A3 — Reconcilia Status do GitHub Project #2 → JSON local do board."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_bs = Path(__file__).resolve().parents[2] / "bootstrap.py"
_spec = importlib.util.spec_from_file_location("orch_bootstrap", _bs)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
_mod.setup()

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from lib.paths import MODULE_ROOT  # noqa: E402
from lib.env_load import ensure_env  # noqa: E402

ensure_env()
from board_automation.board.local_board import load_board, save_board  # noqa: E402
from lib.paths import PROJECT_ITEM_CACHE_PATH

CACHE_PATH = PROJECT_ITEM_CACHE_PATH
from board_automation.board.task_status_workflow import resolve_status  # noqa: E402

GH = Path(r"C:\Program Files\GitHub CLI\gh.exe")
if not GH.exists():
    GH = Path("gh")

ORG = "guardiaofamilia"
PROJECT_NUMBER = 2
TASK_RE = re.compile(r"^\[([A-Z]-[A-Z0-9]+-\d+)\]")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def list_items() -> list[dict]:
    r = subprocess.run(
        [
            str(GH), "project", "item-list", str(PROJECT_NUMBER),
            "--owner", ORG, "--limit", "500", "--format", "json",
        ],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr or r.stdout)
    return (json.loads(r.stdout or "{}")).get("items") or []


def parse_task_id(title: str) -> str | None:
    m = TASK_RE.match(title or "")
    return m.group(1) if m else None


def reconcile(*, dry_run: bool = False, force: bool = False) -> dict:
    """Reconcilia Status Project #2 → JSON local. Sem force: só alinha Todo→remoto e loga conflitos."""
    items = list_items()
    remote: dict[str, dict] = {}
    cache = {"updated_at": _now(), "items": {}}
    for it in items:
        title = it.get("title") or ""
        tid = parse_task_id(title)
        if not tid:
            continue
        st = it.get("status") or "Todo"
        try:
            st = resolve_status(str(st))
        except ValueError:
            st = "Todo"
        remote[tid] = {"status": st, "item_id": it.get("id"), "title": title}
        cache["items"][tid] = {"item_id": it.get("id"), "status": st, "title": title}

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not dry_run:
        CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    board = load_board()
    changed = []
    skipped = []
    for item in board.get("items") or []:
        tid = item.get("id")
        if tid not in remote:
            continue
        fields = item.setdefault("fields", {})
        local_st = str(fields.get("Status") or "Todo")
        rem_st = remote[tid]["status"]
        if local_st == rem_st:
            continue
        if not force and local_st not in ("Todo", rem_st):
            skipped.append({"task_id": tid, "local": local_st, "remote": rem_st})
            continue
        if not dry_run:
            fields["Status"] = rem_st
            if remote[tid].get("item_id"):
                fields["Project Item Id"] = remote[tid]["item_id"]
        changed.append({"task_id": tid, "from": local_st, "to": rem_st})

    if changed and not dry_run:
        save_board(board)

    return {
        "ok": True,
        "dry_run": dry_run,
        "force": force,
        "remote_count": len(remote),
        "changed": len(changed),
        "skipped_conflicts": skipped,
        "sample_changes": changed[:20],
        "cache": str(CACHE_PATH),
    }


def main() -> int:
    p = argparse.ArgumentParser(
        description=(
            "Reconcilia Status Project #2 → JSON local. "
            "Politica operacional (Fase 0): Project vence — use --project-wins."
        )
    )
    p.add_argument("--dry-run", action="store_true")
    p.add_argument(
        "--force",
        action="store_true",
        help="Sobrescreve mesmo se local != remoto",
    )
    p.add_argument(
        "--project-wins",
        action="store_true",
        help="Alias de --force: Status do GitHub Project prevalece sobre o JSON local",
    )
    args = p.parse_args()
    out = reconcile(dry_run=args.dry_run, force=args.force or args.project_wins)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
