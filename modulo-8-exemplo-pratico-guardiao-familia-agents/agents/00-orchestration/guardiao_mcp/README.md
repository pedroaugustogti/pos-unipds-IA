# MCP Server — Guardião Família (v2)

Fachada MCP sobre `lib/*` — **12 tools**. Status **só** via `emit_status_event` (eventos role-based).

## Estrutura do pacote

```
guardiao_mcp/
├── server.py              # FastMCP + register_all (entry in-process)
├── instructions.py        # SERVER_INSTRUCTIONS (prompt global do servidor)
├── contract.py            # ok / fail / wrap_call
├── _helpers.py            # helpers compartilhados (ex: task_by_id)
├── __main__.py            # python -m guardiao_mcp
├── guardiao-mcp.cmd       # launcher Windows (Cursor)
└── tools/                 # uma tool por arquivo
    ├── __init__.py        # register_all + reexport das funções
    ├── emit_status_event.py
    ├── list_status_events.py
    ├── on_status_event.py
    ├── hitl_guard_actuation.py
    ├── execute_agent_actuation_tool.py
    ├── orchestrator_enter_in_progress.py
    ├── developer_implement.py
    ├── developer_review.py
    ├── qa_validate.py
    ├── qa_init_suite_mobile.py
    ├── qa_pipeline_evidence.py
    ├── qa_generate_evidence.py
    └── list_mcp_tools.py
```

Cada arquivo em `tools/` contém:

| Elemento | Função |
|----------|--------|
| `DESCRIPTION` | Prompt da tool (exibido à LLM) |
| `<nome>()` | Implementação (delega para `lib/*`) |
| `register(mcp)` | Registro no FastMCP |

## Grupos

| Grupo | Tools |
|-------|-------|
| gateway | `emit_status_event`, `list_status_events`, `on_status_event`, `hitl_guard_actuation`, `execute_agent_actuation_tool` |
| phase | `developer_implement`, `developer_review`, `qa_validate` |
| orchestrator | `orchestrator_enter_in_progress` |
| qa_mobile | `qa_init_suite_mobile`, `qa_pipeline_evidence`, `qa_generate_evidence` |
| meta | `list_mcp_tools` |

Docs: `agents/00-orchestration/docs/mcp/`
