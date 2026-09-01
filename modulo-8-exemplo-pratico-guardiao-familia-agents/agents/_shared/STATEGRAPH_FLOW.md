# StateGraph v2 — fluxo LangGraph

Código: `agents/00-orchestration/langgraph_app/` · catálogo: MCP `list_status_events` ou `registry/catalog.py`

## Diagrama

```mermaid
flowchart TD
    START([invoke]) --> sync_board --> orchestrator_decide
    orchestrator_decide --> evt["evt_* (55 eventos role-based)"]
    evt --> sync_board
    orchestrator_decide --> END_NODE([END])
    sync_board --> END_NODE
```

## Arquivos

| Caminho | Conteúdo |
|---------|----------|
| `registry/catalog.py` | `EVENT_REGISTRY` |
| `registry/pipelines.py` | Pipeline MCP por evento |
| `nodes/factory.py` | Factory `evt_*` |
| `graph.py` | Grafo v2 |

Detalhes: `agents/00-orchestration/docs/STATEGRAPH_FLOW.md`
