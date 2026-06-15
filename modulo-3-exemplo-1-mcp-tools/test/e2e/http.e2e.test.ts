import { after, before, describe, test } from 'node:test';
import assert from 'node:assert/strict';
import type { FastifyInstance } from 'fastify';
import { createServer } from '../../src/server.ts';

describe('POST /chat (HTTP)', () => {
  let app: FastifyInstance;

  before(async () => {
    app = await createServer();
  });

  after(async () => {
    await app.close();
  });

  test('rejects body when question shorter than 10 chars', async () => {
    const res = await app.inject({
      method: 'POST',
      url: '/chat',
      payload: { question: 'short' },
    });
    assert.equal(res.statusCode, 400);
  });

  test('rejects missing question', async () => {
    const res = await app.inject({
      method: 'POST',
      url: '/chat',
      payload: {},
    });
    assert.equal(res.statusCode, 400);
  });
});
