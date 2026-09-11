"""Carrega tasks do GitHub Project (gh) com fallback no board JSON (GUARDAO_BOARD_JSON)."""

from __future__ import annotations

import json
import re
from typing import Any

from board_automation.board.board_client import ORG, PROJECT_NUMBER, _gh_json
from board_automation.board.local_board import board_json_path, load_board
from board_automation.board.reviewer_pairs import CREATOR_ROLES, normalize_creator_role
from board_automation.board.task_status_workflow import resolve_status
from lib.core.agent_registry import classify_task

TASK_ID_RE = re.compile(r"^\[([A-Z]-[A-Z0-9]+-\d+)\]")

_WORKFLOW_LABEL_ROLES = frozenset(
    {
        "todo",
        "in-progress",
        "in-test",
        "in-code-review",
        "ready-for-test",
        "ready-for-code-review",
        "in-pull-request",
        "done",
    }
)


def _fields(item: dict[str, Any]) -> dict[str, Any]:
    raw = item.get("fields")
    return raw if isinstance(raw, dict) else {}


def _creator_from_labels(labels: list[Any]) -> str:
    for raw in labels:
        lb = str(raw).strip()
        if not lb.startswith("agent:"):
            continue
        role = lb[6:].strip()
        if not role or role in _WORKFLOW_LABEL_ROLES or role.endswith("-reviewer"):
            continue
        if role in CREATOR_ROLES or role == "qa":
            return normalize_creator_role(role)
    return ""


def _parse_task_id(title: str) -> str:
    m = TASK_ID_RE.match(str(title or "").strip())
    return m.group(1) if m else ""


def _repo_slug(raw: str) -> str:
    s = str(raw or "").strip()
    if not s:
        return ""
    if "/" in s:
        return s.split("/", 1)[-1].strip()
    if s.startswith("https://github.com/"):
        parts = s.rstrip("/").split("/")
        return parts[-1] if len(parts) >= 2 else s
    return s


def _resolve_board_status(status_raw: str) -> str:
    try:
        return resolve_status(str(status_raw or "Todo"))
    except ValueError:
        return "Todo"


def board_item_to_task(item: dict[str, Any], *, board_source: str | None = None) -> dict[str, Any]:
    """Normaliza item do github-project-*-import.json para dict usado pelo LangGraph."""
    fields = _fields(item)
    labels = list(item.get("labels") or [])
    repo = str(fields.get("Repo alvo") or item.get("repository") or "").strip()
    repo = _repo_slug(repo)
    track = str(fields.get("Trilha") or "produto").strip()
    epic = str(fields.get("Epic") or "").strip()
    board_status = _resolve_board_status(str(fields.get("Status") or item.get("status") or "Todo"))

    content = item.get("content") if isinstance(item.get("content"), dict) else {}
    issue_url = str(item.get("issue_url") or content.get("url") or "").strip()
    issue_number = str(item.get("issue_number") or content.get("number") or "").strip()
    title = str(item.get("title") or content.get("title") or item.get("id") or "")

    row: dict[str, Any] = {
        "id": str(item.get("id") or _parse_task_id(title) or ""),
        "title": title,
        "repo": repo,
        "repository": repo,
        "board_status": board_status,
        "track": track,
        "epic_id": epic,
        "sprint": str(fields.get("Sprint") or "1"),
        "priority_rank": str(fields.get("Priority Rank") or "99"),
        "story_points": str(fields.get("Story Points") or ""),
        "issue_number": issue_number,
        "issue_url": issue_url,
        "labels": labels,
        "qa": item.get("qa") if isinstance(item.get("qa"), dict) else {},
        "refinement": item.get("refinement") if isinstance(item.get("refinement"), dict) else {},
        "project_item_id": str(item.get("project_item_id") or item.get("item_id") or ""),
        "board_source": board_source or str(board_json_path()),
    }

    agent_role = _creator_from_labels(labels)
    classified, secondary, reason = classify_task(row)
    if not agent_role:
        agent_role = normalize_creator_role(classified)
    row["agent_role"] = agent_role
    row["agent_role_secondary"] = normalize_creator_role(secondary) if secondary else ""
    row["match_reason"] = reason
    return row


def _github_project_item_to_task(item: dict[str, Any]) -> dict[str, Any]:
    """Converte item de `gh project item-list` para dict do LangGraph."""
    title = str(item.get("title") or "")
    task_id = _parse_task_id(title)
    content = item.get("content") if isinstance(item.get("content"), dict) else {}
    labels = list(item.get("labels") or [])
    repo = _repo_slug(
        content.get("repository")
        or item.get("repository")
        or ""
    )
    issue_url = str(content.get("url") or "").strip()
    issue_number = str(content.get("number") or "").strip()

    normalized: dict[str, Any] = {
        "id": task_id,
        "title": title,
        "repository": repo,
        "labels": labels,
        "status": item.get("status") or "Todo",
        "issue_url": issue_url,
        "issue_number": issue_number,
        "project_item_id": str(item.get("id") or ""),
        "item_id": str(item.get("id") or ""),
    }
    return board_item_to_task(
        normalized,
        board_source=f"github:project#{PROJECT_NUMBER}",
    )


def _list_github_project_items(*, query: str = "") -> list[dict[str, Any]]:
    args = [
        "project",
        "item-list",
        str(PROJECT_NUMBER),
        "--owner",
        ORG,
        "--limit",
        "500",
        "--format",
        "json",
    ]
    if query:
        args.extend(["--query", query])
    payload = _gh_json(*args)
    if isinstance(payload, dict):
        return list(payload.get("items") or [])
    if isinstance(payload, list):
        return payload
    return []


def _load_issue_cache_entry(task_id: str) -> dict[str, Any]:
    """Cache canônico task_id → issue/project_item (project3_item_cache.json)."""
    try:
        from lib.paths import BOARD_IMPORTS_DIR, PROJECT3_ITEM_CACHE_PATH

        if PROJECT3_ITEM_CACHE_PATH.is_file():
            cache = json.loads(PROJECT3_ITEM_CACHE_PATH.read_text(encoding="utf-8"))
            entry = cache.get(task_id)
            if isinstance(entry, dict):
                return entry

        board_path = BOARD_IMPORTS_DIR / "github-project-3-import.json"
        if board_path.is_file():
            board = json.loads(board_path.read_text(encoding="utf-8"))
            for item in board.get("items") or []:
                if str(item.get("id") or "") == task_id:
                    return {
                        "task_id": task_id,
                        "issue_number": str(item.get("issue_number") or ""),
                        "issue_url": str(item.get("issue_url") or ""),
                        "project_item_id": str(
                            item.get("project_item_id") or item.get("fields", {}).get("Project Item Id") or ""
                        ),
                    }
    except Exception:  # noqa: BLE001
        pass
    return {}


def _collect_github_project_items(task_id: str) -> list[dict[str, Any]]:
    tid = str(task_id or "").strip()
    if not tid:
        return []
    seen: set[str] = set()
    matches: list[dict[str, Any]] = []
    for item in _list_github_project_items(query=tid):
        if _parse_task_id(str(item.get("title") or "")) != tid:
            continue
        item_id = str(item.get("id") or "")
        if item_id and item_id in seen:
            continue
        if item_id:
            seen.add(item_id)
        matches.append(item)
    if matches:
        return matches
    for item in _list_github_project_items():
        if _parse_task_id(str(item.get("title") or "")) != tid:
            continue
        item_id = str(item.get("id") or "")
        if item_id and item_id in seen:
            continue
        if item_id:
            seen.add(item_id)
        matches.append(item)
    return matches


def _pick_project_item(task_id: str, items: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not items:
        return None
    if len(items) == 1:
        return items[0]

    cache = _load_issue_cache_entry(task_id)
    cache_item_id = str(cache.get("project_item_id") or "").strip()
    cache_issue = str(cache.get("issue_number") or "").strip()

    if cache_item_id:
        for item in items:
            if str(item.get("id") or "") == cache_item_id:
                return item

    if cache_issue:
        for item in items:
            content = item.get("content") if isinstance(item.get("content"), dict) else {}
            if str(content.get("number") or "") == cache_issue:
                return item

    # fallback: maior issue_number (issue mais recente)
    def _issue_num(item: dict[str, Any]) -> int:
        content = item.get("content") if isinstance(item.get("content"), dict) else {}
        try:
            return int(content.get("number") or 0)
        except (TypeError, ValueError):
            return 0

    return max(items, key=_issue_num)


def fetch_github_project_task(task_id: str) -> dict[str, Any] | None:
    """Lê task ao vivo do GitHub Project configurado em .env (ORG + PROJECT_NUMBER)."""
    tid = str(task_id or "").strip()
    if not tid:
        return None

    items = _collect_github_project_items(tid)
    picked = _pick_project_item(tid, items)
    if picked:
        return _github_project_item_to_task(picked)
    return None


def get_board_task_from_json(task_id: str, *, path=None) -> dict[str, Any] | None:
    tid = str(task_id or "").strip()
    if not tid:
        return None
    board = load_board(path)
    for item in board.get("items") or []:
        if str(item.get("id") or "") == tid:
            return board_item_to_task(item, board_source=str(board_json_path()))
    return None


def get_board_task(task_id: str, *, path=None) -> dict[str, Any] | None:
    """
    Fonte primária: GitHub Project via `gh`.
    Fallback: board JSON local (GUARDAO_BOARD_JSON) quando gh indisponível.
    """
    tid = str(task_id or "").strip()
    if not tid:
        return None

    try:
        live = fetch_github_project_task(tid)
        if live:
            return live
    except Exception:  # noqa: BLE001
        pass

    return get_board_task_from_json(tid, path=path)


def load_tasks_from_board(*, path=None) -> list[dict[str, Any]]:
    try:
        items = _list_github_project_items()
        rows = [_github_project_item_to_task(it) for it in items if _parse_task_id(str(it.get("title") or ""))]
        if rows:
            return rows
    except Exception:  # noqa: BLE001
        pass

    board = load_board(path)
    return [board_item_to_task(item) for item in (board.get("items") or []) if item.get("id")]
