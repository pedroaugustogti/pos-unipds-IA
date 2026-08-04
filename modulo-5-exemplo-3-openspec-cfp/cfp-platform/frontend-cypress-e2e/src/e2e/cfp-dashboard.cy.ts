// spec: openspec/specs/cfp-cypress-e2e/spec.md — Dashboard Listing E2E

describe('CFP Dashboard', () => {
  it('Submission visible in dashboard', () => {
    const speakerName = `Cypress Speaker ${Date.now()}`;

    cy.visit('/submit-talk');
    cy.get('#name').type(speakerName);
    cy.get('#email').type('cypress-dashboard@example.com');
    cy.get('#talkTitle').type('Dashboard E2E Test');
    cy.get('button.submit-btn').click();
    cy.contains('Proposal submitted successfully').should('be.visible');

    cy.visit('/dashboard');
    cy.contains('td', speakerName).should('be.visible');
    cy.contains('td', 'cypress-dashboard@example.com').should('be.visible');
    cy.contains('td', 'Dashboard E2E Test').should('be.visible');
  });
});
