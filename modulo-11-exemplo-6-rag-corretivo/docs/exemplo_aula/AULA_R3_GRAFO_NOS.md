# Aula R3: Grafo — retrieve, grade, Serper, answer

> Exemplo 6 — RAG corretivo · Capstone AI Researcher

## Objetivos

- Ligar os nós no LangGraph com aresta condicional.
- Integrar Serper só nas lacunas.
- Fechar answer com citação + guardrail.

## Artefatos de código

| Nó / peça | Arquivo |
|-----------|---------|
| Grafo | `packages/agent/src/graph.ts` |
| Deps / DI | `graph-deps.ts` |
| Retrieve | `nodes/retrieve.ts` · `db/retrieve-similar.ts` |
| Grade | `nodes/grade.ts` · `prompts/grade.ts` |
| Web search | `nodes/web-search.ts` · `search/serper.ts` |
| Upsert web | `db/upsert-web-document.ts` (TTL) |
| Answer | `nodes/answer.ts` · `answer/format-resposta.ts` |
| Resiliência search | `search/resilient-search-provider.ts` |
| Prompts aula | `aula-2.2` … `aula-2.6` |

## Passo a passo

### 1. Env de busca

```powershell
# .env
# SERPER_API_KEY=...
# DEMO=true   # opcional: fakes
```

### 2. Testes unitários dos nós

```powershell
pnpm.cmd --filter @hero/agent test
```

### 3. Subir API e exercitar o grafo

```powershell
pnpm.cmd dev
# POST /api/chat  { "question": "Qual a receita líquida da Ambev no último trimestre disponível?" }
# Observar eventos SSE: retrieve → grade → answer
```

### 4. Forçar caminho web

Pergunta qualitativa / fato recente → grade insuficiente → `webSearch` → upsert → nova retrieve.

### 5. Guardrail

Pergunta de compra/venda → filtro determinístico; resposta de recusa (validado em prod).

## Checkpoint

- [ ] Aresta condicional + max iterações entendidos
- [ ] Serper isolado atrás de `SearchProvider`
- [ ] Answer sempre cita quando há docs
