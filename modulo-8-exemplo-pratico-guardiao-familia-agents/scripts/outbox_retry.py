#!/usr/bin/env python3
"""Retry da outbox GitHub."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.board_client import add_labels, _update_github_status  # noqa: E402
from lib.outbox import process_pending, read_pending  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--once", action="store_true", default=True)
    p.add_argument("--list", action="store_true")
    args = p.parse_args()

    if args.list:
        print(json.dumps(read_pending(), ensure_ascii=False, indent=2))
        return 0

    def handle_status(payload: dict) -> dict:
        return _update_github_status(payload["task_id"], payload["title"], payload["status"])

    def handle_labels(payload: dict) -> dict:
        return add_labels(payload["repo"], payload["task_id"], payload["labels"], dry_run=False)

    result = process_pending({
        "update_status": handle_status,
        "add_labels": handle_labels,
    })
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
