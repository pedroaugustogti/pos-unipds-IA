# Exemplo 4 — Ollama (API local)

Scripts **`bash`** que conversam com o servidor **Ollama** em `http://localhost:11434`, usando o endpoint **compatível com OpenAI** (`/v1/chat/completions`).

## Pré-requisitos

- [Ollama](https://ollama.com/) instalado e em execução.
- `curl` e `jq` no PATH (Git Bash / WSL / Linux / macOS).

## Como rodar

```bash
chmod +x request.sh   # se necessário
./request.sh
```

O script exemplo faz `ollama pull` de um modelo e envia uma requisição de chat. Ajuste o nome do modelo e o prompt dentro do `request.sh` conforme necessário.

## O que observar

- Formato JSON da API e como reutilizar o mesmo padrão de clientes OpenAI apontando para Ollama.
