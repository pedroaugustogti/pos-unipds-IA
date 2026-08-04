## ADDED Requirements

### Requirement: CFP Submission E2E (Cypress)

The Cypress suite MUST verify the complete CFP submission happy path.

#### Scenario: Submit talk successfully
- **WHEN** the user visits `/submit-talk`
- **AND** fills Full Name, Email, and Talk Title
- **AND** clicks "Submit Proposal"
- **THEN** the success message "Proposal submitted successfully" MUST be visible

### Requirement: Main Navigation E2E (Cypress)

The Cypress suite MUST verify navigation between main routes.

#### Scenario: Navigate via top nav
- **WHEN** the user starts at `/dashboard`
- **AND** clicks "Cadastro de Palestra"
- **THEN** the URL MUST include `/submit-talk`
- **WHEN** the user clicks "Dashboard" in navigation
- **THEN** the URL MUST include `/dashboard`

### Requirement: Dashboard Listing E2E (Cypress)

The Cypress suite MUST verify submissions appear in the dashboard table.

#### Scenario: Submission visible in dashboard
- **WHEN** the user submits a talk with a unique speaker name
- **AND** navigates to `/dashboard`
- **THEN** the dashboard table MUST contain the speaker name, email, and talk title

### Requirement: Event Registration E2E via cy.prompt (Cypress AI)

The Cypress suite MUST support AI-driven testing for event registration using natural language steps.

#### Scenario: Register event with cy.prompt
- **WHEN** the user visits `/event/new`
- **AND** `cy.prompt` fills Nome do Local, Endereço, Capacidade, and Data do Evento
- **AND** submits the form via prompt
- **THEN** a success message MUST be visible
