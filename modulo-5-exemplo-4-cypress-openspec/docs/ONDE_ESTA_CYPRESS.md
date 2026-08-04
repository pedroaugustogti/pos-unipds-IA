# Onde está o Cypress — Exemplo 4

Mapa de **todos os artefatos Cypress** no repositório.

## Monorepo (código executável)

Base: [`modulo-5-exemplo-3-openspec-cfp/cfp-platform/`](../modulo-5-exemplo-3-openspec-cfp/cfp-platform/)

| Local | Função |
|-------|--------|
| `frontend-cypress-e2e/cypress.config.ts` | Configuração (`baseUrl`, `specPattern`, `supportFile`) |
| `frontend-cypress-e2e/project.json` | Projeto Nx **`frontend-e2e`** — targets `e2e` e `open-cypress` |
| `frontend-cypress-e2e/src/e2e/*.cy.ts` | Specs executáveis |
| `frontend-cypress-e2e/src/support/e2e.ts` | Support file global |
| `frontend-cypress-e2e/src/support/commands.ts` | Custom commands (extensível) |
| `package.json` → `devDependencies.cypress` | Binário Cypress |

### Specs E2E (determinísticos — Ex. 3/4)

| Arquivo | Rota | Tipo |
|---------|------|------|
| `cfp-submission.cy.ts` | `/submit-talk` | Seletores CSS (`#name`, `.submit-btn`) |
| `navigation.cy.ts` | `/dashboard` → nav | `cy.contains`, `cy.get('nav')` |
| `cfp-dashboard.cy.ts` | submit + `/dashboard` | Fluxo completo na tabela |

### Spec AI-driven (`cy.prompt` — Ex. 4)

| Arquivo | Rota | Tipo |
|---------|------|------|
| **`event-registration-ai.cy.ts`** | `/event/new` | **`cy.prompt()`** — passos em linguagem natural |

## OpenSpec

| Local | Função |
|-------|--------|
| `openspec/changes/archive/2026-03-31-add-cypress-e2e/` | Change arquivada (proposal, design, tasks) |
| `openspec/changes/archive/.../specs/cfp-cypress-e2e/spec.md` | Delta spec E2E |
| `openspec/specs/cfp-cypress-e2e/spec.md` | Spec canônica após archive |
| `openspec/config.yaml` | Contexto menciona Cypress |

## Documentação Ex. 4

| Arquivo | Conteúdo |
|---------|----------|
| [`README.md`](../README.md) | Visão geral e comandos |
| [`docs/FLUXO_CYPRESS_OPENSPEC.md`](FLUXO_CYPRESS_OPENSPEC.md) | Fases propose → apply → archive |
| [`docs/ROTEIRO_AULA.md`](ROTEIRO_AULA.md) | Labs em sala |
| [`prompts/cypress-from-spec.md`](../prompts/cypress-from-spec.md) | Spec OpenSpec → `.cy.ts` |
| [`prompts/cypress-ai-prompt-testing.md`](../prompts/cypress-ai-prompt-testing.md) | Lab `cy.prompt()` |

## O que **não** é Cypress

| Local | Runner |
|-------|--------|
| `frontend-e2e/` (pasta) | **Playwright** — projeto Nx `frontend-playwright-e2e` |
| `frontend-e2e/src/aceite.spec.ts` | Playwright (aceite Ex. 3) |

## Comandos

```bash
cd ../modulo-5-exemplo-3-openspec-cfp/cfp-platform
npx nx run-many -t serve -p api frontend

# Todos os specs Cypress (inclui cy.prompt)
npx nx e2e frontend-e2e

# UI interativa (recomendado para cy.prompt + Cypress Cloud)
npx nx open-cypress frontend-e2e
```

> **`cy.prompt()`** requer Cypress **≥ 15.4** e login no **Cypress Cloud** no App (`cypress open`).
