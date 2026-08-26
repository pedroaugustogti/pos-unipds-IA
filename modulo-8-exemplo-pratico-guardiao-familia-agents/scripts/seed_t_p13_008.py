#!/usr/bin/env python3
"""Seed T-P13-008 no board local + Status Todo no Project."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.env_load import ensure_env  # noqa: E402
from lib.board_client import PROJECT_ID, _get_status_field, _gh_run  # noqa: E402
from lib.paths import BOARD_JSON  # noqa: E402

ensure_env()

TASK_ID = "T-P13-008"
ITEM_ID = "PVTI_lADOEDZbAM4Bg2rEzg4Bunw"
TITLE = "Atualizar hero home: Tranquilidade para sua família"


def seed_board() -> None:
    board = json.loads(BOARD_JSON.read_text(encoding="utf-8"))
    if any(i.get("id") == TASK_ID for i in board.get("items") or []):
        for i in board["items"]:
            if i.get("id") == TASK_ID:
                i["fields"]["Status"] = "Todo"
                i["fields"]["Project Item Id"] = ITEM_ID
        BOARD_JSON.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("board updated")
        return
    board.setdefault("items", []).append(
        {
            "id": TASK_ID,
            "title": TITLE,
            "repository": "guardiao-familia-site",
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
                "Repo alvo": "guardiao-familia-site",
                "Refinamento": "Hero H1 + title: Tranquilidade para sua familia. Aceite Playwright.",
                "Project Item Id": ITEM_ID,
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
    )
    BOARD_JSON.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("board item added")


def seed_csv() -> None:
    csv_path = ROOT / "TASK_AGENT_MAP.csv"
    line = (
        "T-P13-008,Atualizar hero home: Tranquilidade para sua família,"
        "frontend-web,,produto,guardiao-familia-site,E-P13,12,0,1,3.0,1.5,todo,False,"
        '"track=produto,repo=guardiao-familia-site,epic=E-P13",\n'
    )
    text = csv_path.read_text(encoding="utf-8")
    if "T-P13-008" in text:
        print("csv already has T-P13-008")
        return
    csv_path.write_text(text.rstrip("\n") + "\n" + line, encoding="utf-8")
    print("csv appended")


def set_project_todo() -> None:
    field = _get_status_field(False)
    option_id = next(o["id"] for o in field["options"] if o["name"] == "Todo")
    edit = _gh_run(
        "project",
        "item-edit",
        "--id",
        ITEM_ID,
        "--project-id",
        PROJECT_ID,
        "--field-id",
        field["id"],
        "--single-select-option-id",
        option_id,
    )
    print("project Todo", edit.returncode == 0, (edit.stderr or edit.stdout or "")[:200])


if __name__ == "__main__":
    seed_board()
    try:
        seed_csv()
    except PermissionError:
        print("csv locked — skip (board JSON ok)")
    set_project_todo()
