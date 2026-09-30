# Relatório Didático — Projeto Final Amplitude

> Aula `modulo-9-exemplo-6-projeto-final`  
> Caso: escalar o fine-tuning **Auto + Saúde** depois do veredito do Ex.5.

## Objetivo

Dataset ~3.000 com a higiene do Ex.2, assistente que classifica o domínio, verificação de novo com o harness do Ex.5.

## Camadas

| Camada | Artefato | Papel |
|--------|----------|-------|
| 6.1 Assistente | `amplitude-seguros-assistente.js` · `chamar_modelo_local.py` | Roteia Auto vs Saúde e chama o modelo |
| 6.2 Escala | `m6_dataset_scaling_tool` · JSONL de 3.000 | Mais fontes, distrator, ruído de OCR |
| 6.3 Remedir | `m6_scaled_model_verification_tool` | O número antigo não garante o modelo de hoje |

Artefato de execução: [`FT_AMPLITUDE_E_SAUDE.md`](./FT_AMPLITUDE_E_SAUDE.md).

## Ponte

| Exemplo | Ligação |
|---------|---------|
| Ex.2 | Filtro do dataset grande |
| Ex.4 | Adapter na chamada local |
| Ex.5 | Veredito e harness |
| Guardião | [`../exemplo_real/RAG_PROMPT_GUARDIAO.md`](../exemplo_real/RAG_PROMPT_GUARDIAO.md) |
