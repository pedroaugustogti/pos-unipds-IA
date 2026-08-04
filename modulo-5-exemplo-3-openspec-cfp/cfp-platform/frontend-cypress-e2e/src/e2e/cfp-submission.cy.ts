// spec: openspec/specs/cfp-cypress-e2e/spec.md — CFP Submission E2E

describe('CFP Submission', () => {
  it('Submit talk successfully', () => {
    cy.visit('/submit-talk');

    cy.contains('h1', 'Call for Papers').should('be.visible');
    cy.get('#name').type('Cypress User');
    cy.get('#email').type('cypress@example.com');
    cy.get('#talkTitle').type('Cypress E2E Talk');
    cy.get('button.submit-btn').click();

    cy.contains('Proposal submitted successfully').should('be.visible');
  });
});
