# 3.5 (extra) — Refinamento iterativo

> Cruza com [35-refinamento-iterativo.md](./35-refinamento-iterativo.md).

## Cinco regras com o mesmo domínio (billing / support)

### 1) Exemplos I/O quando o formato **varia**

E-mails de refund vs shipping vs “outras” → 2–4 pares INPUT/OUTPUT no prompt/skill.  
Instrução genérica “extraia os campos” falha na variação.

### 2) Tests para edge cases

- `amount == 100` (limiar inclusivo)  
- `order_id` null → não inventar  
- `already_voided` → idempotente  

### 3) Domínio novo → Claude te **entrevista**

Chargeback do adquirente X: peça até N perguntas antes de implementar.  
Evita inventar policy.

### 4) Bugs que **interagem** = **uma** mensagem

Void não idempotente **causa** double comment no ticket → descrever a **cadeia** juntos.

### 5) Bugs **não relacionados** = **um por vez**

`refund.py` `<=` **e** typo CSS → dois turnos separados.

---

## Fluxo do dia (cola)

```text
Extractor que varia → I/O examples + edge tests
Domínio novo → entrevista
Bugs soltos → 1 msg cada
Bugs ligados → 1 msg com a cadeia
```

## Checkpoint

- [ ] Variação ⇒ exemplos
- [ ] Interagem juntos; soltos separados

← [3.5](./35-refinamento-iterativo.md) · [ESTUDO](./ESTUDO.md)
