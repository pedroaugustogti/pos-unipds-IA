# Playwright MCP — Automação E2E com Agentes

**Módulo 5 — Exemplo 5** (`modulo-5-exemplo-5-playwright-mcp`)

Automação de testes E2E no **CFP Platform** com **Playwright MCP**: agentes 🎭 planner, generator e healer exploram a aplicação, geram specs e corrigem testes via linguagem natural.

**Referência UNIPDS:** [modulo-04 Playwright](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-04) · [Test Agents](https://playwright.dev/docs/test-agents)

## Contexto

| Anterior | Esta aula | Próxima |
|----------|-----------|---------|
| Ex. 4 — Cypress + OpenSpec ✅ | **Ex. 5 — Playwright MCP** ✅ | Ex. 6 — BragBot + Genkit |

## Objetivos

1. Conectar **Playwright Test MCP** no Cursor (`playwright-test-cfp`)
2. Usar agentes 🎭 **planner → generator → healer** no CFP Platform
3. Gerar planos em `specs/` e testes em `frontend-e2e/src/`
4. Comparar automação MCP (Playwright) vs `cy.prompt()` (Cypress, Ex. 4)

## Pré-requisitos

- Monorepo: [`../modulo-5-exemplo-3-openspec-cfp/cfp-platform/`](../modulo-5-exemplo-3-openspec-cfp/cfp-platform/)
- Guia MCP: [`../modulo-5-exemplo-4-cypress-openspec/docs/PLAYWRIGHT_MCP.md`](../modulo-5-exemplo-4-cypress-openspec/docs/PLAYWRIGHT_MCP.md)

## Estrutura

```
modulo-5-exemplo-5-playwright-mcp/
├── README.md
├── docs/
│   ├── ROTEIRO_AULA.md
│   ├── EVIDENCIAS_ACEITE.md
│   ├── HEALER_LAB.md             ← lab healer (seletor quebrado)
│   └── PROXIMA_AULA.md          ← Ex. 6 BragBot
└── prompts/
    └── playwright-mcp-event-registration.md
```

## Início rápido

```bash
cd ../modulo-5-exemplo-3-openspec-cfp/cfp-platform
npm install
$env:NODE_OPTIONS = "--use-system-ca"   # Windows — certificados corporativos
npx playwright install chromium
npx nx run-many -t serve -p api frontend
```

No Cursor:

1. **Settings → MCP** → `playwright-test-cfp` verde
2. Invocar o agent `playwright-test-planner` ou usar o prompt em [`prompts/playwright-mcp-event-registration.md`](prompts/playwright-mcp-event-registration.md)

## Lab validado

Prompt: [`prompts/playwright-mcp-event-registration.md`](prompts/playwright-mcp-event-registration.md)

Fluxo `/event/new` executado via MCP (`planner_setup_page` → `browser_fill_form` → `browser_click` → `browser_verify_text_visible`) com mensagem **"Evento cadastrado com sucesso!"**.

## Critérios de sucesso

Validação executada em **2026-08-04** — ver [`docs/EVIDENCIAS_ACEITE.md`](docs/EVIDENCIAS_ACEITE.md).

- [x] Lab cadastro de evento documentado e validado via MCP
- [x] MCP `playwright-test-cfp` configurado em `.cursor/mcp.json`
- [x] Agents planner / generator / healer em `cfp-platform/.cursor/agents/`
- [x] `frontend-e2e/src/seed.spec.ts` criado
- [x] Prompt em `prompts/playwright-mcp-event-registration.md`

## Checklist do aluno (aula)

Validação **2026-08-04** — todos os itens concluídos.

- [x] `playwright-test-cfp` MCP configurado (`.cursor/mcp.json` raiz + `cfp-platform/.cursor/mcp.json`)
- [x] `seed.spec.ts` passa localmente (**1/1**)
- [x] Plano em `cfp-platform/specs/event-registration.md`
- [x] Teste gerado `event-registration.spec.ts` executa com sucesso (**2/2**)
- [x] Healer corrige cenário quebrado — lab documentado em [`docs/HEALER_LAB.md`](docs/HEALER_LAB.md)

## Anterior

[`modulo-5-exemplo-4-cypress-openspec`](../modulo-5-exemplo-4-cypress-openspec/)

---

## Próxima aula

**Exemplo seguinte:** [`modulo-5-exemplo-6-brag-bot`](../modulo-5-exemplo-6-brag-bot/) ([modulo-05/brag-bot](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-05/brag-bot)).
