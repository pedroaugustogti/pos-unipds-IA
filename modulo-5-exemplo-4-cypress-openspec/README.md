# Cypress + OpenSpec — CFP Platform

**Módulo 5 — Exemplo 4** (`modulo-5-exemplo-4-cypress-openspec`)

Testes E2E com **Cypress** guiados por **OpenSpec**: specs → change `add-cypress-e2e` → implementação → archive.

**Referência UNIPDS:** [modulo-04](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-04)

## Objetivo

1. **Propor** change `add-cypress-e2e` com cenários E2E
2. **Aplicar** projeto Cypress no monorepo Nx
3. **Executar** testes via browser (`open-cypress`) e headless (`e2e`)
4. **Arquivar** em `openspec/specs/cfp-cypress-e2e/`

## Contexto

| Anterior | Esta aula | Próxima |
|----------|-----------|---------|
| Ex. 3 — OpenSpec + CFP ✅ | **Ex. 4 — Cypress + OpenSpec** | Ex. 5 — AI Integration |

## Estrutura

```
modulo-5-exemplo-4-cypress-openspec/
├── README.md
├── docs/          ← roteiro, evidências, fluxo
└── prompts/       ← propose + spec→cypress
```

**App alvo:** [`../modulo-5-exemplo-3-openspec-cfp/cfp-platform/`](../modulo-5-exemplo-3-openspec-cfp/cfp-platform/)

| Pasta física | Projeto Nx | Runner |
|--------------|------------|--------|
| `frontend-cypress-e2e/` | `frontend-e2e` | Cypress |
| `frontend-e2e/` | `frontend-playwright-e2e` | Playwright (Ex. 3) |

## Início rápido

```bash
cd ../modulo-5-exemplo-3-openspec-cfp/cfp-platform
npm install
npx nx run-many -t serve -p api frontend

# Headless
npx nx e2e frontend-e2e

# Browser interativo
npx nx open-cypress frontend-e2e
```

## Fluxo OpenSpec

```
/opsx:propose add-cypress-e2e → /opsx:apply → /opsx:archive
```

Archive de referência: `cfp-platform/openspec/changes/archive/2026-03-31-add-cypress-e2e/`

## Critérios de sucesso

- [ ] Change `add-cypress-e2e` explorada/arquivada
- [ ] ≥ 3 specs em `frontend-cypress-e2e/src/e2e/`
- [ ] `npx nx e2e frontend-e2e` verde
- [ ] `npx nx open-cypress frontend-e2e` validado no browser
- [ ] `docs/EVIDENCIAS_ACEITE.md` preenchido

## Anterior / Próximo

- Anterior: [`modulo-5-exemplo-3-openspec-cfp`](../modulo-5-exemplo-3-openspec-cfp/)
- Próximo: [modulo-05 UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-05) — AI Integration
