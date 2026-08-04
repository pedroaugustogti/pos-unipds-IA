import { defineConfig } from 'cypress';

const projectRoot = 'frontend-cypress-e2e';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:4200',
    supportFile: `${projectRoot}/src/support/e2e.ts`,
    specPattern: `${projectRoot}/src/e2e/**/*.cy.ts`,
    viewportWidth: 1280,
    viewportHeight: 800,
    defaultCommandTimeout: 10_000,
  },
});
