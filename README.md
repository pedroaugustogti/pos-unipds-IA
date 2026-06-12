# POS — Engenharia de IA Aplicada

Repositório com **exemplos práticos** usados na pós-graduação: modelos em JavaScript/TypeScript, integração com APIs de LLM, **LangGraph**, embeddings, grafo **Neo4j** e **RAG** (Retrieval-Augmented Generation).

## Estrutura

### Módulo 1 — Fundamentos de IA e LLMs

| Pasta | Tema resumido |
|--------|----------------|
| [`modulo-1-exemplo-1-training-model`](./modulo-1-exemplo-1-training-model/) | Treino/uso de modelo com **TensorFlow.js** no Node. |
| [`modulo-1-exemplo-2- e-commerce`](./modulo-1-exemplo-2-%20e-commerce/) | **Recomendação** em e-commerce com TensorFlow.js e front estático. |
| [`modulo-1-exemplo-3-duck game`](./modulo-1-exemplo-3-duck%20game/) | Jogo estilo Duck Hunt com uso de **ML** (já possui README próprio). |
| [`modulo-1-exemplo-4-ollama`](./modulo-1-exemplo-4-ollama/) | Chamadas **HTTP** ao servidor local **Ollama** (API compatível com OpenAI). |
| [`modulo-1-exemplo-5-open router`](./modulo-1-exemplo-5-open%20router/) | Chamadas à API **OpenRouter** via `curl` e variáveis de ambiente. |
| [`modulo-1-exemplo-6-embeddings-neo4j`](./modulo-1-exemplo-6-embeddings-neo4j/) | **Embeddings** locais (Transformers.js), indexação no **Neo4j** e busca por similaridade. |
| [`modulo-1-exemplo-7-embeddings-rag-neo4j`](./modulo-1-exemplo-7-embeddings-rag-neo4j/) | **RAG** completo: Neo4j + LangChain + prompts em arquivo + LLM via OpenRouter. |

### Módulo 2 — LangGraph e agentes

| Pasta | Tema resumido |
|--------|----------------|
| [`modulo-2-exemplo-1-langgraph-medical-appointment`](./modulo-2-exemplo-1-langgraph-medical-appointment/) | Agente **LangGraph** para agendamento médico (roteamento de intenções, tools e fluxo multi-nó). |
| [`modulo-2-exemplo-2-song-highlights`](./modulo-2-exemplo-2-song-highlights/) | Recomendação musical com **memória persistente** (LangGraph + Postgres). |
| [`modulo-2-exemplo-3-safe-guard`](./modulo-2-exemplo-3-safe-guard/) | Demo de **prompt injection** e **guardrails** com controle de acesso por perfil. |
| [`modulo-2-exemplo-4-neo4j-students`](./modulo-2-exemplo-4-neo4j-students/) | **Text-to-Cypher** com LangGraph: planejamento de consultas, execução no Neo4j e resposta analítica. |

## Requisitos gerais

- **Node.js** 22+ nos exemplos em TS/JS (ver `engines` em cada `package.json` quando existir).
- **Docker** onde houver `docker-compose` (Neo4j nos exemplos 6 e 7 do módulo 1; Neo4j e Postgres no módulo 2).
- Chaves e URLs em **`.env`** (não versionados); copie de `.env.example` quando existir.
- **LangGraph Studio** (`npm run langgraph:serve`) nos projetos do módulo 2.

## Autor / contexto

Exemplos derivados de material de curso (vários com base em conteúdo do **Erick Wendel** nos projetos Node/LangChain). Ajustes e extensões: **Pedro Augusto**.
