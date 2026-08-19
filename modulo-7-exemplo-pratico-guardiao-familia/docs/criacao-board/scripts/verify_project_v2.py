#!/usr/bin/env python3
"""GraphQL verify Project #2 vs 272 tasks."""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

ORG = "guardiaofamilia"
PROJECT_NUMBER = 2
ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "08-board" / "github-project-2-import.json"


def token() -> str:
    t = (os.environ.get("CURSOR_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN") or "").strip()
    if not t:
        raise SystemExit("Defina CURSOR_GITHUB_TOKEN")
    return t


def gql(query: str, variables: dict) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode())
    if data.get("errors"):
        raise SystemExit("; ".join(e["message"] for e in data["errors"]))
    return data["data"]


def list_titles() -> set[str]:
    titles: set[str] = set()
    cursor = None
    while True:
        d = gql(
            """
            query($org: String!, $num: Int!, $after: String) {
              organization(login: $org) {
                projectV2(number: $num) {
                  items(first: 100, after: $after) {
                    pageInfo { hasNextPage endCursor }
                    nodes { content { ... on DraftIssue { title } ... on Issue { title } } }
                  }
                }
              }
            }
            """,
            {"org": ORG, "num": PROJECT_NUMBER, "after": cursor},
        )
        conn = d["organization"]["projectV2"]["items"]
        for n in conn["nodes"]:
            t = (n.get("content") or {}).get("title")
            if t:
                titles.add(t)
        if not conn["pageInfo"]["hasNextPage"]:
            break
        cursor = conn["pageInfo"]["endCursor"]
    return titles


def main() -> int:
    expected = {f"[{it['id']}] {it['title']}" for it in json.loads(JSON_PATH.read_text(encoding="utf-8"))["items"]}
    actual = list_titles()
    v2 = {t for t in actual if t.startswith("[T-")}
    missing = expected - actual

    print(f"Esperado: {len(expected)} | No Project: {len(actual)} | [T-*]: {len(v2)} | Faltando: {len(missing)}")
    if missing:
        for t in sorted(missing)[:10]:
            print(f"  - {t[:75]}")
    out = ROOT / "08-board" / "verify_report.json"
    out.write_text(json.dumps({"expected": len(expected), "actual": len(actual), "missing": len(missing)}, indent=2))
    return 0 if not missing else 2


if __name__ == "__main__":
    raise SystemExit(main())
