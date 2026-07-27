import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const dataDir = resolve(dirname(fileURLToPath(import.meta.url)), '../../data');

export const getFSTool = () => ({
  filesystem: {
    transport: 'stdio' as const,
    command: 'npx',
    args: ['-y', '@modelcontextprotocol/server-filesystem', dataDir],
    defaultToolTimeout: Number(process.env.MCP_CONNECT_TIMEOUT_MS ?? 120_000),
  },
});
