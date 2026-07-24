# Atividade: API OpenRouter com curl

Este diretório é o **Módulo 1 — Exemplo 5** (`modulo-1-exemplo-5-open router`) e demonstra chamadas **HTTPS** à API de chat da **OpenRouter**.

## Objetivo da atividade (Pós)

1. Autenticar com `OPENROUTER_API_KEY`
2. Montar payload `messages` no formato OpenAI
3. Trocar modelos via variável `NLP_MODEL`

## Pré-requisitos

- `.env` com `OPENROUTER_API_KEY`
- `curl` e `jq`

## Como realizar a atividade

```bash
source .env   # ou exporte no PowerShell / WSL
bash request.sh
```

### Critérios de sucesso

- [ ] Resposta JSON válida da API
- [ ] Modelo alterado com sucesso
- [ ] Cabeçalhos opcionais (`HTTP-Referer`, `X-Title`) compreendidos

## Relação com o Módulo 1

Ponte para **LLMs na nuvem** — usado nos Módulos 2 e 3 (LangGraph, RAG, agentes).
