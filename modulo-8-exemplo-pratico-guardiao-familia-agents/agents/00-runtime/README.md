# Runtime dos agentes

Ambiente Python e artefatos gerados em execução.

| Path | Função |
|------|--------|
| `requirements.txt` | Deps (LangGraph, MCP, OpenRouter, …) |
| [`output/`](output/) | Artefatos **por ticket** (`T-P*/`) — gitignored |
| [`system/`](system/) | Estado global (orquestrador, dispatch, audit, …) — gitignored |

## Decisões

- Instalar deps: `pip install -r agents/00-runtime/requirements.txt`
- Env: `.env` na raiz do módulo (`lib/env_load.py`)
- Paths: `lib/paths.py` — **nunca** hardcodar `output/` ou `system/` em código novo
- Orquestração vive em `agents/00-orchestration/`, não aqui

## output/

Somente pastas de ticket (`T-P{n}-{seq}/`). Handoff canônico: `{ticket}/handoff.json`. Evidências QA: `{ticket}/qa-gate-({N})/evidence/`.

## system/

Estado compartilhado: `orchestrator/`, `dispatch/`, `board/`, `audit/`, `observability/`, `mobile/guides/`, etc.

Criado por `lib.paths.ensure_output_dirs()`. Não versionar conteúdo de runs anteriores.
