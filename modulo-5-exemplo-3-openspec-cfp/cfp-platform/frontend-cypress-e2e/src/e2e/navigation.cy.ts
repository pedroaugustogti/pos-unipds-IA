// spec: openspec/specs/cfp-cypress-e2e/spec.md — Main Navigation E2E

describe('Main Navigation', () => {
  it('Navigate via top nav', () => {
    cy.visit('/dashboard');
    cy.contains('h1', 'CFP Dashboard').should('be.visible');

    cy.contains('a', 'Cadastro de Palestra').click();
    cy.url().should('include', '/submit-talk');
    cy.contains('h1', 'Call for Papers').should('be.visible');

    cy.get('nav').contains('a', 'Dashboard').click();
    cy.url().should('include', '/dashboard');

    cy.contains('a', 'Cadastro de Evento').click();
    cy.url().should('include', '/event/new');
  });
});
