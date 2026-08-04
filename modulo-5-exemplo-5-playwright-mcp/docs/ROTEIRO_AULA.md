# Roteiro de Aula — Playwright MCP (~2h)

**Referência UNIPDS:** [modulo-04 Playwright](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-04)

**App alvo:** `../modulo-5-exemplo-3-openspec-cfp/cfp-platform/`

## Contexto

| Anterior | Esta aula | Próxima |
|----------|-----------|---------|
| Ex. 4 — Cypress + OpenSpec ✅ | **Ex. 5 — Playwright MCP** ✅ | Ex. 6 — BragBot + Genkit |

## Roteiro

### 1. Recapitulação Cypress (10 min)

- Ex. 4: `cy.prompt()`, Cypress Cloud, specs em `frontend-cypress-e2e/`
- Pergunta: e se a IA pudesse **planejar, gerar e curar** testes Playwright?

### 2. Playwright Test Agents (15 min)

- Agentes 🎭 **planner → generator → healer**
- MCP `playwright-test-cfp` no Cursor
- Guia: [`../modulo-5-exemplo-4-cypress-openspec/docs/PLAYWRIGHT_MCP.md`](../modulo-5-exemplo-4-cypress-openspec/docs/PLAYWRIGHT_MCP.md)

### 3. Lab 1 — Conectar MCP (20 min)

```bash
cd ../modulo-5-exemplo-3-openspec-cfp/cfp-platform
npm install
npx playwright install chromium
npx nx run-many -t serve -p api frontend
```

No Cursor: **Settings → MCP** → `playwright-test-cfp` verde.

### 4. Lab 2 — Cadastro de evento via MCP (30 min)

Prompt: [`prompts/playwright-mcp-event-registration.md`](../prompts/playwright-mcp-event-registration.md)

Fluxo validado:
1. `planner_setup_page`
2. `browser_navigate` → `/event/new`
3. `browser_fill_form` + `browser_click`
4. `browser_verify_text_visible` → **"Evento cadastrado com sucesso!"**

### 5. Lab 3 — Planner gera plano (25 min)

- Invocar agent `playwright-test-planner`
- Salvar plano em `cfp-platform/specs/`
- Revisar cenários vs OpenSpec Ex. 3

### 6. Lab 4 — Generator + Healer (25 min)

- Generator: criar spec a partir do plano
- Healer: quebrar seletor propositalmente e corrigir via agente

### 7. Comparativo e encerramento (15 min)

| Ferramenta | Papel da IA | Artefato |
|------------|-------------|----------|
| Cypress `cy.prompt()` | Gera steps no teste | `.cy.ts` |
| Playwright MCP | Explora, planeja, gera, cura | `specs/` + `.spec.ts` |
| Genkit (Ex. 6) | Gera conteúdo no produto | Brag Document |

Próxima aula: [`docs/PROXIMA_AULA.md`](PROXIMA_AULA.md)
