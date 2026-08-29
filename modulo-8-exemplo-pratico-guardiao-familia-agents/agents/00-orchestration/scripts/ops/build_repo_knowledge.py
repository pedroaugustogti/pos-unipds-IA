#!/usr/bin/env python3
"""Gera REPO_KNOWLEDGE.md e copia KNOWLEDGE.md para cada agente."""

from __future__ import annotations

import os
import re
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[4]
AGENTS_DIR = MODULE_ROOT / "agents"
SHARED = AGENTS_DIR / "_shared"
OUT_SHARED = SHARED / "REPO_KNOWLEDGE.md"

SKIP_PARTS = {"output", "__pycache__", "crew", ".git", "node_modules"}
SKIP_PREFIXES = ("agents/skills/",)  # legado — canônico em agents/{role}/

ROLES = [
    "backend",
    "backend-reviewer",
    "frontend-mobile",
    "frontend-mobile-reviewer",
    "frontend-web",
    "frontend-web-reviewer",
    "cloud-infra",
    "cloud-infra-reviewer",
    "database",
    "database-reviewer",
    "devops-cicd",
    "devops-cicd-reviewer",
    "stores-release",
    "stores-release-reviewer",
    "qa",
    "qa-reviewer",
    "qa-author",
    "qa-author-reviewer",
    "qa-gate",
]

AGENT_MD_BLOCK = """\
## Base de conhecimento do repositório

Antes de decidir fora do seu escopo, consulte **`./KNOWLEDGE.md`** (digest de todos os `README.md` do módulo 8).

Canônico compartilhado: [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — regenerar com `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`
"""

README_BLOCK = """\
## Base de conhecimento do repositório

- [`KNOWLEDGE.md`](./KNOWLEDGE.md) — digest local (cópia do índice global)
- [`../_shared/REPO_KNOWLEDGE.md`](../_shared/REPO_KNOWLEDGE.md) — canônico compartilhado
"""

SKILL_BLOCK = """\
## Base de conhecimento

Consulte [`./KNOWLEDGE.md`](./KNOWLEDGE.md) — mapa de decisão de **todas** as pastas do módulo 8 (gerado dos READMEs).
"""


def rel_posix(path: Path) -> str:
    return path.relative_to(MODULE_ROOT).as_posix()


def should_skip(path: Path) -> bool:
    rel = rel_posix(path)
    if any(part in SKIP_PARTS for part in path.parts):
        return True
    return any(rel.startswith(p) for p in SKIP_PREFIXES)


def extract_summary(text: str) -> dict[str, list[str]]:
    lines = text.splitlines()
    title = ""
    papel = ""
    quando: list[str] = []
    decisoes: list[str] = []
    section = ""

    for line in lines:
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            continue
        if line.startswith("**Papel:**"):
            papel = line.replace("**Papel:**", "").strip()
            continue
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        if section.startswith("quando acionar") and line.startswith("- ") and len(quando) < 3:
            quando.append(line[2:].strip())
        if section.startswith("decis") and line.startswith("- ") and len(decisoes) < 2:
            decisoes.append(line[2:].strip())
        if not papel and line.strip() and not line.startswith("|") and not line.startswith("```"):
            if section in ("", "papel") or (not section and not title):
                if len(line.strip()) > 20 and not line.startswith("#"):
                    papel = line.strip()
                    section = ""

    return {"title": [title], "papel": [papel] if papel else [], "quando": quando, "decisoes": decisoes}


def collect_readmes() -> list[tuple[str, dict[str, list[str]]]]:
    items: list[tuple[str, dict[str, list[str]]]] = []
    for readme in sorted(MODULE_ROOT.rglob("README.md")):
        if should_skip(readme.parent):
            continue
        rel = rel_posix(readme.parent)
        summary = extract_summary(readme.read_text(encoding="utf-8", errors="replace"))
        items.append((rel, summary))
    return items


def render_knowledge(items: list[tuple[str, dict[str, list[str]]]], link_base: Path) -> str:
    parts = [
        "# Base de conhecimento — módulo 8",
        "",
        "Digest gerado de todos os `README.md` (exceto `output/`, `skills/` legado).",
        "Regenerar: `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`",
        "",
    ]
    current_top = ""
    for rel, s in items:
        top = rel.split("/")[0] if "/" in rel else rel
        if top != current_top:
            parts.append(f"## {top}/")
            parts.append("")
            current_top = top
        title = s["title"][0] if s["title"] else rel
        parts.append(f"### `{rel}/`")
        if s["papel"]:
            parts.append(f"- **Papel:** {s['papel'][0]}")
        elif title:
            parts.append(f"- **Título:** {title}")
        for w in s["quando"]:
            parts.append(f"- Acionar: {w}")
        for d in s["decisoes"]:
            parts.append(f"- Decisão: {d}")
        readme_path = MODULE_ROOT / rel / "README.md"
        href = Path(os.path.relpath(readme_path, link_base)).as_posix()
        parts.append(f"- README: [`{rel}/README.md`]({href})")
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def patch_file(path: Path, marker: str, block: str, insert_after: str | None = None) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return False
    if insert_after and insert_after in text:
        idx = text.index(insert_after) + len(insert_after)
        new_text = text[:idx] + "\n\n" + block.strip() + "\n" + text[idx:]
    else:
        lines = text.splitlines()
        if lines and lines[0].startswith("#"):
            new_text = lines[0] + "\n\n" + block.strip() + "\n\n" + "\n".join(lines[1:])
        else:
            new_text = block.strip() + "\n\n" + text
    path.write_text(new_text, encoding="utf-8")
    return True


def patch_skill(path: Path) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    if "Base de conhecimento" in text:
        return False
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            end += 3
            new_text = text[:end] + "\n\n" + SKILL_BLOCK.strip() + "\n" + text[end:]
            path.write_text(new_text, encoding="utf-8")
            return True
    return patch_file(path, "Base de conhecimento", SKILL_BLOCK)


def main() -> None:
    items = collect_readmes()
    SHARED.mkdir(parents=True, exist_ok=True)
    OUT_SHARED.write_text(render_knowledge(items, SHARED), encoding="utf-8")

    for role in ROLES:
        role_dir = AGENTS_DIR / role
        if not role_dir.is_dir():
            continue
        (role_dir / "KNOWLEDGE.md").write_text(
            render_knowledge(items, role_dir), encoding="utf-8"
        )
        patch_file(role_dir / "agent.md", "Base de conhecimento do repositório", AGENT_MD_BLOCK)
        patch_file(role_dir / "README.md", "Base de conhecimento do repositório", README_BLOCK)
        patch_skill(role_dir / "SKILL.md")

    # _shared README index entry
    shared_readme = SHARED / "README.md"
    if shared_readme.is_file():
        text = shared_readme.read_text(encoding="utf-8")
        if "REPO_KNOWLEDGE.md" not in text:
            text = text.replace(
                "| `MCP_TOOLS.md` | Catálogo de tools MCP e dry_run |\n",
                "| `MCP_TOOLS.md` | Catálogo de tools MCP e dry_run |\n"
                "| `REPO_KNOWLEDGE.md` | Digest de todos os READMEs do módulo 8 |\n",
            )
            shared_readme.write_text(text, encoding="utf-8")

    print(f"OK: {len(items)} READMEs -> {OUT_SHARED}")
    print(f"KNOWLEDGE.md em {len(ROLES)} agentes")


if __name__ == "__main__":
    main()
