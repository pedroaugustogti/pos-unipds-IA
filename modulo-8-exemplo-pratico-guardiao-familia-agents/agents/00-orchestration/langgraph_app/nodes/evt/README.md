# Nós evt_* — índice por classificação

Os 55 nós de evento são **gerados em runtime** por `nodes/factory.py` a partir de `registry/catalog.py`.

Este diretório agrupa os nós por **papel** para navegação no filesystem:

| Arquivo | Classificação | Conteúdo |
|---------|---------------|----------|
| `orchestrator.py` | orchestrator | claim Todo, emit todo |
| `creator.py` | creator | implement, open PR, resubmit |
| `reviewer.py` | reviewer | start/approve/request review |
| `qa_gate.py` | qa-gate | start test, pass/fail, PR |
| `ops.py` | ops | merge, release, done |

Cada arquivo exporta `EVENTS` (specs completas) e `NODE_IDS`.

Para listar pipelines no terminal: `python scripts/langgraph/list_nodes.py`

Para alterar **qual** MCP tool roda em cada evento: edite `registry/pipelines.py`.
