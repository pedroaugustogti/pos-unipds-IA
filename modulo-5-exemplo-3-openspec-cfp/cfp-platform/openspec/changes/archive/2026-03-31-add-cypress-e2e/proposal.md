## Why

Automated E2E tests are needed to prevent regressions in the CFP submission and dashboard flows defined in Ex. 3 specs. Cypress provides an interactive debugging experience aligned with the UNIPDS modulo-04 curriculum.

## What Changes

- **E2E (Cypress)**: Add Nx project `frontend-cypress-e2e` with Cypress configuration targeting `http://localhost:4200`.
- **Specs**: Implement Cypress tests for CFP submission happy path, main navigation, and dashboard listing.
- **OpenSpec**: New capability `cfp-cypress-e2e` documenting E2E scenarios as canonical specs after archive.

## Capabilities

### New Capabilities

- `cfp-cypress-e2e`: End-to-end test scenarios for CFP Platform using Cypress, mapped from `cfp-submission` and `cfp-dashboard` behavior specs.

### Modified Capabilities

- None (tests only; no production code changes).

## Impact

- **frontend-cypress-e2e**: New Nx application with `src/e2e/*.cy.ts`.
- **package.json**: Add `cypress` dev dependency.
- **openspec/specs/**: New `cfp-cypress-e2e/` after archive.
