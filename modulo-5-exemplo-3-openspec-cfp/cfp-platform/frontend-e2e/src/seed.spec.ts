import { test, expect } from '@playwright/test';

/**
 * Seed test para agentes Playwright (planner / generator / healer).
 * Garante app em http://localhost:4200 antes de explorar via MCP.
 */
test('seed', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'CFP Dashboard' })).toBeVisible();
});
