# Módulo 8 — Exemplo prático: Agents Guardião Família

Evolução do [`10-agents`](../modulo-7-exemplo-pratico-guardiao-familia/docs/02-criacao-board/10-agents) com padrões do **Módulo 8** (AI-First, multi-agent, HITL, enterprise gates).

**Orquestração:** somente **LangGraph** (`langgraph_app/`). CrewAI foi removido.

## O que mudou vs módulo 7

| Tema | Antes | Agora |
|------|-------|-------|
| Orquestração | Crew sequential “faz o sprint” | **LangGraph** + policy Kanban + LLM OpenRouter |
| Eventos | Várias CLIs | **Gateway** `emit_status_event` + contrato |
| Tools | CLIs soltas | **MCP** `guardiao_mcp` (+ bridge no grafo) |
| QA | Papel misturado | **qa-author** (harness) × **qa-gate** (pipeline) |
| Review | LLM finaliza | LLM **propõe**; HITL em alto risco |
| Merge | Texto “não mergear” | `merge_pr` **bloqueado** até humano |
| Bugs | Sempre skill creator | `regression` vs `flaky` |
| ReAct | Implícito | Teto de iterações + trilha no handoff / HTML |

## Estrutura

```
modulo-8-exemplo-pratico-guardiao-familia-agents/
├── agents/           # prompts Cursor (+ qa-author/qa-gate)
├── langgraph_app/    # StateGraph (orquestração)
├── guardiao_mcp/     # MCP server sobre lib/*
├── crew/             # .env, requirements, output/ (runtime — não orquestra)
├── lib/              # gateway, hitl, handoff, react_policy, model_tier
├── evals/            # dataset estático + avaliadores (Fase D)
├── scripts/          # langgraph_run, gateway_cli, demo, …
├── skills/
├── templates/
└── docs/             # autonomia (fases + orquestracao), operacao, …
```

Board JSON continua no módulo 7 (não duplicado).

## Quick start

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents

# Pipeline LangGraph (dry_run)
python scripts/langgraph_run.py --task T-P05-006 --mode dry_run --from-zero

# Dry-run de evento via gateway
python scripts/gateway_cli.py --task T-P05-001 --event claim --dry-run

# MCP (Cursor)
python -m guardiao_mcp

# Eval regressão Kanban
python scripts/langsmith_eval.py
```

## Documentação

Índice: [docs/README.md](docs/README.md)

- [**Mapa didático de orquestração**](docs/autonomia/orquestracao/README.md) (HTML)
- [Estado atual — fluxo e processo](docs/autonomia/ESTADO_ATUAL_FLUXO_E_PROCESSO.md)
- [Configuração e tecnologia](docs/autonomia/CONFIGURACAO_E_TECNOLOGIA.md)
- [Guia LangGraph + MCP + LLM](docs/autonomia/GUIA_LANGGRAPH_MCP_LLM.md)
- [Fases A–D](docs/autonomia/fases/README.md)
- [Execução e observabilidade](docs/autonomia/EXECUCAO_E_OBSERVABILIDADE.md)
- [Operação / HITL](docs/operacao/PROCESSO_HITL.md)
- [Apresentação live](docs/apresentacao/APRESENTACAO_LIVE_DEMO.md)

## Dashboard ao vivo

> ### <a href="https://pedroaugustogti.github.io/pos-unipds-IA/modulo-8-exemplo-pratico-guardiao-familia-agents/docs/live/dashboard.html" target="_blank" rel="noopener noreferrer">Abrir dashboard live (GitHub Pages)</a>

```powershell
python scripts/live_server.py
# http://127.0.0.1:8765/dashboard.html
python scripts/publish_live_pages.py   # espelho docs/live
```

## Critérios de sucesso

- [x] Gateway + HITL + handoff + ReAct policy
- [x] LangGraph + OpenRouter + model_tier
- [x] MCP `guardiao_mcp` (porta única via gateway)
- [x] LangSmith tracing + dataset estático de regressão
- [x] Separação qa-author / qa-gate
- [x] Dashboard live / demo
