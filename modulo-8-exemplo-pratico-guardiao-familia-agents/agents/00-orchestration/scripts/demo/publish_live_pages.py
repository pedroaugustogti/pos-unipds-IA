#!/usr/bin/env python3
"""Copia snapshot + dashboard para docs/live (espelho GitHub Pages)."""

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
import shutil
import sys
from pathlib import Path

from lib.paths import MODULE_ROOT  # noqa: E402
from lib.env_load import ensure_env  # noqa: E402

ensure_env()
from lib.observability import DASHBOARD_PATH, SNAPSHOT_PATH, build_snapshot, write_dashboard  # noqa: E402

LIVE_DIR = MODULE_ROOT / "docs" / "live"


def publish(*, refresh: bool = True) -> dict:
    if refresh:
        write_dashboard(build_snapshot())
    LIVE_DIR.mkdir(parents=True, exist_ok=True)
    snap_dst = LIVE_DIR / "snapshot.json"
    dash_dst = LIVE_DIR / "dashboard.html"
    shutil.copy2(SNAPSHOT_PATH, snap_dst)
    shutil.copy2(DASHBOARD_PATH, dash_dst)
    # index redirect
    (LIVE_DIR / "index.html").write_text(
        '<!DOCTYPE html><meta http-equiv="refresh" content="0; url=dashboard.html">'
        "<title>Guardião agents live</title>",
        encoding="utf-8",
    )
    return {
        "ok": True,
        "live_dir": str(LIVE_DIR),
        "snapshot": str(snap_dst),
        "dashboard": str(dash_dst),
        "pages_url": (
            "https://pedroaugustogti.github.io/pos-unipds-IA/"
            "modulo-8-exemplo-pratico-guardiao-familia-agents/docs/live/dashboard.html"
        ),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--no-refresh", action="store_true")
    args = p.parse_args()
    out = publish(refresh=not args.no_refresh)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
