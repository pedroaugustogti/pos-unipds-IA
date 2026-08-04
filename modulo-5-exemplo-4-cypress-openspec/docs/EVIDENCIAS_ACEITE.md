# Evidências de Aceite — Exemplo 4 (Cypress + OpenSpec)

Preencher após a aula.

## Comandos de validação

```bash
cd ../modulo-5-exemplo-3-openspec-cfp/cfp-platform
npm install

# Servidores
npx nx run-many -t serve -p api frontend

# Cypress E2E
npx nx e2e frontend-e2e

# Cypress UI (debug)
npx nx open-cypress frontend-e2e

# OpenSpec
openspec list --specs
```

## Checklist

| Critério | Status | Evidência |
|----------|--------|-----------|
| `openspec/specs/cfp-cypress-e2e/` existe | ⬜ | `openspec list --specs` |
| Change arquivada em `changes/archive/` | ⬜ | fs check |
| Projeto `frontend-e2e` no monorepo | ⬜ | `nx show project frontend-e2e` |
| Spec submissão CFP (happy path) | ⬜ | `cfp-submission.cy.ts` |
| Spec navegação entre rotas | ⬜ | `navigation.cy.ts` |
| Spec submissão no dashboard | ⬜ | `cfp-dashboard.cy.ts` |
| `nx e2e frontend-e2e` verde | ⬜ | output terminal |
| Playwright `aceite.spec.ts` continua verde | ⬜ | baseline Ex. 3 |

## URLs verificadas

| URL | OK |
|-----|-----|
| http://localhost:4200/submit-talk | ⬜ |
| http://localhost:4200/dashboard | ⬜ |
| http://localhost:4200/event/new | ⬜ |

## Registro de execução

| Lab | Prompt / comando | Resultado |
|-----|------------------|-----------|
| Lab 1 | Explorar archive `add-cypress-e2e` | |
| Lab 2 | `/opsx:propose add-cypress-e2e` | |
| Lab 3 | `nx e2e frontend-e2e` | |
| Lab 4 | `cypress-from-spec.md` | |
