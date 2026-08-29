#!/usr/bin/env python3
"""Sincroniza Status do Project #2 + labels agent:* com o workflow LangGraph."""

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
import sys
from pathlib import Path

from lib.paths import MODULE_ROOT  # noqa: E402
from lib.env_load import ensure_env  # noqa: E402

ensure_env()
from lib.env_load import load_dotenv  # noqa: E402
from board_automation.board.project_status_sync import (  # noqa: E402
    ensure_status_labels,
    sync_project_status_field,
)


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--labels-only", action="store_true")
    parser.add_argument("--field-only", action="store_true")
    args = parser.parse_args()

    out: dict = {}
    if not args.labels_only:
        out["field"] = sync_project_status_field(dry_run=args.dry_run)
    if not args.field_only:
        out["labels"] = ensure_status_labels(dry_run=args.dry_run)

    print(json.dumps(out, indent=2, ensure_ascii=False))
    ok = all(part.get("ok", True) for part in out.values())
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
