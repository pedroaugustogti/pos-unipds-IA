<!--
Copiar para: .claude/skills/billing-ship-check/SKILL.md
CCAR-F 3.2 — context: fork | allowed-tools | argument-hint
-->

---
name: billing-ship-check
description: >
  Roda testes de billing e devolve veredito curto pass/fail.
  Use quando pedirem ship-check, “posso abrir PR?”, ou validar billing antes do PR.
context: fork
allowed-tools:
  - Bash(pytest *)
  - Read
  - Grep
argument-hint: [optional-path-or-filter]
---

# Billing ship check

Filtro/alvo: $ARGUMENTS

## Missão
1. Rode os testes de billing (respeite $ARGUMENTS se vier path/filtro)
2. Analise a saída no SEU contexto isolado
3. Devolva ao lead APENAS:

```text
status: pass|fail
ran: <comando>
failed: <N>
top_failures:
  - file:line — mensagem curta
risk: <1 linha>
next: open_pr|fix_failures
```

Não cole o log completo. Não edite código. Não faça git push/commit.
