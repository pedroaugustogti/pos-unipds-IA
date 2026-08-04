# Evidências de Aceite — Exemplo 4 (Cypress + OpenSpec)

Validação executada em **2026-08-04**.

## Comandos executados

```bash
cd ../modulo-5-exemplo-3-openspec-cfp/cfp-platform

# Servidores (já em execução: :4200 + :3000)
npx nx run-many -t serve -p api frontend

# Specs determinísticos (3/3 verde)
npx cypress run --config-file frontend-cypress-e2e/cypress.config.ts \
  --spec "frontend-cypress-e2e/src/e2e/cfp-dashboard.cy.ts,frontend-cypress-e2e/src/e2e/cfp-submission.cy.ts,frontend-cypress-e2e/src/e2e/navigation.cy.ts"

# Playwright baseline Ex. 3 (9/9 verde)
npx playwright test frontend-e2e/src/aceite.spec.ts --config frontend-e2e/playwright.config.ts

# OpenSpec
openspec list --specs

# Lab cy.prompt (requer CYPRESS_RECORD_KEY + --record)
npm run cy:run:ai -- --record
```

## Checklist

| Critério | Status | Evidência |
|----------|--------|-----------|
| `openspec/specs/cfp-cypress-e2e/` existe | ✅ | `openspec list --specs` → `cfp-cypress-e2e` |
| Change arquivada em `changes/archive/` | ✅ | `openspec/changes/archive/2026-03-31-add-cypress-e2e/` |
| Projeto `frontend-e2e` no monorepo | ✅ | `nx show project frontend-e2e` |
| Spec submissão CFP (happy path) | ✅ | `cfp-submission.cy.ts` — 1 passing |
| Spec navegação entre rotas | ✅ | `navigation.cy.ts` — 1 passing |
| Spec submissão no dashboard | ✅ | `cfp-dashboard.cy.ts` — 1 passing |
| Spec AI `cy.prompt` cadastro evento | ✅ | `event-registration-ai.cy.ts` — `cy.prompt()` + `projectId: axsqin` |
| Specs determinísticos Cypress | ✅ | **3/3 passing** (~4s) |
| Playwright `aceite.spec.ts` continua verde | ✅ | **9/9 passing** (~7s) |

## URLs verificadas

| URL | OK |
|-----|-----|
| http://localhost:4200/submit-talk | ✅ HTTP 200 |
| http://localhost:4200/dashboard | ✅ HTTP 200 |
| http://localhost:4200/event/new | ✅ HTTP 200 |

## Registro de execução

| Lab | Prompt / comando | Resultado |
|-----|------------------|-----------|
| Lab 1 | Archive `add-cypress-e2e` | ✅ proposal, design, tasks, specs |
| Lab 2 | `/opsx:propose add-cypress-e2e` | ✅ change arquivada como referência |
| Lab 3 | Cypress specs determinísticos | ✅ 3/3 passing |
| Lab 4 | `event-registration-ai.cy.ts` + `cy.prompt` | ✅ spec + Cloud `projectId: axsqin` |
| Lab 5 | `cypress-from-spec.md` | ✅ specs mapeados aos `.cy.ts` |

## Nota — `cy.prompt` headless

O spec `event-registration-ai.cy.ts` exige **Cypress Cloud** (`projectId` + `--record` ou login no `open-cypress`). Sem `CYPRESS_RECORD_KEY`, `cy:run:ai` falha com erro de conexão — comportamento esperado. Guia: [`CYPRESS_CLOUD_SETUP.md`](CYPRESS_CLOUD_SETUP.md).

## Resultado consolidado

| Suite | Resultado |
|-------|-----------|
| Cypress determinístico (3 specs) | ✅ All passed |
| Cypress AI (`cy.prompt`) | ✅ Implementado + Cloud configurado |
| Playwright aceite (Ex. 3) | ✅ 9/9 passed |
| OpenSpec `cfp-cypress-e2e` | ✅ Spec arquivada |
