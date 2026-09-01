# MCP — Guardião Família (módulo 8)

Servidor: `guardiao_mcp` · **`list_mcp_tools`**

## Pipeline

```
orchestrator_enter_in_progress (opcional)
→ emit_status_event
→ on_status_event
→ hitl_guard_actuation
→ developer_implement | developer_review | qa_validate  (por fase)
→ execute_agent_actuation_tool
```

## Catálogo (14 tools)

| Grupo | Tools |
|-------|-------|
| gateway | `emit_status_event`, `list_status_events`, `on_status_event`, `hitl_guard_actuation`, `execute_agent_actuation_tool` |
| phase | `developer_implement`, `developer_review`, `qa_validate` |
| orchestrator | `orchestrator_enter_in_progress` |
| qa_mobile | `qa_db_seed`, `qa_db_cleanup`, `qa_appium_suite_parent`, `qa_appium_suite_child` |
| meta | `list_mcp_tools` |

`qa_validate` orquestra `qa_db_seed` → `qa_appium_suite_*` → `qa_db_cleanup` via MCP.

Guia por papel: [`MCP_ROLE_GUIDE.md`](MCP_ROLE_GUIDE.md)
