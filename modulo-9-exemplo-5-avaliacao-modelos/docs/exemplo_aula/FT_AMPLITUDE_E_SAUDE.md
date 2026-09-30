# Artefato de aula — avaliação do fine-tuning (Auto e Saúde)

O job ou o adapter só “existe” para o produto se passar neste gate. Domínios medidos **separados**.

## O que medir

| Critério | Auto | Saúde |
|----------|------|--------|
| Teste retido | Exemplos gerados com índice fora do treino | O mesmo gerador, outro domínio |
| Schema | `segurado`, `placa`, `valor` | `beneficiario`, `procedimento`, `valor` |
| Distrator | Não copiar o primeiro valor do texto | O mesmo |
| Ablação | `amplitude-auto-only-120.jsonl` | `amplitude-saude-only-80.jsonl` |
| Custo | NPV com billing real, não a estimativa do Ex.1 | Idem |

Ledger: `materiais_aula/resultado-medido.json`. Veredito de escalar: `veredito_escala_tool` (reabre Ex.1 + reavaliação Saúde).

LLM-as-judge pode preferir prosa a JSON certo. O aceite da Amplitude é o schema, não o gosto do juiz — normalizar formato antes de comparar.

## Comando local (sem endpoint)

```bash
cd modulo-9-exemplo-5-avaliacao-modelos/materiais_aula
python npv_real_vs_projetado_tool.py
python veredito_escala_tool.py
```

Harness contra o modelo publicado pede `ENDPOINT_MODULO32`. Adapter local: `avaliacao_modelo_local_tool` (LoRA rank 8 do Ex.4).

Relatório: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
