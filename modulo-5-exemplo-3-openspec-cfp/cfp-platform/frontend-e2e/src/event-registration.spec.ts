// spec: specs/event-registration.md — gerado pelo agente playwright-test-generator (Ex. 5)

import { test, expect } from '@playwright/test';

test.describe('Cadastro de Local do Evento', () => {
  test('happy path — cadastro completo', async ({ page }) => {
    // Step 1: Navegar para /event/new
    await page.goto('/event/new');

    // Step 2: Verificar heading
    await expect(
      page.getByRole('heading', { name: 'Cadastro de Local do Evento' }),
    ).toBeVisible();

    // Steps 3–6: Preencher formulário
    await page.getByLabel('Nome do Local').fill('Auditório Oracle');
    await page.getByLabel('Endereço').fill('Av. Dr. Chucri Zaidan, SP');
    await page.getByLabel('Capacidade').fill('500');
    await page.getByLabel('Data do Evento').fill('2026-12-31');

    // Step 7: Submeter
    await page.getByRole('button', { name: 'Cadastrar Evento' }).click();

    // Step 8: Verificar sucesso
    await expect(page.getByText('Evento cadastrado com sucesso!')).toBeVisible({
      timeout: 10_000,
    });
  });

  test('validação — campos obrigatórios', async ({ page }) => {
    await page.goto('/event/new');
    await page.getByRole('button', { name: 'Cadastrar Evento' }).click();
    await expect(page.getByText('O nome é obrigatório.')).toBeVisible();
    await expect(page.getByText('O endereço é obrigatório.')).toBeVisible();
  });
});
