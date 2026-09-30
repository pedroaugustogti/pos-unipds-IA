# Aplicação do Ex.6 (Projeto Final) ao Guardião Família (M8)

O fechamento da Amplitude escala um **formato** já aprovado. No Guardião o equivalente é escalar o **corpus RAG** e o prompt por papel — não treinar o monorepo.

| Origem (Ex.6) | Destino (M8) |
|---------------|----------------|
| JSONL de 3.000 com limpeza | Índice maior sem largar dedup e PII |
| Assistente que classifica domínio | Ramo do LangGraph antes da tool |
| Verificação com o harness do Ex.5 | `qa_validate` depois de reindexar |
| Template de prompt | [`RAG_PROMPT_GUARDIAO.md`](./RAG_PROMPT_GUARDIAO.md) |

Base: [`../../../modulo-9-exemplo-1-decision-framework/docs/exemplo_real/APLICACAO_M9_AO_GUARDIAO_M8.md`](../../../modulo-9-exemplo-1-decision-framework/docs/exemplo_real/APLICACAO_M9_AO_GUARDIAO_M8.md)  
Avaliação: [`../../../modulo-9-exemplo-5-avaliacao-modelos/docs/exemplo_real/APLICACAO_M9_EX5_AO_GUARDIAO_M8.md`](../../../modulo-9-exemplo-5-avaliacao-modelos/docs/exemplo_real/APLICACAO_M9_EX5_AO_GUARDIAO_M8.md)

| Hipótese | Decisão |
|----------|---------|
| Modelo único treinado no repo Guardião | **Não** |
| Decidir → limpar corpus → prompt → medir → escalar → medir de novo | **Sim** |

M8: [`../../../modulo-8-exemplo-pratico-guardiao-familia-agents/`](../../../modulo-8-exemplo-pratico-guardiao-familia-agents/)  
Aula: [`../../`](../../) · Relatório: [`../exemplo_aula/RELATORIO_DIDATICO_AULA.md`](../exemplo_aula/RELATORIO_DIDATICO_AULA.md)
