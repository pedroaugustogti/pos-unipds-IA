# langgraph/

| Script | Uso |
|--------|-----|
| `langgraph_run.py` | Um ciclo completo por task (`--mode dry_run\|live`) |
| `langsmith_eval.py` | Regressão Kanban no LangSmith |
| `eval_gate.py` | Gate antes de approve automático |
| `smoke_pipeline.py` | Smoke rápido do grafo |

Decisão: `dry_run` para banca; `live` só com tokens e HITL configurados.
