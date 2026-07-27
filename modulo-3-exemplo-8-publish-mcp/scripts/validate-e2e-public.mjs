import { spawn } from 'node:child_process';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

process.env.NODE_OPTIONS = [process.env.NODE_OPTIONS, '--use-system-ca'].filter(Boolean).join(' ');

const PACKAGE = '@gorgan/customers-mcp';
const API_URL = process.env.CUSTOMERS_API_URL ?? 'http://127.0.0.1:9999/v1';

async function assertApiHealth() {
  const res = await fetch(`${API_URL}/health`);
  if (!res.ok) throw new Error(`Legacy API unhealthy (${res.status})`);
  const body = await res.json();
  console.log(`OK: Legacy API healthy — ${body.app} ${body.version}`);
}

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
    throw new Error(`Service token failed (${res.status}). Is legacy-api running on port 9999?`);
  }

  const { serviceToken } = await res.json();
  console.log('OK: SERVICE_TOKEN obtained');
  return serviceToken;
}

async function createClient(serviceToken) {
  const useLocal = process.env.MCP_E2E_LOCAL === '1';
  const transport = new StdioClientTransport({
    command: useLocal ? 'node' : 'npx',
    args: useLocal ? ['src/index.ts'] : ['--yes', PACKAGE],
    env: { ...process.env, SERVICE_TOKEN: serviceToken },
  });

  const client = new Client({ name: 'validate-e2e-public', version: '1.0.0' }, { capabilities: {} });
  await client.connect(transport);
  return client;
}

function structured(result) {
  return result.structuredContent ?? JSON.parse(result.content?.[0]?.text ?? '{}');
}

async function main() {
  await assertApiHealth();
  const serviceToken = await getServiceToken();
  const client = await createClient(serviceToken);

  const tools = await client.listTools();
  const resources = await client.listResources();
  console.log(`OK: MCP connected via npx — ${tools.tools.length} tools, ${resources.resources.length} resources`);

  const listBefore = structured(await client.callTool({ name: 'list_customers', arguments: {} }));
  console.log(`OK: list_customers — ${listBefore.customers?.length ?? 0} customer(s)`);

  const created = structured(await client.callTool({
    name: 'create_customer',
    arguments: { name: 'E2E Public MCP', phone: '555-0100' },
  }));
  if (!created.id) throw new Error('create_customer did not return id');
  console.log(`OK: create_customer — id ${created.id}`);

  const fetched = structured(await client.callTool({
    name: 'get_customer',
    arguments: { _id: created.id },
  }));
  if (fetched.customer?.name !== 'E2E Public MCP') {
    throw new Error(`get_customer mismatch: ${JSON.stringify(fetched)}`);
  }
  console.log('OK: get_customer — name matches');

  const updated = structured(await client.callTool({
    name: 'update_customer',
    arguments: { _id: created.id, name: 'E2E Public MCP Updated', phone: '555-0101' },
  }));
  if (!updated.message?.toLowerCase().includes('updated')) {
    throw new Error(`update_customer unexpected response: ${JSON.stringify(updated)}`);
  }
  console.log('OK: update_customer');

  const deleted = structured(await client.callTool({
    name: 'delete_customer',
    arguments: { _id: created.id },
  }));
  if (!deleted.message?.toLowerCase().includes('delet')) {
    throw new Error(`delete_customer unexpected response: ${JSON.stringify(deleted)}`);
  }
  console.log('OK: delete_customer');

  const resource = await client.readResource({ uri: 'customers://api-info' });
  if (!resource.contents?.length) throw new Error('api-info resource empty');
  console.log('OK: customers://api-info resource readable');

  await client.close();
  console.log('E2E validation complete: API + public npm MCP + full CRUD OK.');
}

main().catch((error) => {
  console.error('E2E validation failed:', error.message ?? error);
  process.exit(1);
});
