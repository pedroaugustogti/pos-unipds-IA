# Módulo 8 — Agents Guardião Família

Base de conhecimento para **agentes autônomos**: orquestração LangGraph, board GitHub, gateway único de Status, MCP e QA mobile.

Evolução do módulo 7 com HITL, multi-agent e gates enterprise.

## Estrutura (onde decidir)

| Pasta | Quando consultar |
|-------|------------------|
| [`agents/`](agents/) | Escolher papel, prompt, skill, scripts QA |
| [`agents/00-orchestration/`](agents/00-orchestration/) | Pipeline LangGraph, MCP, CLIs |
| [`board_automation/`](board_automation/) | Roteamento task, reconcile, templates issue |
| [`lib/`](lib/) | Gateway, dispatch, observability, mobile |
| [`docs/`](docs/) | Fluxo, operação, configuração |
| [`.env.example`](.env.example) | Variáveis de ambiente |

Layout completo: [`docs/ESTRUTURA.md`](docs/ESTRUTURA.md)

## Regras de decisão (resumo)

1. **Status** — só via `emit_status_event` (`lib/gateway`)
2. **Roteamento** — `agent_role` no CSV + `task_router.pick_task`
3. **Código produto** — dispatch Cursor no repo mapeado em `REPOS_AND_ROUTING`
4. **Review** — creator → reviewer pareado → qa-gate
5. **Alto risco** — HITL antes de merge (`hitl_gates`)

## Quick start

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents

python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task T-P05-006 --mode dry_run
python agents/00-orchestration/scripts/cli/gateway_cli.py --task T-P05-001 --event claim --dry-run
python -m guardiao_mcp
```

## Documentação

- Índice: [`docs/README.md`](docs/README.md)
- Fluxo atual: [`docs/autonomia/ESTADO_ATUAL_FLUXO_E_PROCESSO.md`](docs/autonomia/ESTADO_ATUAL_FLUXO_E_PROCESSO.md)
- Mapa visual: [`docs/autonomia/orquestracao/README.md`](docs/autonomia/orquestracao/README.md)

## Dashboard

[`docs/live/dashboard.html`](docs/live/dashboard.html) · local: `python agents/00-orchestration/scripts/demo/live_server.py`
