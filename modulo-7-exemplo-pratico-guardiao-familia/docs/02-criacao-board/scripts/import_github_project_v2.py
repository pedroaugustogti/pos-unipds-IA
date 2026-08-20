#!/usr/bin/env python3
"""Importa items do github-project-2-import.json para GitHub Project v2."""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "08-board" / "github-project-2-import.json"


def gh(*args: str) -> str:
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr or r.stdout)
    return r.stdout.strip()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--project-number", type=int, default=2)
    p.add_argument("--owner", default="guardiaofamilia")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--limit", type=int, default=0)
    args = p.parse_args()

    board = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    items = board["items"]
    if args.limit:
        items = items[: args.limit]

    print(f"Project #{args.project_number} @ {args.owner}: {len(items)} items")
    if args.dry_run:
        for it in items[:5]:
            print(f"  [DRY] {it['id']}: {it['title']}")
        print(f"  ... +{len(items)-5} more" if len(items) > 5 else "")
        return

    created = 0
    for it in items:
        body = (
            f"**Task ID:** {it['id']}\n"
            f"**Trilha:** {it['fields']['Trilha']}\n"
            f"**OKR:** {it['fields']['OKR']}\n"
            f"**Epic:** {it['fields']['Epic']}\n"
            f"**Sprint:** S{it['fields']['Sprint']}\n"
            f"**SP:** {it['fields']['Story Points']} | RICE: {it['fields']['RICE Score']} | WSJF: {it['fields']['WSJF']}\n"
            f"**Baseline:** {it['fields']['Baseline']} | Blocker: {it['fields']['Release Blocker']}\n"
        )
        if it.get("commit_evidence"):
            body += f"**Commit:** `{it['commit_evidence']}`\n"

        title = f"[{it['id']}] {it['title']}"
        gh(
            "project", "item-create", str(args.project_number),
            "--owner", args.owner,
            "--title", title,
            "--body", body,
        )
        created += 1
        if created % 20 == 0:
            print(f"  created {created}/{len(items)}")
            time.sleep(2)  # rate limit courtesy

    print(f"Done: {created} draft issues created")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
