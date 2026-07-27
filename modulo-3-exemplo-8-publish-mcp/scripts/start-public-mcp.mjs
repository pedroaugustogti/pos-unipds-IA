import { register } from 'tsx/esm/api';

process.env.NODE_OPTIONS = [process.env.NODE_OPTIONS, '--use-system-ca'].filter(Boolean).join(' ');

const API_URL = process.env.CUSTOMERS_API_URL ?? 'http://127.0.0.1:9999/v1';

async function getServiceToken() {
  const res = await fetch(`${API_URL}/auth/service-token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: 'erickwendel',
      password: '123123',
      adminSuperSecret: 'AM I THE BOSS?',
    }),
  });

  if (!res.ok) {
    console.error(`[customers-mcp-public] Failed to get SERVICE_TOKEN (${res.status}). Start legacy-api on port 9999.`);
    process.exit(1);
  }

  const { serviceToken } = await res.json();
  return serviceToken;
}

process.env.SERVICE_TOKEN = await getServiceToken();

// Cursor attaches stdio to this process — run MCP in-process (same pattern as customers-secure-mcp).
register();
await import('../src/index.ts');
