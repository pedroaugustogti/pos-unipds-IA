# Guardião — aplicação do Ex.4

> Unidade: **Frontend** (aulas 18-21)

No Guardião a UI (backoffice/parent) mostra estado do ticket e nunca esconde o HITL. Disclaimer e E2E cobrem o fluxo antes de merge/deploy.

| Origem (Capstone) | Destino (Guardião / M8) |
|-------------------|-------------------------|
| AI Researcher | Gateway MCP + agentes LangGraph |
| RAG CVM | Corpus API / fluxos / knowledge |
| Guardrail por código | `hitl_guard_actuation` |
| Budget / rate limit | Teto de tentativas do ticket |

M8: [`modulo-8-exemplo-pratico-guardiao-familia-agents`](../../../../modulo-8-exemplo-pratico-guardiao-familia-agents/)

Aula: [`MAPA_AULAS.md`](../../exemplo_aula/MAPA_AULAS.md)
