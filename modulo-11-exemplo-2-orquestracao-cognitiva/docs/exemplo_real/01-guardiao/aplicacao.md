# Guardião — aplicação do Ex.2

> Unidade: **Orquestracao Cognitiva e APIs** (aulas 8-13)

No Guardião o retrieve consulta corpus/API; o grade decide se o contexto basta; fallback não vira instrução. Citação e guardrail por código antes de qualquer atuação.

| Origem (Capstone) | Destino (Guardião / M8) |
|-------------------|-------------------------|
| AI Researcher | Gateway MCP + agentes LangGraph |
| RAG CVM | Corpus API / fluxos / knowledge |
| Guardrail por código | `hitl_guard_actuation` |
| Budget / rate limit | Teto de tentativas do ticket |

M8: [`modulo-8-exemplo-pratico-guardiao-familia-agents`](../../../../modulo-8-exemplo-pratico-guardiao-familia-agents/)

Aula: [`MAPA_AULAS.md`](../../exemplo_aula/MAPA_AULAS.md)
