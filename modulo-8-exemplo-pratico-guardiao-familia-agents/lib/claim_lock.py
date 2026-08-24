"""Lock de claim: WIP por role + Status In Progress (JSON + issue labels quando houver)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lib.local_board import get_local_status, load_board, save_board
from lib.paths import MODULE_ROOT
from lib.task_status_workflow import resolve_status

LOCKS_PATH = MODULE_ROOT / "crew" / "output" / "claim_locks.json"
DEFAULT_WIP_PER_ROLE = int(os.environ.get("GUARDAO_WIP_PER_ROLE", "1"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_locks() -> dict[str, Any]:
    if not LOCKS_PATH.exists():
        return {"version": 1, "by_task": {}, "by_role": {}}
    return json.loads(LOCKS_PATH.read_text(encoding="utf-8"))


def save_locks(data: dict[str, Any]) -> Path:
    LOCKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = _now()
    LOCKS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return LOCKS_PATH


def count_in_progress_for_role(role: str) -> int:
    """Conta locks ativos do role (espelho de WIP; Status In Progress quando sincronizado)."""
    locks = load_locks()
    by_task = locks.get("by_task") or {}
    n = 0
    for task_id, meta in by_task.items():
        if meta.get("role") != role:
            continue
        st = get_local_status(task_id) or "Todo"
        try:
            resolved = resolve_status(st)
        except ValueError:
            resolved = "Todo"
        # Conta se In Progress OU se ha lock ativo (claim recente ainda em Todo)
        if resolved == "In Progress" or meta.get("role") == role:
            n += 1
    return n


def check_claim_allowed(
    task_id: str,
    role: str,
    *,
    wip_per_role: int | None = None,
) -> dict[str, Any]:
    """Valida se claim pode prosseguir (lock + WIP)."""
    wip = DEFAULT_WIP_PER_ROLE if wip_per_role is None else wip_per_role
    locks = load_locks()
    existing = (locks.get("by_task") or {}).get(task_id)
    st = get_local_status(task_id) or "Todo"
    try:
        st = resolve_status(st)
    except ValueError:
        st = "Todo"

    if existing and existing.get("role") and existing.get("role") != role:
        return {
            "ok": False,
            "code": "locked",
            "reason": f"Task {task_id} ja claimada por `{existing.get('role')}`",
            "lock": existing,
        }

    if st == "In Progress" and existing and existing.get("role") == role:
        return {
            "ok": True,
            "code": "already_owned",
            "reason": "Mesmo role ja detem o lock",
            "lock": existing,
        }

    if st not in ("Todo",) and st != "In Progress":
        return {
            "ok": False,
            "code": "bad_status",
            "reason": f"Status atual `{st}` nao permite claim",
        }

    in_prog = count_in_progress_for_role(role)
    # se ja somos donos desta task em IP, nao conta como WIP extra
    if existing and existing.get("role") == role and st == "In Progress":
        pass
    elif in_prog >= wip:
        return {
            "ok": False,
            "code": "wip_exceeded",
            "reason": f"WIP {wip} atingido para role `{role}` (In Progress={in_prog})",
            "wip": in_prog,
        }

    return {"ok": True, "code": "allowed", "wip": in_prog, "wip_limit": wip}


def acquire_lock(task_id: str, role: str, *, actor: str | None = None) -> dict[str, Any]:
    check = check_claim_allowed(task_id, role)
    if not check.get("ok") and check.get("code") != "already_owned":
        return check
    locks = load_locks()
    by_task = locks.setdefault("by_task", {})
    by_role = locks.setdefault("by_role", {})
    meta = {
        "role": role,
        "actor": actor or os.environ.get("GUARDAO_CLAIM_ASSIGNEE") or "local-agent",
        "at": _now(),
    }
    by_task[task_id] = meta
    by_role.setdefault(role, [])
    if task_id not in by_role[role]:
        by_role[role].append(task_id)
    save_locks(locks)
    # espelho no board JSON (campo auxiliar)
    try:
        data = load_board()
        for item in data.get("items") or []:
            fields = item.setdefault("fields", {})
            title = item.get("title") or ""
            if f"[{task_id}]" in title or fields.get("Task ID") == task_id:
                fields["Claimed By"] = meta["actor"]
                fields["Agent Role Lock"] = role
                break
        save_board(data)
    except Exception as exc:  # noqa: BLE001
        meta["board_mirror_error"] = str(exc)
    return {"ok": True, "code": "acquired", "lock": meta}


def release_lock(task_id: str) -> dict[str, Any]:
    locks = load_locks()
    by_task = locks.setdefault("by_task", {})
    meta = by_task.pop(task_id, None)
    if meta:
        role = meta.get("role")
        if role and role in (locks.get("by_role") or {}):
            locks["by_role"][role] = [t for t in locks["by_role"][role] if t != task_id]
    save_locks(locks)
    return {"ok": True, "released": meta}
