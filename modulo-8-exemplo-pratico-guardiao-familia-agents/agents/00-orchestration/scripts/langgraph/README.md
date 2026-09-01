# langgraph/

Scripts **v2** — invocam `langgraph_app.run_once`.

| Script | Uso |
|--------|-----|
| `langgraph_run.py` | Um ciclo completo por task (`--mode dry_run\|live`) |
| `list_nodes.py` | Catálogo dos 55 nós `evt_*` + pipeline MCP |
| `smoke_pipeline.py` | Smoke rápido do grafo |
| `langsmith_eval.py` | Regressão Kanban no LangSmith |
| `eval_gate.py` | Gate determinístico antes de approve (não é nó do grafo) |

Decisão: `dry_run` para banca; `live` só com tokens e HITL configurados.
