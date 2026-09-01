#!/usr/bin/env python3
"""D2 — Eval gate deterministico antes do review LLM."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_bs = Path(__file__).resolve().parents[2] / "bootstrap.py"
_spec = importlib.util.spec_from_file_location("orch_bootstrap", _bs)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
_mod.setup()

import argparse
import json
import re

from lib.env_load import ensure_env  # noqa: E402

ensure_env()
from board_automation.board.task_router import load_tasks  # noqa: E402
from lib.core.repo_paths import REPO_ENV, resolve_repo_path  # noqa: E402
from lib.gateway.handoff import load_handoff, write_handoff  # noqa: E402

SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (RSA |EC )?PRIVATE KEY-----"),
    re.compile(r"(?i)(api[_-]?key|secret|password)\s*[:=]\s*['\"][^'\"]{8,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
]


def scan_secrets(repo_path: Path, max_files: int = 200) -> list[str]:
    hits: list[str] = []
    exts = {".ts", ".tsx", ".js", ".jsx", ".py", ".env", ".json", ".yml", ".yaml"}
    count = 0
    for path in repo_path.rglob("*"):
        if count >= max_files:
            break
        if not path.is_file() or path.suffix.lower() not in exts:
            continue
        if "node_modules" in path.parts or ".git" in path.parts or "dist" in path.parts:
            continue
        count += 1
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pat in SECRET_PATTERNS:
            if pat.search(text):
                hits.append(f"{path.relative_to(repo_path)}:{pat.pattern[:40]}")
                break
    return hits


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--task", required=True)
    p.add_argument("--repo-path", default=None)
    p.add_argument("--write-handoff", action="store_true")
    args = p.parse_args()

    task = next((t for t in load_tasks() if t["id"] == args.task), None)
    if not task:
        print(json.dumps({"ok": False, "error": "task nao encontrada"}))
        return 1

    repo = task.get("repo") or "guardiao-familia-api"
    repo_path = Path(args.repo_path) if args.repo_path else resolve_repo_path(repo)
    checks: dict = {
        "repo": repo,
        "repo_path": str(repo_path) if repo_path else None,
        "secrets": [],
        "migration_hint": None,
        "handoff_pr": None,
    }
    errors: list[str] = []

    if not repo_path or not repo_path.exists():
        errors.append(f"Repo path ausente: {repo} (defina {REPO_ENV.get(repo)})")
    else:
        secrets = scan_secrets(repo_path)
        checks["secrets"] = secrets[:20]
        if secrets:
            errors.append(f"{len(secrets)} possivel(is) secret(s) no working tree")

    title = (task.get("title") or "").lower()
    if task.get("agent_role") == "backend" and any(k in title for k in ("schema", "migration", "tabela")):
        checks["migration_hint"] = "Task sugere schema — conferir migration no PR"
        # nao falha sozinho; so avisa

    handoff = load_handoff(args.task) or {}
    checks["handoff_pr"] = handoff.get("pr_url")
    if not handoff.get("pr_url"):
        errors.append("Handoff sem pr_url — eval pre-review incompleto")

    result = {
        "ok": len(errors) == 0,
        "task_id": args.task,
        "errors": errors,
        "checks": checks,
    }

    if args.write_handoff:
        write_handoff(
            args.task,
            from_agent="eval_gate",
            to_agent=(task.get("agent_role") or "backend") + "-reviewer",
            event="eval_gate",
            status="Ready for Code Review",
            pr_url=handoff.get("pr_url"),
            summary="Eval gate deterministico",
            metrics={"eval_gate": result},
        )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
