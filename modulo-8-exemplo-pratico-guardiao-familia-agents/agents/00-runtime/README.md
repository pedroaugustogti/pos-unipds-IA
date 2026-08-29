# Runtime dos agentes

Ambiente Python e artefatos gerados em execução.

| Path | Função |
|------|--------|
| `requirements.txt` | Deps (LangGraph, MCP, OpenRouter, …) |
| [`output/`](output/) | Artefatos efêmeros (gitignored) |

## Decisões

- Instalar deps: `pip install -r agents/00-runtime/requirements.txt`
- Env: `.env` na raiz do módulo (`lib/env_load.py`)
- Paths: `lib/paths.py` — **nunca** hardcodar `output/` em código novo
- Orquestração vive em `agents/00-orchestration/`, não aqui

## output/

Recriado por `lib.paths.ensure_output_dirs()`. Subpastas: `handoffs/`, `observability/`, `langgraph/`, `dispatch/`, `board/`, `mobile/`, `orchestrator/`, `audit/`, `demo/`.

Não versionar conteúdo de runs anteriores.
