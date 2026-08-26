#!/usr/bin/env python3
"""Seed T-P13-010 no board local + Project #2 (Todo)."""

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

TASK_ID = "T-P13-010"
TITLE = "Atualizar hero home: Tranquilidade para sua família"
REPO = "guardiao-familia-site"
# preenchido apos create
ISSUE_URL = ""
ISSUE_NUMBER = ""


def create_issue() -> tuple[str, str]:
    body = """## Objetivo
Atualizar o hero da home do site institucional:
- De: **Tranquilidade para quem mais importa**
- Para: **Tranquilidade para sua família**

## Escopo
- Arquivo: `index.html` (H1 + `<title>`)
- Agente: `frontend-web`
- Repo: `guardiao-familia-site`

## Aceite
1. Texto do H1 e title atualizados
2. Evidência visual (Playwright) nos comentários
3. Pipeline Kanban até **In Pull Request** com comentários thought/action/observation + **modelo LLM + tokens** (`select_model`)
4. **Sem merge** — HITL humano pré-merge

## Notas
Ticket novo (substitui T-P13-009) para exercicio com LLM real via select_model.
"""
    proc = _gh_run(
        "issue",
        "create",
        "--repo",
        f"{ORG}/{REPO}",
        "--title",
        f"[{TASK_ID}] {TITLE}",
        "--body",
        body,
        "--label",
        "produto",
        "--label",
        "O3",
        "--label",
        "E-P13",
    )
    if proc.returncode != 0:
        raise RuntimeError(f"issue create failed: {(proc.stderr or proc.stdout or '')[:500]}")
    url = (proc.stdout or "").strip().splitlines()[-1].strip()
    num = url.rstrip("/").split("/")[-1]
    return url, num


def add_to_project(issue_url: str) -> str:
    proc = _gh_run(
        "project",
        "item-add",
        str(PROJECT_NUMBER),
        "--owner",
        ORG,
        "--url",
        issue_url,
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


def remove_old_items() -> None:
    cache_path = ROOT / "crew" / "output" / "project_item_cache.json"
    if not cache_path.exists():
        return
    data = json.loads(cache_path.read_text(encoding="utf-8"))
    for old_id in ("T-P13-008", "T-P13-009"):
        meta = data.get(old_id) or {}
        item = meta.get("item_id")
        if not item:
            continue
        r = _gh_run(
            "project",
            "item-delete",
            str(PROJECT_NUMBER),
            "--owner",
            ORG,
            "--id",
            item,
        )
        print(f"remove {old_id}", r.returncode == 0)
        data.pop(old_id, None)
    cache_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def seed_board(item_id: str) -> None:
    board = json.loads(BOARD_JSON.read_text(encoding="utf-8"))
    items = [i for i in (board.get("items") or []) if i.get("id") not in ("T-P13-008", "T-P13-009")]
    board["items"] = items
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
            "Refinamento": "Hero H1 + title: Tranquilidade para sua familia. Aceite Playwright + LLM comments.",
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
                "comentarios com modelo+tokens via select_model",
            ],
        },
    }
    existing = next((i for i in items if i.get("id") == TASK_ID), None)
    if existing:
        existing.clear()
        existing.update(payload)
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
    lines = [
        ln
        for ln in text.splitlines(True)
        if not ln.startswith("T-P13-008,") and not ln.startswith("T-P13-009,")
    ]
    text = "".join(lines)
    if TASK_ID in text:
        csv_path.write_text(text, encoding="utf-8")
        print("csv already has", TASK_ID)
        return
    csv_path.write_text(text.rstrip("\n") + "\n" + line, encoding="utf-8")
    print("csv appended")


def cache_item(item_id: str, issue_number: str) -> None:
    cache_path = ROOT / "crew" / "output" / "project_item_cache.json"
    data = {}
    if cache_path.exists():
        data = json.loads(cache_path.read_text(encoding="utf-8"))
    data[TASK_ID] = {
        "item_id": item_id,
        "issue": issue_number,
        "title": f"[{TASK_ID}] {TITLE}",
    }
    data.pop("T-P13-008", None)
    data.pop("T-P13-009", None)
    cache_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("cache ok")


def close_old_issues() -> None:
    for num, tid in (("74", "T-P13-008"), ("75", "T-P13-009")):
        r = _gh_run(
            "issue",
            "close",
            num,
            "--repo",
            f"{ORG}/{REPO}",
            "--reason",
            "not planned",
            "--comment",
            f"Substituido por {TASK_ID} (rerun com select_model + LLM).",
        )
        print(f"close {tid}#{num}", r.returncode == 0)


def main() -> int:
    close_old_issues()
    remove_old_items()
    url, num = create_issue()
    print("issue", url)
    item_id = add_to_project(url)
    print("project item", item_id)
    set_todo(item_id)
    seed_board(item_id)
    try:
        seed_csv()
    except PermissionError:
        print("csv locked — skip")
    cache_item(item_id, num)
    meta = {"task_id": TASK_ID, "issue_url": url, "issue": num, "item_id": item_id}
    (ROOT / "crew" / "output" / "langgraph" / f"{TASK_ID}_seed.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(meta, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
