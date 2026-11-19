# 4.5 — Validation-retry loop

## Objetivo
Montar: gerar → validar schema → validar negocio → feedback especifico → retry com limite → escalate/parcial.

## Analogia
Conferencia de nota fiscal: volta para o emitente com "item 3 sem NCM", nao "esta errado".

## Fluxo
```text
generate → schema_validate → business_validate
   │              │                 │
   │              └─ fail → erro de campo ─┐
   │              └─ fail negocio ─────────┤
   └───────────────────────────────────────┴→ retry (max N) → escalate
```

## Exemplo
```python
def extract_with_retry(doc: str, max_tries: int = 3):
    feedback = None
    for i in range(max_tries):
        data = call_model(doc, feedback)
        ok, err = schema_check(data)
        if not ok:
            feedback = f"Schema: {err}"
            continue
        ok, err = business_check(data)  # totais, datas
        if not ok:
            feedback = f"Negocio: {err}"
            continue
        return data
    return escalate_partial(data, feedback)
```

Metricas: por tipo de documento — nao so accuracy agregada.

## Mini-lab
Liste 3 erros de negocio tipicos de invoice + mensagem de feedback.

## Checkpoint
- [ ] Schema ≠ semantica
- [ ] Feedback especifico + max retries

← [4.3](./43-structured-output.md) · [ESTUDO](./ESTUDO.md) · → [4.5](./46-batch-processing.md)
