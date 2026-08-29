#!/usr/bin/env python3
"""CLI — seed DB + handoff para evidências Appium."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib.env_load import ensure_env  # noqa: E402

ensure_env()

from lib.mobile.mobile_e2e_seed import (  # noqa: E402
    SEED_PROFILES,
    cleanup_db_seed,
    default_db_seed_config,
    provision_handoff,
)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--task", required=True)
    p.add_argument("--profile", default="child_home", choices=sorted(SEED_PROFILES))
    p.add_argument("--cleanup-only", action="store_true")
    p.add_argument("--no-bootstrap", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if args.cleanup_only:
        out = cleanup_db_seed({"handoff": {}, "handoff_path": None})
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0 if out.get("ok") else 1

    cfg = default_db_seed_config(args.task, profile=args.profile)
    if args.no_bootstrap:
        cfg["bootstrap_api"] = False
    out = provision_handoff(args.task, config=cfg)
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
    else:
        print(json.dumps({k: v for k, v in out.items() if k != "steps"}, indent=2, ensure_ascii=False))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
