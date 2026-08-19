#!/usr/bin/env python3
"""GraphQL verify Project #2 — contagem e gaps de campos (Trilha, OKR, Epic, Refinamento)."""
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
REPORT_PATH = ROOT / "08-board" / "verify_report.json"


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


def list_items() -> list[dict]:
    items: list[dict] = []
    cursor = None
    while True:
        d = gql(
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
                      content {
                        ... on DraftIssue { title body }
                        ... on Issue { title }
                      }
                    }
                  }
                }
              }
            }
            """,
            {"org": ORG, "num": PROJECT_NUMBER, "after": cursor},
        )
        conn = d["organization"]["projectV2"]["items"]
        for n in conn["nodes"]:
            row: dict = {}
            content = n.get("content") or {}
            row["title"] = content.get("title", "")
            row["body"] = content.get("body", "")
            for fv in n.get("fieldValues", {}).get("nodes", []):
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


def main() -> int:
    board = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    expected = {f"[{it['id']}] {it['title']}": it for it in board["items"]}
    actual_items = list_items()
    actual_titles = {i["title"] for i in actual_items if i.get("title")}
    v2 = [i for i in actual_items if (i.get("title") or "").startswith("[T-")]
    missing = set(expected.keys()) - actual_titles

    gap_trilha = gap_okr = gap_epic = gap_refin = gap_blocker_motivo = []

    for title, exp in expected.items():
        gh = next((i for i in v2 if i.get("title") == title), None)
        if not gh:
            continue
        tid = exp["id"]
        if not gh.get("Trilha"):
            gap_trilha.append(tid)
        if not gh.get("OKR"):
            gap_okr.append(tid)
        if not gh.get("Epic"):
            gap_epic.append(tid)
        refin = gh.get("Refinamento") or gh.get("body") or ""
        if len(refin) < 50:
            gap_refin.append(tid)
        if gh.get("Release Blocker") == "yes" and not gh.get("Blocker Motivo"):
            exp_motivo = exp.get("fields", {}).get("Blocker Motivo", "")
            if exp_motivo:
                gap_blocker_motivo.append(tid)

    report = {
        "expected": len(expected),
        "actual": len(actual_items),
        "v2_cards": len(v2),
        "missing_cards": len(missing),
        "missing_trilha": len(gap_trilha),
        "missing_okr": len(gap_okr),
        "missing_epic": len(gap_epic),
        "missing_refinamento": len(gap_refin),
        "missing_blocker_motivo": len(gap_blocker_motivo),
        "sample_missing": sorted(missing)[:5],
        "sample_gap_trilha": gap_trilha[:5],
        "sample_gap_refin": gap_refin[:5],
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(
        f"Esperado: {report['expected']} | No Project: {report['actual']} | [T-*]: {report['v2_cards']} | "
        f"Faltando cards: {report['missing_cards']}"
    )
    print(
        f"Gaps campos — Trilha: {report['missing_trilha']} | OKR: {report['missing_okr']} | "
        f"Epic: {report['missing_epic']} | Refinamento: {report['missing_refinamento']} | "
        f"Blocker motivo: {report['missing_blocker_motivo']}"
    )
    if missing:
        for t in sorted(missing)[:5]:
            print(f"  - card: {t[:70]}")

    ok = not missing and not any([
        gap_trilha, gap_okr, gap_epic, gap_refin, gap_blocker_motivo,
    ])
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
