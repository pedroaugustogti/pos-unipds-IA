#!/usr/bin/env python3
"""Converte Project V2 DraftIssue -> Issue no repo alvo (piloto / batch)."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path

GH = Path(r"C:\Program Files\GitHub CLI\gh.exe")
if not GH.exists():
    GH = Path("gh")

ORG = "guardiaofamilia"
PROJECT_NUMBER = 2
ROOT = Path(__file__).resolve().parents[1]
MAP_CSV = ROOT / "TASK_AGENT_MAP.csv"
LOG_PATH = ROOT / "crew" / "output" / "convert_drafts_log.jsonl"

MUTATION = """
mutation($itemId: ID!, $repositoryId: ID!) {
  convertProjectV2DraftIssueItemToIssue(
    input: { itemId: $itemId, repositoryId: $repositoryId }
  ) {
    item {
      id
      content {
        ... on Issue {
          id
          number
          url
          title
          repository { nameWithOwner }
        }
        ... on DraftIssue { id title }
      }
    }
  }
}
"""

REPO_IDS_CACHE: dict[str, str] = {}


def gh_graphql(query: str, variables: dict | None = None) -> dict:
    payload = json.dumps({"query": query, "variables": variables or {}})
    r = subprocess.run(
        [str(GH), "api", "graphql", "--input", "-"],
        input=payload,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr or r.stdout or "gh graphql failed")
    data = json.loads(r.stdout)
    if data.get("errors"):
        raise RuntimeError(json.dumps(data["errors"], ensure_ascii=False))
    return data["data"]


def repo_node_id(name: str) -> str:
    if name in REPO_IDS_CACHE:
        return REPO_IDS_CACHE[name]
    r = subprocess.run(
        [str(GH), "repo", "view", f"{ORG}/{name}", "--json", "id,nameWithOwner"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if r.returncode != 0:
        raise RuntimeError(f"Repo nao encontrado: {ORG}/{name}: {r.stderr}")
    rid = json.loads(r.stdout)["id"]
    REPO_IDS_CACHE[name] = rid
    return rid


def list_project_items(limit: int | None = None) -> list[dict]:
    fetch = max(limit or 500, 100)
    args = [
        str(GH),
        "project",
        "item-list",
        str(PROJECT_NUMBER),
        "--owner",
        ORG,
        "--limit",
        str(fetch),
        "--format",
        "json",
    ]
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(r.stderr or r.stdout)
    payload = json.loads(r.stdout or "{}")
    items = payload.get("items") or []
    if limit:
        return items[:limit]
    return items


def load_task_repo_map() -> dict[str, str]:
    rows = list(csv.DictReader(MAP_CSV.open(encoding="utf-8")))
    return {r["id"]: r.get("repo") or "guardiao-familia-api" for r in rows}


def parse_task_id(title: str) -> str | None:
    if title.startswith("[") and "]" in title:
        return title[1 : title.index("]")]
    return None


def item_is_draft(item: dict) -> bool:
    content = item.get("content") or {}
    t = (content.get("type") or item.get("type") or "").lower()
    if t in ("draftissue", "draft_issue"):
        return True
    # gh format uses content.type
    if isinstance(content, dict) and content.get("type") == "DraftIssue":
        return True
    # sem number de issue
    if content.get("type") == "Issue":
        return False
    body_id = content.get("id") or ""
    return str(body_id).startswith("DI_")


def convert_one(item: dict, repo: str, *, dry_run: bool = False) -> dict:
    item_id = item["id"]
    title = item.get("title") or (item.get("content") or {}).get("title") or ""
    task_id = parse_task_id(title)
    row = {
        "task_id": task_id,
        "title": title,
        "item_id": item_id,
        "repo": repo,
        "dry_run": dry_run,
    }
    if dry_run:
        row["ok"] = True
        row["skipped"] = "dry_run"
        return row
    rid = repo_node_id(repo)
    data = gh_graphql(MUTATION, {"itemId": item_id, "repositoryId": rid})
    content = (((data.get("convertProjectV2DraftIssueItemToIssue") or {}).get("item") or {}).get("content") or {})
    row["ok"] = True
    row["issue_number"] = content.get("number")
    row["issue_url"] = content.get("url")
    row["issue_id"] = content.get("id")
    row["repository"] = (content.get("repository") or {}).get("nameWithOwner")
    return row


def append_log(row: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=0, help="0 = todos")
    p.add_argument("--only-task", default="", help="Ex.: T-P05-001")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--pilot", action="store_true", help="Converte so o primeiro draft")
    p.add_argument("--sleep", type=float, default=0.4, help="Pausa entre conversoes")
    args = p.parse_args()

    task_repos = load_task_repo_map()
    items = list_project_items(limit=args.limit or None)
    drafts = [i for i in items if item_is_draft(i)]
    print(f"Itens: {len(items)} | Drafts: {len(drafts)}", flush=True)

    if args.only_task:
        drafts = [i for i in drafts if parse_task_id(i.get("title") or "") == args.only_task]
    if args.pilot:
        drafts = drafts[:1]

    ok = fail = 0
    for item in drafts:
        title = item.get("title") or ""
        task_id = parse_task_id(title)
        repo = (
            item.get("repo alvo")
            or item.get("repo Alvo")
            or (task_repos.get(task_id) if task_id else None)
            or "guardiao-familia-api"
        )
        # normalizar nome curto
        if isinstance(repo, str) and "/" in repo:
            repo = repo.split("/")[-1]
        try:
            row = convert_one(item, repo, dry_run=args.dry_run)
            append_log(row)
            if row.get("ok"):
                ok += 1
                print(f"OK {task_id} -> {repo} #{row.get('issue_number')} {row.get('issue_url')}", flush=True)
            else:
                fail += 1
                print(f"FAIL {task_id}: {row}", flush=True)
        except Exception as exc:  # noqa: BLE001
            fail += 1
            err = {"ok": False, "task_id": task_id, "title": title, "repo": repo, "error": str(exc)}
            append_log(err)
            print(f"ERROR {task_id}: {exc}", flush=True)
            # Impedimento critico tipico: auth/permission — parar
            msg = str(exc).lower()
            if any(x in msg for x in ("forbidden", "401", "403", "resource not accessible", "not found")):
                print("IMPEDIMENTO RUNTIME: permissao/API. Abortando batch.", flush=True)
                return 2
        if args.sleep and not args.dry_run:
            time.sleep(args.sleep)

    print(json.dumps({"ok": ok, "fail": fail, "log": str(LOG_PATH)}, ensure_ascii=False), flush=True)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
