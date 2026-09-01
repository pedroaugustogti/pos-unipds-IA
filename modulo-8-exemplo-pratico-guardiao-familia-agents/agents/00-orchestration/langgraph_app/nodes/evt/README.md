# Nós evt_* — índice por classificação

Os 55 nós de evento são **gerados em runtime** por `nodes/factory.py` a partir de `registry/catalog.py`.

Este diretório agrupa os nós por **papel** para navegação no filesystem:

| Arquivo | Classificação | Conteúdo |
|---------|---------------|----------|
| `orchestrator.py` | orchestrator | `orchestrator_enter_in_progress` |
| `creator.py` | creator | `{role}_in_progress`, `_ready_for_code_review` |
| `reviewer.py` | reviewer | `{role}_in_code_review`, `_ready_for_test`, `_return_in_progress` |
| `qa_gate.py` | qa-gate | `qa-gate_in_test`, `_in_pull_request`, `_return_in_progress` |
| `ops.py` | ops | `{role}_done` |

Cada arquivo exporta `EVENTS` (specs completas) e `NODE_IDS`.

Para listar pipelines no terminal: `python scripts/langgraph/list_nodes.py`

Para alterar **qual** MCP tool roda em cada evento: edite `registry/pipelines.py`.
