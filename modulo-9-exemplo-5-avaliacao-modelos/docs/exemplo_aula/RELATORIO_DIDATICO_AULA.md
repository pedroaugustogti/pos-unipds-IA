# Relatório Didático — Avaliação de Modelos

> Aula `modulo-9-exemplo-5-avaliacao-modelos`  
> Caso: medir o fine-tuning **Amplitude Auto** e **Saúde Empresarial** antes de escalar.

## Objetivo

Teste retido, ablação por domínio, stress de overfitting e NPV com custo medido. O veredito decide o Ex.6.

## Camadas

| Camada | Artefato | Papel |
|--------|----------|-------|
| 5.1 Harness | `model_evaluation_harness_tool` · `avaliacao_modelo_local_tool` | Índices fora do treino; schema |
| 5.2 Domínio | `ab_and_domain_tradeoff_tool` · JSONL only-auto / only-saúde | Score separado |
| 5.3 Escala | `npv_real_vs_projetado_tool` · `veredito_escala_tool` | Billing real no NPV do Ex.1 |

Artefato de execução: [`FT_AMPLITUDE_E_SAUDE.md`](./FT_AMPLITUDE_E_SAUDE.md).

## Conceitos

- O piloto de 200 exemplos **foi** o treino. O harness desloca o índice do gerador do Ex.3.
- LLM-as-judge pode punir JSON certo. O aceite é o schema.
- Auto e Saúde não compartilham o score.
- Escalar sem o checklist é o que o Ex.6 existe para **não** fazer no escuro.

## Ponte

| Exemplo | Ligação |
|---------|---------|
| Ex.1 | Projeção que o custo real corrige |
| Ex.3 / Ex.4 | Modelo e adapter avaliados |
| Ex.6 | Executa o “escalar” |
| Guardião | [`../exemplo_real/RAG_PROMPT_GUARDIAO.md`](../exemplo_real/RAG_PROMPT_GUARDIAO.md) |
