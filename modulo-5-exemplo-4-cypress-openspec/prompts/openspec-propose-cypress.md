# Template — `/opsx:propose add-cypress-e2e`

Copie e adapte. Referência UNIPDS arquivada:

`cfp-platform/openspec/changes/archive/2026-03-31-add-cypress-e2e/`

## Comando no Cursor

```
/opsx:propose add-cypress-e2e
```

## proposal.md — checklist

- [ ] **Why** — garantir regressão E2E das specs de comportamento (Ex. 3)
- [ ] **What Changes** — projeto `frontend-cypress-e2e`, specs `.cy.ts`
- [ ] **Capabilities** — nova `cfp-cypress-e2e`
- [ ] **Impact** — `cfp-platform/`, sem alterar API

## design.md — checklist

- [ ] `baseUrl`: `http://localhost:4200`
- [ ] Estrutura: `frontend-cypress-e2e/src/e2e/*.cy.ts`
- [ ] Seletores: `#name`, `#email`, `#talkTitle`, `.submit-btn`, `.glass-table`
- [ ] Cenários mapeados de `openspec/specs/cfp-submission/` e `cfp-dashboard/`
- [ ] Non-goals: sem visual regression, sem API mocking

## tasks.md — checklist

- [ ] Adicionar Cypress ao workspace Nx
- [ ] Criar projeto `frontend-cypress-e2e`
- [ ] `cfp-submission.cy.ts` — happy path
- [ ] `navigation.cy.ts` — nav principal
- [ ] `cfp-dashboard.cy.ts` — submissão na tabela
- [ ] `nx e2e frontend-e2e` verde

## Após propose

```
/opsx:apply add-cypress-e2e
/opsx:archive add-cypress-e2e
```
