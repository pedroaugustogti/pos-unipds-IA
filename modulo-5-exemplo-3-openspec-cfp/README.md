# OpenSpec + CFP Platform

**Módulo 5 — Exemplo 3** (`modulo-5-exemplo-3-openspec-cfp`)

Construção do monorepo **cfp-platform** (Nx + Angular 21 + NestJS) com **OpenSpec** e agentes no Cursor, alinhado ao [modulo-03/cfp-platform UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-03/cfp-platform).

## Objetivo

Demonstrar o fluxo **spec-driven** com OpenSpec:

1. Scaffold Nx (infraestrutura)
2. `openspec init` com contexto rico
3. Changes pequenas (`propose` → `apply` → `archive`)
4. Styling UI (dark mode) como passo explícito

O código em `cfp-platform/` é o **estado final** após todas as fases. Guia completo: [`docs/FLUXO_OPENSPEC.md`](docs/FLUXO_OPENSPEC.md).

## Contexto da sequência do curso

| Anterior | Esta aula | Próxima |
|----------|-----------|---------|
| Ex. 2 — Prototyping UI ✅ | **Ex. 3 — OpenSpec + CFP** ✅ | Ex. 4 — Cypress → Ex. 5 — Playwright MCP |

## Estrutura

```
modulo-5-exemplo-3-openspec-cfp/
├── README.md
├── cfp-platform/
│   ├── api/
│   ├── frontend/
│   ├── shared-types/
│   ├── frontend-e2e/              ← Playwright (projeto Nx: frontend-playwright-e2e)
│   ├── frontend-cypress-e2e/      ← Cypress (projeto Nx: frontend-e2e)
│   ├── .cursor/agents/            ← agents Playwright MCP (Ex. 5)
│   └── openspec/
├── docs/
└── prompts/
```

## Início rápido

```bash
cd cfp-platform
npm install
npx nx test api
npx nx test frontend
npx nx run-many -t serve -p api frontend
```

| URL | Conteúdo |
|-----|----------|
| http://localhost:4200/dashboard | Dashboard |
| http://localhost:4200/talks/new | Formulário CFP |
| http://localhost:4200/submit-talk | Formulário CFP (alias) |
| http://localhost:4200/event/new | Cadastro de local do evento |

### Testes E2E

```bash
# Playwright (aceite)
cd frontend-e2e && npx playwright test

# Cypress determinístico (Ex. 4)
npx nx e2e frontend-e2e
npx nx open-cypress frontend-e2e

# Cypress AI — cy.prompt (Ex. 4, requer Cypress Cloud)
npm run cy:run:ai

# Playwright MCP — seed dos agentes (Ex. 5)
npx playwright test frontend-e2e/src/seed.spec.ts --config frontend-e2e/playwright.config.ts
```

## Critérios de sucesso

- [x] `cfp-platform` builda e testes passam
- [x] Formulário dark mode em `/talks/new`
- [x] `openspec/specs/` com `cfp-submission` e `cfp-dashboard`
- [x] Changes em `openspec/changes/archive/`
- [x] [`docs/EVIDENCIAS_ACEITE.md`](docs/EVIDENCIAS_ACEITE.md) preenchido

## Próximas aulas

- Ex. 4: [`modulo-5-exemplo-4-cypress-openspec`](../modulo-5-exemplo-4-cypress-openspec/)
- Ex. 5: [`modulo-5-exemplo-5-playwright-mcp`](../modulo-5-exemplo-5-playwright-mcp/) — guia MCP em [`PLAYWRIGHT_MCP.md`](../modulo-5-exemplo-4-cypress-openspec/docs/PLAYWRIGHT_MCP.md)
