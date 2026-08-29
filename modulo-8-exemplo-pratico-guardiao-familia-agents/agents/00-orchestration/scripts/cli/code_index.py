#!/usr/bin/env python3
"""D5 — Indice leve (ripgrep) + manifesto de modulos."""

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
import os
import shutil
import subprocess
import sys
from pathlib import Path

from lib.paths import MODULE_ROOT  # noqa: E402
from lib.env_load import ensure_env  # noqa: E402

ensure_env()
import importlib.util
from lib.paths import orch_script

_spec = importlib.util.spec_from_file_location(
    "eval_gate", orch_script("langgraph", "eval_gate.py")
)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
DEFAULT_PATHS = _mod.DEFAULT_PATHS
resolve_repo_path = _mod.resolve_repo_path


MANIFESTS = {
    "backend": [
        "src/auth", "src/users", "src/families", "src/children", "src/location",
        "src/geofences", "src/sos", "src/notifications", "src/payments", "src/compliance",
    ],
    "frontend-mobile": [
        "src/notifications", "src/devices", "src/location", "src/sos", "app",
    ],
    "database": [
        "src/migrations", "prisma", "typeorm",
    ],
}


def rg(repo: Path, query: str, globs: list[str] | None = None, limit: int = 15) -> list[str]:
    exe = shutil.which("rg") or shutil.which("ripgrep")
    if exe:
        cmd = [exe, "-n", "--no-heading", "-S", query, str(repo), "-m", str(limit)]
        if globs:
            for g in globs:
                cmd.extend(["-g", g])
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        lines = [ln for ln in (r.stdout or "").splitlines() if ln.strip()]
        return lines[:limit]
    # fallback: grep simples
    hits = []
    for path in repo.rglob("*.ts"):
        if "node_modules" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if query.lower() in text.lower():
            hits.append(f"{path}:{query}")
        if len(hits) >= limit:
            break
    return hits


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--role", default="backend")
    p.add_argument("--query", required=True)
    p.add_argument("--repo", default=None)
    args = p.parse_args()

    repo_name = args.repo or {
        "backend": "guardiao-familia-api",
        "frontend-mobile": "guardiao-familia-parent",
        "database": "guardiao-familia-api",
    }.get(args.role, "guardiao-familia-api")

    path = resolve_repo_path(repo_name)
    if not path or not path.exists():
        print(json.dumps({
            "ok": False,
            "error": f"repo nao montado: {repo_name}",
            "hint": "Defina GUARDAO_API_PATH / GUARDAO_PARENT_PATH",
            "manifest": MANIFESTS.get(args.role, []),
        }, ensure_ascii=False, indent=2))
        return 1

    hits = rg(path, args.query)
    # prioriza paths do manifesto
    manifest = MANIFESTS.get(args.role, [])
    ranked = sorted(
        hits,
        key=lambda h: (0 if any(m.replace("\\", "/") in h.replace("\\", "/") for m in manifest) else 1, h),
    )
    print(json.dumps({
        "ok": True,
        "role": args.role,
        "repo": repo_name,
        "repo_path": str(path),
        "query": args.query,
        "manifest": manifest,
        "hits": ranked[:15],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
