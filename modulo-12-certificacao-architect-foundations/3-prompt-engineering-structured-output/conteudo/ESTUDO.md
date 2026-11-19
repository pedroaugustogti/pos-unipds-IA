# D4 — Prompt Engineering & Structured Output (20%)

> 6 task statements · [CertPrep D4](https://certprep.pratechlabs.com/claude/ccar-f/learn/) · [mapa 30 tasks](../../README.md#mapa-dos-30-tasks)

## O que a prova valida

Critérios explícitos + FP; few-shot; structured via tool/schema; validation-retry; **batch**; **multi-instance / multi-pass**.

## Trilha = tasks 4.1–4.6

| Task | Arquivo | One-liner |
|------|---------|-----------|
| 4.1 | [41-criterios-explicitos.md](./41-criterios-explicitos.md) | Include/exclude + exemplos; desligar categoria ruidosa |
| 4.2 | [42-few-shot.md](./42-few-shot.md) | 2–4 exemplos com reasoning |
| 4.3 | [43-structured-output.md](./43-structured-output.md) | Tool schema / tool_choice; nullable se ausente |
| 4.3+ | [43b-cenarios-tool-choice-structured.md](./43b-cenarios-tool-choice-structured.md) | Intake forçado; liga D2 23b + exemplo Python |
| 4.4 | [45-validation-retry.md](./45-validation-retry.md) | Validar significado; retry com erro exato; parar se não está no doc |
| 4.5 | [46-batch-processing.md](./46-batch-processing.md) | Batches ~50% custo; sem tools mid-request; `custom_id` |
| 4.6 | [47-multipass-review.md](./47-multipass-review.md) | Instância independente; multi-pass; confidence nos findings |

**Apoio a 4.3:** [44-strict-schema.md](./44-strict-schema.md)  
**Extra (fora dos 30):** [48-thinking-effort-EXTRA.md](./48-thinking-effort-EXTRA.md)

## Cronograma dias 8–10

| Dia | Tasks | Prática |
|-----|-------|---------|
| 8 | 4.1–4.2 | Reescrever prompt vago |
| 9 | 4.3 + 44 | Extrator + nullable |
| 10 | 4.4–4.6 | Retry loop + batch vs sync + multipass |

## Hábitos CertPrep (D4)

- Schema = forma, não verdade → validação de negócio  
- Pre-merge que alguém espera → Messages, não Batch  
- Self-review same-session → errado  

## Checklist

- [ ] Critérios com fronteira
- [ ] Nullable vs inventar campo
- [ ] Sync vs batch
- [ ] Multi-pass / nova instância

## Prova

[`../prova/PROVA.md`](../prova/PROVA.md)
