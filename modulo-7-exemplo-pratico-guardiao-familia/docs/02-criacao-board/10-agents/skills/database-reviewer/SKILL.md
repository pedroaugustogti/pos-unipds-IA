---
name: guardiao-reviewer-database
description: >-
  Revisor PostgreSQL/Redis/migrations. Pareado com database. Valida DDL, rollback,
  finaliza PR e board.
---

# Revisor Database — par de `skills/database`

Skill criador: [../database/SKILL.md](../database/SKILL.md)

## Checklist

- [ ] Migration reversivel (up/down)
- [ ] Indices para queries location/geofence/SOS
- [ ] Impacto dados/backfill documentado
- [ ] LGPD retenção respeitada
- [ ] Coordenacao com backend se breaking API

## Veredito

`approved` -> Done | migration destrutiva sem plano -> `changes_requested`
