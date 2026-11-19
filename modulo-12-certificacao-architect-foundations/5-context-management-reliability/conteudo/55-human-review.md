# 5.5 — Workflows de review humano

## Objetivo
HITL em acoes destrutivas; multi-pass com criterios; **evitar same-session self-review**.

## Analogia
Autor nao e o unico revisor do proprio artigo na mesma sentada sem checklist novo.

## Padroes
| Situacao | Padrao |
|----------|--------|
| Refund / deploy / delete | HITL gate |
| PR grande | Multi-pass / sessoes novas |
| PR pequeno focado | Single-pass ok |

Liga D4 (criterios) + D3 CI.

## Mini-lab
Desenhe 2 passes de review para mudanca em `auth/`.

## Checkpoint
- [ ] Por que same-session self-review erra
- [ ] HITL ≠ "pedir para o modelo revisar sozinho"

← [5.4](./54-large-codebase.md) · [ESTUDO](./ESTUDO.md) · → [5.6](./56-provenance.md)
