# Exemplo real — Capstone · RAG corretivo

Guia operacional do **RAG corretivo** do AI Researcher (síntese U1 corpus + U2 grafo + validação prod).

**Referência:** [exemplo-pratico](../../../modulo-11-exemplo-pratico-automacao-capstone/)  
**Evidências:** `02-u2-rag-pipeline/` · `03-u3-…` · `05-u5-…` · `06-check-11-11/`  
**Teoria:** [`../exemplo_aula/MAPA_AULAS.md`](../exemplo_aula/MAPA_AULAS.md)

---

## O que esta etapa entrega

Loop LangGraph em `packages/agent`:

1. **retrieve** — embedding Vertex + top-k pgvector (CVM + web TTL)  
2. **grade** — julga se o contexto basta  
3. **webSearch** (se insuficiente) — Serper → upsert embedding  
4. **answer** — citação + guardrail em código + SSE  

---

## Pré-requisitos

| Tipo | Item |
|------|------|
| Runtime | Node ≥ 24, pnpm 11, Docker Desktop |
| GCP / Vertex | Projeto, Vertex AI API, ADC ([`gcloud_env.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/gcloud_env.ps1)) |
| Dados | Postgres + extensão `vector` |
| Keys | `SERPER_API_KEY` (ou `DEMO=true`) |
| Repo | `workspace/capstone-project-ai-researcher` |

---

## Ferramentas

| Camada | Arquivo / script |
|--------|------------------|
| Embeddings | [`embeddings.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/embeddings.ts) |
| Seed | [`seed/`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/seed/) |
| Migrate | [`migrate.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/db/migrate.ts) |
| Schema | [`schema.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/db/schema.ts) |
| Retrieve | [`retrieve.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/nodes/retrieve.ts) |
| Grade | [`grade.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/nodes/grade.ts) |
| Web search | [`web-search.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/nodes/web-search.ts) |
| Serper | [`serper.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/search/serper.ts) |
| Resiliência | [`resilient-search-provider.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/search/resilient-search-provider.ts) |
| Upsert web | [`upsert-web-document.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/db/upsert-web-document.ts) |
| Answer | [`answer.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/nodes/answer.ts) |
| Grafo | [`graph.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/graph.ts) |
| Stack local | [`up_local.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/up_local.ps1) |
| Evidências aula | [`run_evidencias_capstone.py`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/run_evidencias_capstone.py) |
| Aceite prod | [`capstone-check.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/capstone-check.ts) |

---

## Scripts e comandos

| Comando / script | Abrir |
|------------------|--------|
| Auth helper | [`gcloud_env.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/gcloud_env.ps1) |
| Stack local | [`up_local.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/up_local.ps1) |
| Evidências | [`run_evidencias_capstone.py`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/run_evidencias_capstone.py) |
| `pnpm db:migrate` | [`migrate.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/db/migrate.ts) |
| `pnpm seed` | [`seed/`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/seed/) |
| `pnpm capstone:check` | [`capstone-check.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/capstone-check.ts) |

```powershell
cd modulo-11-exemplo-pratico-automacao-capstone
. .\scripts\gcloud_env.ps1
gcloud auth application-default login

cd workspace\capstone-project-ai-researcher
docker compose up -d
pnpm.cmd install --frozen-lockfile
pnpm.cmd db:migrate
pnpm.cmd collect
pnpm.cmd seed
pnpm.cmd --filter @hero/agent test
pnpm.cmd dev

pnpm.cmd capstone:check --url https://ai-researcher-api-xsjfcd5t3a-uc.a.run.app
```

Alternativa stack: [`up_local.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/up_local.ps1).  
Regenerar evidências: [`run_evidencias_capstone.py`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/run_evidencias_capstone.py).

---

## Ações

1. Subir Postgres + `vector` ([`up_local.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/up_local.ps1) ou compose).  
2. ADC / Vertex ([`gcloud_env.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/gcloud_env.ps1)).  
3. `migrate` → `collect` → `seed` ([`embeddings.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/embeddings.ts)).  
4. Testar nós; `pnpm dev`.  
5. Smoke quantitativo + qualitativo + guardrail.  
6. Aceite: [`capstone-check.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/capstone-check.ts).

---

## Validação de funcionamento

| Cenário | Evidência |
|---------|-----------|
| ABEV + pipeline | `02-u2-rag-pipeline/` |
| Guardrail | `03-u3-resiliencia-guardrails/` |
| Traces / custo | `05-u5-observabilidade/` |
| SCORE 11/11 | [`capstone-check.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/capstone-check.ts) → `06-check-11-11/` |

### Critérios

- [x] Corpus + Vertex + pgvector  
- [x] Grafo corretivo em produção  
- [x] Search condicional + guardrail  
- [x] Observabilidade dos nós  
