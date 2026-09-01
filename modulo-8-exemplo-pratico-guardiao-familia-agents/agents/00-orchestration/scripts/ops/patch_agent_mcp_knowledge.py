#!/usr/bin/env python3
"""Injeta seção MCP v2 no topo de KNOWLEDGE.md e atualiza agent.md."""

from __future__ import annotations

import re
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parents[3]
ROLE_BASED_DIR = AGENTS_DIR / "01-role-based"
DOCS = "../../00-orchestration/docs"

MCP_HEADER = f"""\
## MCP Guardião Família (v2)

Servidor: `guardiao_mcp` · [`{DOCS}/mcp/MCP_TOOLS.md`]({DOCS}/mcp/MCP_TOOLS.md) · [`{DOCS}/mcp/MCP_ROLE_GUIDE.md`]({DOCS}/mcp/MCP_ROLE_GUIDE.md) · `list_mcp_tools`

"""
CREATORS = (
    "backend",
    "frontend-mobile",
    "frontend-web",
    "cloud-infra",
    "database",
    "devops-cicd",
    "qa-author",
    "stores-release",
)

REVIEWER_FOR = {
    "backend": "backend-reviewer",
    "frontend-mobile": "frontend-mobile-reviewer",
    "frontend-web": "frontend-web-reviewer",
    "cloud-infra": "cloud-infra-reviewer",
    "database": "database-reviewer",
    "devops-cicd": "devops-cicd-reviewer",
    "qa-author": "qa-author-reviewer",
    "stores-release": "stores-release-reviewer",
}

def creator_block(role: str) -> str:
    rev = REVIEWER_FOR[role]
    return f"""{MCP_HEADER}**Classificação:** creator · **Papel:** `{role}` · Revisor: `{rev}`

| Tool | Quando |
|------|--------|
| `list_status_events` | Filtrar `agent_role={role}` |
| `on_status_event` | Antes de atuar — ticket, handoff, playbook |
| `hitl_guard_actuation` | Obrigatório antes de `execute_agent_actuation_tool` |
| `developer_implement` | Fase implement (`In Progress`) |
| `execute_agent_actuation_tool` | Fecha fase + emite próximo evento |
| `emit_status_event` | Única porta de status |

**Sequência:** `on_status_event` → `hitl_guard_actuation` → `developer_implement` → `execute` (use `phase_work`).

| Status | Evento |
|--------|--------|
| In Progress | `{role}_in_progress` |
| Ready for Code Review | `{role}_ready_for_code_review` (+ `pr_url`) |
| In Code Review | `{role}_in_code_review` |

Handoff: `agents/00-runtime/output/{{task_id}}/handoff.json`

---

"""


def reviewer_block(role: str) -> str:
    return f"""{MCP_HEADER}**Classificação:** reviewer · **Papel:** `{role}`

| Tool | Quando |
|------|--------|
| `on_status_event` | Contexto + handoff do creator |
| `hitl_guard_actuation` | Antes de `execute` |
| `developer_review` | Fase review (`In Code Review`) |
| `execute_agent_actuation_tool` | Emite aprovação ou retrocesso |
| `emit_status_event` | Transição manual |

**Sequência:** `on_status_event` → `hitl_guard_actuation` → `developer_review` → `execute`.

| Intenção | Evento |
|----------|--------|
| Iniciar review | `{role}_in_code_review` |
| Aprovar | `{role}_ready_for_test` |
| Pedir mudanças | `{role}_return_in_progress` |

---

"""


def qa_gate_block() -> str:
    return f"""{MCP_HEADER}**Classificação:** qa-gate · **Papel:** `qa-gate`

| Tool | Quando |
|------|--------|
| `on_status_event` | AC, config QA, handoff do revisor |
| `hitl_guard_actuation` | Antes de `execute` |
| `qa_validate` | Orquestra seed + Appium + AC |
| `qa_db_seed` / `qa_db_cleanup` | Massa API / purge pós-evidência |
| `qa_appium_suite_parent` / `_child` | Evidências mobile |
| `execute_agent_actuation_tool` | Emite pass/fail role-based |

| Status | Evento |
|--------|--------|
| In Test | `qa-gate_in_test` |
| In Pull Request | `qa-gate_in_pull_request` |
| Retrocesso | `qa-gate_return_in_progress` |

Evidências: `agents/00-runtime/output/{{task_id}}/qa-gate-({{cycle}})/evidence/`

---

"""


def ops_block(role: str) -> str:
    extra = ""
    if role in CREATORS:
        extra = f"\nComo **creator**, use também `developer_implement` nas fases de implementação (`{role}_in_progress`, etc.).\n"
    return f"""{MCP_HEADER}**Classificação:** ops (+ creator quando aplicável) · **Papel:** `{role}`
{extra}
| Tool | Quando |
|------|--------|
| `on_status_event` | Contexto merge/release |
| `hitl_guard_actuation` | Obrigatório (score alto em live) |
| `execute_agent_actuation_tool` | Merge leve → Done |
| `emit_status_event` | `{role}_done` |

---

"""


def qa_author_alias_block() -> str:
    return creator_block("qa-author").replace(
        "**Classificação:** creator · **Papel:** `qa-author`",
        "**Classificação:** creator · **Papel:** `qa` (alias CSV → `qa-author`)",
    )


ROLE_BLOCKS: dict[str, str] = {r: creator_block(r) for r in CREATORS}
ROLE_BLOCKS.update({v: reviewer_block(v) for v in REVIEWER_FOR.values()})
ROLE_BLOCKS["qa-gate"] = qa_gate_block()
ROLE_BLOCKS["qa"] = qa_author_alias_block()

MCP_SECTION_RE = re.compile(
    r"## MCP Guardião Família \(v2\)\n.*?\n---\n\n",
    re.DOTALL,
)

AGENT_MCP_LINKS = f"[`{DOCS}/mcp/MCP_TOOLS.md`]({DOCS}/mcp/MCP_TOOLS.md) · [`{DOCS}/mcp/MCP_ROLE_GUIDE.md`]({DOCS}/mcp/MCP_ROLE_GUIDE.md) · `list_mcp_tools`"

AGENT_MCP_CREATOR = f"""\
## MCP

{AGENT_MCP_LINKS}

| Tool | Uso neste papel |
|------|-----------------|
| `on_status_event` | Contexto antes de atuar |
| `hitl_guard_actuation` | Obrigatório antes de `execute` |
| `developer_implement` | Fase implement |
| `execute_agent_actuation_tool` | Fecha fase + próximo evento |
| `emit_status_event` | `{{role}}_in_progress`, `_ready_for_code_review`, `_in_code_review` |
| `list_status_events` | Catálogo filtrado por `{{role}}` |
"""

AGENT_MCP_REVIEWER = f"""\
## MCP

{AGENT_MCP_LINKS}

| Tool | Uso neste papel |
|------|-----------------|
| `on_status_event` | Handoff + ticket do creator |
| `hitl_guard_actuation` | Antes de `execute` |
| `developer_review` | Review estruturado |
| `execute_agent_actuation_tool` | `_ready_for_test` ou `_return_in_progress` |
| `emit_status_event` | Transições role-based |
"""

AGENT_MCP_QA_GATE = f"""\
## MCP

{AGENT_MCP_LINKS}

| Tool | Uso neste papel |
|------|-----------------|
| `on_status_event` | AC + handoff do revisor |
| `hitl_guard_actuation` | Antes de `execute` |
| `qa_validate` | Orquestra QA completo |
| `qa_db_seed` / `qa_db_cleanup` | Massa API / purge |
| `qa_appium_suite_parent` / `_child` | Evidências Appium |
| `execute_agent_actuation_tool` | `qa-gate_in_pull_request` ou retrocesso |
"""

AGENT_MCP_OPS = f"""\
## MCP

{AGENT_MCP_LINKS}

| Tool | Uso neste papel |
|------|-----------------|
| `on_status_event` | Contexto merge |
| `hitl_guard_actuation` | HITL em live |
| `execute_agent_actuation_tool` | Fase merge → Done |
| `emit_status_event` | `{{role}}_done` |
| `developer_implement` | Fases creator (quando task em implementação) |
"""

AGENT_MCP_RE = re.compile(r"## MCP\n.*?(?=\n## )", re.DOTALL)


def patch_knowledge(agent_dir: Path, role: str) -> bool:
    path = agent_dir / "KNOWLEDGE.md"
    if not path.exists() or role not in ROLE_BLOCKS:
        return False
    text = path.read_text(encoding="utf-8")
    block = ROLE_BLOCKS[role]
    if MCP_SECTION_RE.search(text):
        text = MCP_SECTION_RE.sub(block, text, count=1)
    else:
        lines = text.splitlines(keepends=True)
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith("## agents/") or line.startswith("## lib/"):
                insert_at = i
                break
        else:
            insert_at = min(6, len(lines))
        lines.insert(insert_at, block)
        text = "".join(lines)
    path.write_text(text, encoding="utf-8")
    return True


def patch_agent_md(agent_dir: Path, role: str) -> bool:
    path = agent_dir / "agent.md"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    if role in CREATORS:
        section = AGENT_MCP_CREATOR.format(role=role)
    elif role.endswith("-reviewer"):
        section = AGENT_MCP_REVIEWER
    elif role == "qa-gate":
        section = AGENT_MCP_QA_GATE
    elif role in ("devops-cicd", "stores-release"):
        section = AGENT_MCP_OPS.format(role=role)
    elif role == "qa":
        section = AGENT_MCP_CREATOR.format(role="qa-author")
    else:
        return False
    if not AGENT_MCP_RE.search(text):
        return False
    text = AGENT_MCP_RE.sub(section + "\n", text, count=1)
    path.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    roles_dirs = {p.name: p for p in ROLE_BASED_DIR.iterdir() if p.is_dir() and (p / "KNOWLEDGE.md").exists()}
    k = a = 0
    for role, agent_dir in sorted(roles_dirs.items()):
        if patch_knowledge(agent_dir, role):
            k += 1
        if patch_agent_md(agent_dir, role):
            a += 1
    print(f"KNOWLEDGE: {k} · agent.md: {a}")


if __name__ == "__main__":
    main()
