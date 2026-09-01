#!/usr/bin/env python3
"""Move estado global de output/ para system/ e deixa output/ só com tickets."""

from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

_bs = Path(__file__).resolve().parents[2] / "bootstrap.py"
_spec = importlib.util.spec_from_file_location("orch_bootstrap", _bs)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
_mod.setup()

from lib.paths import RUNTIME_OUTPUT_DIR, RUNTIME_SYSTEM_DIR, ensure_output_dirs  # noqa: E402
from lib.ticket_output import is_ticket_id  # noqa: E402

# Pastas globais que não pertencem a output/
GLOBAL_DIRS = (
    "audit",
    "board",
    "demo",
    "dispatch",
    "disputes",
    "evals",
    "evidence",
    "handoffs",
    "langgraph",
    "logs",
    "mobile",
    "observability",
    "orchestrator",
    "reports",
)


def _merge_tree(src: Path, dest: Path) -> None:
    if not src.exists():
        return
    dest.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dest / item.name
        if item.is_dir():
            _merge_tree(item, target)
        elif not target.exists():
            shutil.copy2(item, target)


def _move_global_dirs(moved: list[str]) -> None:
    ensure_output_dirs()
    for name in GLOBAL_DIRS:
        src = RUNTIME_OUTPUT_DIR / name
        if not src.is_dir():
            continue
        dest = RUNTIME_SYSTEM_DIR / name
        _merge_tree(src, dest)
        shutil.rmtree(src, ignore_errors=True)
        moved.append(f"output/{name}/ -> system/{name}/")


def _remove_non_ticket_entries(removed: list[str]) -> None:
    if not RUNTIME_OUTPUT_DIR.is_dir():
        return
    for item in RUNTIME_OUTPUT_DIR.iterdir():
        if item.is_dir() and is_ticket_id(item.name):
            continue
        if item.name in GLOBAL_DIRS:
            continue
        if item.is_dir():
            shutil.rmtree(item, ignore_errors=True)
            removed.append(f"{item.name}/ (pasta não-ticket)")
        elif item.is_file() and item.name.lower() != "readme.md":
            item.unlink(missing_ok=True)
            removed.append(item.name)


def main() -> int:
    moved: list[str] = []
    removed: list[str] = []

    _move_global_dirs(moved)

    # Migra artefatos legados para dentro dos tickets
    _tickets = Path(__file__).resolve().parent / "reorganize_output_tickets.py"
    _spec2 = importlib.util.spec_from_file_location("reorganize_output_tickets", _tickets)
    _mod2 = importlib.util.module_from_spec(_spec2)
    assert _spec2 and _spec2.loader
    _spec2.loader.exec_module(_mod2)
    _mod2.main()

    _remove_non_ticket_entries(removed)

    print(f"Migracao output->system: {len(moved)} pastas movidas")
    for line in moved:
        print(f"  + {line}")
    if removed:
        print(f"Limpeza output/: {len(removed)} itens removidos")
        for line in removed:
            print(f"  - {line}")

    remaining = sorted(p.name for p in RUNTIME_OUTPUT_DIR.iterdir()) if RUNTIME_OUTPUT_DIR.is_dir() else []
    print(f"output/ agora: {remaining or '(vazio)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
