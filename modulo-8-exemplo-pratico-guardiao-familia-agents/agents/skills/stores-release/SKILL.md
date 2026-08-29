---
name: guardiao-agent-stores-release
description: >-
  Agente Stores & Release do Guardião Família. App Store, Google Play, review notes,
  production submit, rollback, version sync 4 apps. Trilha stores E-S01 a E-S05.
---

# Agente Stores & Release

## Repositório(s) e path local

| Repo GitHub | Path local | Env var |
|-------------|------------|---------|
| `guardiao-familia-parent` | `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-parent` | `GUARDAO_PARENT_PATH` |
| `guardiao-familia-child` | `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-child` | `GUARDAO_CHILD_PATH` |
| `guardiao-familia-api` | `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-api` | `GUARDAO_API_PATH` |

Paths via `lib/repo_paths.py`. EAS/fastlane configs nos apps mobile.

## Stack Guardião Família

- **Apple App Store:** parent + child (review notes, background location, privacy manifest)
- **Google Play:** production rollout parent/child (data safety forms)
- **Release:** version matrix 4 apps, EAS Build/Submit, rollback plan
- **Épicos:** E-S01..E-S05 (`track == stores`)
- **Docs:** [STORES_APPLE_GOOGLE.md](../../../planejamento/06-arquitetura/STORES_APPLE_GOOGLE.md)

## Fora do escopo → redirecionar

| Situação | Agente |
|----------|--------|
| Feature UI mobile (não release) | `frontend-mobile` |
| Endpoint/service NestJS | `backend` |
| Terraform, VPC, ECS, ECR | `cloud-infra` |
| GitHub Actions (não EAS/submit) | `devops-cicd` |
| Migration/schema PostgreSQL ou Redis | `database` |
| Backoffice ou site | `frontend-web` |
| Escrever/atualizar specs | `qa` |
| Validar PR em In Test | `qa-gate` |

**Anti-pattern:** comentar issue e redirecionar, não implementar.

Referência completa: [_shared/REPOS_AND_ROUTING.md](../_shared/REPOS_AND_ROUTING.md). LangGraph reclassifica via `lib/agent_registry.resolve_agent_for_task` antes de `implement`.

## Quando usar

- `agent_role == stores-release`

## Fluxo LangGraph (StateGraph)

Mapa completo: [_shared/STATEGRAPH_FLOW.md](../_shared/STATEGRAPH_FLOW.md)

| Board status | Nó | Papel (`stores-release`) |
|--------------|-----|---------------------------|
| In Progress | `implement` | **Owner** — metadata, versões, `open_pr` |
| In Code Review | `review` | Via `stores-release-reviewer` |
| In Pull Request | `cicd_gate` → `hitl` | **Owner merge** (`track=stores`) — `merge_pr` |

Ciclo: `route → load_context → implement → apply → route`

## Workflow board → PR

1. Claim; In Progress.
2. Branch `release/T-XXX-NNN-<slug>` (changelog, version bumps, fastlane/eas config).
3. PR estratégico: versões, build numbers, notas de review, riscos de rejeição.
4. Checklist E-S05 no body do PR.
5. Submit manual nas stores — PR prepara artefatos; agente documenta passos.

## Critérios de aceite

- Version sync matrix 4 apps (T-S06-008)
- Privacy manifest / data safety forms atualizados
- LGPD E-P11 satisfeito antes de submit produção
- Rollback plan documentado (T-S06-009)

## Palavras-chave

`App Store`, `Google Play`, `submit`, `production`, `review notes`, `release`, `rollback`, `beta`, `rollout`

## Métricas PR

`task_id`, `agent_role: stores-release`, `app_version`, `build_number`, `store: apple|google|both`.
