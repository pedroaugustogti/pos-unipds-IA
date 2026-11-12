# Mapa — Exemplo 6: RAG corretivo

> Capstone AI Researcher · síntese prática das aulas 1 (visão), 5 (corpus), 8–13 (grafo) e validação prod

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Automação: [`modulo-11-exemplo-pratico-automacao-capstone`](../../modulo-11-exemplo-pratico-automacao-capstone/)

## Aulas deste exemplo

### Aula R1 — Visão do RAG corretivo

Arquivo: [`AULA_R1_VISAO_RAG_CORRETIVO.md`](./AULA_R1_VISAO_RAG_CORRETIVO.md)

O que você deve sair sabendo:

- Definir RAG corretivo: retrieve → grade → (search + upsert) → answer.
- Diferenciar pergunta respondida só pelo corpus CVM vs. pergunta que exige web.
- Relacionar o pipeline de raciocínio da UI aos nós do LangGraph.

### Aula R2 — Corpus CVM, Vertex e seed

Arquivo: [`AULA_R2_CORPUS_VERTEX_SEED.md`](./AULA_R2_CORPUS_VERTEX_SEED.md)

O que você deve sair sabendo:

- Explicar a origem dos dados (`packages/corpus`, empresas B3, textos CVM).
- Gerar embeddings com **Vertex AI** e gravar no **pgvector** (HNSW).
- Rodar `collect` / `db:migrate` / `seed` com segurança de custo.

### Aula R3 — Grafo retrieve, grade, Serper e answer

Arquivo: [`AULA_R3_GRAFO_NOS.md`](./AULA_R3_GRAFO_NOS.md)

O que você deve sair sabendo:

- Implementar cada nó e a aresta condicional com limite de iterações.
- Usar Serper só para lacunas; TTL nos chunks web.
- Garantir citação + guardrail determinístico no answer.

### Aula R4 — Produção e validação

Arquivo: [`AULA_R4_PRODUCAO_VALIDACAO.md`](./AULA_R4_PRODUCAO_VALIDACAO.md)

O que você deve sair sabendo:

- Validar o RAG em Hosting/Cloud Run com evidências reais.
- Conferir traces Langfuse e métricas de tokens/custo.
- Fechar com `capstone:check` (itens de chat, guardrail, traces, custo).

## Relatórios

- Didático: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
- Materiais: [`../../materiais_aula/RELATORIO_MATERIAIS.md`](../../materiais_aula/RELATORIO_MATERIAIS.md)
