#!/usr/bin/env python3
"""Gate CI: falha se houver finding high (ou medium, se STRICT=1)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def load_findings(root: Path) -> list[dict]:
    out: list[dict] = []
    for path in root.rglob("review-*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        for f in data.get("findings", []):
            f["_source"] = str(path)
            out.append(f)
    return out


def key(f: dict) -> tuple:
    return (f.get("rule_id"), f.get("file"), f.get("line"))


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "reviews")
    findings = load_findings(root)
    strict = os.getenv("STRICT", "0") == "1"
    block_severities = {"high"} | ({"medium"} if strict else set())

    blockers = [f for f in findings if f.get("severity") in block_severities]
    # ignore resolved_candidate for gate
    blockers = [f for f in blockers if f.get("status") != "resolved_candidate"]

    print(f"findings_total={len(findings)} blockers={len(blockers)}")
    for f in blockers:
        print(
            f"BLOCK [{f.get('severity')}] {f.get('category')} "
            f"{f.get('file')}:{f.get('line')} {f.get('rule_id')} — {f.get('message')}"
        )

    return 1 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
