# 3.4 (extra) — Plan mode vs Direct execution

> Cruza com [34-plan-vs-direct.md](./34-plan-vs-direct.md).

## Vocabulário

| Termo | Significado |
|-------|-------------|
| **Migration** (neste tópico) | Cenário: mudança em **muitos files** de código/API — **não** migration de banco |
| **Plan mode** | Estratégia: planejar antes de editar |
| **Direct execution** | Estratégia: editar já |

A questão cita “migration…” para você **reconhecer o cenário**; a resposta é o **modo**.

---

## Cenário A — Plan mode

Migration `datetime.utcnow()` → `datetime.now(UTC)` em **45+ files**; várias abordagens válidas (helper único vs inline vs shim).

| Não | Sim |
|-----|-----|
| Direct “já vai editando” | **Plan mode first** → aprovar abordagem → Direct |

Plan lista abordagens, riscos, ordem; user escolhe; só então editar.

---

## Cenário B — Direct execution

> “Em `refund.py:88`, troque `<` por `<=` no limiar. Só isso.”

1 file, 1 bug, caminho óbvio → **Direct execution**.  
Plan mode aqui é overhead.

---

## Discovery longo

Explore subagent / isolamento — não poluir o thread principal (liga com fork/Task).

---

## Checkpoint

- [ ] Migration ≠ DB migration neste item
- [ ] 45+ + opções → Plan; fix estreito → Direct

← [3.4](./34-plan-vs-direct.md) · [ESTUDO](./ESTUDO.md)
