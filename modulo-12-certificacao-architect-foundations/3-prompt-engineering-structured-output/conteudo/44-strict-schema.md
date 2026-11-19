# 4.4 — Strict mode e regras de schema

## Objetivo
Aplicar `strict: true` corretamente e modelar opcionais sem invencao.

## Regras classicas do guia
- `additionalProperties: false`
- Todas as properties em `required`
- Opcional real → `["string","null"]` + "null se ausente"

## Exemplo
```json
{
  "purchase_order_number": {
    "type": ["string", "null"],
    "description": "PO se existir no doc; null se nao houver — nao invente"
  }
}
```

## Compliance vs semântica
- Schema OK: `total_amount: 150` (number presente)
- Semantica FAIL: line items somam 175

Host **sempre** valida semantica.

## Mini-lab
Modele schema de endereco com `complement` opcional sem alucinacao.

## Checkpoint
- [ ] Regras do strict
- [ ] Pattern null para opcional

← [4.3](./43-structured-output.md) · [ESTUDO](./ESTUDO.md) · → [4.5](./45-validation-retry.md)
