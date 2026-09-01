# StateGraph v2 — fluxo LangGraph

Código: `agents/00-orchestration/langgraph_app/` · catálogo: `list_status_events` / `event_registry.py`

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

| Arquivo | Conteúdo |
|---------|----------|
| `event_registry.py` | Pipeline MCP por evento |
| `event_nodes.py` | Factory de nós |
| `graph.py` | Grafo v2 |
| `state.py` | `PipelineState` |

Detalhes: `agents/00-orchestration/docs/STATEGRAPH_FLOW.md`
