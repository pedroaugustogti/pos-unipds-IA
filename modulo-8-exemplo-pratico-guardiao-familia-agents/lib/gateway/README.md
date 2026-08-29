# gateway — porta única de Status

| Módulo | Função |
|--------|--------|
| `gateway.py` | `emit_status_event` — **única** escrita de Status |
| `handoff.py` | JSON handoff entre nós/agentes |
| `hitl_gates.py` | Fila HITL, merge bloqueado |
| `event_schema.py` | Validação de eventos |

Regra: LangGraph, MCP e CLIs **devem** passar por aqui.
