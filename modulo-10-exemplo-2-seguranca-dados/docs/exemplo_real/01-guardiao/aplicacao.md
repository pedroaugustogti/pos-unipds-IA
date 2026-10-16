# Guardião — aplicação do Ex.2

A demonstração coloca uma ordem dentro de um histórico recuperado. No Guardião o equivalente é um chunk de código, fluxo ou ticket.

| Origem (Ex.2) | Destino (M8) |
|---------------|----------------|
| `system_instruction` | `SKILL.md` + `agent.md` do papel |
| Histórico vindo do banco | Trecho do RAG (`code_index`, `mobile_flow_rag`) |
| Regra que o dado tenta anular | Escopo do ticket e catálogo de passos |
| Segredo no prompt | Chave fica fora do contexto e do Git |

Responsabilidade do ato: [`aplicacao.md`](../../../../modulo-10-exemplo-1-aspectos-humanos-eticos/docs/exemplo_real/01-guardiao/aplicacao.md)

| Hipótese | Decisão |
|----------|---------|
| Texto recuperado pode mudar a skill | **Não** |
| Chunk é dado; instrução só vem do papel | **Sim** |

M8: [`modulo-8-exemplo-pratico-guardiao-familia-agents`](../../../../modulo-8-exemplo-pratico-guardiao-familia-agents/)  
Aula: [`../`](../../../) · Relatório: [`RELATORIO_DIDATICO_AULA.md`](../../exemplo_aula/RELATORIO_DIDATICO_AULA.md)
