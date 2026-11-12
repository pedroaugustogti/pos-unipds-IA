# Exemplo real — Capstone · Orquestração cognitiva (U2)

Etapa Capstone das **aulas 8–13**: RAG corretivo (retrieve → grade → search → answer) com pgvector, Vertex, Serper e SSE.

**Referência:** [exemplo-pratico](../../../modulo-11-exemplo-pratico-automacao-capstone/) · Evidências: `02-u2-rag-pipeline/`  
**Detalhe RAG:** [`../../../modulo-11-exemplo-6-rag-corretivo/docs/exemplo_real/`](../../../modulo-11-exemplo-6-rag-corretivo/docs/exemplo_real/)  
**Teoria:** [`../exemplo_aula/MAPA_AULAS.md`](../exemplo_aula/MAPA_AULAS.md)

```
pergunta → retrieve → grade ──suficiente──► answer → SSE
                 └──insuficiente──► webSearch → upsert → retrieve (iter)
```

---

## Pré-requisitos

| Tipo | Item |
|------|------|
| U1 | Stack Capstone clonada; Docker; `.env` com `DATABASE_URL` |
| Vertex | ADC + Vertex AI API + `GOOGLE_CLOUD_PROJECT` (ex. `ai-researcher-cap-pedro`) |
| Busca | `SERPER_API_KEY` (ou `DEMO=true` para fakes) |
| Pacotes | `packages/agent`, `packages/corpus` |
| Extensão | Postgres com `vector` (pgvector) |

---

## Ferramentas e artefatos

| Peça | Onde |
|------|------|
| Embeddings Vertex | [`embeddings.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/embeddings.ts) |
| Migrate / schema HNSW | [`migrate.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/db/migrate.ts), [`schema.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/db/schema.ts) |
| Retrieve | [`retrieve.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/nodes/retrieve.ts) · [`retrieve-similar.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/db/retrieve-similar.ts) |
| Grade | [`grade.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/nodes/grade.ts) |
| Serper | [`serper.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/search/serper.ts) |
| Web + upsert | [`web-search.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/nodes/web-search.ts) · [`upsert-web-document.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/db/upsert-web-document.ts) |
| Grafo | [`graph.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/graph.ts) |
| Answer | [`answer.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/nodes/answer.ts) |
| Stack local | [`up_local.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/up_local.ps1) |
| Aceite prod | [`capstone-check.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/capstone-check.ts) |

---

## Scripts e comandos

| Script / comando | Arquivo |
|------------------|---------|
| `pnpm db:migrate` | [`migrate.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/db/migrate.ts) |
| `pnpm collect` | pacote `packages/corpus` |
| `pnpm seed` | pasta [`seed/`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/packages/agent/src/seed/) |
| Stack local | [`up_local.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/up_local.ps1) |
| `pnpm capstone:check` | [`capstone-check.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/capstone-check.ts) |

```powershell
cd modulo-11-exemplo-pratico-automacao-capstone\workspace\capstone-project-ai-researcher

docker compose up -d
pnpm.cmd install --frozen-lockfile
pnpm.cmd db:migrate
pnpm.cmd collect
pnpm.cmd seed
pnpm.cmd --filter @hero/agent test
pnpm.cmd dev

cd ..\..
powershell -File .\scripts\up_local.ps1
```

---

## Ações

1. Garantir Postgres + extensão `vector`.
2. Preencher `.env` (DB, GCP/Vertex, Serper).
3. `migrate` → `collect` → `seed` (Vertex).
4. Testes do agent; subir `dev` (ou [`up_local.ps1`](../../../modulo-11-exemplo-pratico-automacao-capstone/scripts/up_local.ps1)).
5. Smoke quantitativo (ABEV) e qualitativo (Search).
6. Confirmar SSE / painel de nós no frontend.

---

## Validação de funcionamento

**Produção:** https://ai-researcher-cap-pedro.web.app — ABEV → Retrieve → Answer + chips.

Evidências: `01-pipeline-retrieve.png`, `02-chat-abev-resposta.png`.

```powershell
cd workspace\capstone-project-ai-researcher
pnpm.cmd capstone:check --url https://ai-researcher-api-xsjfcd5t3a-uc.a.run.app
```

Script: [`capstone-check.ts`](../../../modulo-11-exemplo-pratico-automacao-capstone/workspace/capstone-project-ai-researcher/scripts/capstone-check.ts).

### Critérios

- [x] Seed Vertex ok  
- [x] Grafo corretivo em prod  
- [x] SSE / pipeline visível  
