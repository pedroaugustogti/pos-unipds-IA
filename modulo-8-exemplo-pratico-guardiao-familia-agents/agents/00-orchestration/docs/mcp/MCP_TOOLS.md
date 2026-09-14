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

## Catálogo (13 tools)

| Grupo | Tools |
|-------|-------|
| gateway | `emit_status_event`, `list_status_events`, `on_status_event`, `hitl_guard_actuation`, `execute_agent_actuation_tool` |
| phase | `developer_implement`, `developer_review`, `qa_validate` |
| orchestrator | `orchestrator_enter_in_progress` |
| qa_mobile | `qa_init_suite_mobile`, `qa_pipeline_evidence`, `qa_generate_evidence` |
| meta | `list_mcp_tools` |

`qa_validate` tem dois caminhos (`worker_mode`): **`local`** = workers na máquina host (sem container); **`docker`** = 1 container por `ticket.qa.scenarios`. Paralelo; PASS só se **todos** ok. Sem fallback entre caminhos.

**Por cenário (interno):** `qa_init_suite_mobile` (`apps_ready_ok`, Metro + fingerprint git) → `qa_pipeline_evidence` (`device`, `reload_mode=hard` se bundle stale/dirty) → `qa_generate_evidence` (seed + Appium + PNG/MP4). Estado Metro: `agents/00-runtime/system/mobile/metro_bundle_state.json`.

Guia por papel: [`MCP_ROLE_GUIDE.md`](MCP_ROLE_GUIDE.md) · código: [`../../../../lib/mobile/README.md`](../../../../lib/mobile/README.md)
