#!/usr/bin/env python3
"""Cria Project #3 (se necessário), issues T-P3-* e board local sandbox agentes."""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
from pathlib import Path

_bs = Path(__file__).resolve().parents[2] / "bootstrap.py"
_spec = importlib.util.spec_from_file_location("ba_bootstrap", _bs)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
_mod.setup()

from board_automation.board.board_client import ORG, _get_status_field, _gh_run  # noqa: E402
from board_automation.board.issue_task_body import build_issue_body  # noqa: E402
from lib.paths import (  # noqa: E402
    BOARD_DIR,
    BOARD_IMPORTS_DIR,
    BOARD_MAPS_DIR,
    PROJECT3_ITEM_CACHE_PATH,
)

BACKLOG_JSON = BOARD_IMPORTS_DIR / "BACKLOG_PROJECT3.json"
EXTRA_JSON = BOARD_IMPORTS_DIR / "PROJECT3_REFINEMENT_EXTRA.json"
BOARD_P3_JSON = BOARD_IMPORTS_DIR / "github-project-3-import.json"
MAP_P3_CSV = BOARD_MAPS_DIR / "TASK_AGENT_MAP_P3.csv"
CACHE_PATH = PROJECT3_ITEM_CACHE_PATH
LOG_PATH = BOARD_DIR / "seed_project3_log.jsonl"


def _deep_merge(base: dict, extra: dict) -> dict:
    out = dict(base)
    for k, v in extra.items():
        if k == "refinement" and isinstance(v, dict):
            ref = dict(out.get("refinement") or {})
            ref.update(v)
            out["refinement"] = ref
        else:
            out[k] = v
    return out


def load_backlog() -> dict:
    backlog = json.loads(BACKLOG_JSON.read_text(encoding="utf-8"))
    extra_all = json.loads(EXTRA_JSON.read_text(encoding="utf-8")) if EXTRA_JSON.is_file() else {}
    tasks = []
    for t in backlog["tasks"]:
        tasks.append(_deep_merge(t, extra_all.get(t["id"], {})))
    backlog["tasks"] = tasks
    return backlog


def resolve_project_id(project_number: int) -> tuple[str, int]:
    r = _gh_run("project", "list", "--owner", ORG, "--format", "json")
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "")[:400])
    data = json.loads(r.stdout or "{}")
    for p in data.get("projects") or []:
        if int(p.get("number") or 0) == project_number:
            return str(p["id"]), int(p["number"])
    raise RuntimeError(f"Project #{project_number} não encontrado em {ORG}")


def create_project(title: str, *, dry_run: bool) -> tuple[str, int]:
    if dry_run:
        return "PVT_dry_project3", 3
    r = _gh_run("project", "create", "--owner", ORG, "--title", title, "--format", "json")
    if r.returncode != 0:
        raise RuntimeError(f"project create: {(r.stderr or r.stdout or '')[:400]}")
    proj = json.loads(r.stdout or "{}")
    return str(proj["id"]), int(proj["number"])


def create_issue(task: dict, body: str, *, dry_run: bool) -> tuple[str, str]:
    tid = task["id"]
    repo = task["repo"]
    title = f"[{tid}] {task['title']}"
    if dry_run:
        return f"https://github.com/{ORG}/{repo}/issues/0", "0"
    labels = [f"agent:{task['agent_role']}"]
    sec = task.get("agent_role_secondary")
    if sec:
        labels.append(f"agent:{sec}")
    args = [
        "issue", "create",
        "--repo", f"{ORG}/{repo}",
        "--title", title,
        "--body", body,
    ]
    for lb in labels:
        args.extend(["--label", lb])
    r = _gh_run(*args)
    if r.returncode != 0:
        raise RuntimeError(f"issue create {tid}: {(r.stderr or r.stdout or '')[:400]}")
    url = (r.stdout or "").strip().splitlines()[-1].strip()
    num = url.rstrip("/").split("/")[-1]
    return url, num


def add_to_project(url: str, project_number: int, *, dry_run: bool) -> str:
    if dry_run:
        return "PVTI_dry_run"
    r = _gh_run(
        "project", "item-add", str(project_number),
        "--owner", ORG, "--url", url, "--format", "json",
    )
    if r.returncode != 0:
        raise RuntimeError(f"item-add: {(r.stderr or r.stdout or '')[:400]}")
    item = json.loads(r.stdout or "{}")
    item_id = item.get("id")
    if not item_id:
        raise RuntimeError(f"item-add sem id: {item}")
    return str(item_id)


def set_project_todo(item_id: str, project_id: str, project_number: int, *, dry_run: bool) -> None:
    if dry_run:
        return
    import board_automation.board.board_client as bc

    old_num = bc.PROJECT_NUMBER
    old_id = bc.PROJECT_ID
    try:
        bc.PROJECT_NUMBER = project_number
        bc.PROJECT_ID = project_id
        field = _get_status_field(False)
    finally:
        bc.PROJECT_NUMBER = old_num
        bc.PROJECT_ID = old_id
    if not field:
        print(f"  warn: Status field não encontrado no project #{project_number}")
        return
    option_id = next((o["id"] for o in field["options"] if o["name"] == "Todo"), None)
    if not option_id:
        print("  warn: opção Todo não encontrada — sync status manualmente")
        return
    edit = _gh_run(
        "project", "item-edit",
        "--id", item_id,
        "--project-id", project_id,
        "--field-id", field["id"],
        "--single-select-option-id", option_id,
    )
    if edit.returncode != 0:
        print(f"  warn set Todo: {(edit.stderr or edit.stdout or '')[:200]}")


def append_log(entry: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def update_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def seed_board_json(backlog: dict, results: list[dict]) -> None:
    items = []
    for task, res in zip(backlog["tasks"], results):
        items.append({
            "id": task["id"],
            "title": task["title"],
            "repository": task["repo"],
            "type": "Issue",
            "issue_number": res.get("issue_number"),
            "issue_url": res.get("issue_url"),
            "fields": {
                "Status": "Todo",
                "Trilha": task["track"],
                "Epic": f"{task['epic_id']} Project 3 Sandbox",
                "Sprint": task.get("sprint", 1),
                "Story Points": task.get("effort_sp", 1),
                "RICE Score": task.get("rice", 5),
                "WSJF": task.get("wsjf", 2),
                "Release Blocker": "no",
                "Priority Rank": task.get("priority_rank", 0),
                "Repo alvo": task["repo"],
                "Project Item Id": res.get("project_item_id", ""),
            },
            "labels": [f"agent:{task['agent_role']}"],
            "refinement": task.get("refinement"),
            "qa": task.get("qa"),
        })
    board = {
        "version": "3.0",
        "organization": ORG,
        "project": {
            "title": backlog.get("project_title"),
            "number": backlog.get("project_number", 3),
            "description": backlog.get("description"),
        },
        "fields": [{"name": "Status", "type": "single_select", "options": [
            "Todo", "In Progress", "Ready for Code Review", "In Code Review",
            "Ready for Test", "In Test", "In Pull Request", "Done",
        ]}],
        "items": items,
    }
    BOARD_P3_JSON.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"board json: {BOARD_P3_JSON}")


def _patch_board_item(backlog: dict, *, task_id: str, entry: dict) -> None:
    """Atualiza só um item no github-project-3-import.json."""
    if not BOARD_P3_JSON.is_file():
        seed_board_json(backlog, [entry] if entry else [])
        return
    board = json.loads(BOARD_P3_JSON.read_text(encoding="utf-8"))
    task = next((t for t in backlog["tasks"] if t["id"] == task_id), None)
    if not task:
        raise ValueError(f"Task {task_id} não encontrada")
    item = {
        "id": task_id,
        "title": task["title"],
        "repository": task["repo"],
        "type": "Issue",
        "issue_number": entry.get("issue_number"),
        "issue_url": entry.get("issue_url"),
        "fields": {
            "Status": "Todo",
            "Trilha": task["track"],
            "Epic": f"{task['epic_id']} Project 3 Sandbox",
            "Sprint": task.get("sprint", 1),
            "Story Points": task.get("effort_sp", 1),
            "RICE Score": task.get("rice", 5),
            "WSJF": task.get("wsjf", 2),
            "Release Blocker": "no",
            "Priority Rank": task.get("priority_rank", 0),
            "Repo alvo": task["repo"],
            "Project Item Id": entry.get("project_item_id", ""),
        },
        "labels": [f"agent:{task['agent_role']}"],
        "refinement": task.get("refinement"),
        "qa": task.get("qa"),
    }
    items = board.get("items") or []
    replaced = False
    for i, row in enumerate(items):
        if row.get("id") == task_id:
            items[i] = item
            replaced = True
            break
    if not replaced:
        items.append(item)
    board["items"] = items
    BOARD_P3_JSON.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"board json patched: {task_id} -> issue #{entry.get('issue_number')}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--create-project", action="store_true", help="Cria Project v3 se não existir")
    parser.add_argument("--project-number", type=int, default=0, help="Default: 3 ou criar novo")
    parser.add_argument("--project-id", default="", help="PVT_... override")
    parser.add_argument("--skip-board-json", action="store_true")
    parser.add_argument("--task", default="", help="Só um task_id (ex: T-P3-009); força recriação se --force")
    parser.add_argument("--force", action="store_true", help="Ignora cache e recria issue/board para --task")
    args = parser.parse_args()

    backlog = load_backlog()
    conventions = backlog.get("comment_conventions") or {}

    project_number = args.project_number or int(backlog.get("project_number") or 3)
    project_id = args.project_id.strip()

    if not project_id:
        try:
            project_id, project_number = resolve_project_id(project_number)
            print(f"Project #{project_number} id={project_id}")
        except RuntimeError:
            if args.create_project or args.project_number == 0:
                title = backlog.get("project_title") or "Guardião Família v3 — Sandbox Agentes"
                project_id, project_number = create_project(title, dry_run=args.dry_run)
                print(f"Created Project #{project_number} id={project_id}")
                backlog["project_number"] = project_number
            else:
                raise

    cache: dict = {}
    if CACHE_PATH.exists():
        cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))

    results: list[dict] = []
    tasks = backlog["tasks"]
    if args.task:
        tasks = [t for t in tasks if t["id"] == args.task]
        if not tasks:
            raise SystemExit(f"Task {args.task} não encontrada no backlog")
        if args.force and args.task in cache:
            cache.pop(args.task, None)

    for task in tasks:
        tid = task["id"]
        if tid in cache and cache[tid].get("issue_url") and cache[tid].get("issue_number") not in (None, "", "0"):
            print(f"skip {tid} (cache)")
            results.append(cache[tid])
            continue

        body = build_issue_body(task, conventions)
        print(f"creating {tid}...")
        url, num = create_issue(task, body, dry_run=args.dry_run)
        item_id = add_to_project(url, project_number, dry_run=args.dry_run)
        set_project_todo(item_id, project_id, project_number, dry_run=args.dry_run)

        entry = {
            "task_id": tid,
            "issue_url": url,
            "issue_number": num,
            "project_item_id": item_id,
            "project_number": project_number,
            "project_id": project_id,
        }
        cache[tid] = entry
        results.append(entry)
        append_log(entry)
        print(f"  {url} item={item_id}")
        time.sleep(1.5)

    update_cache(cache)
    if not args.skip_board_json:
        if args.task:
            _patch_board_item(backlog, task_id=args.task, entry=cache.get(args.task) or {})
        else:
            seed_board_json(backlog, results)

    print(json.dumps({"project_number": project_number, "project_id": project_id, "tasks": len(results)}, indent=2))
    print(f"\nConfigure: GUARDAO_GITHUB_PROJECT_NUMBER={project_number} GUARDAO_GITHUB_PROJECT_ID={project_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
