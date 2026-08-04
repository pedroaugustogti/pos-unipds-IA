import { test, expect } from '@playwright/test';

/**
 * Demo visual para acompanhar no navegador.
 * Executar: npx playwright test visual-demo.spec.ts --headed --slow-mo=1000
 */
test.describe('Demo visual — /submit-talk', () => {
  test.setTimeout(120_000);

  test('fluxo completo no navegador', async ({ page }) => {
    await page.goto('/submit-talk');

    await expect(
      page.getByRole('heading', { name: 'Call for Papers' })
    ).toBeVisible();

    const speakerName = `Demo ${Date.now()}`;
    await page.getByLabel('Full Name').fill(speakerName);
    await page.getByLabel('Email Address').fill('demo@example.com');
    await page.getByLabel('Talk Title').fill('Cursor Browser Demo');
    await page.getByRole('button', { name: 'Submit Proposal' }).click();

    await expect(page.getByText('Proposal submitted successfully')).toBeVisible({
      timeout: 10_000,
    });

    await page.getByRole('link', { name: 'View Dashboard' }).click();
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.getByRole('cell', { name: speakerName })).toBeVisible({
      timeout: 10_000,
    });

    await page.waitForTimeout(3000);
  });
});
