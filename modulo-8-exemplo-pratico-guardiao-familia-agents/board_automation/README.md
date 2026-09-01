# Board automation

GitHub Project, roteamento de tasks, templates de issue e sincronização de status.

## Quando usar esta pasta

| Necessidade | Onde ir |
|-------------|---------|
| Saber qual agente pega a task | `data/maps/TASK_AGENT_MAP.csv` |
| Reconciliar CSV ↔ Project | `scripts/cli/reconcile_board.py` |
| Gerar body de issue | `board/issue_task_body.py` + `templates/` |
| Entender colunas/eventos | [`../agents/_shared/WORKFLOW_BOARD.md`](../agents/_shared/WORKFLOW_BOARD.md) |
| Seed sandbox | `scripts/seeds/` |

## Subpastas

| Pasta | README |
|-------|--------|
| `board/` | Pacote Python |
| `data/` | CSV, imports, backlogs |
| `scripts/` | CLIs operador |
| `docs/` | Workflow e classificação |
| `templates/` | Issues, mobile flow, GitHub YAML |
| `schemas/` | `board_events.json` |

Cache: `agents/00-runtime/system/board/`

Import: `from board_automation.board.task_router import load_tasks`
