# Orquestração — LangGraph v2

Pipeline LangGraph v2 (55 nós `evt_*`), MCP (14 tools), evals e CLIs.

## Subpastas

| Pasta | Quando usar |
|-------|-------------|
| [`langgraph_app/`](langgraph_app/) | Grafo v2: `registry/`, `nodes/`, `graph.py` |
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
| Listar nós `evt_*` | `scripts/langgraph/list_nodes.py` |
| Smoke do pipeline | `scripts/langgraph/smoke_pipeline.py` |
| Emitir Status manual | `scripts/cli/gateway_cli.py` ou MCP |
| Estender tools MCP | `guardiao_mcp/tools/<nome>.py` |
| Alterar pipeline de um evento | `langgraph_app/registry/pipelines.py` |

Bootstrap: `bootstrap.py` ajusta `PYTHONPATH` para imports.
