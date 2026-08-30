#!/usr/bin/env python3
"""Corrige mojibake UTF-8 na issue #103 (T-P3-009) e publica no GitHub."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = "guardiaofamilia/guardiao-familia-child"
ISSUE = 103

# Sequências mais longas primeiro (evita substituições parciais)
_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("\u00e2\u20ac\u201c", "\u2013"),  # â€" → en dash
    ("\u00e2\u20ac\u201d", "\u2014"),  # â€" → em dash
    ("\u00e2\u2020\u2019", "\u2192"),  # â†' → arrow
    ("\u00e2\u20ac\u00a6", "\u2026"),  # â€¦ → ellipsis
    ("Ã§Ã£o", "ção"),
    ("Ã§Ãµes", "ções"),
    ("Ã§Ã£", "çã"),
    ("Ã§", "ç"),
    ("Ã£", "ã"),
    ("Ã¡", "á"),
    ("Ã©", "é"),
    ("Ã­", "í"),
    ("Ã³", "ó"),
    ("Ãµ", "õ"),
    ("Ãª", "ê"),
    ("Ã¢", "â"),
    ("Ãº", "ú"),
    ("Ã‰", "É"),
    ("Ã ", "à"),
)


def fix_mojibake(text: str) -> str:
    out = text
    for bad, good in _REPLACEMENTS:
        out = out.replace(bad, good)
    # Linhas ainda com Ã: tentar latin-1 → utf-8
    fixed_lines: list[str] = []
    for line in out.splitlines():
        if "Ã" in line:
            try:
                line = line.encode("latin-1").decode("utf-8")
            except UnicodeError:
                pass
        fixed_lines.append(line)
    return "\n".join(fixed_lines)


def fetch_issue() -> dict:
    raw = subprocess.check_output(
        ["gh", "api", f"repos/{REPO}/issues/{ISSUE}"],
        encoding="utf-8",
    )
    return json.loads(raw)


def main() -> int:
    dry = "--dry-run" in sys.argv
    data = fetch_issue()
    body = fix_mojibake(data.get("body") or "")
    title = fix_mojibake(data.get("title") or "")

    remaining = body.count("Ã") + title.count("Ã")
    out = Path(__file__).resolve().parents[5] / ".issue-103-body-fixed.md"
    out.write_text(body, encoding="utf-8")
    print(f"title: {title}")
    print(f"body: {len(body)} chars, Ã restantes: {remaining}")
    print(f"saved -> {out}")

    if remaining:
        # amostra linhas problemáticas
        for i, line in enumerate(body.splitlines(), 1):
            if "Ã" in line or "â€" in line:
                print(f"  L{i}: {line[:100]}")
        if not dry:
            print("AVISO: ainda há mojibake — revise antes de publicar", file=sys.stderr)

    if dry:
        return 0

    payload = {"body": body}
    if title != data.get("title"):
        payload["title"] = title

    subprocess.run(
        [
            "gh",
            "api",
            "-X",
            "PATCH",
            f"repos/{REPO}/issues/{ISSUE}",
            "--input",
            "-",
        ],
        input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        check=True,
    )
    print(f"updated https://github.com/{REPO}/issues/{ISSUE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
