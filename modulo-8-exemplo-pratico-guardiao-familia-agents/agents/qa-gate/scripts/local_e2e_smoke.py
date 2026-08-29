#!/usr/bin/env python3
"""CLI: stack local E2E mobile (Docker + API pairing + Appium opcional)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.mobile.local_e2e import (  # noqa: E402
    bootstrap_api_stack,
    check_prerequisites,
    run_api_pairing_smoke,
    run_appium_pairing,
    start_emulators,
)
from lib.mobile.qa_mobile import run_mobile_pairing_qa  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Guardião Família — local E2E mobile")
    parser.add_argument(
        "command",
        choices=("check", "up", "pairing-api", "pairing-appium", "full"),
        help="check=pré-requisitos; up=Docker+migrations; pairing-api=smoke API; pairing-appium=UI; full=stack+appium",
    )
    parser.add_argument("--single-emulator", action="store_true")
    parser.add_argument("--no-seed", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    if args.command == "check":
        out = check_prerequisites(require_android=args.command == "pairing-appium")
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0 if out.get("ok") else 1

    if args.command == "up":
        out = bootstrap_api_stack(seed=not args.no_seed)
    elif args.command == "pairing-api":
        bootstrap = bootstrap_api_stack(seed=not args.no_seed)
        smoke = run_api_pairing_smoke()
        out = {"bootstrap": bootstrap, "pairing": smoke, "ok": bootstrap.get("ok") and smoke.get("ok")}
    elif args.command == "pairing-appium":
        pre = check_prerequisites(require_android=True)
        if not pre.get("android_sdk"):
            out = {"ok": False, "error": "ANDROID_HOME não configurado", "prerequisites": pre}
        else:
            bootstrap = bootstrap_api_stack(seed=not args.no_seed)
            emu = start_emulators(single=args.single_emulator)
            appium = run_appium_pairing(single_emulator=args.single_emulator)
            out = {
                "bootstrap": bootstrap,
                "emulators": emu,
                "appium": appium,
                "ok": bootstrap.get("ok") and emu.get("ok") and appium.get("ok"),
            }
    else:
        out = run_mobile_pairing_qa("LOCAL-E2E", full_ui=True)

    if args.as_json:
        print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
    else:
        ok = out.get("ok")
        print(f"Resultado: {'PASS' if ok else 'FAIL'}")
        if out.get("error"):
            print(out["error"])
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
