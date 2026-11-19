# 2.1 (extra) — Boa description + confusão de tools

> Cruza com [21-tool-interface.md](./21-tool-interface.md).

## Template 2.1 (prova)

Boa description inclui:

1. O que faz  
2. Inputs e formato  
3. O que retorna  
4. When to use  
5. When **not** to (nomeie a tool similar)  
6. Edge cases  

---

## Cenário: duas tools parecidas

User: “Cancela a cobrança duplicada do pedido 88210.”

| Ruim | Efeito |
|------|--------|
| `cancel_order`: “Cancela um pedido” | Modelo cancela o pedido inteiro |
| `void_charge`: “Cancela uma cobrança” | Sem fronteira |

**Motivo:** descriptions sobrepostas; vocabulário “cancelar” ambíguo.

**Solução:** when/when-not explícitos (`void_charge` vs `cancel_order` vs `process_refund`) + PreToolUse se side effect grave + nomes claros.

---

## Exemplo description boa (`void_charge`)

```text
Anula UMA cobrança (payment) sem cancelar o pedido.

Inputs: payment_id (pref), order_id (opcional), reason enum
Returns: status voided|already_voided|not_found|failed + ids/timestamps

When: duplicata, captura errada
When NOT: desistência do pedido → cancel_order; settle longo → process_refund; só consultar → list_charges

Edges: already_voided idempotente; not_found → list_charges; failed retryable ≠ "no charge"
```

---

## Cenário: agent com muitas tools

18 tools no mesmo `tools[]` → escolhe `cancel_order` / `search_kb` em vez de `list_charges`→`void_charge`.

**Motivo:** tool overload.

**Solução:** hot-set por **phase** + `Task` com **`allowedTools`** curtos + descriptions + gate.  
Prompt “use com cuidado” não basta.

Phase governa o lead; `allowedTools` governa o sub — os dois se complementam.

---

## Checkpoint

- [ ] Checklist 2.1 de memória
- [ ] Tool errada → description (e escopo), não só system CAPS

← [2.1](./21-tool-interface.md) · [ESTUDO](./ESTUDO.md)
