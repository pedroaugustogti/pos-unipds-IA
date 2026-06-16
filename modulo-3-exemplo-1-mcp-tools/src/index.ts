import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { createServer } from './server.ts';

const reportPath = path.join(process.cwd(), 'reports', 'index_run_report.txt');

const app = await createServer();

await app.listen({ port: 3000, host: '0.0.0.0' });
console.log(`Server is running on http://0.0.0.0:3000`);

const salesData = readFileSync('./data/sales-complete.csv', 'utf-8');

const question = `
What is the highest priced product?

${salesData}
`;

try {
  const response = await app.inject({
    method: 'POST',
    url: '/chat',
    payload: { question },
  });

  console.log('Response from /chat:', response.statusCode);
  console.log(response.body);

  mkdirSync(path.dirname(reportPath), { recursive: true });
  const body =
    typeof response.body === 'string'
      ? response.body
      : JSON.stringify(response.body, null, 2);

  const report = [
    `generated_at: ${new Date().toISOString()}`,
    `http_status: ${response.statusCode}`,
    '',
    '--- question (preview, first 2k chars) ---',
    question.length > 2000 ? `${question.slice(0, 2000)}…` : question.trim(),
    '',
    '--- response body ---',
    body,
    '',
  ].join('\n');

  writeFileSync(reportPath, report, 'utf-8');
  console.log(`Report written: ${reportPath}`);
} catch (error) {
  console.error('Error testing /chat endpoint:', error);
  mkdirSync(path.dirname(reportPath), { recursive: true });
  writeFileSync(
    reportPath,
    [
      `generated_at: ${new Date().toISOString()}`,
      'http_status: error',
      '',
      '--- error ---',
      String(error),
    ].join('\n'),
    'utf-8',
  );
  process.exitCode = 1;
} finally {
  await app.close();
}
