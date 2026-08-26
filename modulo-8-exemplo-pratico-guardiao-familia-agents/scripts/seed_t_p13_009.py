#!/usr/bin/env python3
"""Seed T-P13-009 no board local + Project #2 (Todo)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.env_load import ensure_env  # noqa: E402

ensure_env()

from lib.board_client import ORG, PROJECT_ID, PROJECT_NUMBER, _get_status_field, _gh_run  # noqa: E402
from lib.paths import BOARD_JSON  # noqa: E402

TASK_ID = "T-P13-009"
TITLE = "Atualizar hero home: Tranquilidade para sua família"
ISSUE_URL = "https://github.com/guardiaofamilia/guardiao-familia-site/issues/75"
REPO = "guardiao-familia-site"


def add_to_project() -> str:
    """Adiciona issue ao Project e retorna item id."""
    proc = _gh_run(
        "project",
        "item-add",
        str(PROJECT_NUMBER),
        "--owner",
        ORG,
        "--url",
        ISSUE_URL,
        "--format",
        "json",
    )
    if proc.returncode != 0:
        raise RuntimeError(f"item-add failed: {(proc.stderr or proc.stdout or '')[:400]}")
    data = json.loads(proc.stdout or "{}")
    item_id = data.get("id") or data.get("item_id")
    if not item_id:
        raise RuntimeError(f"item-add sem id: {data}")
    return str(item_id)


def set_todo(item_id: str) -> None:
    field = _get_status_field(False)
    option_id = next(o["id"] for o in field["options"] if o["name"] == "Todo")
    edit = _gh_run(
        "project",
        "item-edit",
        "--id",
        item_id,
        "--project-id",
        PROJECT_ID,
        "--field-id",
        field["id"],
        "--single-select-option-id",
        option_id,
    )
    if edit.returncode != 0:
        raise RuntimeError(f"item-edit Todo failed: {(edit.stderr or edit.stdout or '')[:300]}")


def seed_board(item_id: str) -> None:
    board = json.loads(BOARD_JSON.read_text(encoding="utf-8"))
    items = board.setdefault("items", [])
    # remove T-P13-008 se ainda existir
    board["items"] = [i for i in items if i.get("id") not in ("T-P13-008",)]
    items = board["items"]
    existing = next((i for i in items if i.get("id") == TASK_ID), None)
    payload = {
        "id": TASK_ID,
        "title": TITLE,
        "repository": REPO,
        "type": "Issue",
        "fields": {
            "Status": "Todo",
            "Trilha": "produto",
            "OKR": "O3",
            "Epic": "E-P13 Site institucional e campanha",
            "Sprint": 12,
            "Story Points": 1,
            "RICE Score": 3.0,
            "WSJF": 1.5,
            "Reach": 5,
            "Impact": 2,
            "Confidence": 0.9,
            "CoD": 2,
            "PERT (d)": 0.3,
            "Baseline": "todo",
            "Release Blocker": "no",
            "Blocker Motivo": "",
            "Priority Rank": 0,
            "Repo alvo": REPO,
            "Refinamento": "Hero H1 + title: Tranquilidade para sua familia. Aceite Playwright.",
            "Project Item Id": item_id,
        },
        "labels": ["produto", "O3", "E-P13", "agent:frontend-web"],
        "commit_evidence": "",
        "refinement": {
            "context_summary": "Trocar hero mais importa por sua familia.",
            "suggested_files": ["index.html"],
            "acceptance_hints": [
                "H1 = Tranquilidade para sua familia",
                "title atualizado",
                "screenshot Playwright",
            ],
        },
    }
    if existing:
        existing.update(payload)
        existing["fields"] = payload["fields"]
    else:
        items.append(payload)
    BOARD_JSON.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("board seeded", TASK_ID)


def seed_csv() -> None:
    csv_path = ROOT / "TASK_AGENT_MAP.csv"
    line = (
        f"{TASK_ID},{TITLE},frontend-web,,produto,{REPO},E-P13,12,0,1,3.0,1.5,todo,False,"
        f'"track=produto,repo={REPO},epic=E-P13",\n'
    )
    text = csv_path.read_text(encoding="utf-8")
    # remove linha antiga T-P13-008
    lines = [ln for ln in text.splitlines(True) if not ln.startswith("T-P13-008,")]
    text = "".join(lines)
    if TASK_ID in text:
        print("csv already has", TASK_ID)
        csv_path.write_text(text, encoding="utf-8")
        return
    csv_path.write_text(text.rstrip("\n") + "\n" + line, encoding="utf-8")
    print("csv appended")


def cache_item(item_id: str) -> None:
    cache_path = ROOT / "crew" / "output" / "project_item_cache.json"
    data = {}
    if cache_path.exists():
        data = json.loads(cache_path.read_text(encoding="utf-8"))
    data[TASK_ID] = {
        "item_id": item_id,
        "issue": "75",
        "title": f"[{TASK_ID}] {TITLE}",
    }
    data.pop("T-P13-008", None)
    cache_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("cache ok")


def main() -> int:
    item_id = add_to_project()
    print("project item", item_id)
    set_todo(item_id)
    seed_board(item_id)
    try:
        seed_csv()
    except PermissionError:
        print("csv locked — skip")
    cache_item(item_id)
    print("issue", ISSUE_URL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
