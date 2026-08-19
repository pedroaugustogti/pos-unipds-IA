#!/usr/bin/env python3
"""Sync Story Points and RICE/WSJF prioritization fields to GitHub Project #1."""

from __future__ import annotations

import csv
import json
import os
import re
import sys
import time
from pathlib import Path

import urllib.request

ORG = "guardiaofamilia"
PROJECT_NUMBER = 1
PROJECT_ID = "PVT_kwDOEDZbAM4BTJdj"
STATUS_FIELD_ID = "PVTSSF_lADOEDZbAM4BTJdjzhAeRt0"
STATUS_TODO_OPTION = "f75ad846"

FIELD_IDS = {
    "Story Points": "PVTF_lADOEDZbAM4BTJdjzhf0iqE",
    "RICE Score": "PVTF_lADOEDZbAM4BTJdjzhf0irA",
    "WSJF": "PVTF_lADOEDZbAM4BTJdjzhf0irE",
    "Reach": "PVTF_lADOEDZbAM4BTJdjzhf0irI",
    "Impact": "PVTF_lADOEDZbAM4BTJdjzhf0irg",
    "Confidence": "PVTF_lADOEDZbAM4BTJdjzhf0isc",
    "CoD": "PVTF_lADOEDZbAM4BTJdjzhf0iuQ",
    "OKR": "PVTF_lADOEDZbAM4BTJdjzhf0iuU",
    "Epic": "PVTF_lADOEDZbAM4BTJdjzhf0iuY",
    "Sprint": "PVTF_lADOEDZbAM4BTJdjzhf0iuc",
    "Release Blocker": "PVTF_lADOEDZbAM4BTJdjzhf0ivw",
}

ONDA_DEFAULTS = {
    "Onda 0 - Fundacao": {
        "epic": "E1",
        "okr": "O2-KR2",
        "sprint": "S1",
        "reach": 600,
        "impact": 3,
        "confidence": 0.8,
        "cod": 34,
        "release_blocker": "sim",
        "base_sp": 5,
    },
    "Onda 1 - Auth/Pairing": {
        "epic": "E2",
        "okr": "O3-KR1",
        "sprint": "S2",
        "reach": 300,
        "impact": 2,
        "confidence": 0.8,
        "cod": 20,
        "release_blocker": "nao",
        "base_sp": 5,
    },
    "Onda 2 - Real-time": {
        "epic": "E3",
        "okr": "O1-KR2",
        "sprint": "S6",
        "reach": 420,
        "impact": 2,
        "confidence": 0.8,
        "cod": 31,
        "release_blocker": "sim",
        "base_sp": 5,
    },
    "Onda 3 - GPS/Geofences": {
        "epic": "E3",
        "okr": "O1-KR2",
        "sprint": "S6",
        "reach": 420,
        "impact": 2,
        "confidence": 0.8,
        "cod": 31,
        "release_blocker": "sim",
        "base_sp": 5,
    },
    "Onda 4 - SOS/Emergencia": {
        "epic": "E4",
        "okr": "O1-KR1",
        "sprint": "S4",
        "reach": 500,
        "impact": 3,
        "confidence": 0.8,
        "cod": 39,
        "release_blocker": "sim",
        "base_sp": 5,
    },
    "Onda 5 - Screen Time": {
        "epic": "E5",
        "okr": "O3-KR1",
        "sprint": "S7",
        "reach": 300,
        "impact": 2,
        "confidence": 0.8,
        "cod": 24,
        "release_blocker": "nao",
        "base_sp": 5,
    },
    "Onda 6 - Gamificacao": {
        "epic": "E6",
        "okr": "O3-KR2",
        "sprint": "S9",
        "reach": 260,
        "impact": 1,
        "confidence": 0.8,
        "cod": 18,
        "release_blocker": "nao",
        "base_sp": 3,
    },
    "Onda 7 - AI/Conteudo": {
        "epic": "E7",
        "okr": "O3-KR3",
        "sprint": "S10",
        "reach": 220,
        "impact": 1,
        "confidence": 0.8,
        "cod": 17,
        "release_blocker": "nao",
        "base_sp": 5,
    },
    "Onda 8 - Familia/Comunidade": {
        "epic": "E2",
        "okr": "O3-KR1",
        "sprint": "S10",
        "reach": 180,
        "impact": 1,
        "confidence": 0.5,
        "cod": 12,
        "release_blocker": "nao",
        "base_sp": 5,
    },
    "Onda 9 - Pagamentos/Admin": {
        "epic": "E8",
        "okr": "post-release",
        "sprint": "post-release",
        "reach": 200,
        "impact": 1,
        "confidence": 0.5,
        "cod": 12,
        "release_blocker": "nao",
        "base_sp": 5,
    },
    "Onda 10 - Polish/Release": {
        "epic": "E1",
        "okr": "O2-KR3",
        "sprint": "S11",
        "reach": 500,
        "impact": 2,
        "confidence": 0.8,
        "cod": 34,
        "release_blocker": "sim",
        "base_sp": 5,
    },
}

PLANNING_MARKER = "## Planejamento M7"


def get_token() -> str:
    token = os.environ.get("CURSOR_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("CURSOR_GITHUB_TOKEN or GITHUB_TOKEN required")
    return token.strip()


def graphql(token: str, query: str, variables: dict | None = None) -> dict:
    payload = {"query": query, "variables": variables or {}}
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "guardiao-familia-sync-priorization",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("errors"):
        raise RuntimeError("; ".join(e["message"] for e in data["errors"]))
    return data["data"]


def fetch_items(token: str) -> list[dict]:
    query = """
    query($cursor: String) {
      organization(login: "%s") {
        projectV2(number: %d) {
          items(first: 100, after: $cursor) {
            pageInfo { hasNextPage endCursor }
            nodes {
              id
              fieldValues(first: 25) {
                nodes {
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    name
                    field { ... on ProjectV2SingleSelectField { name } }
                  }
                }
              }
              content {
                __typename
                ... on Issue {
                  title
                  url
                  number
                  body
                  repository { name }
                }
                ... on PullRequest {
                  title
                  url
                  number
                  repository { name }
                }
                ... on DraftIssue {
                  title
                  body
                }
              }
            }
          }
        }
      }
    }
    """ % (ORG, PROJECT_NUMBER)

    items: list[dict] = []
    cursor = None
    while True:
        data = graphql(token, query, {"cursor": cursor})
        block = data["organization"]["projectV2"]["items"]
        for node in block["nodes"]:
            onda = ""
            for fv in node.get("fieldValues", {}).get("nodes", []):
                field = fv.get("field") or {}
                if field.get("name") == "Onda":
                    onda = fv.get("name") or ""
            content = node.get("content") or {}
            items.append(
                {
                    "item_id": node["id"],
                    "onda": onda,
                    "title": content.get("title") or "",
                    "url": content.get("url") or "",
                    "body": content.get("body") or "",
                    "repo": (content.get("repository") or {}).get("name") or "",
                    "number": content.get("number"),
                    "typename": content.get("__typename") or "",
                }
            )
        if not block["pageInfo"]["hasNextPage"]:
            break
        cursor = block["pageInfo"]["endCursor"]
        time.sleep(0.2)
    return items


def adjust_by_title(title: str, base: dict) -> dict:
    t = title.lower()
    result = dict(base)

    if any(k in t for k in ("chore", "deps", "bump", "dependabot")):
        result["base_sp"] = 1
        result["cod"] = min(result["cod"], 8)
    elif any(k in t for k in ("aws", "ecs", "fargate", "vpc", "rds", "redis", "terraform", "ci/cd", "github actions")):
        result.update({"epic": "E1", "okr": "O2-KR2", "sprint": "S1", "base_sp": 8, "release_blocker": "sim"})
    elif any(k in t for k in ("push", "fcm", "apns", "notification", "som", "sons", "critical alerts")):
        result.update({"epic": "E4", "okr": "O1-KR3", "sprint": "S3", "base_sp": 5, "impact": 3, "cod": 39, "release_blocker": "sim"})
    elif "sos" in t or "emerg" in t or "alerta" in t:
        result.update({"epic": "E4", "okr": "O1-KR1", "sprint": "S4", "base_sp": 8, "impact": 3, "cod": 39, "release_blocker": "sim"})
    elif any(k in t for k in ("geofenc", "cerca", "gps", "localiz")):
        result.update({"epic": "E3", "okr": "O1-KR2", "sprint": "S6", "base_sp": 5, "release_blocker": "sim"})
    elif any(k in t for k in ("lgpd", "compliance", "consent", "ripd", "purge", "privac")):
        result.update({"epic": "E9", "okr": "O2-KR1", "sprint": "S8", "base_sp": 8, "cod": 34, "release_blocker": "sim"})
    elif any(k in t for k in ("tempo extra", "screen time", "tempo de tela")):
        result.update({"epic": "E5", "okr": "O3-KR1", "sprint": "S7", "base_sp": 5, "cod": 24})
    elif any(k in t for k in ("stripe", "asaas", "paywall", "pagamento", "monetiz")):
        result.update({"epic": "E8", "okr": "post-release", "sprint": "post-release", "base_sp": 8, "cod": 12, "release_blocker": "nao"})
    elif any(k in t for k in ("vinculo", "rebrand", "inpi")):
        result.update({"epic": "E10", "okr": "out-of-scope", "sprint": "out-of-scope", "base_sp": 13, "cod": 10, "release_blocker": "nao"})
    elif any(k in t for k in ("store", "play store", "app store", "publish", "testflight")):
        result.update({"epic": "E1", "okr": "O2-KR3", "sprint": "S11", "base_sp": 8, "cod": 34, "release_blocker": "sim"})
    elif any(k in t for k in ("ia", "chat", "assistente", "relatorio")):
        result.update({"epic": "E7", "okr": "O3-KR3", "sprint": "S10", "base_sp": 5})
    elif any(k in t for k in ("backoffice", "suporte", "dashboard", "moderacao")):
        result.update({"epic": "E8", "okr": "O2-KR3", "sprint": "S12", "base_sp": 5, "cod": 22})
    elif any(k in t for k in ("gamific", "conquista")):
        result.update({"epic": "E6", "okr": "O3-KR2", "sprint": "S9", "base_sp": 3})
    elif "criar app" in t or "app mobile" in t:
        result["base_sp"] = 8

    sp = max(1, int(result["base_sp"]))
    rice = round((result["reach"] * result["impact"] * result["confidence"]) / sp, 2)
    wsjf = round(result["cod"] / sp, 2)
    result.update({"sp": sp, "rice": rice, "wsjf": wsjf})
    return result


def compute_row(item: dict) -> dict:
    onda = item["onda"] or "Onda 0 - Fundacao"
    base = dict(ONDA_DEFAULTS.get(onda, ONDA_DEFAULTS["Onda 0 - Fundacao"]))
    metrics = adjust_by_title(item["title"], base)
    return {
        "item_id": item["item_id"],
        "title": item["title"],
        "url": item["url"],
        "repo": item["repo"],
        "number": item["number"],
        "onda": onda,
        "epic": metrics["epic"],
        "okr": metrics["okr"],
        "sprint": metrics["sprint"],
        "reach": metrics["reach"],
        "impact": metrics["impact"],
        "confidence": metrics["confidence"],
        "cod": metrics["cod"],
        "sp": metrics["sp"],
        "rice": metrics["rice"],
        "wsjf": metrics["wsjf"],
        "release_blocker": metrics["release_blocker"],
    }


def update_field(token: str, item_id: str, field_id: str, value: dict) -> None:
    mutation = """
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $projectId
        itemId: $itemId
        fieldId: $fieldId
        value: $value
      }) {
        projectV2Item { id }
      }
    }
    """
    graphql(
        token,
        mutation,
        {
            "projectId": PROJECT_ID,
            "itemId": item_id,
            "fieldId": field_id,
            "value": value,
        },
    )


def append_planning_to_issue(token: str, row: dict) -> None:
    if not row["url"] or not row["number"] or not row["repo"]:
        return
    body_req = """
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $number) { body }
      }
    }
    """
    current = graphql(
        token,
        body_req,
        {"owner": ORG, "repo": row["repo"], "number": row["number"]},
    )
    body = (current["repository"]["issue"] or {}).get("body") or ""
    block = (
        f"{PLANNING_MARKER}\n"
        f"- OKR: {row['okr']}\n"
        f"- Epic: {row['epic']}\n"
        f"- Sprint: {row['sprint']}\n"
        f"- Story Points: {row['sp']}\n"
        f"- Reach: {row['reach']} | Impact: {row['impact']} | Confidence: {row['confidence']}\n"
        f"- CoD: {row['cod']} | RICE: {row['rice']} | WSJF: {row['wsjf']}\n"
        f"- Release blocker: {row['release_blocker']}\n"
    )
    if PLANNING_MARKER in body:
        body = re.sub(
            rf"{re.escape(PLANNING_MARKER)}[\s\S]*?(?=\n## |\Z)",
            block.rstrip() + "\n",
            body,
            count=1,
        )
    else:
        body = (body.rstrip() + "\n\n" + block).strip() + "\n"

    mutation = """
    mutation($id: ID!, $body: String!) {
      updateIssue(input: { id: $id, body: $body }) {
        issue { number }
      }
    }
    """
    issue_id_query = """
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $number) { id }
      }
    }
    """
    issue_data = graphql(
        token,
        issue_id_query,
        {"owner": ORG, "repo": row["repo"], "number": row["number"]},
    )
    issue_id = issue_data["repository"]["issue"]["id"]
    graphql(token, mutation, {"id": issue_id, "body": body})


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    skip_issues = "--skip-issues" in sys.argv
    token = get_token()
    items = fetch_items(token)
    rows = [compute_row(item) for item in items]

    out_dir = Path(__file__).resolve().parents[1] / "docs" / "planejamento" / "07-github-board"
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "CARDS_PRIORIZACAO_APLICADA.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "item_id", "title", "url", "repo", "number", "onda", "epic", "okr", "sprint",
                "reach", "impact", "confidence", "cod", "sp", "rice", "wsjf", "release_blocker",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"items={len(rows)} csv={csv_path}")
    if dry_run:
        print("dry-run: no remote updates")
        return 0

    for i, row in enumerate(rows, 1):
        item_id = row["item_id"]
        update_field(token, item_id, STATUS_FIELD_ID, {"singleSelectOptionId": STATUS_TODO_OPTION})
        update_field(token, item_id, FIELD_IDS["Story Points"], {"number": float(row["sp"])})
        update_field(token, item_id, FIELD_IDS["RICE Score"], {"number": float(row["rice"])})
        update_field(token, item_id, FIELD_IDS["WSJF"], {"number": float(row["wsjf"])})
        update_field(token, item_id, FIELD_IDS["Reach"], {"number": float(row["reach"])})
        update_field(token, item_id, FIELD_IDS["Impact"], {"number": float(row["impact"])})
        update_field(token, item_id, FIELD_IDS["Confidence"], {"number": float(row["confidence"])})
        update_field(token, item_id, FIELD_IDS["CoD"], {"number": float(row["cod"])})
        update_field(token, item_id, FIELD_IDS["OKR"], {"text": row["okr"]})
        update_field(token, item_id, FIELD_IDS["Epic"], {"text": row["epic"]})
        update_field(token, item_id, FIELD_IDS["Sprint"], {"text": row["sprint"]})
        update_field(token, item_id, FIELD_IDS["Release Blocker"], {"text": row["release_blocker"]})

        if not skip_issues and row["url"] and row["number"]:
            try:
                append_planning_to_issue(token, row)
            except Exception as exc:  # noqa: BLE001
                print(f"warn issue {row['repo']}#{row['number']}: {exc}")

        if i % 10 == 0:
            print(f"updated {i}/{len(rows)}")
            time.sleep(0.5)

    print(f"done updated={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
