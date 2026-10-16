# Guardião — aplicação do Ex.1

O estudo de caso pergunta quem responde. No Guardião a resposta é o papel humano do ticket, não o modelo.

| Origem (Ex.1) | Destino (M8) |
|---------------|----------------|
| Quem opera | Papel em `agents/01-role-based/{role}/` |
| Quem é afetado | Família e dados do ticket (localização, SOS) |
| Ato irreversível | `hitl_guard_actuation` antes de merge, wipe ou deploy |
| Limite do modelo | O prompt declara o que falta em vez de completar |

| Hipótese | Decisão |
|----------|---------|
| O agente publica porque o modelo “aceitou” | **Não** |
| Ação irreversível espera o humano do papel | **Sim** |

M8: [`modulo-8-exemplo-pratico-guardiao-familia-agents`](../../../../modulo-8-exemplo-pratico-guardiao-familia-agents/)  
Aula: [`../`](../../../) · Relatório: [`RELATORIO_DIDATICO_AULA.md`](../../exemplo_aula/RELATORIO_DIDATICO_AULA.md)
