# POS — Engenharia de IA Aplicada

Repositório com **exemplos práticos** usados na pós-graduação: modelos em JavaScript/TypeScript, integração com APIs de LLM, embeddings, grafo **Neo4j** e **RAG** (Retrieval-Augmented Generation).

## Estrutura

| Pasta | Tema resumido |
|--------|----------------|
| [`exemplo-1-training-model`](./exemplo-1-training-model/) | Treino/uso de modelo com **TensorFlow.js** no Node. |
| [`exemplo-2- e-commerce`](./exemplo-2-%20e-commerce/) | **Recomendação** em e-commerce com TensorFlow.js e front estático. |
| [`exemplo-3-duck game`](./exemplo-3-duck%20game/) | Jogo estilo Duck Hunt com uso de **ML** (já possui README próprio). |
| [`exemplo-4-ollama`](./exemplo-4-ollama/) | Chamadas **HTTP** ao servidor local **Ollama** (API compatível com OpenAI). |
| [`exemplo-5-open router`](./exemplo-5-open%20router/) | Chamadas à API **OpenRouter** via `curl` e variáveis de ambiente. |
| [`exemplo-6-embeddings-neo4j`](./exemplo-6-embeddings-neo4j/) | **Embeddings** locais (Transformers.js), indexação no **Neo4j** e busca por similaridade. |
| [`exemplo-7-embeddings-rag-neo4j`](./exemplo-7-embeddings-rag-neo4j/) | **RAG** completo: Neo4j + LangChain + prompts em arquivo + LLM via OpenRouter. |

## Requisitos gerais

- **Node.js** 22+ nos exemplos em TS/JS (ver `engines` em cada `package.json` quando existir).
- **Docker** onde houver `docker-compose` (Neo4j nos exemplos 6 e 7).
- Chaves e URLs em **`.env`** (não versionados); copie de `.env.example` quando existir.

## Autor / contexto

Exemplos derivados de material de curso (vários com base em conteúdo do **Erick Wendel** nos projetos Node/LangChain). Ajustes e extensões: **Pedro Augusto**.
