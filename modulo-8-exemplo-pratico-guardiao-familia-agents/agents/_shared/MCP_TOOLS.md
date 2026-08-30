# MCP — Guardião Família (módulo 8)

Servidor: `guardiao_mcp` · namespace Cursor: `guardiao-familia-agents`  
Descobrir catálogo: **`list_mcp_tools`**  
Prompts LLM (descrições por tool): `agents/00-orchestration/guardiao_mcp/tool_prompts.py`

## Regras gerais

- **Status do board:** só via `emit_status_event` (porta única). Não invente status nem use CLI direto se o MCP estiver disponível.
- **Escritas:** `dry_run=true` por padrão — confirme payload e use `dry_run=false` para aplicar.
- **Merge:** `merge_pr` exige `approve_hitl` humano antes de `dry_run=false`.
- **Handoff:** `get_handoff` / `write_handoff_tool` em `agents/00-runtime/output/handoffs/{task_id}.json`.
- **ReAct:** registre voltas com `append_task_action_tool`.

## Catálogo por grupo

| Grupo | Tools | Escrita |
|-------|-------|---------|
| gateway | `emit_status_event`, `list_hitl_queue`, `approve_hitl` | sim |
| board | `load_tasks_tool`, `pick_task_tool` | não |
| handoff | `get_handoff`, `write_handoff_tool` | write |
| history | `append_task_action_tool` | sim |
| observability | `snapshot_observability` | opcional HTML |
| orchestrator | `list_idle_agents_tool`, `resolve_agent_for_board_event`, `drain_dispatch_queue`, `mark_agent_idle` | parcial |
| model | `select_model_tier` | não |
| mobile_rag | `query_mobile_flow_rag`, `ingest_mobile_flow_rag` | ingest |
| qa_mobile | `qa_db_seed`, `qa_db_cleanup`, `qa_appium_suite_parent`, `qa_appium_suite_child` | sim |
| dispatch | `dispatch_job_tool` | flag `GUARDIAO_MCP_ALLOW_DISPATCH` |
| meta | `list_mcp_tools` | não |

## Eventos `emit_status_event` (principais)

| Evento | Status alvo | Quem usa |
|--------|-------------|----------|
| `claim` | In Progress | creators |
| `open_pr` | Ready for Code Review | creators |
| `start_review` | In Code Review | reviewers |
| `approve_review` | Ready for Test | reviewers |
| `request_changes` | In Progress | reviewers |
| `resubmit_review` | In Code Review | creators (pós-correção) |
| `start_test` | In Test | qa-gate |
| `test_passed` | In Pull Request | qa-gate |
| `test_failed_bug` | In Progress | qa-gate |
| `merge_pr` | Done | devops-cicd / stores-release (+ HITL) |

## Por papel

| Papel | Tools prioritárias |
|-------|-------------------|
| creators (backend, frontend-*, cloud-infra, database, devops-cicd, stores-release, qa-author) | `pick_task_tool`, `emit_status_event`, `get_handoff`, `write_handoff_tool`, `append_task_action_tool` |
| reviewers | `get_handoff`, `emit_status_event` (`start_review` / `approve_review` / `request_changes`), `append_task_action_tool` |
| frontend-mobile | + `query_mobile_flow_rag` antes de codar |
| qa-author | + `query_mobile_flow_rag`; manutenção RAG: `ingest_mobile_flow_rag` |
| qa-gate | + `qa_db_seed`, `qa_appium_suite_*`, `qa_db_cleanup`, `query_mobile_flow_rag` |
| devops-cicd / stores-release (merge) | `emit_status_event` (`merge_pr`), `list_hitl_queue`, `approve_hitl` |
| orchestrator / supervisor | `load_tasks_tool`, `snapshot_observability`, `drain_dispatch_queue`, `resolve_agent_for_board_event` |

## QA mobile (qa-gate)

```
qa_db_seed(task_id, dry_run=false)
qa_appium_suite_child(from_db_seed=true, task_id=..., dry_run=false)
# capturar evidências / screenshots
qa_db_cleanup(task_id, dry_run=false)
```

Fallback CLI: `agents/qa-gate/scripts/` e `python agents/00-orchestration/scripts/cli/gateway_cli.py` quando MCP indisponível.
