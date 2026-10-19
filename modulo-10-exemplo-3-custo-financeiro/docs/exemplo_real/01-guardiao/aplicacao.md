# Guardião — aplicação do Ex.3

A aula mede operação, falha e governança. No Guardião o equivalente é a chamada MCP, o incidente no board e o HITL.

| Origem (Ex.3) | Destino (M8) |
|---------------|----------------|
| Custo da chamada | `execute_agent_actuation_tool` e tools de QA/Appium |
| Custo do loop | Agente que reexecuta fase ou evidence sem teto |
| Custo do incidente | Ticket errado, wipe, merge sem revisão |
| Custo do controle | `hitl_guard_actuation`, `qa_validate`, reindex do RAG |

Responsabilidade: [`aplicacao.md`](../../../../modulo-10-exemplo-1-aspectos-humanos-eticos/docs/exemplo_real/01-guardiao/aplicacao.md)  
Contexto não é ordem: [`aplicacao.md`](../../../../modulo-10-exemplo-2-seguranca-dados/docs/exemplo_real/01-guardiao/aplicacao.md)

| Hipótese | Decisão |
|----------|---------|
| Rodar de novo “até passar” sem teto | **Não** |
| HITL e teto de tentativa entram no orçamento do ticket | **Sim** |

M8: [`modulo-8-exemplo-pratico-guardiao-familia-agents`](../../../../modulo-8-exemplo-pratico-guardiao-familia-agents/)  
Aula: [`../`](../../../) · Relatório: [`RELATORIO_DIDATICO_AULA.md`](../../exemplo_aula/RELATORIO_DIDATICO_AULA.md)
