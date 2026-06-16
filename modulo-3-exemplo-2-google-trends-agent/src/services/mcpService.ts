import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { MultiServerMCPClient } from '@langchain/mcp-adapters';
import { createGoogleTrendsTool } from '../tools/googleTrendsTool.ts';
import { SerpAPIService } from './serpApiService.ts';
import { config } from '../config.ts';

const require = createRequire(import.meta.url);

/** Cap MCP stdio handshake + listTools (ms). Override with MCP_CONNECT_TIMEOUT_MS. */
const MCP_CONNECT_TIMEOUT_MS = Number(
  process.env.MCP_CONNECT_TIMEOUT_MS ?? 12_000,
);

const resolveFilesystemServerEntry = (): string => {
  const pkgJson = require.resolve(
    '@modelcontextprotocol/server-filesystem/package.json',
  );
  const { bin } = require(pkgJson) as { bin: Record<string, string> | string };
  const rel = typeof bin === 'string' ? bin : bin['mcp-server-filesystem'];
  return join(dirname(pkgJson), rel);
};

const mcpChildEnv = (): Record<string, string> => {
  const env: Record<string, string> = {};
  const nodeOptions = process.env.NODE_OPTIONS?.trim();
  const extraCa = process.env.NODE_EXTRA_CA_CERTS?.trim();

  if (nodeOptions) env.NODE_OPTIONS = nodeOptions;
  else env.NODE_OPTIONS = '--use-system-ca';

  if (extraCa) env.NODE_EXTRA_CA_CERTS = extraCa;

  return env;
};

export const getMCPTools = async () => {
  const mcpClient = new MultiServerMCPClient({
    filesystem: {
      transport: 'stdio',
      command: process.execPath,
      args: [resolveFilesystemServerEntry(), process.cwd()],
      env: mcpChildEnv(),
    },
  });

  let connectTimer: ReturnType<typeof setTimeout> | undefined;
  const deadline = new Promise<never>((_, reject) => {
    connectTimer = setTimeout(
      () =>
        reject(
          new Error(
            `MCP filesystem: exceeded ${MCP_CONNECT_TIMEOUT_MS}ms (stdio or listTools). Set MCP_CONNECT_TIMEOUT_MS to adjust.`,
          ),
        ),
      MCP_CONNECT_TIMEOUT_MS,
    );
  });

  let mcpTools;
  try {
    mcpTools = await Promise.race([mcpClient.getTools(), deadline]);
  } catch (e) {
    await mcpClient.close().catch(() => {});
    throw e;
  } finally {
    if (connectTimer !== undefined) clearTimeout(connectTimer);
  }

  const serpAPIService = new SerpAPIService(config.serpAPIConfig);
  const googleTrendsTool = createGoogleTrendsTool(serpAPIService);

  return [...mcpTools, googleTrendsTool];
};
