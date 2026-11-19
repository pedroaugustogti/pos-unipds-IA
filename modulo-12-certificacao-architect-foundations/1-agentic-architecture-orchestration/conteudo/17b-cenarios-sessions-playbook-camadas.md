# 1.7 (extra) — Resume / Fork / Fresh, camadas de estado, playbook

> Cruza com [17-sessions-resume-fork-fresh.md](./17-sessions-resume-fork-fresh.md).

## Classificar continuidade

| Classe | Quando | Ação |
|--------|--------|------|
| **Resume** | Contexto ainda verdadeiro; mudou um detalhe | `--resume` + diga o que mudou |
| **Fork** | 2 abordagens a partir da mesma análise | Ramo da sessão |
| **Fresh** | Mundo/transcript mentem (muitos files mudaram) | Nova sessão + summary curto |

**Migration** no cheat sheet 3.4 = migração de **código** em massa (cenário), não migration de DB. Continuity de session ≠ Plan mode — mas Plan mode é a resposta a migration grande com várias abordagens.

---

## Camadas de estado (L1/L2/L3)

```text
L3 Externa     DB · ticket · file · memory     verdade operacional
L2 Estruturada CASE FACTS · phase · budget     session oficial
L1 Efêmera     chat · raciocínio · dumps       descartável
```

| Decisão | L1 | L2 | L3 |
|---------|----|----|-----|
| Resume | Reusa | Reusa (patch) | Continua válido |
| Fork | Clona / diverge | Pode divergir por ramo | **Compartilhado** — cuidado side effects |
| Fresh | Descarta | Recria via summary+L3 | Âncora |

IDs, dinheiro, policy, phase HITL → L2+L3, nunca só L1.

---

## Subagents e sessions

- Lead = session do **caso**
- Cada Task = mini-session **própria** (não herda)
- Cancel do user → host cancela subs; marca parcial

---

## Quem decide Resume/Fork/Fresh?

Quase sempre **operador** ou **policy no host** (playbook). Não é `stop_reason` automático.

```python
def continuity(case) -> str:
    if case.head_sha_changed or case.external_refund_done:
        return "fresh"
    if case.want_ab_strategies:
        return "fork"
    if case.facts_still_valid:
        return "resume"
    return "fresh"
```

---

## Playbook e continuity

```yaml
continuity:
  resume_if: [phase == wait_hitl, facts_valid]
  fork_if: [ab_strategy_requested]
  fresh_if: [external_refund_already_done, head_sha_changed]
```

Claude Code: playbook operacional vira trechos de `CLAUDE.md` / skill — pasta `playbooks/` **não** é tipo oficial.

---

## Exemplos reais

| Situação | Escolha |
|----------|---------|
| HITL aprovou; mesmos fatos | Resume |
| Testar rollback vs feature-flag | Fork |
| `git pull` reescreveu branch reviewado | Fresh + summary |
| Stripe já voidou; chat diz pendente | Fresh lendo L3 |

---

## Checkpoint

- [ ] Resume/Fork/Fresh em 15s
- [ ] L1/L2/L3 e side effects no fork
- [ ] Decisão = humano/policy, não magia da API

← [1.7 Sessions](./17-sessions-resume-fork-fresh.md) · [ESTUDO](./ESTUDO.md)
