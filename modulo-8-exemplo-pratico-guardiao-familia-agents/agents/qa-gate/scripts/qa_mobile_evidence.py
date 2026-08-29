#!/usr/bin/env python3
"""Captura evidências E2E mobile via guardiao-familia-mobile-setup."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib.env_load import ensure_env  # noqa: E402

ensure_env()

from lib.mobile.qa_mobile_setup_evidence import (  # noqa: E402
    collect_artifacts,
    format_evidence_comment,
    run_mobile_evidence,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True, help="ID da task (ex. T-P04-001)")
    parser.add_argument("--feature", default="pairing", help="GF_APPIUM_FEATURE")
    parser.add_argument(
        "--mode",
        choices=("check", "full", "cycle", "smoke"),
        default="cycle",
        help="check=só inventário; full=fast-stack; cycle=PairingCycle; smoke=Phase Smoke",
    )
    parser.add_argument("--skip-build", action="store_true", default=True)
    parser.add_argument("--record-video", action="store_true", help="adb screenrecord parent+child")
    parser.add_argument("--no-package", action="store_true")
    parser.add_argument("--comment-issue", action="store_true", help="Comenta issue via gh (se disponível)")
    parser.add_argument("--timeout", type=int, default=1200)
    args = parser.parse_args()

    if args.mode == "check":
        arts = collect_artifacts()
        print(json.dumps(arts, indent=2, ensure_ascii=False))
        return 0 if arts.get("setup_root") else 1

    result = run_mobile_evidence(
        args.task,
        feature=args.feature,
        mode=args.mode,
        skip_build=args.skip_build,
        record_video=args.record_video,
        package=not args.no_package,
        timeout_sec=args.timeout,
    )
    comment = format_evidence_comment(result)
    print(comment)
    print(json.dumps({k: v for k, v in result.items() if k != "run"}, indent=2, ensure_ascii=False, default=str))

    if args.comment_issue:
        try:
            import subprocess

            subprocess.run(
                ["gh", "issue", "comment", args.task, "--body", comment],
                check=False,
                cwd=str(ROOT),
            )
        except OSError:
            print("gh não disponível — cole o comentário manualmente", file=sys.stderr)

    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
