# LangGraph v2 — motor de eventos · MCP centralizado

55 nós `evt_*` (factory em `event_nodes.py`) + `orchestrator_decide` + `sync_board`.

## Arquivos

| Arquivo | Função |
|---------|--------|
| `event_registry.py` | Catálogo + pipeline MCP por evento |
| `event_nodes.py` | Factory de nós + runner MCP (`_run_mcp_tool`) |
| `graph.py` | StateGraph v2 |
| `policy.py` | `suggested_event` / `status_after_event` |
| `llm.py` | LLM structured (fases implement/review) |
| `schemas.py` | Pydantic verdicts |
| `persist.py` / `tracing.py` | Observabilidade |

## Fluxo

```mermaid
flowchart TB
  START([START]) --> sync_board
  sync_board --> orchestrator_decide
  orchestrator_decide -->|evt_*| EVENT[55 nós de evento]
  orchestrator_decide -->|Done / erro| END_NODE([END])
  EVENT --> sync_board
```

Loop até **Done** ou `max_steps`.

## Executar

```bash
python scripts/langgraph/langgraph_run.py --task T-P3-009 --from-zero --mode dry_run
```
