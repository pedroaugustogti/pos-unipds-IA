#!/usr/bin/env python3
"""Limpa READMEs de 01-role-based: links quebrados, CSV e aliases legados."""

from __future__ import annotations

import re
from pathlib import Path

MODULE = Path(__file__).resolve().parents[4]
ROLE_BASED = MODULE / "agents" / "01-role-based"
AGENTS_README = MODULE / "agents" / "README.md"

LINE_PATTERNS = [
    re.compile(r"^.*TASK_AGENT_MAP\.csv.*\n", re.MULTILINE),
    re.compile(r" \(ver `TASK_AGENT_MAP\.csv`\)", re.MULTILINE),
    re.compile(r" \(alias CSV `[^`]+`; legado v1 rejeitado\)", re.MULTILINE),
    re.compile(r"^\| Alias legado \|.*\n", re.MULTILINE),
    re.compile(r"^Roteamento task → role:.*\n", re.MULTILINE),
]


def clean_text(text: str, *, in_role_subfolder: bool) -> str:
    if in_role_subfolder:
        text = text.replace(
            "- [`../../_shared/`](../../_shared/) — MCP, board, fluxo LangGraph",
            "- [`00-orchestration/docs/`](../../00-orchestration/docs/README.md) — MCP, board, fluxo LangGraph",
        )
    lines = [ln for ln in text.splitlines() if "docs/comportamento/README.md" not in ln]
    text = "\n".join(lines)
    if text and not text.endswith("\n"):
        text += "\n"
    for pat in LINE_PATTERNS:
        text = pat.sub("", text)
    return re.sub(r"\n{3,}", "\n\n", text)


def main() -> None:
    changed = 0
    for readme in ROLE_BASED.rglob("README.md"):
        text = readme.read_text(encoding="utf-8")
        in_sub = readme.parent != ROLE_BASED
        new = clean_text(text, in_role_subfolder=in_sub)
        if new != text:
            readme.write_text(new, encoding="utf-8")
            changed += 1
            print(f"fixed {readme.relative_to(MODULE)}")
    if AGENTS_README.is_file():
        text = AGENTS_README.read_text(encoding="utf-8")
        new = clean_text(text, in_role_subfolder=False)
        new = new.replace(
            "| `qa` | creator (alias) | `qa-reviewer` | `01-role-based/qa/` |\n",
            "",
        )
        if "TASK_AGENT_MAP.csv" in new:
            new = new.replace(
                "2. `board_automation/data/maps/TASK_AGENT_MAP.csv` → coluna `agent_role`\n"
                "3. Carregar",
                "2. Roteamento: [`00-orchestration/docs/routing/REPOS_AND_ROUTING.md`](00-orchestration/docs/routing/REPOS_AND_ROUTING.md)\n"
                "3. Carregar",
            )
        if new != text:
            AGENTS_README.write_text(new, encoding="utf-8")
            changed += 1
            print(f"fixed {AGENTS_README.relative_to(MODULE)}")
    print(f"Updated {changed} files")


if __name__ == "__main__":
    main()
