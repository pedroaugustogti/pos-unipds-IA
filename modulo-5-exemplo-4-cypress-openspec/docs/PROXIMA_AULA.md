# Próxima Aula — Exemplo 5: Playwright MCP

> Scaffold: [`modulo-5-exemplo-5-playwright-mcp`](../../modulo-5-exemplo-5-playwright-mcp/)

## Objetivos

1. Conectar **Playwright Test MCP** no CFP Platform
2. Usar agentes 🎭 planner / generator / healer para automação E2E
3. Gerar planos em `specs/` e testes em `frontend-e2e/src/`
4. Comparar Playwright MCP vs Cypress `cy.prompt()` (Ex. 4)

## Pré-requisito — Playwright MCP

Guia: [`PLAYWRIGHT_MCP.md`](PLAYWRIGHT_MCP.md)

```bash
cd ../modulo-5-exemplo-3-openspec-cfp/cfp-platform
npm install
npx playwright install chromium
npx nx run-many -t serve -p api frontend
```

No Cursor: **Settings → MCP** → `playwright-test-cfp` verde.

## Comandos de validação

```bash
cd ../modulo-5-exemplo-3-openspec-cfp/cfp-platform
npx playwright test frontend-e2e/src/seed.spec.ts --config frontend-e2e/playwright.config.ts
npx nx e2e frontend-playwright-e2e
```

## Referência UNIPDS

[modulo-04 — Playwright](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-04)
