# MCP Server — Guardião Família (v2)

Fachada MCP sobre `lib/*` — **14 tools**. Status **só** via `emit_status_event` (eventos role-based).

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
    ├── _qa_appium_scenarios.py
    ├── emit_status_event.py
    ├── list_status_events.py
    ├── on_status_event.py
    ├── hitl_guard_actuation.py
    ├── execute_agent_actuation_tool.py
    ├── orchestrator_enter_in_progress.py
    ├── developer_implement.py
    ├── developer_review.py
    ├── qa_validate.py
    ├── qa_db_seed.py
    ├── qa_db_cleanup.py
    ├── qa_appium_suite_parent.py
    ├── qa_appium_suite_child.py
    └── list_mcp_tools.py
```

Cada arquivo em `tools/` contém:

| Elemento | Função |
|----------|--------|
| `DESCRIPTION` | Prompt da tool (exibido à LLM) |
| `<nome>()` | Implementação (delega para `lib/*`) |
| `register(mcp)` | Registro no FastMCP |

## Editar ou adicionar uma tool

1. Abra `tools/<nome>.py` — altere `DESCRIPTION` e/ou a função.
2. Lógica de negócio fica em `lib/*`; o arquivo da tool é só fachada MCP.
3. Nova tool: crie `tools/nova_tool.py`, adicione o nome em `_TOOL_MODULES` (`tools/__init__.py`) e em `TOOL_CATALOG` (`tools/list_mcp_tools.py`).
4. Reinicie o servidor MCP no Cursor após mudanças.

Prompt global do servidor (regras cross-tool): `instructions.py`.

## Subir

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents
pip install "mcp>=1.0"
$env:PYTHONPATH = "agents\00-orchestration;$PWD"
python -m guardiao_mcp
```

Launcher Windows: `agents/00-orchestration/guardiao_mcp/guardiao-mcp.cmd` (já configura `PYTHONPATH`).

Validação rápida:

```powershell
python -c "from guardiao_mcp.server import list_mcp_tools; import json; print(json.loads(list_mcp_tools())['result']['count'])"
# esperado: 14
```

## Cursor

- Monorepo: `.cursor/mcp.json` → server `guardiao-familia-agents`
- Módulo: `.cursor/mcp.json`

Reinicie o MCP após alterar o JSON ou qualquer arquivo em `tools/`.

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

O grafo invoca estas tools in-process via `lib/mcp_invoke` → `guardiao_mcp.server` em cada nó `evt_*` (`langgraph_app/registry/`).
