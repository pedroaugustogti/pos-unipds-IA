#!/usr/bin/env python3
"""Move agents/skills/ → agents/skills/ e atualiza referências."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SKILLS_SRC = ROOT / "agents" / "skills"
SKILLS_DST = ROOT / "agents" / "skills"

SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    "00-runtime",
}

# não reescrever artefatos históricos de runtime/crew
SKIP_PATH_PARTS = ("00-runtime/output", "crew/output", "crew\\output")

REPLACEMENTS: list[tuple[re.Pattern[str], str]] = [
    # paths locais módulo 8 (não modulo-7 10-agents/skills)
    (re.compile(r"(?<![\w/-])agents/skills/"), "agents/skills/"),
    (re.compile(r'MODULE_ROOT / "agents" / "skills"'), 'MODULE_ROOT / "agents" / "skills"'),
    (re.compile(r'ROOT / "agents" / "skills"'), 'ROOT / "agents" / "skills"'),
    (re.compile(r'`agents/skills/`'), "`agents/skills/`"),
]


def move_skills() -> None:
    if not SKILLS_SRC.is_dir():
        return
    SKILLS_DST.parent.mkdir(parents=True, exist_ok=True)
    if SKILLS_DST.exists():
        return
    shutil.move(str(SKILLS_SRC), str(SKILLS_DST))


def should_skip(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if any(part in SKIP_DIRS for part in path.parts):
        return True
    return any(skip in rel for skip in SKIP_PATH_PARTS)


def rewrite_file(path: Path) -> bool:
    if should_skip(path):
        return False
    if path.suffix not in {".py", ".md", ".yml", ".yaml", ".json"}:
        return False
    text = path.read_text(encoding="utf-8")
    new = text
    for pat, repl in REPLACEMENTS:
        new = pat.sub(repl, new)
    # evitar agents/agents/skills
    new = new.replace("agents/skills/", "agents/skills/")
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def update_readme() -> None:
    readme = SKILLS_DST / "README.md"
    if readme.is_file():
        readme.write_text(
            """# Skills (legado)

Conteúdo canônico em **`agents/{agent_role}/SKILL.md`**.

Esta pasta mantém cópias legadas por papel (`agents/skills/{role}/SKILL.md`).

| Legado | Canônico |
|--------|----------|
| `agents/skills/backend/SKILL.md` | `agents/backend/SKILL.md` |
| `agents/skills/_shared/*` | `agents/_shared/*` |
| `agents/skills/qa/*` | `agents/qa-author/` · `agents/qa-gate/` |

Resolução: `lib.core.agent_paths.skill_path()`.
""",
            encoding="utf-8",
        )


def main() -> int:
    move_skills()
    changed = 0
    for path in ROOT.rglob("*"):
        if path.is_file() and rewrite_file(path):
            changed += 1
    update_readme()
    print(f"skills -> agents/skills; {changed} arquivos atualizados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
