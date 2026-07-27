import { spawn } from 'node:child_process';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

const REGISTRY = process.env.NPM_REGISTRY ?? 'http://localhost:4873';
const PACKAGE = process.env.MCP_PACKAGE ?? '@pedroaugusto/customers-mcp';
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
    throw new Error(`API not ready (${res.status}). Start legacy-api on port 9999.`);
  }

  const { serviceToken } = await res.json();
  return serviceToken;
}

async function assertPublished() {
  const view = spawn('npm', ['view', PACKAGE, 'version', '--registry', REGISTRY], {
    shell: true,
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  let stdout = '';
  let stderr = '';
  view.stdout.on('data', (chunk) => { stdout += chunk; });
  view.stderr.on('data', (chunk) => { stderr += chunk; });

  const code = await new Promise((resolve) => view.on('close', resolve));
  if (code !== 0) {
    throw new Error(`Package not found in registry: ${stderr || stdout}`);
  }

  const version = stdout.trim();
  console.log(`OK: ${PACKAGE}@${version} published at ${REGISTRY}`);
  return version;
}

async function assertMcpConnection(serviceToken) {
  const transport = new StdioClientTransport({
    command: 'npx',
    args: ['--yes', '--registry', REGISTRY, PACKAGE],
    env: { ...process.env, SERVICE_TOKEN: serviceToken },
  });

  const client = new Client({ name: 'validate-published-mcp', version: '1.0.0' }, { capabilities: {} });
  await client.connect(transport);

  const tools = await client.listTools();
  const resources = await client.listResources();

  console.log(`OK: MCP connected — ${tools.tools.length} tools, ${resources.resources.length} resources`);
  console.log('Tools:', tools.tools.map((tool) => tool.name).join(', '));

  await client.close();
}

async function main() {
  await assertPublished();
  const serviceToken = await getServiceToken();
  await assertMcpConnection(serviceToken);
  console.log('Validation complete: publish + MCP connection OK.');
}

main().catch((error) => {
  console.error('Validation failed:', error.message ?? error);
  process.exit(1);
});
