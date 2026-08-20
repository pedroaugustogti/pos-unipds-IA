---
name: guardiao-reviewer-qa
description: >-
  Revisor de testes QA. Pareado com qa. Valida cobertura cenarios criticos,
  finaliza PR e board.
---

# Revisor QA — par de `skills/qa`

Skill criador: [../qa/SKILL.md](../qa/SKILL.md)

## Checklist

- [ ] Cenarios criticos: SOS <30s, geofence E2E, push emergencia
- [ ] Testes rodam em CI
- [ ] Sem flaky nao documentado
- [ ] Gaps listados no PR
- [ ] Nao alterou logica prod desnecessariamente

## Veredito

Cobertura insuficiente em release_blocker -> `changes_requested`. Caso contrario `approved` -> Done.
