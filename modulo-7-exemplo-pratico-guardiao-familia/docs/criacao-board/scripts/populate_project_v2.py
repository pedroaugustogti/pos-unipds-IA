#!/usr/bin/env python3
"""Cria campos, importa 272 draft issues, refinamento e priorização no Project #2."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from task_refinement import build_issue_body  # noqa: E402

ORG = "guardiaofamilia"
PROJECT_NUMBER = 2
PROJECT_ID = "PVT_kwDOEDZbAM4Bg2rE"
ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "08-board" / "github-project-2-import.json"
GH = os.environ.get("GH_PATH", "gh")

FIELD_SPECS = [
    ("Trilha", "SINGLE_SELECT", ["produto", "infraestrutura", "stores"]),
    ("OKR", "TEXT", None),
    ("Epic", "TEXT", None),
    ("Sprint", "NUMBER", None),
    ("Story Points", "NUMBER", None),
    ("RICE Score", "NUMBER", None),
    ("WSJF", "NUMBER", None),
    ("Reach", "NUMBER", None),
    ("Impact", "NUMBER", None),
    ("Confidence", "NUMBER", None),
    ("CoD", "NUMBER", None),
    ("PERT (d)", "NUMBER", None),
    ("Baseline", "SINGLE_SELECT", ["done", "partial", "todo"]),
    ("Release Blocker", "SINGLE_SELECT", ["yes", "no"]),
    ("Priority Rank", "NUMBER", None),
    ("Repo alvo", "TEXT", None),
    ("Refinamento", "TEXT", None),
]


def token() -> str:
    t = os.environ.get("CURSOR_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not t:
        raise RuntimeError("CURSOR_GITHUB_TOKEN required")
    return t.strip()


def graphql(q: str, variables: dict | None = None) -> dict:
    payload = {"query": q, "variables": variables or {}}
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {token()}",
            "Content-Type": "application/json",
            "User-Agent": "gf-populate-v2",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode())
    if data.get("errors"):
        raise RuntimeError("; ".join(e["message"] for e in data["errors"]))
    return data["data"]


def gh_json(*args: str) -> dict:
    """Fallback gh CLI — preferir graphql para org projects."""
    env = os.environ.copy()
    env["GH_TOKEN"] = token()
    r = subprocess.run(
        [GH, *args, "--format", "json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr or r.stdout or "gh failed")
    return json.loads(r.stdout) if (r.stdout or "").strip() else {}


def list_items_graphql() -> list[dict]:
    items: list[dict] = []
    cursor = None
    while True:
        data = graphql(
            """
            query($org: String!, $num: Int!, $after: String) {
              organization(login: $org) {
                projectV2(number: $num) {
                  items(first: 100, after: $after) {
                    pageInfo { hasNextPage endCursor }
                    nodes {
                      id
                      fieldValues(first: 30) {
                        nodes {
                          ... on ProjectV2ItemFieldTextValue {
                            text
                            field { ... on ProjectV2FieldCommon { name } }
                          }
                          ... on ProjectV2ItemFieldNumberValue {
                            number
                            field { ... on ProjectV2FieldCommon { name } }
                          }
                          ... on ProjectV2ItemFieldSingleSelectValue {
                            name
                            field { ... on ProjectV2FieldCommon { name } }
                          }
                        }
                      }
                      content {
                        ... on DraftIssue { title body id }
                        ... on Issue { title number }
                      }
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
            row: dict = {"id": node["id"]}
            content = node.get("content") or {}
            row["title"] = content.get("title", "")
            row["draft_issue_id"] = content.get("id")
            for fv in node.get("fieldValues", {}).get("nodes", []):
                fname = (fv.get("field") or {}).get("name", "")
                if "text" in fv:
                    row[fname] = fv["text"]
                elif "number" in fv:
                    row[fname] = fv["number"]
                elif "name" in fv and fname:
                    row[fname] = fv["name"]
            items.append(row)
        if not conn["pageInfo"]["hasNextPage"]:
            break
        cursor = conn["pageInfo"]["endCursor"]
    return items


def ensure_fields_graphql() -> dict[str, dict]:
    data = graphql(
        """
        query($org: String!, $num: Int!) {
          organization(login: $org) {
            projectV2(number: $num) {
              fields(first: 50) {
                nodes {
                  ... on ProjectV2FieldCommon { id name }
                  ... on ProjectV2SingleSelectField { id name options { id name } }
                }
              }
            }
          }
        }
        """,
        {"org": ORG, "num": PROJECT_NUMBER},
    )
    by_name: dict[str, dict] = {}
    for f in data["organization"]["projectV2"]["fields"]["nodes"]:
        by_name[f["name"]] = f

    result = dict(by_name)
    for name, dtype, options in FIELD_SPECS:
        if name in result:
            continue
        if dtype == "SINGLE_SELECT":
            mutation = """
            mutation($pid: ID!, $name: String!, $opts: [ProjectV2SingleSelectFieldOptionInput!]!) {
              createProjectV2Field(input: {
                projectId: $pid, dataType: SINGLE_SELECT, name: $name,
                singleSelectOptions: $opts
              }) { projectV2Field { ... on ProjectV2SingleSelectField { id name options { id name } } } }
            }
            """
            opts = [{"name": o, "color": "GRAY", "description": o} for o in (options or [])]
            created = graphql(mutation, {"pid": PROJECT_ID, "name": name, "opts": opts})
            field = created["createProjectV2Field"]["projectV2Field"]
        elif dtype == "NUMBER":
            created = graphql(
                """
                mutation($pid: ID!, $name: String!) {
                  createProjectV2Field(input: { projectId: $pid, dataType: NUMBER, name: $name }) {
                    projectV2Field { ... on ProjectV2FieldCommon { id name } }
                  }
                }
                """,
                {"pid": PROJECT_ID, "name": name},
            )
            field = created["createProjectV2Field"]["projectV2Field"]
        else:
            created = graphql(
                """
                mutation($pid: ID!, $name: String!) {
                  createProjectV2Field(input: { projectId: $pid, dataType: TEXT, name: $name }) {
                    projectV2Field { ... on ProjectV2FieldCommon { id name } }
                  }
                }
                """,
                {"pid": PROJECT_ID, "name": name},
            )
            field = created["createProjectV2Field"]["projectV2Field"]
        result[name] = field
        print(f"  field created: {name}")
        time.sleep(0.5)

    # refresh options
    data2 = graphql(
        """
        query($org: String!, $num: Int!) {
          organization(login: $org) {
            projectV2(number: $num) {
              fields(first: 50) {
                nodes {
                  ... on ProjectV2SingleSelectField { id name options { id name } }
                  ... on ProjectV2FieldCommon { id name }
                }
              }
            }
          }
        }
        """,
        {"org": ORG, "num": PROJECT_NUMBER},
    )
    for f in data2["organization"]["projectV2"]["fields"]["nodes"]:
        if f["name"] in {n for n, _, _ in FIELD_SPECS}:
            result[f["name"]] = f
    return result


def create_draft_graphql(title: str, body: str) -> str:
    data = graphql(
        """
        mutation($pid: ID!, $title: String!, $body: String!) {
          addProjectV2DraftIssue(input: { projectId: $pid, title: $title, body: $body }) {
            projectItem { id }
          }
        }
        """,
        {"pid": PROJECT_ID, "title": title, "body": body},
    )
    return data["addProjectV2DraftIssue"]["projectItem"]["id"]


def item_has_fields_synced(item: dict) -> bool:
    if item.get("trilha") or item.get("Trilha"):
        return True
    if item.get("priority Rank") is not None or item.get("priorityRank") is not None:
        return True
    for k, v in item.items():
        if k.lower().replace(" ", "") in ("trilha", "priorityrank") and v is not None:
            return True
    return False


def create_draft(title: str, body: str) -> str:
    return create_draft_graphql(title, body)


def get_draft_issue_id(project_item_id: str) -> str | None:
    data = graphql(
        """
        query($id: ID!) {
          node(id: $id) {
            ... on ProjectV2Item {
              content { ... on DraftIssue { id } }
            }
          }
        }
        """,
        {"id": project_item_id},
    )
    content = data.get("node", {}).get("content") or {}
    return content.get("id")


def update_draft_body(project_item_id: str, body: str) -> None:
    draft_id = get_draft_issue_id(project_item_id)
    if not draft_id:
        raise RuntimeError(f"DraftIssue id not found for item {project_item_id}")
    graphql(
        """
        mutation($id: ID!, $body: String!) {
          updateProjectV2DraftIssue(input: { draftIssueId: $id, body: $body }) {
            draftIssue { id }
          }
        }
        """,
        {"id": draft_id, "body": body},
    )


def set_field(item_id: str, field_id: str, value: dict) -> None:
    for attempt in range(5):
        try:
            graphql(
                """
                mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
                  updateProjectV2ItemFieldValue(input: {
                    projectId: $projectId, itemId: $itemId, fieldId: $fieldId, value: $value
                  }) { projectV2Item { id } }
                }
                """,
                {"projectId": PROJECT_ID, "itemId": item_id, "fieldId": field_id, "value": value},
            )
            return
        except RuntimeError as e:
            if "rate limit" in str(e).lower() and attempt < 4:
                time.sleep(30 * (attempt + 1))
                continue
            raise


def option_id(field: dict, name: str) -> str:
    for opt in field.get("options", []):
        if opt["name"] == name:
            return opt["id"]
    raise KeyError(f"option {name} not in {field.get('name')}")


def apply_fields(item_id: str, fields: dict[str, dict], it: dict) -> None:
    f = it["fields"]
    set_field(item_id, fields["Trilha"]["id"], {"singleSelectOptionId": option_id(fields["Trilha"], f["Trilha"])})
    set_field(item_id, fields["OKR"]["id"], {"text": str(f["OKR"])})
    set_field(item_id, fields["Epic"]["id"], {"text": str(f["Epic"])})
    set_field(item_id, fields["Sprint"]["id"], {"number": float(f["Sprint"])})
    set_field(item_id, fields["Story Points"]["id"], {"number": float(f["Story Points"])})
    set_field(item_id, fields["RICE Score"]["id"], {"number": float(f["RICE Score"])})
    set_field(item_id, fields["WSJF"]["id"], {"number": float(f["WSJF"])})
    set_field(item_id, fields["Reach"]["id"], {"number": float(f["Reach"])})
    set_field(item_id, fields["Impact"]["id"], {"number": float(f["Impact"])})
    set_field(item_id, fields["Confidence"]["id"], {"number": float(f["Confidence"])})
    set_field(item_id, fields["CoD"]["id"], {"number": float(f["CoD"])})
    set_field(item_id, fields["PERT (d)"]["id"], {"number": float(f["PERT (d)"])})
    set_field(item_id, fields["Baseline"]["id"], {"singleSelectOptionId": option_id(fields["Baseline"], f["Baseline"])})
    set_field(item_id, fields["Release Blocker"]["id"], {"singleSelectOptionId": option_id(fields["Release Blocker"], f["Release Blocker"])})
    set_field(item_id, fields["Priority Rank"]["id"], {"number": float(f["Priority Rank"])})
    set_field(item_id, fields["Repo alvo"]["id"], {"text": it["repository"]})
    refin = f.get("Refinamento") or (it.get("refinement") or {}).get("context_summary", "")
    if refin and "Refinamento" in fields:
        set_field(item_id, fields["Refinamento"]["id"], {"text": str(refin)[:1000]})


def main() -> int:
    dry = "--dry-run" in sys.argv
    drafts_only = "--drafts-only" in sys.argv
    fields_only = "--fields-only" in sys.argv
    update_bodies = "--update-bodies" in sys.argv
    board = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    items = board["items"]

    print(f"Project #{PROJECT_NUMBER} — {len(items)} tasks")
    if dry:
        sample = build_issue_body(items[0])
        print(f"Sample body ({items[0]['id']}):\n{sample[:600]}...")
        return 0

    fields = {}
    if not drafts_only or update_bodies:
        print("Ensuring fields...")
        fields = ensure_fields_graphql()

    existing_items = list_items_graphql()
    existing_titles = {i.get("title") for i in existing_items}
    title_to_id = {i.get("title"): i["id"] for i in existing_items if i.get("title")}
    synced_titles = {i.get("title") for i in existing_items if i.get("title") and item_has_fields_synced(i)}
    print(f"Existing: {len(existing_titles)} | fields synced: {len(synced_titles)}")

    created = updated = bodies_updated = 0

    for it in items:
        title = f"[{it['id']}] {it['title']}"
        body = build_issue_body(it)

        if title in existing_titles:
            item_id = title_to_id.get(title)
            if update_bodies and item_id:
                update_draft_body(item_id, body)
                bodies_updated += 1
                time.sleep(0.8)
            if item_id and fields and (fields_only or (not drafts_only and not update_bodies)):
                if title not in synced_titles:
                    apply_fields(item_id, fields, it)
                    updated += 1
                    time.sleep(1.0)
            continue

        if fields_only or update_bodies:
            continue

        item_id = create_draft(title, body)
        if fields and not drafts_only:
            apply_fields(item_id, fields, it)
        created += 1
        existing_titles.add(title)
        title_to_id[title] = item_id

        if (created + updated + bodies_updated) % 10 == 0:
            print(f"  progress created={created} fields={updated} bodies={bodies_updated}")
            time.sleep(2)
        else:
            time.sleep(0.6 if drafts_only else 1.0)

    print(f"Done: created={created} fields_synced={updated} bodies_updated={bodies_updated}")

    # Regenera dashboard local
    dash_script = SCRIPTS / "generate_backlog_dashboard.py"
    if dash_script.exists():
        subprocess.run([sys.executable, str(dash_script)], check=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
