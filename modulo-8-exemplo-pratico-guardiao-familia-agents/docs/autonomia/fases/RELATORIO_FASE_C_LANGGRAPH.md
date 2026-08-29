# Relatório — Fase C: LangGraph + OpenRouter

> Data: 2026-08-25  
> Status: **Concluída (MVP)** · orquestração **LangGraph**  
> Pré-requisitos: [Fase A](RELATORIO_FASE_A_MODEL_TIER.md) · [Fase B](RELATORIO_FASE_B_MCP.md)

---

## 1. Objetivo (atingido)

OpenRouter no loop de orquestração para decidir/resumir passos do Kanban; Status via gateway (demo/live) ou simulação (dry_run); código via Cursor/demo; HITL no merge em mode `live`.

---

## 2. Entregáveis

| Path | Função |
|------|--------|
| `langgraph_app/policy.py` | Evento canônico por Status |
| `langgraph_app/nodes.py` | route, context, decide, implement, review, qa, hitl, apply |
| `langgraph_app/graph.py` | StateGraph com loop até Done |
| `langgraph_app/llm.py` | ChatOpenAI + `select_model` |
| `langgraph_app/tools_bridge.py` | Gateway/MCP |
| `langgraph_app/persist.py` | `agents/00-runtime/output/langgraph/{task}.json` |
| `agents/00-orchestration/scripts/langgraph/langgraph_run.py` | CLI `--from-zero` / `--mode` |

### Env

```env
GUARDIAO_ORCHESTRATOR=langgraph
GUARDIAO_LANGGRAPH_MODE=dry_run
GUARDIAO_LANGGRAPH_MAX_STEPS=40
OPENAI_API_KEY=...
OPENAI_API_BASE=https://openrouter.ai/api/v1
GUARDIAO_LLM_DEFAULT=openai/gpt-4o-mini
GUARDIAO_LLM_HIGH=x-ai/grok-4.3
LANGSMITH_API_KEY=...
```

### Pipeline

```text
Todo -> claim -> In Progress -> implement/open_pr
 -> review -> Ready for Test -> qa -> In Pull Request
 -> merge_pr -> Done
```

---

## 3. Modes

| Mode | Comportamento |
|------|----------------|
| `dry_run` | LLM + simula Status (não grava board) |
| `demo` | Emite gateway; merge com `force_hitl_approved` |
| `live` | Emite gateway; merge pode ficar `hitl_pending` |

---

## 4. Validar

```powershell
python -m unittest tests.test_langgraph_decisions -v
python agents/00-orchestration/scripts/langgraph/langgraph_run.py --task T-P05-006 --mode dry_run --from-zero
```

---

## 5. Próximo

**Fase D — LangSmith** datasets/evals (tracing já pode estar ativo).
