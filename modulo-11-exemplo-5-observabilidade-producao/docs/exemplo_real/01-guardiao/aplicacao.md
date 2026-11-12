# Guardião — aplicação do Ex.5

> Unidade: **Observabilidade e producao** (aulas 22-24)

No Guardião Langfuse/métricas cobrem custo do loop; budget de tentativas e rate limit entram no orçamento do ticket (ponte com M10 Ex.3).

| Origem (Capstone) | Destino (Guardião / M8) |
|-------------------|-------------------------|
| AI Researcher | Gateway MCP + agentes LangGraph |
| RAG CVM | Corpus API / fluxos / knowledge |
| Guardrail por código | `hitl_guard_actuation` |
| Budget / rate limit | Teto de tentativas do ticket |

M8: [`modulo-8-exemplo-pratico-guardiao-familia-agents`](../../../../modulo-8-exemplo-pratico-guardiao-familia-agents/)

Aula: [`MAPA_AULAS.md`](../../exemplo_aula/MAPA_AULAS.md)
