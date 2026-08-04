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
