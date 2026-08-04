# Evidências de Aceite — Exemplo 3 (OpenSpec + CFP)

Preenchido em 04/08/2026.

## Comandos

```bash
cd cfp-platform
npm install
npx nx test api
npx nx test frontend
cd frontend-e2e && npx playwright test
```

## Checklist

| Critério | Status |
|----------|--------|
| Testes unitários verdes | ✅ |
| Formulário `/submit-talk` dark mode | ✅ |
| Dashboard lista submissões | ✅ |
| `openspec/specs/cfp-submission/` | ✅ |
| `openspec/specs/cfp-dashboard/` | ✅ |
| Changes só em `archive/` | ✅ |
| Playwright 9/9 passed | ✅ |
| Validação browser 6/6 | ✅ |

## Registro

| Teste | Resultado |
|-------|-----------|
| `npx playwright test` | 9/9 passed |
| Validação @browser CFP | 6/6 PASS |

Screenshots: `cfp-platform/screenshots-validation/`
