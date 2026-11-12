# Guardião — aplicação do Ex.3

> Unidade: **Qualidade, Resiliencia e MCP** (aulas 14-17)

No Guardião o MCP role-based já existe no M8: testes isolam tools, circuit breaker protege API legada e erros padronizados alimentam o HITL.

| Origem (Capstone) | Destino (Guardião / M8) |
|-------------------|-------------------------|
| AI Researcher | Gateway MCP + agentes LangGraph |
| RAG CVM | Corpus API / fluxos / knowledge |
| Guardrail por código | `hitl_guard_actuation` |
| Budget / rate limit | Teto de tentativas do ticket |

M8: [`modulo-8-exemplo-pratico-guardiao-familia-agents`](../../../../modulo-8-exemplo-pratico-guardiao-familia-agents/)

Aula: [`MAPA_AULAS.md`](../../exemplo_aula/MAPA_AULAS.md)
