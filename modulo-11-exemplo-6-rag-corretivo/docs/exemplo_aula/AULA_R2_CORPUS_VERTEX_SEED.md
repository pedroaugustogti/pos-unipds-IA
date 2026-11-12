# Aula R2: Corpus CVM, Vertex e seed

> Exemplo 6 — RAG corretivo · Capstone AI Researcher

## Objetivos

- Montar o corpus a partir de fontes CVM / empresas B3.
- Usar Vertex AI para embeddings.
- Popular Postgres + pgvector com `seed`.

## Peças

| Item | Detalhe |
|------|---------|
| Pacote corpus | `packages/corpus` — `empresas.csv`, JSON por ticker (ABEV, VALE, PETR, …) |
| Collect | `pnpm collect` → `@hero/corpus` |
| Embeddings | `packages/agent/src/embeddings.ts` · Vertex |
| DB | `packages/agent/src/db/*` · extensão `vector` · índice HNSW |
| Seed | `pnpm seed` · `packages/agent/src/seed/` |
| Prompt oficial | `prompts_aula/aula-1.5-corpus-cvm.md`, `aula-2.1-pgvector-hnsw-e-seed.md` |

## Passo a passo (comandos)

```powershell
cd modulo-11-exemplo-pratico-automacao-capstone\workspace\capstone-project-ai-researcher

# 1) Docker Postgres (compose do Capstone; porta local típica 5434)
docker compose up -d

# 2) ADC / projeto para Vertex
gcloud auth application-default login
$env:GOOGLE_CLOUD_PROJECT = "ai-researcher-cap-pedro"
# Vertex AI API habilitada no projeto

# 3) .env com DATABASE_URL apontando para o Postgres local

# 4) Schema + embeddings
pnpm.cmd db:migrate
pnpm.cmd collect          # atualiza corpus se necessário
pnpm.cmd seed             # gera embeddings (custo Vertex) — ~80 docs na validação Pedro
```

## Cuidados

- Não versionar PDFs/binários enormes desnecessários; o repo já traz JSON estruturado.
- Seed consome cota Vertex — use `DEMO=true` só para testes de grafo sem embeddings reais.
- Em produção, a mesma migration/seed alimenta Cloud SQL (`ai-researcher-db`).

## Checkpoint

- [ ] Extensão `vector` ativa
- [ ] `seed` conclui sem erro
- [ ] Consulta similar retorna tickers conhecidos (ABEV/VALE…)
