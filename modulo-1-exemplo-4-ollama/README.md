# Atividade: LLM local com Ollama

Este diretório é o **Módulo 1 — Exemplo 4** (`modulo-1-exemplo-4-ollama`) e demonstra chamadas à API **Ollama** em `http://localhost:11434` (compatível com OpenAI).

## Objetivo da atividade (Pós)

1. Subir modelo local com Ollama
2. Enviar chat completion via `curl` + JSON
3. Comparar com clientes OpenAI (mesmo formato de mensagens)

## Pré-requisitos

- [Ollama](https://ollama.com/) instalado e em execução
- `curl` e `jq` (Git Bash / WSL / Linux / macOS)

## Como realizar a atividade

```bash
chmod +x request.sh   # se necessário
./request.sh
```

Ajuste modelo e prompt em `request.sh`.

### Critérios de sucesso

- [ ] Ollama responde em `/v1/chat/completions`
- [ ] Você troca o modelo no script com sucesso
- [ ] Entende como reutilizar o padrão em SDKs OpenAI

## Relação com o Módulo 1

Primeiro contato com **LLM em produção local** — base para OpenRouter (Ex. 5) e RAG (Ex. 7).
