# evals — avaliação LangGraph

Datasets e runners de regressão do pipeline Kanban.

| Path | Uso |
|------|-----|
| `datasets/` | Casos esperados (sequência de Status) |
| (scripts) | `scripts/langgraph/langsmith_eval.py`, `eval_gate.py` |

## Decisões

- Falha de eval → não promover mudança de policy sem revisão
- Traces em LangSmith (`LANGCHAIN_PROJECT`)
