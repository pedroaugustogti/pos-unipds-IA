import { MultiServerMCPClient } from '@langchain/mcp-adapters';
import { getCustomersTool } from '../tools/customersTool.ts';
import { getFSTool } from '../tools/fsTool.ts';

let mcpClient: MultiServerMCPClient | undefined;

export const getMCPTools = async () => {
  if (!mcpClient) {
    mcpClient = new MultiServerMCPClient({
      mcpServers: {
        ...getCustomersTool(),
        ...getFSTool(),
      },
      onMessage: (log, source) => {
        console.log(`[${source.server}] ${log.data}`);
      },
      onInitialized: (source) => {
        console.log(`MCP server connected: ${source.server}`);
      },
      onConnectionError: (source, error) => {
        console.error(`MCP server failed: ${source.serverName}`, error);
        throw error;
      },
    });
  }

  return mcpClient.getTools();
};

export const closeMcpConnections = async () => {
  if (!mcpClient) return;
  await mcpClient.close();
  mcpClient = undefined;
};
