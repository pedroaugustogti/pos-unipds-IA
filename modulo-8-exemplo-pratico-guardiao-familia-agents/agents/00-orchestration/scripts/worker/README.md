# worker (removido)

Fila `worker_jobs` / dispatch Cursor foi substituída pelo pipeline MCP:

`orchestrator_enter_in_progress` → `on_status_event` → `hitl_guard_actuation` → `execute_agent_actuation_tool`
