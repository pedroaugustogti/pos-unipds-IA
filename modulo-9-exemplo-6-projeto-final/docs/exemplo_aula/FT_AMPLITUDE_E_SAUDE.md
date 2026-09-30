# Artefato de aula — fine-tuning em escala (Amplitude Auto e Saúde)

Fecha o ciclo: o veredito do Ex.5 autoriza sair do piloto de 200 para o dataset de produção (~3.000), com o **mesmo** filtro do Ex.2 e o **mesmo** harness do Ex.5 depois.

## Dataset de produção

Arquivo: `materiais_aula/amplitude-seguros-dataset-producao-3000.jsonl`.

Não é o piloto repetido. O gerador (`m6_dataset_scaling_tool`) muda de verdade:

- Mais oficinas e clínicas, com personas de redação diferentes.  
- Campo distrator que **não** entra no JSON (apólice, CRM, franquia).  
- Subconjunto com ruído de OCR.

Regenerar:

```bash
cd modulo-9-exemplo-6-projeto-final/materiais_aula
python m6_dataset_scaling_tool.py
```

## Assistente

`amplitude-seguros-assistente.js` classifica o domínio (vocabulário específico — “sinistro” sozinho não decide) e chama o modelo: adapter LoRA do Ex.4 ou endpoint do job escalado. A verificação reusa o harness do Ex.5 (`m6_scaled_model_verification_tool`).

Relatório: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
