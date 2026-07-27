import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const moduleRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const repoRoot = resolve(moduleRoot, '..');
const customersLauncher = resolve(
  repoRoot,
  'modulo-3-exemplo-8-publish-mcp/scripts/start-public-mcp.mjs',
);

export const getCustomersTool = () => {
  const env: Record<string, string> = {
    NODE_OPTIONS: [process.env.NODE_OPTIONS, '--use-system-ca'].filter(Boolean).join(' '),
  };

  if (process.env.SERVICE_TOKEN) {
    env.SERVICE_TOKEN = process.env.SERVICE_TOKEN;
  }

  return {
    'customers-mcp': {
      transport: 'stdio' as const,
      command: process.execPath,
      args: [customersLauncher],
      env,
      defaultToolTimeout: Number(process.env.MCP_CONNECT_TIMEOUT_MS ?? 120_000),
    },
  };
};
