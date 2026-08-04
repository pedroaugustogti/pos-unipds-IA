# Cypress Cloud — criar e conectar o projeto

O `cy.prompt()` exige um projeto vinculado ao **Cypress Cloud** com `projectId` no `cypress.config.ts`.

## 1. Criar conta (se necessário)

1. Acesse [https://cloud.cypress.io/](https://cloud.cypress.io/)
2. Crie conta gratuita ou faça login (GitHub/Google/e-mail)

## 2. Conectar via Cypress App (recomendado)

No monorepo:

```bash
cd ../modulo-5-exemplo-3-openspec-cfp/cfp-platform
npm install
npx nx open-cypress frontend-e2e
```

No Cypress App:

1. **Faça login** (canto superior direito → Sign in)
2. Aba **Runs** → **Connect to Cypress Cloud**
3. **Create new project**
   - Nome sugerido: `CFP Platform E2E`
   - Visibilidade: **Private** (recomendado)
4. **Setup Project** — o wizard grava o `projectId` em `frontend-cypress-e2e/cypress.config.ts`

## 3. Alternativa: criar no dashboard web

1. [cloud.cypress.io](https://cloud.cypress.io/) → sua organização
2. **Create project** → nome `CFP Platform E2E`
3. Copie o **Project ID** (6 caracteres, ex.: `a7bq2k`)
4. Cole em `frontend-cypress-e2e/cypress.config.ts`:

```typescript
export default defineConfig({
  projectId: 'SEU_PROJECT_ID',
  e2e: { /* ... */ },
});
```

## 4. Record Key (CI e headless com `--record`)

1. No Cloud: **Project → Settings → Record Keys**
2. Copie a key (GUID) — **não commitar**
3. Defina localmente:

```powershell
$env:CYPRESS_RECORD_KEY = "sua-record-key"
```

Ou no PowerShell de forma persistente na sessão:

```bash
# Linux/macOS
export CYPRESS_RECORD_KEY="sua-record-key"
```

## 5. Validar `cy.prompt`

```bash
cd ../modulo-5-exemplo-3-openspec-cfp/cfp-platform
npx nx run-many -t serve -p api frontend

# UI (recomendado para cy.prompt)
npx nx open-cypress frontend-e2e
# Executar: event-registration-ai.cy.ts

# Headless com gravação no Cloud
npx cypress run --config-file frontend-cypress-e2e/cypress.config.ts `
  --spec frontend-cypress-e2e/src/e2e/event-registration-ai.cy.ts `
  --record
```

## 6. Variáveis de ambiente (opcional)

| Variável | Uso |
|----------|-----|
| `CYPRESS_PROJECT_ID` | Substitui `projectId` no config (sem commitar) |
| `CYPRESS_RECORD_KEY` | Autentica gravação de runs |

## Troubleshooting

| Erro | Solução |
|------|---------|
| `cy.prompt requires a valid projectId` | Conectar projeto ao Cloud (passos 2 ou 3) |
| `PromptAuthenticationError` | Login no Cypress App ou `--record` + `CYPRESS_RECORD_KEY` |
| Wizard não acha o config | Rodar a partir de `cfp-platform/` com `--config-file frontend-cypress-e2e/cypress.config.ts` |
