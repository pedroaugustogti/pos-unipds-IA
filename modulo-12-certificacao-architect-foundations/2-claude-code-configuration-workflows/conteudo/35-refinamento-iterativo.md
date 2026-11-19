# 3.5 — Refinamento iterativo

## Objetivo
Feedback curto e cirurgico; evitar "refaz tudo"; isolar exploracao ruidosa com fork.

## Analogia
Ensaio: "so o baixo no refrao" — nao a musica inteira de novo.

## Bom
- "Mude so `handler.ts`; nao toque testes ainda"
- "Inverta o early-return; mantenha assinatura"

## Ruim
- "Melhora isso"
- Rewrite total a cada turno
- Research de 30 arquivos na mesma thread de patch fino

## Exemplo
```text
T1: implementa feature
T2: "Erros de validacao → 422 ERR_VALIDATION — so isso"
T3: "1 teste para body vazio"
```

## Mini-lab
Reescreva 3 feedbacks vagos em cirurgicos.

## Checkpoint
- [ ] Escopo + nao-objetivos
- [ ] Sei quando fork ajuda

← [3.4](./34-plan-vs-direct.md) · [ESTUDO](./ESTUDO.md) · → [3.6](./36-cicd-claude-code.md)
