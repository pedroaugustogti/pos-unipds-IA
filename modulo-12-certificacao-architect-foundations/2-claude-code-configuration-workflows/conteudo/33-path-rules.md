# 3.3 — Path-specific rules (`.claude/rules/`)

## Objetivo
Regras globais vs path-scoped; saber o que acontece apos `/compact`.

## Analogia
Placa "silencio" so na biblioteca.

## Exemplo

```markdown
---
paths:
  - "src/billing/**"
  - "**/payments*.ts"
---
# Billing security
- Nunca logar PAN/CVV
- Mudanca de preco exige pricing.spec.ts
```

Sem `paths` → carrega no start. Com `paths` → quando Claude toca arquivo matching.

**Trap:** apos compact, rule path-scoped some ate retocar o path. Regra permanente → CLAUDE.md raiz.

## Mini-lab
1 rule global + 1 path-scoped para React + API.

## Checkpoint
- [ ] Com/sem paths
- [ ] Trap do compact

← [3.2](./32-skills-e-commands.md) · [ESTUDO](./ESTUDO.md) · → [3.4](./34-plan-vs-direct.md)
