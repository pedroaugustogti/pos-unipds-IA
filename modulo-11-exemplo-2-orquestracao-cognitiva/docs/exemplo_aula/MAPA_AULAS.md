# Mapa — Unidade 2: Orquestração Cognitiva e APIs

> Capstone AI Researcher · aulas 8-13

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher

## Aulas desta unidade

### Aula 8 — pgvector, seed

Arquivo: [`AULA_08_PGVECTOR_SEED.md`](./AULA_08_PGVECTOR_SEED.md)

O que você deve sair sabendo:

- Explicar como embeddings, proximidade vetorial e top-k permitem encontrar os documentos que respondem a uma pergunta.
- Descrever o papel do índice HNSW no pgvector e a sua principal característica: a busca rápida, porém aproximada.
- Criar a tabela vetorial com migration e popular o banco com um script de seed que gera os embeddings em lotes.

### Aula 9 — Os nós retrieve e grade

Arquivo: [`AULA_09_RETRIEVE_GRADE.md`](./AULA_09_RETRIEVE_GRADE.md)

O que você deve sair sabendo:

- Construir o nó retrieve, que transforma a pergunta em embedding e busca no Postgres os documentos mais similares.
- Justificar por que padrões de projeto, como a inversão de dependência, continuam importantes quando quem escreve o código é um agente.
- Construir o nó grade, que usa saída estruturada da LLM e uma regra explícita para julgar se o contexto recuperado é suficiente.

### Aula 10 — Serper

Arquivo: [`AULA_10_SERPER.md`](./AULA_10_SERPER.md)

O que você deve sair sabendo:

- Explicar por que o agente precisa de um provedor de busca na web e por que o Serper foi o escolhido.
- Criar a interface SearchProvider com o padrão adapter, para poder trocar de fornecedor sem grandes mudanças.
- Testar o provedor de busca com respostas falsas, sem consumir a cota do serviço de terceiro.

### Aula 11 — Fallback pra busca web, upsert retroativo

Arquivo: [`AULA_11_FALLBACK_UPSERT.md`](./AULA_11_FALLBACK_UPSERT.md)

O que você deve sair sabendo:

- Construir o nó de busca na web, que pesquisa apenas os aspectos que faltam, extrai o texto das páginas e grava os chunks com embedding.
- Explicar por que a informação vinda da web recebe um prazo de validade (TTL) e a informação da CVM não.
- Descrever como o retrieve passa a combinar os documentos da CVM e os da web, fazendo o agente se retroalimentar.

### Aula 12 — O grafo real: aresta condicional e o guard do

Arquivo: [`AULA_12_GRAFO_GUARD.md`](./AULA_12_GRAFO_GUARD.md)

O que você deve sair sabendo:

- Montar o grafo do agente com LangGraph, ligando os nós retrieve, grade e web search.
- Explicar a aresta condicional que sai do grade e o limite de iterações que impede o loop infinito.
- Relacionar a simplicidade do grafo ao princípio de responsabilidade única aplicado a cada nó.

### Aula 13 — O nó answer, citação obrigatória, guardrail por

Arquivo: [`AULA_13_ANSWER_SSE.md`](./AULA_13_ANSWER_SSE.md)

O que você deve sair sabendo:

- Construir o nó answer, que monta a resposta final com base no contexto, com citação de fonte e data-base.
- Explicar por que o guardrail não pode depender só do system prompt e como um filtro determinístico, com expressão regular, garante a regra.
- Expor o grafo em um endpoint POST que transmite a execução por Server-Sent Events, inclusive no Cloud Run.

## Relatórios

- Didático da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
- Materiais (PDF/slides): [`../../materiais_aula/RELATORIO_MATERIAIS.md`](../../materiais_aula/RELATORIO_MATERIAIS.md)
