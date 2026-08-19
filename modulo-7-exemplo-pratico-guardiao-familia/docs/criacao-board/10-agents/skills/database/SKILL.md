---
name: guardiao-agent-database
description: >-
  Agente Database do Guardião Família. PostgreSQL, Redis, migrations TypeORM,
  RDS multi-AZ, ElastiCache. Épico E-I04 e tasks de schema na API.
---

# Agente Database — PostgreSQL & Redis

## Quando usar

- `agent_role == database`
- Épico E-I04 ou título com migration/postgres/redis/schema/RDS
- Alterações em `migrations/`, entities, índices na API

## Stack

- PostgreSQL 15+ (RDS multi-AZ staging/prod)
- Redis ElastiCache (sessions, cache)
- ORM: conforme repo (TypeORM migrations em `guardiao-familia-api`)
- Backup/restore policies documentadas

## Workflow board → PR

1. Claim; In Progress.
2. Branch `db/T-XXX-NNN-<slug>`.
3. Migration reversível (up/down) quando possível.
4. PR inclui: DDL summary, impacto em dados, tempo estimado de migration prod.
5. Coordenar com `backend` se migration quebra contratos API.

## Critérios de aceite

- Índices para queries de location/geofence/SOS
- LGPD: retenção e soft-delete onde aplicável
- Connection pooling documentado
- Zero downtime strategy para migrations grandes

## Palavras-chave

`PostgreSQL`, `RDS`, `Redis`, `ElastiCache`, `migration`, `schema`, `index`, `TypeORM`, `multi-AZ`

## Métricas PR

`task_id`, `agent_role: database`, `migration_files[]`, `tables_affected[]`, `rollback_sql`.
