"""Estado do bundle Metro servido vs. código-fonte local do app (parent/child)."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lib.core.repo_paths import resolve_repo_path
from lib.mobile.mobile_runtime_config import stack

STATE_PATH = (
    Path(__file__).resolve().parents[2]
    / "agents"
    / "00-runtime"
    / "system"
    / "mobile"
    / "metro_bundle_state.json"
)

WATCH_TOP_DIRS = ("screens", "components", "app", "src", "navigation", "hooks", "contexts")
SOURCE_SUFFIXES = (".tsx", ".ts", ".jsx", ".js", ".json")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _watch_paths(app_cfg: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for key in ("app_tsx", "screens_dir"):
        val = str(app_cfg.get(key) or "").strip()
        if val and val not in paths:
            paths.append(val)
    for d in WATCH_TOP_DIRS:
        if d not in paths:
            paths.append(d)
    return paths


def _git_cmd(repo: Path, *args: str) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    return (proc.stdout or "").strip()


def _mtime_fingerprint(repo: Path, watch_paths: list[str]) -> dict[str, Any]:
    parts: list[str] = []
    for rel in watch_paths:
        base = repo / rel
        if base.is_file():
            st = base.stat()
            parts.append(f"F:{rel}:{st.st_mtime_ns}:{st.st_size}")
            continue
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in SOURCE_SUFFIXES:
                continue
            rel_path = path.relative_to(repo).as_posix()
            st = path.stat()
            parts.append(f"{rel_path}:{st.st_mtime_ns}:{st.st_size}")
    digest = hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:16]
    return {
        "fingerprint": f"mtime:{digest}",
        "head": "",
        "dirty_files": parts[:30],
        "method": "mtime",
        "repo": str(repo),
    }


def compute_metro_source_fingerprint(app: str) -> dict[str, Any]:
    """Fingerprint do código que o Metro deve servir (HEAD git + working tree em paths do app)."""
    cfg = stack(app)
    repo_name = str(cfg["repo"])
    repo = resolve_repo_path(repo_name)
    watch = _watch_paths(cfg)
    if not repo or not repo.is_dir():
        return {
            "fingerprint": "repo_missing",
            "head": "",
            "dirty_files": [],
            "method": "missing",
            "repo": repo_name,
            "error": f"repo not found: {repo_name}",
        }

    if not (repo / ".git").is_dir():
        fp = _mtime_fingerprint(repo, watch)
        fp["repo"] = repo_name
        return fp

    head = _git_cmd(repo, "rev-parse", "HEAD") or "no_head"
    existing = [p for p in watch if (repo / p).exists()]
    path_args = existing or ["."]
    diff = (_git_cmd(repo, "diff", "--name-only", "HEAD", "--", *path_args) or "").splitlines()
    cached = (_git_cmd(repo, "diff", "--cached", "--name-only", "--", *path_args) or "").splitlines()
    status = (_git_cmd(repo, "status", "--porcelain", "--", *path_args) or "").splitlines()
    dirty: set[str] = set()
    for line in diff + cached:
        line = line.strip()
        if line:
            dirty.add(line)
    for line in status:
        if len(line) > 3:
            dirty.add(line[3:].strip())

    dirty_sorted = sorted(dirty)
    dirty_sig = hashlib.sha256("\n".join(dirty_sorted).encode("utf-8")).hexdigest()[:12]
    return {
        "fingerprint": f"{head[:12]}:{dirty_sig}",
        "head": head,
        "dirty_files": dirty_sorted[:40],
        "dirty_count": len(dirty_sorted),
        "method": "git",
        "repo": repo_name,
        "repo_path": str(repo),
        "watch_paths": watch,
    }


def _load_state() -> dict[str, Any]:
    if not STATE_PATH.is_file():
        return {}
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_state(data: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def assess_metro_bundle(app: str) -> dict[str, Any]:
    """Compara fingerprint atual do repo com o último bundle registrado para o app."""
    cfg = stack(app)
    port = int(cfg["metro_port"])
    current = compute_metro_source_fingerprint(app)
    all_state = _load_state()
    served_raw = all_state.get(app)
    served = served_raw if isinstance(served_raw, dict) else {}
    served_fp = str(served.get("fingerprint") or "").strip()
    current_fp = str(current.get("fingerprint") or "").strip()

    stale = False
    reason = ""
    if current_fp in ("", "repo_missing"):
        stale = True
        reason = current.get("error") or "fingerprint_unavailable"
    elif not served_fp:
        stale = True
        reason = "no_served_bundle_record"
    elif served_fp != current_fp:
        stale = True
        reason = "repo_changed_since_last_metro_serve"
        if current.get("dirty_count"):
            reason = f"repo_changed ({current.get('dirty_count')} dirty file(s))"

    return {
        "app": app,
        "metro_port": port,
        "stale": stale,
        "reason": reason,
        "current_fingerprint": current_fp,
        "served_fingerprint": served_fp,
        "current": current,
        "served": served,
    }


def record_metro_bundle_served(app: str, *, task_id: str = "") -> dict[str, Any]:
    """Grava fingerprint servido após Metro subir/reiniciar com sucesso."""
    cfg = stack(app)
    current = compute_metro_source_fingerprint(app)
    fp = str(current.get("fingerprint") or "")
    row = {
        "app": app,
        "metro_port": int(cfg["metro_port"]),
        "repo": str(cfg["repo"]),
        "fingerprint": fp,
        "head": current.get("head") or "",
        "dirty_count": current.get("dirty_count", 0),
        "method": current.get("method") or "",
        "recorded_at": _now(),
        "task_id": task_id,
    }
    state = _load_state()
    state[app] = row
    _save_state(state)
    return row
