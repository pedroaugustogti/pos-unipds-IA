# Prompt — Spec OpenSpec → Cypress

Use após ler uma spec em `openspec/specs/`.

## Prompt

```
Leia openspec/specs/cfp-submission/spec.md e, para cada Scenario listado,
gere um teste Cypress em frontend-cypress-e2e/src/e2e/.

Regras:
- Um describe() por Requirement
- Um it() por Scenario
- Comentário com o texto do Scenario antes de cada it()
- baseUrl http://localhost:4200
- Usar cy.get('#name'), cy.get('#email'), cy.get('#talkTitle')
- cy.contains('Submit Proposal').click()
- cy.contains('Proposal submitted successfully').should('be.visible')
- Não duplicar testes já existentes em frontend-cypress-e2e/src/e2e/

Ao final, rode: npx nx e2e frontend-e2e
```

## Exemplo de mapeamento

**Spec (Gherkin):**

```markdown
#### Scenario: Valid Submission
- **WHEN** user fills name, email, talkTitle and clicks Submit
- **THEN** success message is shown
```

**Cypress:**

```typescript
it('Valid Submission', () => {
  cy.visit('/submit-talk');
  cy.get('#name').type('Test User');
  cy.get('#email').type('test@example.com');
  cy.get('#talkTitle').type('Demo');
  cy.contains('button', 'Submit Proposal').click();
  cy.contains('Proposal submitted successfully').should('be.visible');
});
```
