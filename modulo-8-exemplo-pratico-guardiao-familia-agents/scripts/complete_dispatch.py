#!/usr/bin/env python3
"""Fecha um job apos o executor (Cursor Agent / Automation) gravar o contrato JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.complete_dispatch import RESULTS_DIR, apply_dispatch_result  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Aplica contrato de conclusao do dispatch")
    p.add_argument("--job", help="job_id (le crew/output/dispatch_results/{job}.json)")
    p.add_argument("--file", help="caminho do JSON de resultado")
    p.add_argument("--stdin", action="store_true", help="le JSON do stdin")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if args.stdin:
        payload = json.load(sys.stdin)
        out = apply_dispatch_result(payload, dry_run=args.dry_run)
    elif args.file:
        out = apply_dispatch_result(Path(args.file), dry_run=args.dry_run)
    elif args.job:
        path = RESULTS_DIR / f"{args.job}.json"
        if not path.exists():
            print(json.dumps({"ok": False, "error": f"arquivo nao encontrado: {path}"}, ensure_ascii=False))
            return 1
        out = apply_dispatch_result(path, dry_run=args.dry_run)
    else:
        p.error("informe --job, --file ou --stdin")

    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
