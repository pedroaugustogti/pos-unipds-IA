#!/usr/bin/env python3
"""Sincroniza opções do campo Status no GitHub Project #2 com o workflow v2."""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS.parent / "10-agents" / "lib"))
sys.path.insert(0, str(SCRIPTS))

from task_status_workflow import STATUSES  # noqa: E402

ORG = "guardiaofamilia"
PROJECT_NUMBER = 2
PROJECT_ID = "PVT_kwDOEDZbAM4Bg2rE"


def token() -> str:
    t = (os.environ.get("CURSOR_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN") or "").strip()
    if not t:
        raise SystemExit("Defina CURSOR_GITHUB_TOKEN")
    return t


def graphql(query: str, variables: dict | None = None) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={
            "Authorization": f"Bearer {token()}",
            "Content-Type": "application/json",
            "User-Agent": "gf-sync-status",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode())
    if data.get("errors"):
        raise SystemExit("; ".join(e["message"] for e in data["errors"]))
    return data["data"]


def find_status_field() -> dict | None:
    data = graphql(
        """
        query($org: String!, $num: Int!) {
          organization(login: $org) {
            projectV2(number: $num) {
              fields(first: 50) {
                nodes {
                  ... on ProjectV2SingleSelectField {
                    id
                    name
                    options { id name }
                  }
                }
              }
            }
          }
        }
        """,
        {"org": ORG, "num": PROJECT_NUMBER},
    )
    for f in data["organization"]["projectV2"]["fields"]["nodes"]:
        if f.get("name") == "Status":
            return f
    return None


def sync_options(dry_run: bool = False) -> None:
    field = find_status_field()
    if not field:
        raise SystemExit("Campo Status nao encontrado no Project #2")

    existing = {o["name"]: o["id"] for o in field.get("options", [])}
    missing = [s for s in STATUSES if s not in existing]
    print(f"Status field: {field['id']}")
    print(f"Existentes: {len(existing)} | Faltando: {len(missing)}")
    for s in missing:
        print(f"  + {s}")

    if dry_run or not missing:
        return

    # GitHub: adicionar opções preservando existentes
    all_options = []
    colors = ["GRAY", "BLUE", "YELLOW", "ORANGE", "RED", "PINK", "PURPLE", "GREEN"]
    for i, name in enumerate(STATUSES):
        entry: dict = {"name": name, "color": colors[i % len(colors)], "description": name}
        if name in existing:
            entry["id"] = existing[name]
        all_options.append(entry)

    graphql(
        """
        mutation($fieldId: ID!, $options: [ProjectV2SingleSelectFieldOptionInput!]!) {
          updateProjectV2Field(input: { fieldId: $fieldId, singleSelectOptions: $options }) {
            projectV2Field { ... on ProjectV2SingleSelectField { name options { id name } } }
          }
        }
        """,
        {"fieldId": field["id"], "options": all_options},
    )
    print("Opcoes Status sincronizadas.")


def main() -> int:
    dry = "--dry-run" in sys.argv
    sync_options(dry_run=dry)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
