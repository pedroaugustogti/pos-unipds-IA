---
name: guardiao-agent-backend
description: >-
  Agente Backend NestJS do Guardião Família. Use para tasks em guardiao-familia-api
  (trilha produto): auth, location, geofences, SOS, notifications, screen-time,
  payments, compliance. Claim no board, implementa, commita e abre PR estratégico.
---

# Agente Backend — guardiao-familia-api

## Repositório(s) e path local

| Repo GitHub | Path local | Env var |
|-------------|------------|---------|
| `guardiao-familia-api` | `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-api` | `GUARDAO_API_PATH` |

Paths resolvidos por `lib/repo_paths.py` (`resolve_repo_path`).

## Stack Guardião Família

- **Runtime:** NestJS 10+, TypeScript, Node 20+
- **Dados:** PostgreSQL (TypeORM), Redis (sessions/cache)
- **Integrações:** Mapbox, FCM/APNs, AWS S3/SES, Stripe, Sentry
- **Módulos:** `src/` — auth, users, devices, families, children, pairing, location, maps, geofences, sos, escalation, notifications, screen-time, gamification, payments, compliance, analytics
- **Branch base:** `main`

## Fora do escopo → redirecionar

| Situação | Agente |
|----------|--------|
| Terraform, VPC, ECS, ECR, ALB | `cloud-infra` |
| GitHub Actions, deploy pipeline | `devops-cicd` |
| Migration/schema PostgreSQL ou Redis RDS | `database` |
| Tela parent/child mobile | `frontend-mobile` |
| Backoffice ou site | `frontend-web` |
| Escrever/atualizar specs de teste | `qa` |
| Validar PR em In Test | `qa-gate` |
| Submit App Store / Play | `stores-release` |

**Anti-pattern:** comentar issue e redirecionar, não implementar.

Referência completa: [_shared/REPOS_AND_ROUTING.md](../_shared/REPOS_AND_ROUTING.md) · [_shared/STATEGRAPH_FLOW.md](../_shared/STATEGRAPH_FLOW.md). LangGraph reclassifica via `lib/agent_registry.resolve_agent_for_task` antes de `implement`.

## Quando usar

- `agent_role == backend`

## Fluxo LangGraph (StateGraph)

Mapa completo: [_shared/STATEGRAPH_FLOW.md](../_shared/STATEGRAPH_FLOW.md)

| Board status | Nó | Papel (`backend`) |
|--------------|-----|-------------------|
| In Progress | `implement` | **Owner** — código, commit, `open_pr` |
| Ready for Code Review | — | Aguarda `backend-reviewer` |
| In Code Review | — | Corrige se `request_changes` |
| In Test | — | — (`qa-gate`) |
| In Pull Request | — | — merge owner |

Ciclo: `route → load_context → implement → apply → route`

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
- Migrations quando alterar schema (coordenar com `database`)
- Sem secrets no código; usar env/Secrets Manager
- Logs estruturados em fluxos críticos (SOS, auth)

## Palavras-chave de identificação

`API`, `endpoint`, `NestJS`, `service`, `controller`, `webhook`, `push`, `geofence`, `SOS`, `auth`, `pareamento`, `LGPD`, `Stripe`

## Métricas no PR

Incluir no body: `task_id`, `agent_role: backend`, `story_points`, `rice`, `wsjf`, `files_changed_count`, `duration_minutes`.
