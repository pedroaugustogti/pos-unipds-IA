# Aula R4: Produção e validação do RAG

> Exemplo 6 — RAG corretivo · Capstone AI Researcher

## Objetivos

- Validar o RAG corretivo em Hosting + Cloud Run.
- Cruzar UI, Langfuse e métricas.
- Usar `capstone:check` como aceite.

## Ambientes

| Camada | URL / recurso |
|--------|----------------|
| Web | https://ai-researcher-cap-pedro.web.app |
| API | https://ai-researcher-api-xsjfcd5t3a-uc.a.run.app |
| Health | `GET /api/health` |
| Metrics | `GET /api/metrics` |
| Langfuse | cloud.langfuse.com · projeto My Project |
| Evidências | `evidencias/validacao-prod-2026-11-12/02-u2-rag-pipeline/` |

## Passo a passo

### 1. Smoke UI

1. Abrir Hosting  
2. Perguntar sobre ABEV (quantitativo)  
3. Capturar Retrieve + resposta + chips  
4. Nova conversa → pergunta de recomendação → recusa  

### 2. Observabilidade do grafo

- Langfuse Tracing: spans `retrieve`, `grade`, `answer`, `webSearch`, generations Vertex  
- `/api/metrics`: `llm_tokens_total`, `llm_cost_usd_total` por nó  

### 3. Check automatizado

```powershell
cd modulo-11-exemplo-pratico-automacao-capstone\workspace\capstone-project-ai-researcher
# carregar .env (LANGFUSE_*, GRAFANA_*, GOOGLE_CLOUD_PROJECT_ID)
pnpm.cmd capstone:check --url https://ai-researcher-api-xsjfcd5t3a-uc.a.run.app
```

Itens ligados ao RAG: **5** degradação, **6** traces, **9** custo, **10** guardrail (além de health/deploy).

### 4. Scripts de apoio (exemplo-pratico)

```powershell
cd modulo-11-exemplo-pratico-automacao-capstone
powershell -File .\scripts\up_local.ps1
python .\scripts\run_evidencias_capstone.py
```

## Checkpoint

- [ ] Evidências U2 (pipeline + resposta) arquivadas
- [ ] Check ≥ itens RAG verdes / ideal 11/11
