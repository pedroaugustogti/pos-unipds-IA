# Orquestração — LangGraph v2

Pipeline LangGraph v2 (55 nós `evt_*`), MCP (14 tools), evals e CLIs.

## Subpastas

| Pasta | Quando usar |
|-------|-------------|
| [`docs/`](docs/) | **Base de conhecimento canônica** dos agentes (MCP, board, grafo, policy) |
| [`langgraph_app/`](langgraph_app/) | Grafo v2: `registry/`, `nodes/`, `graph.py` |
| [`guardiao_mcp/`](guardiao_mcp/) | Tools MCP para Cursor (`python -m guardiao_mcp`) |
| [`evals/`](evals/) | Regressão Kanban / LangSmith |
| [`schemas/`](schemas/) | Contrato JSON de eventos |
| [`scripts/`](scripts/) | CLIs operacionais + ops (`build_repo_knowledge`, `patch_agent_*`) |

Runtime: [`../00-runtime/output/`](../00-runtime/output/)

## Docs para agentes

Índice completo: [`docs/README.md`](docs/README.md)

```
docs/
  graph/       STATEGRAPH_FLOW, NODE_LOOP_SEQUENCE
  mcp/         MCP_TOOLS, MCP_ROLE_GUIDE
  board/       WORKFLOW_BOARD
  routing/     REPOS_AND_ROUTING
  knowledge/   REPO_KNOWLEDGE (gerado)
  policy/      ACTUATION_GUARDRAIL_POLICY
```

## Decisões

| Situação | Ação |
|----------|------|
| Rodar uma task ponta a ponta | `scripts/langgraph/langgraph_run.py` |
| Listar nós `evt_*` | `scripts/langgraph/list_nodes.py` |
| Smoke do pipeline | `scripts/langgraph/smoke_pipeline.py` |
| Emitir Status manual | `scripts/cli/gateway_cli.py` ou MCP |
| Estender tools MCP | `guardiao_mcp/tools/<nome>.py` |
| Alterar pipeline de um evento | `langgraph_app/registry/pipelines.py` |
| Regenerar base de conhecimento | `scripts/ops/build_repo_knowledge.py` |

Bootstrap: `bootstrap.py` ajusta `PYTHONPATH` para imports.
