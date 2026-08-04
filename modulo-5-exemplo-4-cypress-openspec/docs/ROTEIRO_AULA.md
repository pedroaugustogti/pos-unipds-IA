# Roteiro de Aula — Cypress + OpenSpec (~2h)

**Referência UNIPDS:** [modulo-04](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-04)

**App alvo:** `../modulo-5-exemplo-3-openspec-cfp/cfp-platform/`

## Contexto

| Anterior | Esta aula | Próxima |
|----------|-----------|---------|
| Ex. 3 — OpenSpec + CFP ✅ | **Ex. 4 — Cypress + OpenSpec** | Ex. 5 — Playwright MCP |

## Roteiro

### 1. Recapitulação (10 min)

- Ex. 3: specs → changes → código → archive
- Demo: `openspec/specs/cfp-submission/spec.md` — cenários em Gherkin
- Pergunta: como transformar Scenario em teste automatizado?

### 2. Introdução Cypress + OpenSpec (15 min)

- Mostrar [`FLUXO_CYPRESS_OPENSPEC.md`](FLUXO_CYPRESS_OPENSPEC.md)
- Comparar Playwright (`aceite.spec.ts`) vs Cypress (`frontend-cypress-e2e/`)
- Abrir change arquivada: `openspec/changes/archive/2026-03-31-add-cypress-e2e/`

### 3. Lab 1 — Explorar change arquivada (25 min)

Arquivos em `openspec/changes/archive/2026-03-31-add-cypress-e2e/`:

- `proposal.md` — capability `cfp-cypress-e2e`
- `design.md` — baseUrl, seletores, estrutura de pastas
- `tasks.md` — checklist
- `specs/cfp-cypress-e2e/spec.md` — cenários E2E

Exercício: mapear cada Scenario ao arquivo `.cy.ts` correspondente.

### 4. Lab 2 — Simular propose (20 min)

Prompt: [`prompts/openspec-propose-cypress.md`](../prompts/openspec-propose-cypress.md)

Em sala (sem implementar): `/opsx:propose add-cypress-e2e` e revisar artefatos vs archive.

### 5. Lab 3 — Rodar Cypress (30 min)

```bash
cd ../modulo-5-exemplo-3-openspec-cfp/cfp-platform
npx nx run-many -t serve -p api frontend

# Terminal 2
npx nx e2e frontend-e2e
npx nx open-cypress frontend-e2e   # debug interativo
```

Exercício: quebrar um seletor propositalmente e corrigir via Cypress UI.

### 6. Lab 4 — AI Driven Testing (`cy.prompt`) (15 min)

Mapa: [`docs/ONDE_ESTA_CYPRESS.md`](ONDE_ESTA_CYPRESS.md)

Prompt: [`prompts/cypress-ai-prompt-testing.md`](../prompts/cypress-ai-prompt-testing.md)

Spec: `frontend-cypress-e2e/src/e2e/event-registration-ai.cy.ts`

```bash
npx nx open-cypress frontend-e2e
# Login Cypress Cloud → executar "Cadastro de Eventos - AI Driven Testing"
```

### 7. Lab 5 — Spec → teste determinístico (10 min)

Prompt: [`prompts/cypress-from-spec.md`](../prompts/cypress-from-spec.md)

### 8. Encerramento (5 min)

- Preencher [`EVIDENCIAS_ACEITE.md`](EVIDENCIAS_ACEITE.md)
- Preview Ex. 5 (Playwright MCP — planner/generator/healer)

## Discussão

1. Por que OpenSpec **antes** de escrever Cypress?
2. `data-cy` vs seletores por texto/role — trade-offs
3. Cypress vs Playwright no mesmo monorepo — quando usar cada um?
4. Como archive de E2E difere de archive de feature?
5. Quando usar `cy.prompt()` vs seletores fixos no CI?
