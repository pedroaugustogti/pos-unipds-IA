# Exemplo 5 — OpenRouter (`curl`)

Demonstra chamada **HTTPS** à API de chat da **OpenRouter** (`/api/v1/chat/completions`) com **`curl`**, cabeçalhos opcionais (`HTTP-Referer`, `X-Title`) e corpo JSON.

## Pré-requisitos

- Arquivo **`.env`** na mesma pasta com `OPENROUTER_API_KEY`.
- `curl` e `jq`.

## Como rodar

```bash
source .env   # ou exporte a variável manualmente no Windows
bash request.sh
```

No **PowerShell**, carregue a chave e execute o `curl` equivalente, ou use WSL/Git Bash para rodar o script como está.

## O que observar

- Troca de modelo via variável `NLP_MODEL`.
- Estrutura `messages` igual à API OpenAI, roteada pelo OpenRouter.
