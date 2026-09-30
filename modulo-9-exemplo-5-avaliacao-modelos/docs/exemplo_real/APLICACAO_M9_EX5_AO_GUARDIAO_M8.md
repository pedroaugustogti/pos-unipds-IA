# Aplicação do Ex.5 (Avaliação) ao Guardião Família (M8)

Avaliar **não** autoriza fine-tuning do código. Autoriza promover índice, skill ou prompt só com caso retido e score separado por superfície.

| Origem (Ex.5) | Destino (M8) |
|---------------|----------------|
| Teste retido | Fluxo ou arquivo que a skill não citou como exemplo |
| A/B Auto vs Saúde | Parent/child vs API vs evidência |
| LLM-as-judge vs schema | `qa_validate` olha contrato |
| Veredito antes de escalar | Não reindexar o monorepo inteiro porque um piloto passou |

Base: [`../../../modulo-9-exemplo-1-decision-framework/docs/exemplo_real/APLICACAO_M9_AO_GUARDIAO_M8.md`](../../../modulo-9-exemplo-1-decision-framework/docs/exemplo_real/APLICACAO_M9_AO_GUARDIAO_M8.md)

Etapa de execução: [`RAG_PROMPT_GUARDIAO.md`](./RAG_PROMPT_GUARDIAO.md)

| Hipótese | Decisão |
|----------|---------|
| FT do monorepo porque o piloto ficou bom | **Não** |
| Promover RAG/skill só com eval | **Sim** |
| Um score único para todas as superfícies | **Não** |

M8: [`../../../modulo-8-exemplo-pratico-guardiao-familia-agents/`](../../../modulo-8-exemplo-pratico-guardiao-familia-agents/)  
Aula: [`../../`](../../) · Relatório: [`../exemplo_aula/RELATORIO_DIDATICO_AULA.md`](../exemplo_aula/RELATORIO_DIDATICO_AULA.md)
