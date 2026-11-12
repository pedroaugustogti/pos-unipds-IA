# Relatório Didático — Orquestração Cognitiva e APIs

> Aula `modulo-11-exemplo-2-orquestracao-cognitiva`  
> Capstone AI Researcher · aulas 8-13

## Objetivo da unidade

Construir o cérebro do agente: pgvector/seed, nós retrieve e grade, Serper, fallback com upsert, aresta condicional com guard de loop e answer com citação + SSE.

## Percurso das aulas

| Aula | Arquivo | Síntese |
|------|---------|---------|
| 8 | [`AULA_08_PGVECTOR_SEED.md`](./AULA_08_PGVECTOR_SEED.md) | Explicar como embeddings, proximidade vetorial e top-k permitem encontrar os documentos que respondem a uma pergunta. |
| 9 | [`AULA_09_RETRIEVE_GRADE.md`](./AULA_09_RETRIEVE_GRADE.md) | Construir o nó retrieve, que transforma a pergunta em embedding e busca no Postgres os documentos mais similares. |
| 10 | [`AULA_10_SERPER.md`](./AULA_10_SERPER.md) | Explicar por que o agente precisa de um provedor de busca na web e por que o Serper foi o escolhido. |
| 11 | [`AULA_11_FALLBACK_UPSERT.md`](./AULA_11_FALLBACK_UPSERT.md) | Construir o nó de busca na web, que pesquisa apenas os aspectos que faltam, extrai o texto das páginas e grava os chunks com embedding. |
| 12 | [`AULA_12_GRAFO_GUARD.md`](./AULA_12_GRAFO_GUARD.md) | Montar o grafo do agente com LangGraph, ligando os nós retrieve, grade e web search. |
| 13 | [`AULA_13_ANSWER_SSE.md`](./AULA_13_ANSWER_SSE.md) | Construir o nó answer, que monta a resposta final com base no contexto, com citação de fonte e data-base. |

## Caso permanente

O **AI Researcher** busca na base vetorial (CVM), julga se o contexto basta, recorre à web quando não basta e responde com **citação** (fonte + data-base). Nunca recomenda compra ou venda — a restrição vive no **código**, não só no system prompt.

## Como estudar

1. Abrir [`MAPA_AULAS.md`](./MAPA_AULAS.md) e ler a aula na ordem.
2. Conferir slides/roteiro em [`../../materiais_aula/RELATORIO_MATERIAIS.md`](../../materiais_aula/RELATORIO_MATERIAIS.md).
3. Reproduzir no [seed](https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed) ou no [projeto completo](https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher).
4. Anotar a ponte Guardião em [`../exemplo_real/01-guardiao/aplicacao.md`](../exemplo_real/01-guardiao/aplicacao.md).

## Checkpoint da unidade

- [ ] Explicar o objetivo da Unidade 2 em duas frases
- [ ] Completar o checkpoint de cada aula 8-13
- [ ] Relacionar ao menos um conceito ao Guardião Família
