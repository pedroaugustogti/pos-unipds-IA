# MCP Server — Guardião Família (v2)

Fachada MCP sobre `lib/*` — **14 tools**. Status **só** via `emit_status_event` (eventos role-based).

## Subir

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents
pip install "mcp>=1.0"
python -m guardiao_mcp
```

Launcher Windows: `agents/00-orchestration/guardiao_mcp/guardiao-mcp.cmd`.

## Cursor

- Monorepo: `.cursor/mcp.json` → server `guardiao-familia-agents`
- Módulo: `.cursor/mcp.json`

Reinicie o MCP após alterar o JSON.

## Catálogo

| Grupo | Tools |
|-------|-------|
| gateway | `emit_status_event`, `list_status_events`, `on_status_event`, `hitl_guard_actuation`, `execute_agent_actuation_tool` |
| phase | `developer_implement`, `developer_review`, `qa_validate` |
| orchestrator | `orchestrator_enter_in_progress` |
| qa_mobile | `qa_db_seed`, `qa_db_cleanup`, `qa_appium_suite_parent`, `qa_appium_suite_child` |
| meta | `list_mcp_tools` |

Documentação: [`agents/_shared/MCP_TOOLS.md`](../../_shared/MCP_TOOLS.md) · [`MCP_ROLE_GUIDE.md`](../../_shared/MCP_ROLE_GUIDE.md)

## Segurança

- Escritas com `dry_run=true` por padrão.
- `hitl_guard_actuation` obrigatório antes de `execute_agent_actuation_tool`.

## LangGraph v2

O grafo invoca estas tools via `lib/mcp_invoke` em cada nó `evt_*` (`event_registry.py`).
