import { MultiServerMCPClient } from "@langchain/mcp-adapters";
import { getMongoDBTool } from "../tools/mongodbTool.ts";
import { getCSVTOJSONTool } from "../tools/csvToJSONTool.ts";
import { getFSTool } from "../tools/fsTool.ts";
import { patchMongoAggregateMcpTools } from "./mongoMcpToolSchemaPatch.ts";

let mcpClient: MultiServerMCPClient | undefined;

export const getMCPTools = async () => {
  if (!mcpClient) {
    mcpClient = new MultiServerMCPClient({
      mcpServers: {
        ...getMongoDBTool(),
        ...getFSTool(),
      },
      onMessage: (log, source) => {
        console.log(`[${source.server}] ${log.data}`);
      },
    });
  }

  const mcpTools = patchMongoAggregateMcpTools(await mcpClient.getTools());

  return [...mcpTools, getCSVTOJSONTool()];
};

/** Ends stdio MCP subprocesses (avoids open handles after e2e / dev). */
export const closeMcpConnections = async () => {
  if (!mcpClient) return;
  await mcpClient.close();
  mcpClient = undefined;
};
