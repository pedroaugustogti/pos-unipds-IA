# gateway — porta única de Status (v2 role-based)

| Módulo | Função |
|--------|--------|
| `gateway.py` | `emit_status_event` — **única** escrita de Status |
| `v2_events.py` | Rejeição de legado + predicados semânticos v2 |
| `event_schema.py` | Validação de payload |
| `handoff.py` | JSON handoff entre nós/agentes |
| `hitl_gates.py` | Fila HITL, merge bloqueado |

**Formato v2:** `{agent_role}_{status_slug}` ou `{agent_role}_return_{status_slug}`.

Eventos legados (`claim`, `open_pr`, `start_test`, …) são **rejeitados** na entrada.

LangGraph, MCP e CLIs devem passar por aqui.
