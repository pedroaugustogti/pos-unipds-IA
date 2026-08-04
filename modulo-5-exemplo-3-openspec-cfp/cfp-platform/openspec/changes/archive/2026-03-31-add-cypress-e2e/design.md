## Context

The CFP Platform (Ex. 3) already has Playwright tests in `frontend-e2e/`. This change adds **Cypress** as a second E2E runner, introduced via OpenSpec to demonstrate spec-driven test planning (UNIPDS modulo-04).

## Goals

- Map OpenSpec Scenarios from `cfp-submission` and `cfp-dashboard` to Cypress `it()` blocks.
- Enable `npx nx e2e frontend-e2e` and `npx nx open-cypress frontend-e2e`.

## Decisions

### Project structure

```
frontend-cypress-e2e/
├── cypress.config.ts
├── project.json
└── src/
    ├── e2e/
    │   ├── cfp-submission.cy.ts
    │   ├── navigation.cy.ts
    │   └── cfp-dashboard.cy.ts
    └── support/
        ├── e2e.ts
        └── commands.ts
```

### Configuration

- **baseUrl**: `http://localhost:4200`
- **implicitDependencies**: `["frontend"]`
- **viewport**: 1280×800

### Selectors

Prefer stable IDs from the Angular template:

| Element | Selector |
|---------|----------|
| Full Name | `#name` |
| Email | `#email` |
| Talk Title | `#talkTitle` |
| Submit | `button.submit-btn` |
| Success | `.success-msg` |
| Dashboard table | `.glass-table tbody tr` |

### Non-goals

- Visual regression testing
- API mocking (tests hit real `POST /api/speakers`)
- Replacing Playwright (`frontend-e2e/` remains)
