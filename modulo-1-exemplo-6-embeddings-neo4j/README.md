# Atividade: embeddings e busca vetorial no Neo4j

Este diretório é o **Módulo 1 — Exemplo 6** (`modulo-1-exemplo-6-embeddings-neo4j`) e implementa **indexação e recuperação semântica** sem LLM de resposta.

## Objetivo da atividade (Pós)

1. Extrair chunks de um **PDF**
2. Gerar **embeddings** localmente (Transformers.js)
3. Persistir vetores no **Neo4j**
4. Executar **similarity search** e interpretar scores

## Pré-requisitos

- Docker: `npm run infra:up` (Neo4j)
- `.env` com `NEO4J_*` e `EMBEDDING_MODEL`

## Como realizar a atividade

```bash
npm install
npm run infra:up
npm start
```

### Critérios de sucesso

- [ ] Chunks indexados no Neo4j
- [ ] Busca retorna trechos relevantes no console
- [ ] Você explica papel do índice vetorial e do score

## Relação com o Módulo 1

Prepara o **RAG** do Exemplo 7 (retrieve + generate).
