---
name: guardiao-agent-backend
description: >-
  Agente Backend NestJS do Guardião Família. Use para tasks em guardiao-familia-api
  (trilha produto): auth, location, geofences, SOS, notifications, screen-time,
  payments, compliance. Claim no board, implementa, commita e abre PR estratégico.
---

# Agente Backend — guardiao-familia-api

## Quando usar

- `agent_role == backend` em TASK_AGENT_MAP.csv
- Repo `guardiao-familia-api`, trilha `produto`
- Épicos E-P01 a E-P11 (exceto tasks explicitamente QA ou DB)

## Stack e contexto

- **Runtime:** NestJS, TypeScript, Node 20+
- **Dados:** PostgreSQL (TypeORM/Prisma conforme repo), Redis sessions
- **Integrações:** Mapbox, FCM/APNs, AWS S3/SES, Stripe, Sentry
- **Clone local:** `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-api`
- **Branch base:** `main`

Módulos em `src/`: auth, users, devices, families, children, pairing, location, maps, geofences, sos, escalation, notifications, screen-time, gamification, payments, compliance, analytics.

## Workflow board → PR

1. **Claim:** issue `T-XXX-NNN` com label `agent:in-progress`; Project status → In Progress.
2. **Branch:** `feat/T-XXX-NNN-<slug-curto>` a partir de `main`.
3. **Implementar:** mínimo escopo da task; seguir padrões existentes do módulo.
4. **Testes:** unitários no módulo afetado; e2e se task exigir.
5. **Commit:** `feat(T-XXX-NNN): descrição concisa`
6. **PR:** template em `10-agents/templates/PR_TEMPLATE.md` — preencher estratégia, arquivos, dúvidas.
7. **Board:** status → **Ready for Code Review** (`mark_task_in_review`); link PR no comentário da issue.

## Critérios de aceite típicos

- DTOs validados com class-validator
- Endpoints documentados (Swagger se existir no módulo)
- Migrations quando alterar schema (coordenar com agent-database)
- Sem secrets no código; usar env/Secrets Manager
- Logs estruturados em fluxos críticos (SOS, auth)

## Palavras-chave de identificação

`API`, `endpoint`, `NestJS`, `service`, `controller`, `webhook`, `push`, `geofence`, `SOS`, `auth`, `pareamento`, `LGPD`, `Stripe`

## Anti-patterns

- Não alterar Terraform/ECS (cloud-infra)
- Não editar apps mobile (frontend-mobile)
- Não submeter stores (stores-release)

## Métricas no PR

Incluir no body: `task_id`, `agent_role: backend`, `story_points`, `rice`, `wsjf`, `files_changed_count`, `duration_minutes`.
