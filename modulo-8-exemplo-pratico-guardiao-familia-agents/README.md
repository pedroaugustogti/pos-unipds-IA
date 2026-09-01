# Módulo 8 — Agents Guardião Família

Base de conhecimento para **agentes autônomos**: LangGraph v2, board GitHub, gateway MCP e QA mobile.

Evolução do módulo 7 com HITL, multi-agent e gates enterprise.

## Estrutura (onde decidir)

| Pasta | Quando consultar |
|-------|------------------|
| [`agents/`](agents/) | Papel, prompt, skill, KNOWLEDGE.md |
| [`agents/00-orchestration/`](agents/00-orchestration/) | LangGraph v2, MCP (14 tools), CLIs |
| [`board_automation/`](board_automation/) | Roteamento task, reconcile, templates issue |
| [`lib/`](lib/) | Gateway, orchestrator, `mcp_invoke`, mobile |
| [`docs/`](docs/) | Fluxo, operação, configuração |
| [`.env.example`](.env.example) | Variáveis de ambiente |

Layout completo: [`docs/ESTRUTURA.md`](docs/ESTRUTURA.md)

## Regras de decisão (resumo)

1. **Status** — só via `emit_status_event` (eventos role-based, 55 no catálogo)
2. **Roteamento** — `agent_role` no CSV + `task_router.pick_task`
3. **Pipeline** — LangGraph v2 ou MCP manual: `on_status_event` → `hitl_guard` → fase → `execute`
4. **Review** — creator → reviewer pareado → qa-gate → ops (merge)
5. **Alto risco** — HITL antes de merge (`hitl_guard_actuation`)

## Quick start

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents

python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task T-P3-009 --mode dry_run
python agents/00-orchestration/scripts/langgraph/smoke_pipeline.py --task T-P3-009 --mode dry_run
python agents/00-orchestration/scripts/cli/gateway_cli.py --task T-P3-009 --agent-role frontend-mobile --board-status "In Progress" --dry-run
python -m guardiao_mcp
```

## Documentação

- Índice: [`docs/README.md`](docs/README.md)
- Fluxo v2: [`agents/00-orchestration/docs/STATEGRAPH_FLOW.md`](agents/00-orchestration/docs/STATEGRAPH_FLOW.md)
- MCP por papel: [`agents/_shared/MCP_ROLE_GUIDE.md`](agents/_shared/MCP_ROLE_GUIDE.md)
- Mapa visual: [`docs/autonomia/orquestracao/README.md`](docs/autonomia/orquestracao/README.md)

## Dashboard

`agents/00-runtime/system/observability/dashboard.html` (gerado durante execuções do pipeline).
