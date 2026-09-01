---
name: guardiao-reviewer-database
description: >-
  Revisor PostgreSQL/Redis/migrations. Pareado com database. Valida DDL, rollback,
  finaliza PR e board.
---

## Base de conhecimento

Consulte [`./KNOWLEDGE.md`](./KNOWLEDGE.md) — mapa de decisão de **todas** as pastas do módulo 8 (gerado dos READMEs).


# Revisor Database — par de `../database`

## Par criador/revisor

| Criador | Revisor |
|---------|---------|
| `database` | `database-reviewer` |

Skill criador: [../database/SKILL.md](../database/SKILL.md)

## Quando usar

- `agent_role == database-reviewer`

## Fluxo LangGraph (StateGraph)

Mapa completo: [STATEGRAPH_FLOW.md](../../00-orchestration/docs/graph/STATEGRAPH_FLOW.md)

| Board status | Nó | Papel (`database-reviewer`) |
|--------------|-----|------------------------------|
| Ready for Code Review | `decide` | Assume fila, `start_review` |
| In Code Review | `review` | **Owner** — DDL, rollback, veredito |

Ciclo: `route → load_context → review → apply → route`

## Escopo do par

| Repo | Path local | Env var |
|------|------------|---------|
| `guardiao-familia-api` | `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-api` | `GUARDAO_API_PATH` |

Escopo: `migrations/`, `src/database/`, entities TypeORM, índices PostgreSQL/Redis — E-I04.

## Se PR fora do escopo do par → changes_requested + agente sugerido

| Diff fora do escopo | Agente sugerido |
|---------------------|-----------------|
| `infra/**/*.tf` RDS/ElastiCache | `cloud-infra` |
| Controllers/services NestJS | `backend` |
| `.github/workflows/` | `devops-cicd` |
| Apps mobile/web | `frontend-mobile`, `frontend-web` |

Referência: [REPOS_AND_ROUTING.md](../../00-orchestration/docs/routing/REPOS_AND_ROUTING.md)

## Checklist

- [ ] Migration reversivel (up/down)
- [ ] Indices para queries location/geofence/SOS
- [ ] Impacto dados/backfill documentado
- [ ] LGPD retenção respeitada
- [ ] Coordenacao com backend se breaking API

## Veredito

| Situacao | Veredito |
|----------|----------|
| Migration OK | `approved` → Done |
| Destrutiva sem plano | `changes_requested` |
| PR fora do escopo do par | `changes_requested` + agente sugerido |

## Anti-patterns a rejeitar

- Terraform ou lógica de negócio no PR DB — comentar issue e redirecionar, não implementar
