import { after, before, describe, test } from 'node:test';
import assert from 'node:assert/strict';
import type { FastifyInstance } from 'fastify';
import { createServer } from '../../src/server.ts';
import { closeMcpConnections } from '../../src/services/mcpService.ts';

const OPENROUTER = Boolean(process.env.OPENROUTER_API_KEY);
/** Full stack (OpenRouter + MCP Mongo + filesystem). Set RUN_FULL_E2E=1 to enable. */
const RUN_FULL =
  process.env.RUN_FULL_E2E === '1' &&
  OPENROUTER &&
  process.env.CI !== 'true';

describe('POST /chat full pipeline (intent + agent + tools)', () => {
  let app: FastifyInstance | undefined;

  before(async () => {
    if (!RUN_FULL) return;
    app = await createServer();
  });

  after(async () => {
    if (app) await app.close();
    await closeMcpConnections();
  });

  test(
    'returns 200 and non-empty answer for CSV revenue question',
    { skip: !RUN_FULL, timeout: 90_000 },
    async () => {
      assert.ok(app, 'app should be created');
      const csv = `id,product,price,date
1,soap,5.49,2024-01-01
2,milk,6.99,2024-01-01
3,rice,22.9,2024-01-01
`;
      const question = `Intent: sum the price column for total revenue.
File name: sales.csv
File type: csv
Extract fileContent from the block below.

---FILE---
${csv}
---END---
`;

      const res = await app.inject({
        method: 'POST',
        url: '/chat',
        payload: { question },
      });

      assert.equal(res.statusCode, 200, `body: ${res.body}`);
      assert.ok(
        typeof res.body === 'string' && res.body.length > 20,
        'expected textual answer',
      );
      assert.ok(
        !res.body.startsWith('Sorry, I had trouble'),
        `pipeline error: ${res.body.slice(0, 200)}`,
      );
    },
  );
});
