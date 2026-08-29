"""Trabalho real no site institucional (hero) — usado pelo no implement/qa do LangGraph."""

from __future__ import annotations

import http.server
import socket
import socketserver
import subprocess
import threading
import time
from functools import partial
from pathlib import Path
from typing import Any

from lib.core.repo_paths import resolve_repo_path

OLD = "mais importa"
NEW = "sua família"
EXPECTED = "Tranquilidade para sua família"


def is_site_hero_task(task: dict[str, Any]) -> bool:
    fields = task.get("fields") if isinstance(task.get("fields"), dict) else {}
    repo = str(
        task.get("repo")
        or task.get("repository")
        or fields.get("Repo alvo")
        or ""
    ).lower()
    ref = task.get("refinement") if isinstance(task.get("refinement"), dict) else {}
    hints = " ".join(str(x) for x in (ref.get("acceptance_hints") or [])).lower()
    blob = f"{task.get('title') or ''} {task.get('id') or ''} {hints}".lower()
    site = "guardiao-familia-site" in repo or repo.endswith("site")
    hero = any(
        k in blob
        for k in ("hero", "sua família", "sua familia", "mais importa", "tranquilidade", "t-p13")
    )
    return bool(site and hero)

def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace"
    )


def apply_hero_commit(task_id: str) -> dict[str, Any]:
    """Altera index.html e versiona na feature branch."""
    site = resolve_repo_path("guardiao-familia-site")
    branch = f"feat/{task_id.lower()}-hero-sua-familia"
    _run(["git", "checkout", "main"], site)
    _run(["git", "checkout", "-B", branch], site)

    index = site / "index.html"
    raw = index.read_text(encoding="utf-8")
    updated = raw.replace(
        "Tranquilidade para quem mais importa",
        "Tranquilidade para sua família",
    ).replace(
        "Tranquilidade para quem <span>mais importa</span>",
        "Tranquilidade para <span>sua família</span>",
    )
    if EXPECTED.lower() not in updated.lower():
        raise RuntimeError("Falha ao aplicar texto do hero em index.html")
    index.write_text(updated, encoding="utf-8")
    _run(["git", "add", "index.html"], site)
    commit = _run(
        [
            "git",
            "-c",
            "user.name=Guardiao Agents",
            "-c",
            "user.email=agents@guardiaofamilia.local",
            "commit",
            "-m",
            f"{task_id}: hero home — Tranquilidade para sua família",
        ],
        site,
    )
    sha = (_run(["git", "rev-parse", "HEAD"], site).stdout or "").strip()
    ok = commit.returncode == 0 or "nothing to commit" in (
        (commit.stdout or "") + (commit.stderr or "")
    )
    return {
        "ok": ok,
        "branch": branch,
        "sha": sha,
        "site": str(site),
        "file": "index.html",
        "expected": EXPECTED,
    }


def _free_port(preferred: int = 8080) -> int:
    for port in (preferred, 8081, 8766, 0):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return s.getsockname()[1] if port == 0 else port
            except OSError:
                continue
    return preferred


def run_hero_qa(task_id: str) -> dict[str, Any]:
    """Sobe HTTP local + Playwright hero."""
    from lib.mobile.qa_playwright import run_hero_home_playwright

    site = resolve_repo_path("guardiao-familia-site")

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):  # noqa: ANN002
            return

    port = _free_port()
    handler = partial(Quiet, directory=str(site))
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    httpd.allow_reuse_address = True
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    time.sleep(0.35)
    try:
        return run_hero_home_playwright(
            base_url=f"http://127.0.0.1:{port}/",
            expected_text=EXPECTED,
            forbidden_in_h1=OLD,
            task_id=task_id,
        )
    finally:
        httpd.shutdown()
