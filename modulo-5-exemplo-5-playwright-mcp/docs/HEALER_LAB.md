# Lab Healer — Exemplo 5 (Playwright MCP)

Documentação do exercício em que o agente 🎭 **healer** corrige um seletor quebrado.

## Cenário simulado

Após mudança de copy no botão de submit, um teste gerado falhava:

```typescript
// ❌ Antes (seletor desatualizado — simulação do healer)
await page.getByRole('button', { name: 'Salvar Evento' }).click();
```

Erro Playwright:

```
TimeoutError: locator.click: Timeout 10000ms exceeded.
waiting for getByRole('button', { name: 'Salvar Evento' })
```

## Correção pelo healer

O agente `playwright-test-healer` inspecionou o snapshot da página e corrigiu para o label real:

```typescript
// ✅ Depois — alinhado ao componente event-registration.component.html
await page.getByRole('button', { name: 'Cadastrar Evento' }).click();
```

## Arquivo final validado

A correção está aplicada em:

`cfp-platform/frontend-e2e/src/event-registration.spec.ts`

## Como reproduzir em sala

1. Quebre propositalmente o seletor do botão em `event-registration.spec.ts`
2. Rode `npx playwright test event-registration.spec.ts`
3. Invocar agente `playwright-test-healer` com o log de falha
4. Validar que o teste volta a passar

## Evidência

| Item | Status |
|------|--------|
| Falha reproduzida com seletor errado | ✅ Documentado |
| Healer sugere `Cadastrar Evento` | ✅ |
| Spec corrigida passa | ✅ `event-registration.spec.ts` |
