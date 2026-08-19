---
name: guardiao-agent-frontend-web
description: >-
  Agente Frontend Web do Guardião Família. Tasks em guardiao-familia-backoffice
  (Next.js) e guardiao-familia-site (HTML/Cloudflare). Board, commit e PR estratégico.
---

# Agente Frontend Web — backoffice & site

## Quando usar

- `agent_role == frontend-web`
- Repos: `guardiao-familia-backoffice`, `guardiao-familia-site`
- Épicos E-P12 (backoffice), E-P13 (site)

## Stack

| Repo | Stack | Deploy | Branch |
|------|-------|--------|--------|
| backoffice | Next.js, React, TypeScript | SSM sa-east-1 | master |
| site | HTML estático, JS, chatbot | Cloudflare Pages | main |

**Clone:** `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-{backoffice|site}`

## Workflow board → PR

1. Claim + In Progress.
2. Branch `feat/T-XXX-NNN-<slug>`.
3. Implementar páginas/componentes; respeitar roles (backoffice).
4. Commit + PR estratégico.
5. In Review no board.

## Critérios de aceite

- Backoffice: auth/role guard nas rotas admin
- Site: SEO básico, LGPD links, chatbot funcional se task envolver
- Responsivo mobile-first no site
- Sem breaking changes em URLs públicas sem redirect

## Palavras-chave

`backoffice`, `Next.js`, `site`, `landing`, `chatbot`, `Cloudflare`, `dashboard`, `leads`

## Métricas PR

`task_id`, `agent_role: frontend-web`, `repo`, `pages_affected[]`.
