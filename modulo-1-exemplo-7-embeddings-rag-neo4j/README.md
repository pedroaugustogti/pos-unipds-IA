# Atividade: RAG com Neo4j e OpenRouter

Este diretório é o **Módulo 1 — Exemplo 7** (`modulo-1-exemplo-7-embeddings-rag-neo4j`) e implementa **RAG end-to-end**: retrieve no grafo + geração com LLM.

## Objetivo da atividade (Pós)

1. Reutilizar pipeline de embeddings (PDF, chunks, Neo4j)
2. Montar **RunnableSequence** LangChain: retrieve → prompt → LLM
3. Versionar prompts em `prompts/` e salvar respostas em `respostas/`
4. Aplicar limiar de score na classe `AI`

## Pré-requisitos

- Neo4j (Docker) e `.env` com `NEO4J_*`, `EMBEDDING_MODEL`, `OPENROUTER_API_KEY`, `NLP_MODEL`

## Como realizar a atividade

```bash
npm install
npm run infra:up
npm start
```

### Critérios de sucesso

- [ ] Pergunta retorna resposta fundamentada no contexto recuperado
- [ ] Separação clara entre etapa **retrieve** e **generate**
- [ ] Prompts editáveis sem alterar código TypeScript

## O que observar

- Separação entre **retrieve** (vetor + Neo4j) e **generate** (LLM com contexto injetado).
- Arquivos em `prompts/` para versionar persona, instruções e template.

## Relação com o Módulo 1

Culmina o módulo com **RAG** — conceito retomado no Módulo 2 (agentes) e Módulo 3 (MCP com contexto externo).
