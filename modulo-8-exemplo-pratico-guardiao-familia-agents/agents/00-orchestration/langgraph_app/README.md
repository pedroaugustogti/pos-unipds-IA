# langgraph_app — StateGraph

Orquestração Kanban: claim → context → decide → implement → review → QA → CI → HITL → apply.

| Módulo | Função |
|--------|--------|
| `policy.py` | Evento canônico por Status do board |
| `nodes.py` | Nós do grafo (route, implement, review, qa, hitl) |
| `ci_nodes.py` | Integração sinais CI |
| `llm.py` | OpenRouter via `lib.core.model_tier` |
| `tools_bridge.py` | Chama libs sem MCP remoto |
| `schemas.py` | Tipos de estado |

## Quando usar

- Executar pipeline de uma task: `scripts/langgraph/langgraph_run.py`
- Estender fluxo: adicionar nó + aresta em `nodes.py`, respeitar gateway

## Quando NÃO usar

- Escrever Status direto no GitHub Project
- Substituir dispatch Cursor para código de produto

CLI: `python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task T-XXX --mode dry_run`
