# 2.3 / 4.3 (extra) — `tool_choice`: auto, any, tool forçada

> Cruza com [23-distribuicao-tool-choice.md](./23-distribuicao-tool-choice.md) e D4 structured output.

## Tabela

| `tool_choice` | Comportamento | Quando |
|---------------|---------------|--------|
| `auto` | Tool **ou** texto | Chat; tool opcional |
| `any` | **Deve** chamar alguma tool | Structured obrigatório + **N** schemas |
| `{"type":"tool","name":…}` | **Deve** chamar aquela | Um schema / step first |
| `none` | Só texto | Proibir tools |

---

## Cenário `auto`

“Bom dia” vs “status do pedido 88210”.  
`any` no cumprimento → tool fantasma. **`auto`** deixa optar.

## Cenário `any`

Intake de e-mail com `extract_refund_ticket` | `extract_shipping_ticket` | `extract_cancel_ticket`.  
`auto` → prosa sem parse. Forçar só refund → shipping vira refund. **`any`** garante tool e deixa escolher schema.

## Cenário tool forçada + fluxo

```python
resp = client.messages.create(
    ...,
    tools=tools,
    tool_choice={"type": "tool", "name": "extract_ticket_fields"},
    messages=[{"role": "user", "content": f"Customer email:\n{email_body}"}],
)
# stop_reason=tool_use → host lê .input → open_ticket
# 2ª create com auto → end_turn mensagem ao user
```

```text
① tool_choice força extract
② tool_use.input = JSON tipado
③ PreToolUse opcional
④ open_ticket(fields)
⑤ PostToolUse opcional
⑥ tool_result + create(auto) → end_turn
```

## Por que não PostToolUse no lugar

Sem `tool_use`, PostToolUse **não roda**. `tool_choice` age na **geração**.

---

## Checkpoint

- [ ] auto vs any vs forced
- [ ] Structured output = tool + tool_choice, não “JSON no prompt”

← [2.3](./23-distribuicao-tool-choice.md) · [ESTUDO](./ESTUDO.md)
