# 1.5 (extra) — PreToolUse, PostToolUse e `stop_reason`

> Cruza com [15-agent-sdk-hooks.md](./15-agent-sdk-hooks.md).

## Ordem no loop

```text
Claude pede tool (stop_reason já = tool_use)
  → PreToolUse   (block / redirect / rewrite / hitl)
  → executa tool
  → PostToolUse  (normalize / trim / enrich)
  → tool_result → próxima create (novo stop_reason)
```

Hooks = **host**. Não reescrevem o `stop_reason` da response já gerada.

---

## PreToolUse — exemplos

### Block (refund acima do limiar)

```python
if tool_name == "process_refund" and amount > limit:
    return {"decision": "block", "reason": "above auto-refund limit"}
```

### Redirect (verify first)

```python
if tool_name == "process_refund" and not case["customer_verified"]:
    return {"decision": "redirect", "replace_with": "lookup_customer"}
```

### Rewrite (cap de janela de logs)

```python
tool_input["window_hours"] = min(tool_input.get("window_hours", 24), 24)
```

---

## PostToolUse — exemplos

### Normalize weather / trim search / enrich com hint de limiar

```python
# trim
hits = raw["hits"][:3]
# enrich
raw["refund_gate_hint"] = "AUTO_OK" if amount <= 100 else "REQUIRES_HITL"
```

---

## PreToolUse muda `stop_reason` para `stop_sequence`?

**Não.** Camadas diferentes.

| Conceito | Quem |
|----------|------|
| `stop_reason` / `stop_sequence` | Geração da API |
| PreToolUse | Host após `tool_use` já emitido |

### Próximo `stop_reason` típico

| Após PreToolUse | Próxima geração (se houver) |
|-----------------|----------------------------|
| Redirect | Quase sempre outro `tool_use` |
| HITL + avisa user | `end_turn` |
| HITL + aprovou + tool rodou | `end_turn` |
| Block | `end_turn` ou outro `tool_use` alternativo |

---

## `tool_choice` ≠ PostToolUse

| | `tool_choice` | `PostToolUse` |
|--|---------------|---------------|
| Quando | Na **geração** | Depois da tool **rodar** |
| Controla | Se/qual tool pedir | Como o result chega ao modelo |
| Se só texto | Pode forçar tool | Nem dispara |

Structured output obrigatório → `tool_choice`, não PostToolUse.

---

## Checkpoint

- [ ] Pre = catraca; Post = limpeza
- [ ] Hook ≠ stop_sequence
- [ ] Redirect → tipicamente novo tool_use; HITL → end_turn comum

← [1.5 Hooks](./15-agent-sdk-hooks.md) · [ESTUDO](./ESTUDO.md)
