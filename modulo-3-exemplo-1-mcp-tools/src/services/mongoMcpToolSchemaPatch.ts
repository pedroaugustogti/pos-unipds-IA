import { DynamicStructuredTool } from "@langchain/core/tools";
import { z } from "zod";

const stage = z.record(z.string(), z.any());

const aggregateSchema = z.object({
  database: z.string(),
  collection: z.string(),
  pipeline: z.array(stage),
  responseBytesLimit: z.number().optional(),
});

const aggregateDbSchema = z.object({
  database: z.string(),
  pipeline: z.array(stage),
  responseBytesLimit: z.number().optional(),
});

function isMcpDynamicTool(tool: unknown): tool is DynamicStructuredTool {
  return tool instanceof DynamicStructuredTool;
}

/**
 * mcp-adapters simplifyJsonSchemaForLLM merges pipeline stage oneOf incorrectly,
 * so $group/$match fail local Zod before the MCP server runs. Replace aggregate schemas only.
 */
export function patchMongoAggregateMcpTools(tools: unknown[]): unknown[] {
  return tools.map((tool) => {
    if (!isMcpDynamicTool(tool)) return tool;
    const t = tool;
    if (t.name === "aggregate") {
      return new DynamicStructuredTool({
        name: t.name,
        description: `${t.description} Use for collection pipelines ($match, $group, $sum). Do not use aggregate-db for that.`,
        schema: aggregateSchema,
        responseFormat: t.responseFormat,
        metadata: t.metadata,
        defaultConfig: t.defaultConfig,
        func: (input, runManager, config) =>
          t.func(input as never, runManager, config),
      });
    }
    if (t.name === "aggregate-db") {
      return new DynamicStructuredTool({
        name: t.name,
        description: `${t.description} Only for DB-level first stages ($documents, $currentOp, …). For $group on a collection use aggregate.`,
        schema: aggregateDbSchema,
        responseFormat: t.responseFormat,
        metadata: t.metadata,
        defaultConfig: t.defaultConfig,
        func: (input, runManager, config) =>
          t.func(input as never, runManager, config),
      });
    }
    return tool;
  });
}
