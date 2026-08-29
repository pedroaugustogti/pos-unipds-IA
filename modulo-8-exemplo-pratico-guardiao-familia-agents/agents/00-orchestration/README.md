# Orquestração

Pipeline LangGraph, MCP, evals e CLIs do módulo 8.

## Subpastas

| Pasta | Quando usar |
|-------|-------------|
| [`langgraph_app/`](langgraph_app/) | Alterar nós, policy, LLM do grafo |
| [`guardiao_mcp/`](guardiao_mcp/) | Tools MCP para Cursor (`python -m guardiao_mcp`) |
| [`evals/`](evals/) | Regressão Kanban / LangSmith |
| [`schemas/`](schemas/) | Contrato JSON de eventos |
| [`scripts/`](scripts/) | CLIs operacionais |
| [`docs/`](docs/) | Docs técnicas do grafo |

Runtime: [`../00-runtime/output/`](../00-runtime/output/)

## Decisões

| Situação | Ação |
|----------|------|
| Rodar uma task ponta a ponta | `scripts/langgraph/langgraph_run.py` |
| Emitir Status manual | `scripts/cli/gateway_cli.py` ou MCP |
| Demo banca | `scripts/demo/demo_apresentacao.py` |
| Estender tools | `guardiao_mcp/server.py` + `lib/*` |

Bootstrap: `bootstrap.py` ajusta `PYTHONPATH` para imports.
