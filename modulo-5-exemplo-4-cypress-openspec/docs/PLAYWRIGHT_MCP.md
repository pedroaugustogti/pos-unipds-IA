# Playwright MCP — CFP Platform

Configuração do **Playwright Test MCP** para agentes 🎭 planner, generator e healer — preparação para o **Ex. 5 (Playwright MCP)**.

**Referência:** [Playwright Test Agents](https://playwright.dev/docs/test-agents) · [Módulo 3 Ex. 3 — dev instructions](../../modulo-3-exemplo-3-dev-instructions-events/)

## Arquivos

| Artefato | Local |
|----------|-------|
| MCP (workspace CFP) | `cfp-platform/.cursor/mcp.json` → `playwright-test` |
| MCP (repo raiz) | `.cursor/mcp.json` → `playwright-test-cfp` |
| Agents Cursor | `cfp-platform/.cursor/agents/playwright-test-*.md` |
| Agents VS Code | `cfp-platform/.github/agents/*.agent.md` |
| Seed test | `frontend-e2e/src/seed.spec.ts` |
| Planos | `cfp-platform/specs/` |
| Config Playwright | `frontend-e2e/playwright.config.ts` |

## Conectar no Cursor

1. Abra o workspace na **raiz do repo** ou em `cfp-platform/`
2. **Settings → MCP** → recarregue servidores
3. Confirme **`playwright-test-cfp`** (raiz) ou **`playwright-test`** (pasta cfp-platform) **verde**

### Pré-requisitos

```bash
cd modulo-5-exemplo-3-openspec-cfp/cfp-platform
npm install
# Windows com proxy/certificado corporativo:
# $env:NODE_OPTIONS = "--use-system-ca"
npx playwright install chromium
npx nx run-many -t serve -p api frontend
```

## Lab — Cadastro de Evento

Prompt completo: [`modulo-5-exemplo-5-playwright-mcp/prompts/playwright-mcp-event-registration.md`](../../modulo-5-exemplo-5-playwright-mcp/prompts/playwright-mcp-event-registration.md)

Fluxo validado em `/event/new` com mensagem **"Evento cadastrado com sucesso!"**.

## Fluxo planner → generator → healer

```mermaid
flowchart LR
  A[🎭 planner] -->|specs/plan.md| B[🎭 generator]
  B -->|frontend-e2e/src/*.spec.ts| C[🎭 healer]
  C -->|testes verdes| D[CI / aceite]
```

### 1. Planner

Agent: `playwright-test-planner`

```
Gere um plano de testes para submissão CFP em /submit-talk
usando o seed frontend-e2e/src/seed.spec.ts
```

Salva em `specs/`.

### 2. Generator

Agent: `playwright-test-generator`

```
Gere testes Playwright a partir de specs/<plano>.md
```

### 3. Healer

Agent: `playwright-test-healer`

```
Corrija os testes falhando em frontend-e2e/src/
```

## Comandos

```bash
# Seed isolado
cd frontend-e2e && npx playwright test seed.spec.ts

# Suite aceite (Ex. 3)
npx nx e2e frontend-playwright-e2e

# Regenerar agents (após upgrade Playwright)
npx playwright init-agents --loop=vscode -c frontend-e2e/playwright.config.ts
```

## Troubleshooting

| Problema | Solução |
|----------|---------|
| MCP vermelho / `npx playwright` não encontrado | Rodar `npm install` em `cfp-platform/` |
| `No config option` | Servidor deve iniciar em `cfp-platform/` com `--config frontend-e2e/playwright.config.ts` |
| Página em branco | Subir `api` + `frontend` (4200/3000) |
| Chromium não instalado | `NODE_OPTIONS=--use-system-ca npx playwright install chromium` (Windows) |
| `Must setup test before interacting` | Chamar `planner_setup_page` antes de `browser_*` |
| Tools não aparecem | Reload Window no Cursor após editar `mcp.json` |

## Próxima aula

[`modulo-5-exemplo-5-playwright-mcp`](../../modulo-5-exemplo-5-playwright-mcp/) — automação E2E com agentes Playwright MCP.
