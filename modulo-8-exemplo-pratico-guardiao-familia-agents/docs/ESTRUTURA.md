# Estrutura do módulo 8

Paths canônicos: `lib/paths.py`. **Cada pasta tem `README.md`** com propósito, quando usar e links — ponto de entrada para agentes.

```text
modulo-8-exemplo-pratico-guardiao-familia-agents/
├── agents/
│   ├── 00-runtime/          requirements.txt + output/ (artefatos efêmeros)
│   ├── 00-orchestration/    LangGraph, MCP, evals, scripts/
│   ├── {role}/              agent.md + SKILL.md
│   ├── qa-gate/scripts/     CLIs Appium, E2E, RAG
│   └── skills/              legado (canônico: agents/{role}/)
├── board_automation/
│   ├── board/               pacote Python (task_router, board_client, …)
│   ├── data/maps/           TASK_AGENT_MAP*.csv
│   ├── data/imports/        JSON GitHub Project
│   ├── data/backlogs/       backlogs operacionais
│   ├── scripts/cli/         reconcile, classify, sync, outbox
│   ├── scripts/seeds/       seed Project 3, patch issues
│   ├── docs/                workflow, classificação, sandbox
│   └── templates/           issues, mobile flows, .github, workflows
├── lib/                     gateway, orchestrator, mobile, observability
├── docs/                    autonomia, operação, templates PR/review, live
├── certs/                   CA bundle TLS
└── .env.example             variáveis de ambiente (única referência)
```

## CLIs

| Área | Exemplo |
|------|---------|
| LangGraph | `agents/00-orchestration/scripts/langgraph/langgraph_run.py` |
| Gateway / worker | `agents/00-orchestration/scripts/cli/gateway_cli.py` |
| Board | `board_automation/scripts/cli/reconcile_board.py` |
| QA mobile | `agents/qa-gate/scripts/qa_mobile_evidence.py` |

## Runtime

`agents/00-runtime/output/` — recriado por `lib.paths.ensure_output_dirs()`. Não versionar.

Subpastas: `handoffs/`, `observability/`, `langgraph/`, `dispatch/`, `board/`, `mobile/`, `orchestrator/`, `audit/`, `demo/`.

## MCP (Cursor)

- Server: `guardiao-familia-agents` (`.cursor/mcp.json`)
- Launcher Windows: `agents/00-orchestration/guardiao_mcp/guardiao-mcp.cmd`
- Manual: `python -m guardiao_mcp` (com `agents/00-orchestration` no `PYTHONPATH`)
