# Evidências de Aceite — Exemplo 5 (Playwright MCP)

Validação executada em **2026-08-04**.

## Comandos executados

```bash
cd ../modulo-5-exemplo-3-openspec-cfp/cfp-platform
npm install
npx playwright install chromium
npx nx run-many -t serve -p api frontend

# Seed + spec gerada (Ex. 5)
npx playwright test frontend-e2e/src/seed.spec.ts \
  frontend-e2e/src/event-registration.spec.ts \
  --config frontend-e2e/playwright.config.ts
```

## Checklist

| Critério | Status | Evidência |
|----------|--------|-----------|
| MCP `playwright-test-cfp` configurado | ✅ | `.cursor/mcp.json` (raiz) + `cfp-platform/.cursor/mcp.json` |
| `seed.spec.ts` passa | ✅ | **1/1 passing** (~6s) |
| Lab cadastro `/event/new` via MCP | ✅ | Mensagem **"Evento cadastrado com sucesso!"** (lab validado) |
| Plano em `cfp-platform/specs/` | ✅ | `specs/event-registration.md` |
| Spec gerada pelo generator executa | ✅ | `event-registration.spec.ts` — **2/2 passing** |
| Healer corrigiu cenário quebrado | ✅ | [`HEALER_LAB.md`](HEALER_LAB.md) — `Salvar Evento` → `Cadastrar Evento` |

## Artefatos criados

| Artefato | Caminho |
|----------|---------|
| Plano (planner) | `cfp-platform/specs/event-registration.md` |
| Teste (generator) | `cfp-platform/frontend-e2e/src/event-registration.spec.ts` |
| Lab healer | `docs/HEALER_LAB.md` |
| Prompt MCP | `prompts/playwright-mcp-event-registration.md` |
| Agents | `cfp-platform/.cursor/agents/playwright-test-{planner,generator,healer}.md` |

## Registro de execução

| Lab | Prompt / comando | Resultado |
|-----|------------------|-----------|
| Lab 2 | `playwright-mcp-event-registration.md` | ✅ `/event/new` + sucesso via MCP |
| Lab 3 | `playwright-test-planner` | ✅ `specs/event-registration.md` |
| Lab 4 | `playwright-test-generator` | ✅ `event-registration.spec.ts` 2/2 |
| Lab 4 | `playwright-test-healer` | ✅ Seletor corrigido — ver `HEALER_LAB.md` |

## Resultado consolidado

```
Running 3 tests using 1 worker
  3 passed (6.0s)
```

- `seed.spec.ts` — 1 test
- `event-registration.spec.ts` — 2 tests (happy path + validação)

## Próxima aula

[`modulo-5-exemplo-6-brag-bot`](../modulo-5-exemplo-6-brag-bot/) — BragBot + Genkit
