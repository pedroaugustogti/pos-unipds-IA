# Exemplo 6 — Embeddings + Neo4j (sem LLM de resposta)

Pipeline **LangChain** + **Neo4j Vector Store**:

1. Lê um **PDF** e gera chunks de texto.
2. Gera **embeddings** localmente (**Transformers.js** / HuggingFace).
3. Grava vetores no **Neo4j**.
4. Executa **busca por similaridade** e exibe os trechos no console.

Não há geração de resposta com LLM — foco é **indexação** e **recuperação**.

## Pré-requisitos

- Docker: `npm run infra:up` (sobe Neo4j).
- `.env` com `NEO4J_*` e `EMBEDDING_MODEL`.

## Como rodar

```bash
npm install
npm run infra:up
npm start
```

## O que observar

- Papel do índice vetorial no Neo4j e do `similaritySearch` / scores.
