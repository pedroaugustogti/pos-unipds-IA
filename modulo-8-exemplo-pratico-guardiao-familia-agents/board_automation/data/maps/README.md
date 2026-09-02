# maps — TASK_AGENT_MAP

| Arquivo | Uso |
|---------|-----|
| `TASK_AGENT_MAP.csv` | Mapa principal task → agent_role |
| `TASK_AGENT_MAP_FARGATE.csv` | Infra Fargate |
| `TASK_AGENT_MAP_P3.csv` | Project 3 sandbox |

Env: `GUARDAO_TASK_MAP_CSV` (default `TASK_AGENT_MAP.csv`).

Colunas-chave: `id`, `agent_role`, `agent_role_secondary`, `repo`, `track`, `status_baseline`.

Eventos board v2: [`../../agents/00-orchestration/docs/board/WORKFLOW_BOARD.md`](../../agents/00-orchestration/docs/board/WORKFLOW_BOARD.md)
