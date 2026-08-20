#!/usr/bin/env python3
"""Auditoria de qualidade do board v2: refinamento, OKR/Epic/Trilha e blockers."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from task_refinement import refine_item, blocker_reason  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "08-board" / "github-project-2-import.json"
REPORT_PATH = ROOT / "08-board" / "audit_quality_report.json"
ORG = "guardiaofamilia"
PROJECT_NUMBER = 2


def audit_local(board: dict) -> dict:
    items = board["items"]
    gaps = {
        "missing_trilha": [],
        "missing_okr": [],
        "missing_epic": [],
        "missing_refinamento": [],
        "missing_files": [],
        "blocker_without_reason": [],
    }
    fixed_refinement = 0

    for it in items:
        tid = it["id"]
        f = it.get("fields", {})
        ref = it.get("refinement") or {}

        for key, field in [("missing_trilha", "Trilha"), ("missing_okr", "OKR"), ("missing_epic", "Epic")]:
            if not str(f.get(field, "")).strip():
                gaps[key].append(tid)

        refin = f.get("Refinamento", "") or ref.get("context_summary", "")
        if not refin or len(str(refin).strip()) < 30:
            gaps["missing_refinamento"].append(tid)

        if not ref.get("suggested_files"):
            gaps["missing_files"].append(tid)

        if f.get("Release Blocker") == "yes":
            motivo = f.get("Blocker Motivo") or ref.get("blocker_reason") or blocker_reason(it)
            if not motivo:
                gaps["blocker_without_reason"].append(tid)

        # Auto-fix local refinement if thin
        if not ref.get("suggested_files") or len(str(refin).strip()) < 30:
            new_ref = refine_item(it)
            it["refinement"] = new_ref
            f["Refinamento"] = new_ref["context_summary"][:900]
            if f.get("Release Blocker") == "yes":
                f["Blocker Motivo"] = new_ref.get("blocker_reason", "")
            fixed_refinement += 1

    return {
        "source": "local_json",
        "total": len(items),
        "gaps": {k: {"count": len(v), "ids": v[:20]} for k, v in gaps.items()},
        "fixed_refinement": fixed_refinement,
        "blockers_with_reason": sum(
            1 for it in items
            if it.get("fields", {}).get("Release Blocker") == "yes"
            and (it.get("fields", {}).get("Blocker Motivo") or (it.get("refinement") or {}).get("blocker_reason"))
        ),
        "release_blockers": sum(1 for it in items if it.get("fields", {}).get("Release Blocker") == "yes"),
    }


def _token() -> str | None:
    return (os.environ.get("CURSOR_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN") or "").strip() or None


def _gql(query: str, variables: dict) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"Bearer {_token()}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode())
    if data.get("errors"):
        raise RuntimeError("; ".join(e["message"] for e in data["errors"]))
    return data["data"]


def fetch_github_items() -> list[dict]:
    items: list[dict] = []
    cursor = None
    while True:
        data = _gql(
            """
            query($org: String!, $num: Int!, $after: String) {
              organization(login: $org) {
                projectV2(number: $num) {
                  items(first: 100, after: $after) {
                    pageInfo { hasNextPage endCursor }
                    nodes {
                      fieldValues(first: 30) {
                        nodes {
                          ... on ProjectV2ItemFieldTextValue {
                            text
                            field { ... on ProjectV2FieldCommon { name } }
                          }
                          ... on ProjectV2ItemFieldSingleSelectValue {
                            name
                            field { ... on ProjectV2FieldCommon { name } }
                          }
                        }
                      }
                      content { ... on DraftIssue { title body } ... on Issue { title } }
                    }
                  }
                }
              }
            }
            """,
            {"org": ORG, "num": PROJECT_NUMBER, "after": cursor},
        )
        conn = data["organization"]["projectV2"]["items"]
        for node in conn["nodes"]:
            row: dict = {}
            content = node.get("content") or {}
            row["title"] = content.get("title", "")
            row["body"] = content.get("body", "")
            for fv in node.get("fieldValues", {}).get("nodes", []):
                fname = (fv.get("field") or {}).get("name", "")
                if "text" in fv:
                    row[fname] = fv["text"]
                elif "name" in fv and fname:
                    row[fname] = fv["name"]
            items.append(row)
        if not conn["pageInfo"]["hasNextPage"]:
            break
        cursor = conn["pageInfo"]["endCursor"]
    return items


def audit_github(expected_board: dict) -> dict | None:
    if not _token():
        return None

    expected_by_title = {f"[{it['id']}] {it['title']}": it for it in expected_board["items"]}
    gh_items = fetch_github_items()
    v2 = [i for i in gh_items if (i.get("title") or "").startswith("[T-")]

    gaps = {
        "missing_cards": [],
        "missing_trilha": [],
        "missing_okr": [],
        "missing_epic": [],
        "missing_refinamento": [],
        "blocker_without_reason": [],
    }

    for title, exp in expected_by_title.items():
        gh = next((i for i in v2 if i.get("title") == title), None)
        if not gh:
            gaps["missing_cards"].append(exp["id"])
            continue
        if not gh.get("Trilha"):
            gaps["missing_trilha"].append(exp["id"])
        if not gh.get("OKR"):
            gaps["missing_okr"].append(exp["id"])
        if not gh.get("Epic"):
            gaps["missing_epic"].append(exp["id"])
        refin = gh.get("Refinamento") or gh.get("body", "")
        if not refin or len(refin) < 50:
            gaps["missing_refinamento"].append(exp["id"])
        if gh.get("Release Blocker") == "yes" and not gh.get("Blocker Motivo"):
            gaps["blocker_without_reason"].append(exp["id"])

    return {
        "source": "github_project",
        "total_cards": len(v2),
        "expected": len(expected_by_title),
        "gaps": {k: {"count": len(v), "ids": v[:20]} for k, v in gaps.items()},
    }


def main() -> int:
    write = "--write" in sys.argv
    board = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    local = audit_local(board)

    if write and local["fixed_refinement"]:
        JSON_PATH.write_text(json.dumps(board, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"JSON atualizado — {local['fixed_refinement']} refinamentos corrigidos")

    remote = audit_github(board)
    report = {"generated": date.today().isoformat(), "local": local, "github": remote}
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Local: {local['total']} tasks | blockers c/ motivo: {local['blockers_with_reason']}/{local['release_blockers']}")
    for key, info in local["gaps"].items():
        if info["count"]:
            print(f"  LOCAL {key}: {info['count']}")

    if remote:
        print(f"GitHub: {remote['total_cards']}/{remote['expected']} cards")
        for key, info in remote["gaps"].items():
            if info["count"]:
                print(f"  GH {key}: {info['count']}")
    else:
        print("GitHub: skip (sem CURSOR_GITHUB_TOKEN)")

    print(f"Report: {REPORT_PATH}")
    has_gaps = any(v["count"] for v in local["gaps"].values())
    if remote:
        has_gaps = has_gaps or any(v["count"] for v in remote["gaps"].values())
    return 1 if has_gaps else 0


if __name__ == "__main__":
    raise SystemExit(main())
