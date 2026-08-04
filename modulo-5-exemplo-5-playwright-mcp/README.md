# Playwright MCP — Automação E2E com Agentes

**Módulo 5 — Exemplo 5** (`modulo-5-exemplo-5-playwright-mcp`)

Automação de testes E2E no **CFP Platform** com **Playwright MCP**: agentes 🎭 planner, generator e healer exploram a aplicação, geram specs e corrigem testes via linguagem natural.

**Referência UNIPDS:** [modulo-04 Playwright](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-04) · [Test Agents](https://playwright.dev/docs/test-agents)

## Contexto

| Anterior | Esta aula | Próxima |
|----------|-----------|---------|
| Ex. 4 — Cypress + OpenSpec ✅ | **Ex. 5 — Playwright MCP** | — |

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
├── docs/              ← a preencher na aula
└── prompts/
    └── playwright-mcp-event-registration.md   ← lab cadastro de evento
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

- [x] Lab cadastro de evento documentado e validado via MCP
- [ ] `playwright-test-cfp` MCP conectado no Cursor (aluno)
- [ ] `frontend-e2e/src/seed.spec.ts` passa
- [ ] Plano gerado em `cfp-platform/specs/`
- [ ] Teste gerado pelo agente generator executa com sucesso
- [ ] Healer corrige pelo menos um cenário quebrado (lab)

## Anterior

[`modulo-5-exemplo-4-cypress-openspec`](../modulo-5-exemplo-4-cypress-openspec/)
