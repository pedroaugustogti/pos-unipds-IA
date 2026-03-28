# Exemplo 7 — RAG com Neo4j + OpenRouter

Extensão do exemplo 6 com **RAG end-to-end**:

- Mesma base: PDF + imagem (chunks), embeddings locais, **Neo4j**.
- **LangChain** `RunnableSequence`: recuperação vetorial → prompt (`template.txt` + `answerPrompt.json`) → **ChatOpenAI** apontando para **OpenRouter** (`NLP_MODEL` no `.env`).
- Classe **`AI`**: limiar de score, logs didáticos, gravação de respostas em **`./respostas/`** (configurável em `config.ts` → `CONFIG.output`).

## Pré-requisitos

- Neo4j (Docker) e `.env` com `NEO4J_*`, `EMBEDDING_MODEL`, `OPENROUTER_API_KEY`, `NLP_MODEL`, etc.

## Como rodar

```bash
npm install
npm run infra:up
npm start
```

## O que observar

- Separação entre **retrieve** (só vetor + Neo4j) e **generate** (LLM com contexto injetado).
- Arquivos em `prompts/` para versionar persona, instruções e template.
