# board — pacote Python

API de domínio do GitHub Project e roteamento de tasks.

| Módulo | Função |
|--------|--------|
| `task_router.py` | `load_tasks`, `pick_task` por agent_role |
| `board_client.py` | GitHub Project API |
| `task_status_workflow.py` | Máquina de estados |
| `issue_task_body.py` | Gera body de issue a partir do template |
| `reviewer_pairs.py` | Creator ↔ reviewer |
| `task_action_history.py` | Trilha ReAct |
| `local_board.py` | Board offline/dry-run |
| `infra_policy.py` | Regras track infraestrutura |

Import: `from board_automation.board.task_router import load_tasks`

Cache runtime: `agents/00-runtime/system/board/`
