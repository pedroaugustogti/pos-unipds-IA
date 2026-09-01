#!/usr/bin/env python3
"""Gera REPO_KNOWLEDGE.md e sincroniza o digest em agents/*/KNOWLEDGE.md."""

from __future__ import annotations

import re
import sys
from pathlib import Path

MODULE = Path(__file__).resolve().parents[4]
AGENTS = MODULE / "agents"
ROLE_BASED = AGENTS / "01-role-based"
REPO_KNOWLEDGE = MODULE / "agents" / "00-orchestration" / "docs" / "knowledge" / "REPO_KNOWLEDGE.md"
DOCS_MCP = "../00-orchestration/docs/mcp"

SKIP_DIRS = {"output", "__pycache__", "node_modules", ".git"}

HEADER = """\
# Base de conhecimento — módulo 8

Digest gerado de todos os `README.md` (exceto `output/`).
Regenerar: `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`

"""

MCP_SECTION_RE = re.compile(
    r"## MCP Guardião Família \(v2\)\n.*?\n---\n\n",
    re.DOTALL,
)


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def parse_readme(text: str) -> dict:
    lines = text.splitlines()
    title = ""
    papel = ""
    titulo = ""
    acionar: list[str] = []
    decisoes: list[str] = []
    section: str | None = None
    in_code = False

    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if line.startswith("# ") and not title:
            title = line[2:].strip().removeprefix("Agente ").strip("`")
        if line.startswith("**Papel:**"):
            papel = line.removeprefix("**Papel:**").strip()
        if line.startswith("## Quando acionar"):
            section = "acionar"
            continue
        if line.startswith("## Decisões"):
            section = "decisoes"
            continue
        if line.startswith("## "):
            section = None
            continue
        if section == "acionar" and line.startswith("- "):
            acionar.append(line[2:].strip())
        if section == "decisoes" and line.startswith("- "):
            decisoes.append(line[2:].strip())

    if not papel:
        for i, line in enumerate(lines):
            if not line.startswith("# "):
                continue
            in_code = False
            for nxt in lines[i + 1 : i + 12]:
                if nxt.strip().startswith("```"):
                    in_code = not in_code
                    continue
                if in_code:
                    continue
                s = nxt.strip()
                if not s or s.startswith("#") or s.startswith("- [`") or s.startswith("|"):
                    continue
                if "Base de conhecimento" in s or s.startswith("**Papel:**"):
                    continue
                papel = s
                break
            break

    if title == "qa-gate" and not titulo:
        titulo = "qa-gate"

    return {
        "title": title,
        "papel": papel,
        "titulo": titulo,
        "acionar": acionar,
        "decisoes": decisoes,
    }


def link_for(section: str, readme_rel: str) -> str:
    rel = readme_rel.replace("\\", "/")
    label = rel
    if section == "agents":
        sub = rel.removeprefix("agents/")
        if sub.startswith("01-role-based/"):
            sub = sub.removeprefix("01-role-based/")
        href = f"../{sub}"
    else:
        href = f"../../{rel}"
    return f"[`{label}`]({href})"


def format_entry(section: str, dir_rel: str, readme_rel: str, meta: dict) -> list[str]:
    display = dir_rel.replace("\\", "/").rstrip("/") + "/"
    lines = [f"### `{display}`"]
    if meta["titulo"]:
        lines.append(f"- **Título:** {meta['titulo']}")
    if meta["papel"]:
        lines.append(f"- **Papel:** {meta['papel']}")
    for item in meta["acionar"]:
        lines.append(f"- Acionar: {item}")
    for item in meta["decisoes"]:
        lines.append(f"- Decisão: {item}")
    lines.append(f"- README: {link_for(section, readme_rel)}")
    lines.append("")
    return "\n".join(lines) + "\n"


def collect_readmes() -> list[tuple[str, str, Path]]:
    items: list[tuple[str, str, Path]] = []
    for readme in sorted(MODULE.rglob("README.md")):
        if should_skip(readme):
            continue
        rel = readme.relative_to(MODULE)
        dir_rel = str(rel.parent).replace("\\", "/")
        if dir_rel == ".":
            section = "."
        else:
            section = dir_rel.split("/")[0]
        items.append((section, dir_rel, readme))
    return items


def build_digest() -> str:
    by_section: dict[str, list[tuple[str, str, Path]]] = {}
    for section, dir_rel, readme in collect_readmes():
        by_section.setdefault(section, []).append((dir_rel, str(readme.relative_to(MODULE)).replace("\\", "/"), readme))

    order = ["agents", "board_automation", "certs", "docs", "lib", "."]
    parts = [HEADER]
    for section in order:
        entries = by_section.get(section)
        if not entries:
            continue
        heading = "## ./\n\n" if section == "." else f"## {section}/\n\n"
        parts.append(heading)
        for dir_rel, readme_rel, readme in sorted(entries, key=lambda x: x[0]):
            meta = parse_readme(readme.read_text(encoding="utf-8"))
            parts.append(format_entry(section, dir_rel, readme_rel, meta))
    return "".join(parts)


def sync_agent_knowledge(digest: str) -> int:
    body = digest.split("## agents/", 1)[-1]
    body = "## agents/" + body
    count = 0
    for agent_dir in ROLE_BASED.iterdir():
        if not agent_dir.is_dir():
            continue
        path = agent_dir / "KNOWLEDGE.md"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        mcp = MCP_SECTION_RE.search(text)
        mcp_block = mcp.group(0) if mcp else ""
        new_text = HEADER + mcp_block + body
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            count += 1
    return count


def main() -> int:
    digest = build_digest()
    REPO_KNOWLEDGE.write_text(digest, encoding="utf-8")
    synced = sync_agent_knowledge(digest)
    print(f"Wrote {REPO_KNOWLEDGE.relative_to(MODULE)}")
    print(f"Synced {synced} agent KNOWLEDGE.md files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
