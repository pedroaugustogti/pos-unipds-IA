# 4.3 — Structured output (tool schema / output_config)

## Objetivo
Garantir JSON parseavel sem "esperar que venha JSON no texto".

## Analogia
Formulario com campos obrigatorios vs redação livre pedindo "responda em JSON".

## Abordagens
1. Tool cujo `input_schema` e o objeto desejado
2. `strict: true` no tool
3. `output_config.format` com `json_schema`
4. Helper SDK (`messages.parse`) quando disponivel

## tool_choice (conceito)
| Valor | Comportamento |
|-------|----------------|
| auto | Tool ou texto |
| any | Deve chamar alguma tool |
| tool nomeado | Deve chamar aquela |
| none | So texto |

Nota: em modelos 5.x forced any/tool pode dar 400 → `auto` + instrucao + strict, ou `output_config`. Conceito "forcar estrutura" permanece.

## Exemplo — extrair invoice
```json
{
  "name": "extract_invoice",
  "description": "Extrai dados de fatura. Use sempre que houver documento de invoice.",
  "strict": true,
  "input_schema": {
    "type": "object",
    "properties": {
      "vendor_name": {"type": "string"},
      "total_amount": {"type": "number"},
      "currency": {"type": "string", "enum": ["USD", "EUR", "BRL", "other"]}
    },
    "required": ["vendor_name", "total_amount", "currency"],
    "additionalProperties": false
  }
}
```

## Mini-lab
Schema para extrair `pr_number`, `risk` (low|med|high), `blockers[]`.

## Checkpoint
- [ ] Distingo free-form vs schema
- [ ] Sei 2 formas de structured output

← [4.2](./42-few-shot.md) · [ESTUDO](./ESTUDO.md) · → [4.4](./44-strict-schema.md)
