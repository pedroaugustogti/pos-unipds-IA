#!/usr/bin/env python3
"""Atualiza README.md do módulo 8 para LangGraph v2 / MCP v2."""

from __future__ import annotations

import re
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]

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

REPLACEMENTS: list[tuple[str, str]] = [
    # CLI / scripts removidos
    (
        "python agents/00-orchestration/scripts/worker/worker_run.py --next --role backend",
        "python agents/00-orchestration/scripts/langgraph/smoke_pipeline.py --task T-P3-009 --mode dry_run",
    ),
    (
        "- Regenerar índice: `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`",
        "- Seção MCP v2 nos agentes: `python agents/_shared/patch_agent_mcp_knowledge.py`",
    ),
    (
        "python agents/00-orchestration/scripts/cli/gateway_cli.py --task T-P05-001 --event claim --dry-run",
        'python agents/00-orchestration/scripts/cli/gateway_cli.py --task T-P05-001 --agent-role backend --board-status "In Progress" --dry-run',
    ),
    (
        "[`docs/live/dashboard.html`](docs/live/dashboard.html) · local: `python agents/00-orchestration/scripts/demo/live_server.py`",
        "Dashboard: `agents/00-runtime/system/observability/dashboard.html` (gerado pelo pipeline)",
    ),
    (
        "Atualizar: `python agents/00-orchestration/scripts/demo/publish_live_pages.py`",
        "Atualizado automaticamente em `agents/00-runtime/system/observability/` durante execuções do grafo.",
    ),
    (
        "Scripts: `agents/00-orchestration/scripts/demo/`",
        "Pipeline: `agents/00-orchestration/scripts/langgraph/langgraph_run.py`",
    ),
    (
        "Integração: nós `ci_nodes` no LangGraph.",
        "Integração: sinais CI via `scripts/cli/ci_signal.py` → gateway; grafo v2 em `event_registry.py`.",
    ),
    (
        "- `dispatch_job_tool` exige `GUARDIAO_MCP_ALLOW_DISPATCH=1`.",
        "- 14 tools ativas — catálogo: `list_mcp_tools` · guia: `agents/_shared/MCP_ROLE_GUIDE.md`.",
    ),
    (
        "| `observability_cli.py` | Snapshot / HTML dashboard |\n",
        "",
    ),
    (
        "| Gateway / worker | `agents/00-orchestration/scripts/cli/gateway_cli.py` |",
        "| Gateway MCP | `agents/00-orchestration/scripts/cli/gateway_cli.py` · `python -m guardiao_mcp` |",
    ),
    (
        "| [`lib/`](lib/) | Gateway, dispatch, observability, mobile |",
        "| [`lib/`](lib/) | Gateway, orchestrator, MCP invoke, mobile |",
    ),
    (
        "3. **Código produto** — dispatch Cursor no repo mapeado em `REPOS_AND_ROUTING`",
        "3. **Código produto** — implementação via MCP `developer_implement` no repo em `REPOS_AND_ROUTING`",
    ),
    (
        "| [`orchestrator/`](orchestrator/) | Runtime de agentes, actuation, claim, outbox |",
        "| [`orchestrator/`](orchestrator/) | Runtime, actuation MCP, claim lock, fases |",
    ),
    (
        "- Status: `start_test`, `test_passed`, `test_failed_bug` via gateway",
        "- Status: eventos role-based `qa-gate_in_test`, `qa-gate_in_pull_request`, `qa-gate_return_in_progress`",
    ),
    (
        "- Não claimar harness em Todo (`qa-author`)",
        "- Não iniciar harness em Todo — responsabilidade do `qa-author` (`orchestrator_enter_in_progress`)",
    ),
    (
        "- Não claimar harness em Todo (responsabilidade do `qa-author`)",
        "- Não iniciar harness em Todo — responsabilidade do `qa-author`",
    ),
    (
        "Usado por LangGraph, gateway e dispatch.",
        "Usado por LangGraph v2, gateway e MCP.",
    ),
    (
        "Orquestração Kanban: claim → context → decide → implement → review → QA → CI → HITL → apply.",
        "LangGraph v2: sync_board → orchestrator_decide → 55 nós evt_* (pipeline MCP).",
    ),
    (
        "Regenerar: `python agents/00-orchestration/scripts/ops/build_repo_knowledge.py`",
        "MCP v2: `python agents/_shared/patch_agent_mcp_knowledge.py`",
    ),
]

REACT_CREATOR = (
    "- **ReAct:** `on_status_event` → `developer_implement` → `execute_agent_actuation_tool` "
    "(eventos `{role}_*`; ver `agent.md`)"
)

REACT_REVIEWER = (
    "- **ReAct:** `on_status_event` → `developer_review` → `execute_agent_actuation_tool` "
    "(máx. 3 voltas; ver `agent.md`)"
)

REACT_QA_GATE = (
    "- **MCP:** `on_status_event` → `qa_validate` → `execute` — suites em `KNOWLEDGE.md`"
)

REACT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"- \*\*ReAct:\*\* loop claim → implementar.*"), REACT_CREATOR),
    (re.compile(r"- \*\*ReAct:\*\* claim → implementar.*"), REACT_CREATOR),
    (re.compile(r"- \*\*ReAct:\*\* claim → migration.*"), REACT_CREATOR),
    (re.compile(r"- \*\*ReAct:\*\* claim → editar workflow.*"), REACT_CREATOR),
    (re.compile(r"- \*\*ReAct:\*\* claim → plan/apply.*"), REACT_CREATOR),
    (re.compile(r"- \*\*ReAct:\*\* claim → preparar artefatos.*"), REACT_CREATOR),
    (re.compile(r"- \*\*ReAct:\*\* claim → executar cenários.*"), REACT_CREATOR),
    (re.compile(r"- \*\*ReAct:\*\* get_handoff → checklist.*"), REACT_REVIEWER),
    (re.compile(r"- \*\*ReAct:\*\* handoff → checklist.*"), REACT_REVIEWER),
]


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    for pattern, repl in REACT_PATTERNS:
        role = path.parent.name
        sub = repl.format(role=role) if "{role}" in repl else repl
        text = pattern.sub(sub, text)
    if path.parent.name in CREATORS:
        text = re.sub(
            r"- \*\*ReAct:\*\* `on_status_event` → `developer_implement` → `execute_agent_actuation_tool` "
            r"\(eventos `\{role\}\*`; ver `agent\.md`\)",
            REACT_CREATOR.format(role=path.parent.name),
            text,
        )
    if path.parent.name == "qa-gate" and "**MCP:**" not in text:
        text = text.replace(
            "## Decisões\n\n",
            "## Decisões\n\n" + REACT_QA_GATE + "\n",
        )
    if path == MODULE / "agents" / "_shared" / "README.md":
        if "MCP_ROLE_GUIDE.md" not in text:
            text = text.replace(
                "| `MCP_TOOLS.md` | Catálogo de tools MCP e dry_run |",
                "| `MCP_TOOLS.md` | Catálogo de 14 tools MCP |\n"
                "| `MCP_ROLE_GUIDE.md` | Tools e eventos por papel (creator/reviewer/qa-gate/ops) |",
            )
        text = text.replace(
            "| `STATEGRAPH_FLOW.md` | Nós LangGraph e transições de Status |",
            "| `STATEGRAPH_FLOW.md` | LangGraph v2 — 55 nós evt_* e pipeline MCP |",
        )
    if path == MODULE / "lib" / "orchestrator" / "README.md":
        text = text.replace(
            "| `event_orchestrator.py` | Runtime de agentes, emit board, dispatch_queue |",
            "| `event_orchestrator.py` | Runtime de agentes, HITL queue, idempotência |",
        )
    if path == MODULE / "agents" / "00-runtime" / "system" / "README.md":
        text = text.replace(
            "| `dispatch/` | Fila worker, prompts, results |",
            "| `dispatch/` | Legado — fila worker (substituída pelo grafo v2) |",
        )
    return text != original and _write(path, text)


def _write(path: Path, text: str) -> bool:
    path.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    n = 0
    for path in sorted(MODULE.rglob("README.md")):
        if patch_file(path):
            n += 1
            print(path.relative_to(MODULE))
    print(f"updated: {n}")


if __name__ == "__main__":
    main()
