import { chromium } from '@playwright/test';
import { mkdir } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const outDir = __dirname;
const baseURL = 'http://localhost:4200';

const results = [];

function log(step, status, detail) {
  results.push({ step, status, detail });
  console.log(`[${status}] Step ${step}: ${detail}`);
}

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });

try {
  // Step 1: Navigate and verify title
  await page.goto(`${baseURL}/submit-talk`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: path.join(outDir, '01-page-loaded.png'), fullPage: true });

  const title = page.locator('h1#cfp-title');
  await title.waitFor({ state: 'visible' });
  const titleText = await title.textContent();
  if (titleText?.trim() === 'Call for Papers') {
    log(1, 'PASS', `Título "${titleText.trim()}" visível`);
  } else {
    log(1, 'FAIL', `Título esperado "Call for Papers", encontrado "${titleText}"`);
  }

  // Step 2: Dark mode form with centered card
  const container = page.locator('.cfp-container');
  const card = page.locator('.glass-card');
  await card.waitFor({ state: 'visible' });
  await page.screenshot({ path: path.join(outDir, '02-dark-mode-form.png'), fullPage: true });

  const containerStyles = await container.evaluate((el) => {
    const s = getComputedStyle(el);
    return {
      display: s.display,
      justifyContent: s.justifyContent,
      alignItems: s.alignItems,
      background: s.background,
      color: s.color,
    };
  });
  const cardStyles = await card.evaluate((el) => {
    const s = getComputedStyle(el);
    return {
      borderRadius: s.borderRadius,
      maxWidth: s.maxWidth,
    };
  });

  const isDark = containerStyles.color.includes('247') || containerStyles.background.includes('0a0a0c') || containerStyles.background.includes('rgb');
  const isCentered = containerStyles.display === 'flex' && containerStyles.justifyContent === 'center';
  if (isCentered && cardStyles.maxWidth) {
    log(2, 'PASS', `Formulário dark mode com card centralizado (flex center, max-width: ${cardStyles.maxWidth})`);
  } else {
    log(2, 'FAIL', `Layout inesperado: ${JSON.stringify({ containerStyles, cardStyles })}`);
  }

  // Step 3: Fill form
  await page.fill('#name', 'Test User');
  await page.fill('#email', 'test@example.com');
  await page.fill('#talkTitle', 'Demo');
  await page.screenshot({ path: path.join(outDir, '03-form-filled.png'), fullPage: true });
  log(3, 'PASS', 'Formulário preenchido: Test User, test@example.com, Demo');

  // Step 4: Submit
  await page.click('button.submit-btn');
  log(4, 'PASS', 'Botão "Submit Proposal" clicado');

  // Step 5: Success message
  const successMsg = page.locator('.success-msg');
  await successMsg.waitFor({ state: 'visible', timeout: 10000 });
  const successText = await successMsg.textContent();
  await page.screenshot({ path: path.join(outDir, '04-success-message.png'), fullPage: true });
  if (successText?.includes('successfully')) {
    log(5, 'PASS', `Mensagem de sucesso: "${successText.trim()}"`);
  } else {
    log(5, 'FAIL', `Mensagem inesperada: "${successText}"`);
  }

  // Step 6: View Dashboard
  await page.click('a.dashboard-link');
  await page.waitForURL('**/dashboard');
  await page.waitForSelector('.glass-table tbody tr', { timeout: 10000 });
  await page.screenshot({ path: path.join(outDir, '05-dashboard-table.png'), fullPage: true });

  const row = page.locator('.glass-table tbody tr').filter({ hasText: 'Test User' });
  const rowCount = await row.count();
  if (rowCount > 0) {
    const cells = await row.first().locator('td').allTextContents();
    const hasData = cells.some((c) => c.includes('Test User')) &&
      cells.some((c) => c.includes('test@example.com')) &&
      cells.some((c) => c.includes('Demo'));
    if (hasData) {
      log(6, 'PASS', `Submissão encontrada na tabela: ${cells.join(' | ')}`);
    } else {
      log(6, 'FAIL', `Linha encontrada mas dados incorretos: ${cells.join(' | ')}`);
    }
  } else {
    log(6, 'FAIL', 'Submissão "Test User" não encontrada na tabela');
  }

  console.log('\n=== RESUMO ===');
  const passed = results.filter((r) => r.status === 'PASS').length;
  const failed = results.filter((r) => r.status === 'FAIL').length;
  console.log(`Total: ${results.length} | Passou: ${passed} | Falhou: ${failed}`);
  results.forEach((r) => console.log(`  ${r.status} - Step ${r.step}: ${r.detail}`));

  process.exit(failed > 0 ? 1 : 0);
} catch (err) {
  await page.screenshot({ path: path.join(outDir, 'error.png'), fullPage: true });
  console.error('ERRO:', err.message);
  process.exit(1);
} finally {
  await browser.close();
}
