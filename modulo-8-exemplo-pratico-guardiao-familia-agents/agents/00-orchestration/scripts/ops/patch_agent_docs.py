#!/usr/bin/env python3
"""Atualiza seção de base de conhecimento nos agent.md — aponta para docs/."""

from __future__ import annotations

import re
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parents[3]
ROLE_BASED_DIR = AGENTS_DIR / "01-role-based"
DOCS = "../../00-orchestration/docs"

KNOWLEDGE_SECTION = f"""\
## Base de conhecimento (obrigatório antes de agir)

Pasta canônica: [`{DOCS}/`]({DOCS}/README.md)

**Leia nesta ordem** para máximo contexto na task:

| # | Documento | Objetivo |
|---|-----------|----------|
| 1 | [`docs/mcp/MCP_ROLE_GUIDE.md`]({DOCS}/mcp/MCP_ROLE_GUIDE.md) | Tools, eventos e pipeline do **seu papel** |
| 2 | [`docs/board/WORKFLOW_BOARD.md`]({DOCS}/board/WORKFLOW_BOARD.md) | Status Kanban → eventos role-based v2 |
| 3 | [`docs/routing/REPOS_AND_ROUTING.md`]({DOCS}/routing/REPOS_AND_ROUTING.md) | Repo da task, CSV e roteamento |
| 4 | [`./KNOWLEDGE.md`](./KNOWLEDGE.md) | Digest local + seção MCP do papel |
| 5 | [`docs/knowledge/REPO_KNOWLEDGE.md`]({DOCS}/knowledge/REPO_KNOWLEDGE.md) | Índice global do módulo 8 |
| 6 | [`docs/graph/STATEGRAPH_FLOW.md`]({DOCS}/graph/STATEGRAPH_FLOW.md) | Onde você está no grafo LangGraph |
| 7 | [`docs/policy/ACTUATION_GUARDRAIL_POLICY.md`]({DOCS}/policy/ACTUATION_GUARDRAIL_POLICY.md) | HITL e guardrails antes de `execute` |

Após `on_status_event`, combine o JSON retornado (`ticket`, `handoff`, `playbook`) com os docs acima **antes** de `hitl_guard_actuation` → fase → `execute_agent_actuation_tool`.

Regenerar digest: `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`

"""

KNOWLEDGE_RE = re.compile(
    r"## Base de conhecimento[^\n]*\n.*?(?=\n## [A-Za-z])",
    re.DOTALL,
)

LINK_REPLACEMENTS = (
    ("../_shared/MCP_TOOLS.md", f"{DOCS}/mcp/MCP_TOOLS.md"),
    ("../_shared/MCP_ROLE_GUIDE.md", f"{DOCS}/mcp/MCP_ROLE_GUIDE.md"),
    ("../_shared/WORKFLOW_BOARD.md", f"{DOCS}/board/WORKFLOW_BOARD.md"),
    ("../../00-orchestration/docs/routing/REPOS_AND_ROUTING.md", f"{DOCS}/routing/REPOS_AND_ROUTING.md"),
    ("../../00-orchestration/docs/knowledge/REPO_KNOWLEDGE.md", f"{DOCS}/knowledge/REPO_KNOWLEDGE.md"),
    ("../../00-orchestration/docs/graph/STATEGRAPH_FLOW.md", f"{DOCS}/graph/STATEGRAPH_FLOW.md"),
    ("../_shared/ACTUATION_GUARDRAIL_POLICY.md", f"{DOCS}/policy/ACTUATION_GUARDRAIL_POLICY.md"),
)


def patch_agent_md(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    if KNOWLEDGE_RE.search(text):
        text = KNOWLEDGE_RE.sub(KNOWLEDGE_SECTION + "\n", text, count=1)
    else:
        # insere após título H1
        lines = text.splitlines(keepends=True)
        for i, line in enumerate(lines):
            if line.startswith("## "):
                lines.insert(i, "\n" + KNOWLEDGE_SECTION + "\n")
                text = "".join(lines)
                break
    for old, new in LINK_REPLACEMENTS:
        text = text.replace(old, new)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    count = 0
    for agent_dir in sorted(ROLE_BASED_DIR.iterdir()):
        path = agent_dir / "agent.md"
        if path.exists() and patch_agent_md(path):
            count += 1
            print("patched", agent_dir.name)
    print(f"Total: {count} agent.md")


if __name__ == "__main__":
    main()
