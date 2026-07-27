import { spawnSync } from 'node:child_process';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
process.env.NODE_OPTIONS = [process.env.NODE_OPTIONS, '--use-system-ca'].filter(Boolean).join(' ');

const transport = new StdioClientTransport({
  command: 'node',
  args: [resolve(root, 'scripts/start-public-mcp.mjs')],
  cwd: root,
  env: process.env,
});

const client = new Client({ name: 'cursor-launcher-test', version: '1.0.0' }, { capabilities: {} });
await client.connect(transport);
const tools = await client.listTools();
console.log('OK: launcher works —', tools.tools.map((t) => t.name).join(', '));
await client.close();
