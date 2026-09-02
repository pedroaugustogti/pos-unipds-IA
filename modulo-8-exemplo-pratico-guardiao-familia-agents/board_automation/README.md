# Board automation

GitHub Project, roteamento de tasks, templates de issue e sincronização de status — integrado ao **LangGraph v2** e gateway MCP.

## Quando usar esta pasta

| Necessidade | Onde ir |
|-------------|---------|
| Roteamento task → agente | `data/maps/TASK_AGENT_MAP.csv` + [`../agents/00-orchestration/docs/routing/REPOS_AND_ROUTING.md`](../agents/00-orchestration/docs/routing/REPOS_AND_ROUTING.md) |
| Reconciliar CSV ↔ Project | `scripts/cli/reconcile_board.py` |
| Gerar body de issue | `board/issue_task_body.py` + `templates/` |
| Colunas, eventos v2, papéis | [`../agents/00-orchestration/docs/board/WORKFLOW_BOARD.md`](../agents/00-orchestration/docs/board/WORKFLOW_BOARD.md) · MCP `list_status_events` |
| Máquina de estados / catálogo | `board/task_status_workflow.py` · [`../agents/00-orchestration/docs/graph/STATEGRAPH_FLOW.md`](../agents/00-orchestration/docs/graph/STATEGRAPH_FLOW.md) |
| Emitir evento (porta única) | `python agents/00-orchestration/scripts/cli/gateway_cli.py emit --task T-XXX --event backend_ready_for_code_review` |
| Seed sandbox | `scripts/seeds/` |

**Eventos:** só nomes role-based v2 (`{role}_{status_slug}`). Nomes v1 (`claim`, `open_pr`, `merge_pr`, …) são **rejeitados** pelo gateway — ver `lib/gateway/v2_events.py`.

## Subpastas

| Pasta | README |
|-------|--------|
| `board/` | Pacote Python |
| `data/` | CSV, imports, backlogs |
| `scripts/` | CLIs operador (`cli/`, `seeds/`) |
| `docs/` | Workflow e classificação |
| `templates/` | Issues, mobile flow, GitHub YAML |

Cache: `agents/00-runtime/system/board/`

Import: `from board_automation.board.task_router import load_tasks`
