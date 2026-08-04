import { test, expect } from '@playwright/test';
import * as fs from 'node:fs';
import * as path from 'node:path';

const workspaceRoot = path.resolve(__dirname, '../../');

test.describe('Critérios de aceite — CFP Platform', () => {
  test('raiz redireciona para /dashboard', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(
      page.getByRole('heading', { name: 'CFP Dashboard' })
    ).toBeVisible();
  });

  test('/submit-talk exibe formulário CFP em dark mode', async ({ page }) => {
    await page.goto('/submit-talk');

    await expect(
      page.getByRole('heading', { name: 'Call for Papers' })
    ).toBeVisible();
    await expect(page.getByText('Submit your proposal')).toBeVisible();
    await expect(page.getByLabel('Full Name')).toBeVisible();
    await expect(page.getByLabel('Email Address')).toBeVisible();
    await expect(page.getByLabel('Talk Title')).toBeVisible();
    await expect(
      page.getByRole('button', { name: 'Submit Proposal' })
    ).toBeVisible();

    const container = page.locator('.cfp-container').first();
    const background = await container.evaluate(
      (el) => getComputedStyle(el).backgroundImage
    );
    expect(background).toContain('gradient');
  });

  test('/talks/new carrega o mesmo formulário CFP', async ({ page }) => {
    await page.goto('/talks/new');
    await expect(
      page.getByRole('heading', { name: 'Call for Papers' })
    ).toBeVisible();
  });

  test('/event/new exibe cadastro de evento', async ({ page }) => {
    await page.goto('/event/new');
    await expect(
      page.getByRole('heading', { name: 'Cadastro de Local do Evento' })
    ).toBeVisible();
    await expect(page.getByLabel('Nome do Local')).toBeVisible();
  });

  test('navegação principal entre rotas', async ({ page }) => {
    await page.goto('/dashboard');
    await page.getByRole('link', { name: 'Cadastro de Palestra' }).click();
    await expect(page).toHaveURL(/\/submit-talk/);

    await page.getByRole('navigation').getByRole('link', { name: 'Dashboard' }).click();
    await expect(page).toHaveURL(/\/dashboard/);

    await page.getByRole('link', { name: 'Cadastro de Evento' }).click();
    await expect(page).toHaveURL(/\/event\/new/);
  });

  test('não exibe página nx-welcome na raiz', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('Welcome frontend')).not.toBeVisible();
    await expect(page.getByText("You're up and running")).not.toBeVisible();
  });

  test('POST /api/speakers retorna 201 (válido) e 400 (inválido)', async ({
    request,
  }) => {
    const valid = await request.post('http://localhost:3000/api/speakers', {
      data: {
        name: 'Playwright User',
        email: 'playwright@example.com',
        talkTitle: 'E2E Acceptance Talk',
        isGDE: false,
      },
    });
    expect(valid.status()).toBe(201);

    const invalid = await request.post('http://localhost:3000/api/speakers', {
      data: { name: '', email: 'invalid', talkTitle: '' },
    });
    expect(invalid.status()).toBe(400);
  });

  test('submissão via UI aparece no dashboard', async ({ page }) => {
    const speakerName = `E2E Speaker ${Date.now()}`;

    await page.goto('/submit-talk');
    await page.getByLabel('Full Name').fill(speakerName);
    await page.getByLabel('Email Address').fill('e2e-aceite@example.com');
    await page.getByLabel('Talk Title').fill('Playwright Acceptance Test');
    await page.getByRole('button', { name: 'Submit Proposal' }).click();

    await expect(page.getByText('Proposal submitted successfully')).toBeVisible({
      timeout: 10_000,
    });

    await page.goto('/dashboard');
    await expect(page.getByRole('cell', { name: speakerName })).toBeVisible({
      timeout: 10_000,
    });
  });

  test('estrutura OpenSpec conforme critérios', async () => {
    expect(fs.existsSync(path.join(workspaceRoot, 'openspec/config.yaml'))).toBe(
      true
    );
    expect(
      fs.existsSync(
        path.join(workspaceRoot, 'openspec/specs/cfp-submission/spec.md')
      )
    ).toBe(true);
    expect(
      fs.existsSync(
        path.join(workspaceRoot, 'openspec/specs/cfp-dashboard/spec.md')
      )
    ).toBe(true);

    const changesDir = path.join(workspaceRoot, 'openspec/changes');
    if (fs.existsSync(changesDir)) {
      const activeChanges = fs
        .readdirSync(changesDir)
        .filter((entry) => entry !== 'archive');
      expect(activeChanges).toHaveLength(0);
    }

    const config = fs.readFileSync(
      path.join(workspaceRoot, 'openspec/config.yaml'),
      'utf-8'
    );
    expect(config).toContain('CfpSubmissionComponent');
    expect(config).toContain('/submit-talk');
  });
});
