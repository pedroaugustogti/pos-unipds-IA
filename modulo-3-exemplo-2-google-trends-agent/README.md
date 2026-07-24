# Atividade: agente Google Trends com LangGraph

Este diretório é o **Módulo 3 — Exemplo 2** (`modulo-3-exemplo-2-google-trends-agent`) e demonstra como **transformar um serviço externo (SerpAPI / Google Trends) em tool** de um agente LangGraph.

## Objetivo da atividade (Pós)

1. Encapsular **Google Trends** como tool LangChain (`google_trends`)
2. Orquestrar pesquisa e resposta em grafo de dois nós: `researcher` → `responder`
3. Usar **structured outputs** (Zod) para extrair keywords e recomendar títulos de vídeo
4. Expor o agente via API HTTP (`POST /chat`)

## O que há nesta pasta

| Item | Papel |
|------|--------|
| `src/tools/googleTrendsTool.ts` | Tool que consulta SerpAPI |
| `src/graph/` | Nós `researcher` e `responder` |
| `src/services/serpApiService.ts` | Cliente SerpAPI |
| `src/prompts/v1/` | Prompts versionados (keywords, video trends) |
| `data/trendingData.ts` | Dados de apoio para testes |

## Pré-requisitos

- Node.js **24+**
- `.env` com `OPENROUTER_API_KEY` e `SERPAPI_API_KEY`
- Opcional: `LANGSMITH_API_KEY` para tracing

## Como realizar a atividade

```bash
npm install
cp .env.example .env
npm start              # http://localhost:3000
npm test
npm run langgraph:serve
```

### Exemplo de pergunta

```bash
curl -X POST http://localhost:3000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Estou pensando em criar um vídeo sobre Web AI, quais títulos você recomendaria?"}'
```

### Critérios de sucesso

- [ ] O agente invoca a tool `google_trends` quando analisa ideias de título
- [ ] A resposta usa dados reais de tendência (não inventa popularidade)
- [ ] Structured outputs validam keywords e sugestões
- [ ] Testes unitários e e2e passam

## Fluxo do grafo

```
Pergunta do usuário
        ↓
researcher (extrai keywords + chama google_trends)
        ↓
responder (monta recomendações de título/estratégia)
        ↓
Resposta JSON
```

## Relação com o Módulo 3

Antecede servidores MCP completos (Ex. 5–7): aqui o padrão é **serviço → tool → agente**. No Módulo 3, o MCP generaliza essa ideia para qualquer integração.
