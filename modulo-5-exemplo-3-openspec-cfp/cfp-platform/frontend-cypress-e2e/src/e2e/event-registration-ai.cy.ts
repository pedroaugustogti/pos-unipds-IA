// spec: openspec/specs/cfp-cypress-e2e/spec.md — AI Driven Testing (UNIPDS modulo-04)
// Requer Cypress >= 15.4 e login no Cypress Cloud para cy.prompt()

describe('Cadastro de Eventos - AI Driven Testing', () => {
  it('Deve executar o fluxo de cadastro e validar o sucesso de forma semântica', () => {
    cy.visit('/event/new');

    // Múltiplos passos em uma única chamada de array para otimizar o LLM
    cy.prompt([
      'Type "Auditório Oracle" in the Nome do Local field',
      'Type "Av. Dr. Chucri Zaidan, SP" in the Endereço field',
      'Type "500" in the Capacidade field',
      'Type "2026-12-31" in the Data do Evento field',
      'Click the button that submits or saves the event',
    ]);

    // Asserção baseada na intenção visual
    cy.prompt(['Verify that a success message is visible']);
  });
});
