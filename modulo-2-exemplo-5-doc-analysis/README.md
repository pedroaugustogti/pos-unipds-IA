# Atividade: Q&A multimodal em PDF

Este diretório é o **Módulo 2 — Exemplo 5** (`modulo-2-exemplo-5-doc-analysis`) e implementa um pipeline de **perguntas e respostas sobre documentos PDF** com LangGraph e modelo de visão.

## Objetivo da atividade (Pós)

1. Receber PDF + pergunta via API HTTP (**Fastify**)
2. Enviar o documento como **base64** para um LLM multimodal (OpenRouter)
3. Orquestrar o fluxo com **LangGraph** (nó de geração de resposta)
4. Interpretar respostas fundamentadas no conteúdo visual do PDF

## O que há nesta pasta

| Item | Papel |
|------|--------|
| `src/server.ts` | API `POST /chat` (upload multipart) |
| `src/graph/` | Grafo LangGraph com nó `answerGeneration` |
| `docs/` | PDF de exemplo para teste local |
| `langgraph.json` | Configuração do LangGraph Studio |

## Pré-requisitos

- Node.js **24+**
- `.env` com `OPENROUTER_API_KEY` e modelo multimodal compatível

## Como realizar a atividade

```bash
npm install
cp .env.example .env   # se existir
npm start              # sobe servidor em http://localhost:4000
npm test
npm run langgraph:serve
```

### Teste manual com curl

```bash
curl -X POST \
  -F "file=@docs/a-comprehensive-overview-of-large-language-models.pdf" \
  -F "question=Descreva o tema principal deste documento" \
  http://localhost:4000/chat
```

### Critérios de sucesso

- [ ] Servidor responde em `POST /chat` com JSON contendo `answer`
- [ ] A resposta reflete o conteúdo do PDF enviado
- [ ] Você identifica onde o PDF vira `documentBase64` no estado do grafo
- [ ] Testes passam

## Fluxo da atividade

```
PDF + pergunta (HTTP)
        ↓
Fastify multipart → estado LangGraph
        ↓
LLM multimodal (visão + texto)
        ↓
Resposta JSON
```

## Referência técnica

- Artigo de referência sobre LLMs: [A Comprehensive Overview of Large Language Models](https://arxiv.org/pdf/2307.06435) (PDF incluído em `docs/`)

## Relação com o Módulo 2

Fecha o módulo com **análise de documentos** — combina API, grafo e modelo multimodal, preparando integrações externas no Módulo 3 (MCP).
