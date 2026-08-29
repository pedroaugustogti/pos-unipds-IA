---
name: guardiao-agent-frontend-web
description: >-
  Agente Frontend Web do Guardião Família. Tasks em guardiao-familia-backoffice
  (Next.js) e guardiao-familia-site (HTML/Cloudflare). Board, commit e PR estratégico.
---

## Base de conhecimento

Consulte [`./KNOWLEDGE.md`](./KNOWLEDGE.md) — mapa de decisão de **todas** as pastas do módulo 8 (gerado dos READMEs).


# Agente Frontend Web — backoffice & site

## Repositório(s) e path local

| Repo GitHub | Path local | Env var |
|-------------|------------|---------|
| `guardiao-familia-backoffice` | `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-backoffice` | `GUARDAO_BACKOFFICE_PATH` |
| `guardiao-familia-site` | `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-site` | `GUARDAO_SITE_PATH` |

Paths via `lib/repo_paths.py`.

## Stack Guardião Família

| Repo | Stack | Deploy | Branch |
|------|-------|--------|--------|
| backoffice | Next.js 14+, React, TypeScript, auth/roles admin | SSM sa-east-1 | `master` |
| site | HTML estático, JS vanilla, chatbot | Cloudflare Pages | `main` |

## Fora do escopo → redirecionar

| Situação | Agente |
|----------|--------|
| Endpoint/service NestJS | `backend` |
| Terraform, VPC, ECS, ECR | `cloud-infra` |
| GitHub Actions, deploy pipeline | `devops-cicd` |
| Migration PostgreSQL / Redis RDS | `database` |
| Tela parent/child mobile | `frontend-mobile` |
| Escrever/atualizar specs | `qa` |
| Validar PR em In Test | `qa-gate` |
| Submit App Store / Play | `stores-release` |

**Anti-pattern:** comentar issue e redirecionar, não implementar.

Referência completa: [_shared/REPOS_AND_ROUTING.md](../_shared/REPOS_AND_ROUTING.md). LangGraph reclassifica via `lib/agent_registry.resolve_agent_for_task` antes de `implement`.

## Quando usar

- `agent_role == frontend-web`

## Fluxo LangGraph (StateGraph)

Mapa completo: [_shared/STATEGRAPH_FLOW.md](../_shared/STATEGRAPH_FLOW.md)

| Board status | Nó | Papel (`frontend-web`) |
|--------------|-----|------------------------|
| In Progress | `implement` | **Owner** — backoffice/site, `open_pr` |
| Ready for Code Review | — | Aguarda `frontend-web-reviewer` |
| In Code Review | — | Corrige se `request_changes` |
| In Test | — | Playwright via `qa-gate` |
| In Pull Request | — | — merge owner |

Ciclo: `route → load_context → implement → apply → route`

## Workflow board → PR

1. Claim + In Progress.
2. Branch `feat/T-XXX-NNN-<slug>`.
3. Implementar páginas/componentes; respeitar roles (backoffice).
4. Commit + PR estratégico.
5. **Ready for Code Review** no board (`mark_task_in_review`).

## Critérios de aceite

- Backoffice: auth/role guard nas rotas admin
- Site: SEO básico, LGPD links, chatbot funcional se task envolver
- Responsivo mobile-first no site
- Sem breaking changes em URLs públicas sem redirect

## Palavras-chave

`backoffice`, `Next.js`, `site`, `landing`, `chatbot`, `Cloudflare`, `dashboard`, `leads`

## Métricas PR

`task_id`, `agent_role: frontend-web`, `repo`, `pages_affected[]`.
