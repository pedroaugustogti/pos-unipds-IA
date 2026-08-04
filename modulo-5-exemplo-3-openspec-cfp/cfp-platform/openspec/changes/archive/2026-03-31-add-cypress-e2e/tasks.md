## 1. Workspace setup

- [x] 1.1 Add `cypress` to `devDependencies`
- [x] 1.2 Create `frontend-cypress-e2e` Nx project

## 2. Cypress configuration

- [x] 2.1 `cypress.config.ts` with `baseUrl: http://localhost:4200`
- [x] 2.2 `src/support/e2e.ts` and `commands.ts`

## 3. E2E specs

- [x] 3.1 `cfp-submission.cy.ts` — happy path: fill form, submit, success message
- [x] 3.2 `navigation.cy.ts` — nav links between dashboard, submit-talk, event/new
- [x] 3.3 `cfp-dashboard.cy.ts` — submit via UI, verify row in dashboard table

## 4. Verification

- [x] 4.1 `npx nx e2e frontend-e2e` passes (with api + frontend running)
- [x] 4.2 Archive change → `openspec/specs/cfp-cypress-e2e/spec.md`
