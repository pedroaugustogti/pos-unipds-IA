# Lab — Cypress AI Driven Testing (`cy.prompt`)

Alinhado ao [UNIPDS modulo-04](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-04).

## Pré-requisitos

```bash
cd ../modulo-5-exemplo-3-openspec-cfp/cfp-platform
npm install
npx nx run-many -t serve -p api frontend
```

- Cypress **≥ 15.4** (`package.json`)
- Login no **Cypress Cloud** ao abrir `npx nx open-cypress frontend-e2e`

## Spec alvo

`cfp-platform/frontend-cypress-e2e/src/e2e/event-registration-ai.cy.ts`

## Código de referência

```typescript
describe('Cadastro de Eventos - AI Driven Testing', () => {
  it('Deve executar o fluxo de cadastro e validar o sucesso de forma semântica', () => {
    cy.visit('/event/new');

    cy.prompt([
      'Type "Auditório Oracle" in the Nome do Local field',
      'Type "Av. Dr. Chucri Zaidan, SP" in the Endereço field',
      'Type "500" in the Capacidade field',
      'Type "2026-12-31" in the Data do Evento field',
      'Click the button that submits or saves the event',
    ]);

    cy.prompt(['Verify that a success message is visible']);
  });
});
```

## Prompt para o agente (Cursor)

```
Abra o spec event-registration-ai.cy.ts e execute via Cypress.
Valide que cy.prompt preenche o formulário em /event/new e confirma
a mensagem "Evento cadastrado com sucesso!".
Documente no Command Log quais comandos Cypress foram gerados.
```

## Comparar: `cy.prompt` vs seletores

| Abordagem | Arquivo | Quando usar |
|-----------|---------|-------------|
| `cy.prompt()` | `event-registration-ai.cy.ts` | Exploração, protótipo, testes semânticos |
| `cy.get('#nome')` | `cfp-submission.cy.ts` | CI determinístico, regressão |

## Discussão

1. O que o `cy.prompt` gera no Command Log?
2. Quando copiar os comandos gerados para o spec fixo?
3. Por que o Ex. 3 usa Playwright e o Ex. 4 introduz Cypress?
