"""Board local: Status em 08-board/github-project-2-import.json."""

from __future__ import annotations

import json
import tempfile
from datetime import date
from pathlib import Path

def board_json_path() -> Path:
    from lib.paths import BOARD_JSON

    return BOARD_JSON


def _default_board_path() -> Path:
    return board_json_path()


def load_board(path: Path | None = None) -> dict:
    p = path or _default_board_path()
    if not p.exists():
        raise FileNotFoundError(f"Board JSON nao encontrado: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def save_board(data: dict, path: Path | None = None) -> Path:
    p = path or _default_board_path()
    data = dict(data)
    data["generated"] = date.today().isoformat()
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    p.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=p.parent,
        delete=False,
        suffix=".tmp",
    ) as tmp:
        tmp.write(text)
        tmp_path = Path(tmp.name)
    tmp_path.replace(p)
    return p


def status_map(path: Path | None = None) -> dict[str, str]:
    """task_id -> Status canônico do board local."""
    board = load_board(path)
    out: dict[str, str] = {}
    for item in board.get("items", []):
        tid = item.get("id")
        if not tid:
            continue
        fields = item.get("fields") or {}
        out[tid] = str(fields.get("Status") or "Todo")
    return out


def get_local_status(task_id: str, path: Path | None = None) -> str | None:
    board = load_board(path)
    for item in board.get("items", []):
        if item.get("id") == task_id:
            return str((item.get("fields") or {}).get("Status") or "Todo")
    return None


def update_local_status(task_id: str, status: str, path: Path | None = None) -> dict:
    """Atualiza fields.Status do item no JSON local. Retorna resultado."""
    board = load_board(path)
    found = None
    for item in board.get("items", []):
        if item.get("id") == task_id:
            fields = item.setdefault("fields", {})
            prev = fields.get("Status")
            fields["Status"] = status
            found = {"id": task_id, "from": prev, "to": status, "title": item.get("title")}
            break
    if not found:
        return {"ok": False, "error": f"Task {task_id} nao encontrada no board JSON"}
    saved = save_board(board, path)
    return {"ok": True, "task_id": task_id, "status": status, "path": str(saved), **found}


def mark_local_blocker(
    task_id: str,
    reason: str,
    *,
    path: Path | None = None,
) -> dict:
    """Marca Release Blocker=yes e Motivo Blocker no JSON local."""
    board = load_board(path)
    found = None
    for item in board.get("items", []):
        if item.get("id") == task_id:
            fields = item.setdefault("fields", {})
            fields["Release Blocker"] = "yes"
            fields["Blocker Motivo"] = reason[:2000]
            found = {
                "id": task_id,
                "title": item.get("title"),
                "reason": fields["Blocker Motivo"],
            }
            break
    if not found:
        return {"ok": False, "error": f"Task {task_id} nao encontrada no board JSON"}
    saved = save_board(board, path)
    return {"ok": True, "path": str(saved), **found}
