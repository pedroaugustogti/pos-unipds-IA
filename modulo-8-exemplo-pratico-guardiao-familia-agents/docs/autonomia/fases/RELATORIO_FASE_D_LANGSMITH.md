# Relatório — Fase D: LangSmith (observabilidade + evals)

> Data: 2026-08-25  
> Status: **Concluída (P0 + D4/D5)** · D6 opcional · orquestração **somente LangGraph**  
> Base: [GUIA_LANGGRAPH_MCP_LLM.md](../GUIA_LANGGRAPH_MCP_LLM.md) §5  
> Pré-requisitos: [A](RELATORIO_FASE_A_MODEL_TIER.md) · [B](RELATORIO_FASE_B_MCP.md) · [C](RELATORIO_FASE_C_LANGGRAPH.md)

---

## 0. Progresso

### P0 (D1–D3)

| ID | Item | Status |
|----|------|--------|
| D1 | Tracing no entrypoint + fail-soft | OK — `langgraph_app/tracing.py` + `run_once` |
| D2 | Spans `claim` / `open_pr` / `review` / `qa` / `hitl` / `merge` | OK — `pipeline_span` nos nós |
| D3 | Metadata `task_id`, `mode`, `dry_run`, tags | OK — `build_invoke_config` |
| Dep | `langsmith>=0.1` em `requirements.txt` | OK |
| Testes | `tests/test_langsmith_tracing.py` | OK (5) |

### D4–D5

| ID | Item | Status |
|----|------|--------|
| D4 | Dataset estático `evals/datasets/kanban_pipeline.json` | OK — 10 cases (v1.3; exemplo LangGraph live T-P13-011) |
| D5 | Avaliadores + `scripts/langsmith_eval.py` | OK — 7 evaluators |
| Testes | `tests/test_evals_kanban.py` | OK |
| Validação | 8/8 local + `happy_sos_006` com LangGraph | OK |

---

## 1. Objetivo

Instrumentar o grafo LangGraph (Fase C) com **tracing LangSmith**, metadata por run (`task_id`, modelo, mode) e um **dataset estático de regressão** (não memória vetorial) com avaliadores de política Kanban — sem substituir o dashboard Project #2 / HTML ReAct da banca.

| Camada | Papel |
|--------|--------|
| `observability/` + HTML task | Didático / banca (Status, ReAct, tokens locais) |
| LangSmith | Engenheiro: latência por nó, cadeia LLM→tool, compare runs, evals |

---

## 2. Dependências

### Já disponível

| Item | Onde |
|------|------|
| Grafo + CLI | `langgraph_app/`, `scripts/langgraph_run.py` |
| Tokens locais | HTML task + `token_usage` |
| Env / TLS | `crew/.env`, `env_load`, `certs/` |
| Tracing P0 | `langgraph_app/tracing.py` |

### Lacunas restantes (D4–D6)

Dataset/evals versionados; export opcional para `workflow.jsonl`; spans MCP remotos (opcional).

### Pacotes

```text
langsmith>=0.1   # pinado na D P0
```

---

## 3. Escopo D1–D6

| ID | Entrega | Prioridade | Status |
|----|---------|------------|--------|
| **D1** | Tracing entrypoint fail-soft | P0 | Feito |
| **D2** | Spans pipeline | P0 | Feito |
| **D3** | Metadata run | P0 | Feito |
| **D4** | Dataset **estático** de regressão (5–10 cases) | P1 | Feito (8) |
| **D5** | Avaliadores | P1 | Feito |
| **D6** | Export opcional | P2 | Pendente |

---

## 3.1 Decisão D4 — dataset estático (não memória vetorial)

### Perguntas levantadas

| # | Questão | Resposta na Fase D |
|---|---------|-------------------|
| Q1 | O dataset será **dinâmico** via **Postgres vetorial**? | **Não.** Fora do escopo D. |
| Q2 | Haverá **memória curta** iterativa + **memória longa** para melhorar acertividade? | **Não** nesta fase. STM/LTM / RAG seria fase futura à parte. |
| Q3 | O dataset “aprende” e acumula embeddings ao longo dos runs? | **Não.** Cases versionados no repo (JSON) e/ou upload LangSmith; expected fixo. |
| Q4 | Seguimos com o quê então? | **Dataset de regressão estático** + avaliadores de policy Kanban (D4 + D5). |

### O que o dataset D4 é

Mede se o grafo **respeita o Kanban e as regras de autonomia**, não a qualidade literária do LLM.

**Inclusão**

- Tasks piloto do Project #2 (espelho local), preferir `T-P05-005` / `T-P05-006` etc.
- Ground truth: sequência Status + eventos canônicos (`policy.py`).
- Mode explícito (maioria `dry_run`; HITL só se o case for `live`).
- Diversidade mínima: happy path → Done; hint SOS/`model_tier` high; `noop`/Done; falha controlada (evento inválido / `max_steps`) para D5.

**Exclusão**

- Dependência de Cursor dispatch / PR GitHub real para “passar”.
- Expected baseado em prosa livre do LLM.
- Postgres, pgvector, embeddings, memória de agente.

**Campos típicos por case**

| Campo | Uso |
|--------|-----|
| `task_id`, `title`, `agent_role` | input |
| `mode` | dry_run / demo / live |
| `expected_status_sequence` | Status ordenados |
| `expected_events` | eventos canônicos |
| `expected_final_status` | em geral Done |
| `expected_model_tier` / `expected_hitl` | opcionais |
| `max_steps` | teto para avaliador |

**Avaliadores (D5) ligados ao dataset**

- Evento fora de `EVENT_TARGET`?
- Sequência ≠ expected?
- Em live, pulou HITL no merge?
- `steps` > `max_steps`?

### Fora de escopo (possível fase futura)

Postgres + vetores, STM iterativa, LTM, RAG para “acertividade” do agente — **não substitui** o dataset de eval da D; planejar à parte se necessário.

---

## 4. Impacto (resumo)

Kanban/gateway inalterados; HTML da banca intacto; overhead de rede no export de traces; fail-soft sem key ou com tracing off.

---

## 5. Validação

```powershell
python -m unittest tests.test_langsmith_tracing tests.test_langgraph_decisions -v
python scripts/langgraph_run.py --task T-P05-006 --mode dry_run --from-zero
```

| ID | Esperado | P0 |
|----|----------|----|
| **V1** | Done + `langsmith.enabled` | OK |
| **V2** | metadata `task_id` / spans nomeados | OK |
| **V3** | tokens UI vs local | Manual |
| **V4–V7** | dataset / demo / live | Pendente |
| **V8** | sem key → grafo segue | OK (unit) |

Evidências: projeto `guardiao-familia-agents`; run `guardiao-kanban:T-P05-006`; spans `claim`, `open_pr`, `review`, `qa`, `implement`, `hitl`, `merge`.

---

## 6. Próximo

**D6** (opcional/P2) — export de falhas de eval para `workflow.jsonl`. Upload LangSmith UI do dataset é opcional (eval local já cobre).

Validar:

```powershell
python scripts/langsmith_eval.py
python scripts/langsmith_eval.py --with-graph --case happy_sos_006
```

---

## 7. Checklist de saída da fase

- [x] `langsmith` pinado
- [x] Tracing + fail-soft
- [x] Metadata `task_id` + mode
- [x] Spans nomeados
- [x] Decisão documentada: dataset estático (não memória vetorial)
- [x] Dataset ≥ 5 cases (JSON / LangSmith)
- [x] ≥ 2 avaliadores
- [x] V1–V2
- [x] V4–V5 (dataset + fixtures)
- [ ] V6 ou V7 (opcional)
- [ ] D6 export
- [x] Dashboard HTML da banca intacto
