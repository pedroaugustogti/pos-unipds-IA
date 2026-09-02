# Módulo 8 — Agents Guardião Família

Base de conhecimento para **agentes autônomos**: LangGraph v2, board GitHub, gateway MCP role-based e QA mobile.

Evolução do módulo 7 com HITL, multi-agent e gates enterprise.

## Estrutura (onde decidir)

| Pasta | Quando consultar |
|-------|------------------|
| [`agents/01-role-based/`](agents/01-role-based/) | Papel canônico: `agent.md`, `SKILL.md`, `KNOWLEDGE.md` |
| [`agents/00-orchestration/`](agents/00-orchestration/) | LangGraph v2, MCP (14 tools), scripts, evals |
| [`agents/00-orchestration/docs/`](agents/00-orchestration/docs/README.md) | Docs compartilhados (MCP, board, grafo, routing, policy) |
| [`agents/00-runtime/`](agents/00-runtime/) | Artefatos por ticket (`output/`) e estado global (`system/`) |
| [`board_automation/`](board_automation/) | Board GitHub, reconcile, templates de issue |
| [`lib/`](lib/) | Gateway, orchestrator, `mcp_invoke`, mobile |
| [`docs/`](docs/) | Autonomia, operação, templates PR/review |
| [`.env.example`](.env.example) | Variáveis de ambiente |

Layout detalhado: [`docs/ESTRUTURA.md`](docs/ESTRUTURA.md) · índice de agentes: [`agents/README.md`](agents/README.md)

## Árvore `agents/`

```
agents/
  00-orchestration/    LangGraph v2 · guardiao_mcp · docs/ · scripts/
  00-runtime/          output/{task_id}/ · system/
  01-role-based/       {role}/ → agent.md · SKILL.md · KNOWLEDGE.md
```

## Regras de decisão (resumo)

1. **Status** — só via `emit_status_event` (eventos role-based v2)
2. **Roteamento** — [`agents/00-orchestration/docs/routing/REPOS_AND_ROUTING.md`](agents/00-orchestration/docs/routing/REPOS_AND_ROUTING.md) + `lib/agent_registry`
3. **Pipeline** — LangGraph v2 ou MCP manual: `on_status_event` → `hitl_guard_actuation` → fase → `execute_agent_actuation_tool`
4. **Review** — creator → reviewer pareado → qa-gate → ops (merge)
5. **Alto risco** — HITL antes de atuar (`hitl_guard_actuation`)

## Quick start

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents

python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task T-P3-009 --mode dry_run
python agents/00-orchestration/scripts/langgraph/smoke_pipeline.py --task T-P3-009 --mode dry_run
python agents/00-orchestration/scripts/cli/gateway_cli.py emit --task T-P3-009 --event frontend-mobile_in_progress
python -m guardiao_mcp
```

## Documentação

| Tema | Onde |
|------|------|
| Papéis e skills | [`agents/01-role-based/`](agents/01-role-based/) |
| Base canônica dos agentes | [`agents/00-orchestration/docs/`](agents/00-orchestration/docs/README.md) |
| Fluxo LangGraph | [`agents/00-orchestration/docs/graph/STATEGRAPH_FLOW.md`](agents/00-orchestration/docs/graph/STATEGRAPH_FLOW.md) |
| MCP por papel | [`agents/00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md`](agents/00-orchestration/docs/mcp/MCP_ROLE_GUIDE.md) |
| Board / Kanban | [`agents/00-orchestration/docs/board/WORKFLOW_BOARD.md`](agents/00-orchestration/docs/board/WORKFLOW_BOARD.md) |
| Autonomia (conceitual) | [`docs/autonomia/orquestracao/README.md`](docs/autonomia/orquestracao/README.md) |
| Módulo (geral) | [`docs/README.md`](docs/README.md) |

## Manutenção

```bash
python agents/00-orchestration/scripts/ops/build_repo_knowledge.py
python agents/00-orchestration/scripts/ops/patch_agent_docs.py
python agents/00-orchestration/scripts/ops/patch_agent_mcp_knowledge.py
```

## Dashboard

`agents/00-runtime/system/observability/dashboard.html` (gerado durante execuções do pipeline).
