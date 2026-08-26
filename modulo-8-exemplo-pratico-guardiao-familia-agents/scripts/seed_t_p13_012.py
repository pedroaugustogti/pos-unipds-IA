#!/usr/bin/env python3
"""Cria T-P13-012 (LangGraph live + acting agents) e remove T-P13-011 do Project."""

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

TASK_ID = "T-P13-012"
TITLE = "Atualizar hero home: Tranquilidade para sua família"
REPO = "guardiao-familia-site"
PREV = (("77", "T-P13-011"),)


def main() -> int:
    for num, tid in PREV:
        r = _gh_run(
            "issue",
            "close",
            num,
            "--repo",
            f"{ORG}/{REPO}",
            "--reason",
            "not planned",
            "--comment",
            f"Substituido por {TASK_ID} (LangGraph live com acting_agent por evento).",
        )
        print("close", tid, r.returncode == 0)

    cache_path = ROOT / "crew" / "output" / "project_item_cache.json"
    data = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    old = data.get("T-P13-011") or {}
    if old.get("item_id"):
        r = _gh_run(
            "project",
            "item-delete",
            str(PROJECT_NUMBER),
            "--owner",
            ORG,
            "--id",
            old["item_id"],
        )
        print("del item 011", r.returncode == 0)

    body = f"""## Objetivo
Atualizar o hero da home:
- De: **Tranquilidade para quem mais importa**
- Para: **Tranquilidade para sua família**

## Orquestração
`python scripts/langgraph_run.py --task {TASK_ID} --mode live --from-zero --role frontend-web`

Validar agentes por evento:
- claim/open_pr → `frontend-web`
- start_review/approve_review → `frontend-web-reviewer`
- start_test/test_passed → `qa-gate`
- merge_pr → `devops-cicd` (HITL)

## Aceite
1. H1 + title versionados
2. Playwright na issue
3. Comentários com modelo+tokens e **agente correto por etapa**
4. Parar em **In Pull Request** (HITL)
"""
    r = _gh_run(
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
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "")[:500])
    url = (r.stdout or "").strip().splitlines()[-1].strip()
    num = url.rstrip("/").split("/")[-1]
    print("issue", url)

    r = _gh_run(
        "project",
        "item-add",
        str(PROJECT_NUMBER),
        "--owner",
        ORG,
        "--url",
        url,
        "--format",
        "json",
    )
    item = json.loads(r.stdout or "{}")
    item_id = item.get("id")
    if not item_id:
        raise RuntimeError(f"item-add failed: {item}")
    print("item", item_id)

    field = _get_status_field(False)
    opt = next(o["id"] for o in field["options"] if o["name"] == "Todo")
    _gh_run(
        "project",
        "item-edit",
        "--id",
        item_id,
        "--project-id",
        PROJECT_ID,
        "--field-id",
        field["id"],
        "--single-select-option-id",
        opt,
    )

    board = json.loads(BOARD_JSON.read_text(encoding="utf-8"))
    board["items"] = [
        i
        for i in (board.get("items") or [])
        if i.get("id") not in ("T-P13-008", "T-P13-009", "T-P13-010", "T-P13-011")
    ]
    board["items"].append(
        {
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
                "Refinamento": "Hero via LangGraph. Acting agents por evento. Playwright. HITL.",
                "Project Item Id": item_id,
            },
            "labels": ["produto", "O3", "E-P13", "agent:frontend-web"],
            "commit_evidence": "",
            "refinement": {
                "context_summary": "Trocar hero mais importa por sua familia.",
                "suggested_files": ["index.html"],
                "acceptance_hints": [
                    "H1 = Tranquilidade para sua familia",
                    "screenshot Playwright",
                    "agentes corretos por evento",
                ],
            },
        }
    )
    BOARD_JSON.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for k in ("T-P13-010", "T-P13-011"):
        data.pop(k, None)
    data[TASK_ID] = {"item_id": item_id, "issue": num, "title": f"[{TASK_ID}] {TITLE}"}
    cache_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    csv_path = ROOT / "TASK_AGENT_MAP.csv"
    text = csv_path.read_text(encoding="utf-8")
    lines = [
        ln
        for ln in text.splitlines(True)
        if not ln.startswith(("T-P13-008,", "T-P13-009,", "T-P13-010,", "T-P13-011,"))
    ]
    if TASK_ID not in "".join(lines):
        lines.append(
            f"{TASK_ID},{TITLE},frontend-web,,produto,{REPO},E-P13,12,0,1,3.0,1.5,todo,False,"
            f'"track=produto,repo={REPO},epic=E-P13",\n'
        )
    csv_path.write_text("".join(lines), encoding="utf-8")

    meta = {"task_id": TASK_ID, "issue_url": url, "issue": num, "item_id": item_id}
    out = ROOT / "crew" / "output" / "langgraph" / f"{TASK_ID}_seed.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
