import path from "node:path";
import { fileURLToPath } from "node:url";

// https://github.com/mongodb-js/mongodb-mcp-server
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const mongoMcpEntry = path.resolve(
    __dirname,
    "../../node_modules/mongodb-mcp-server/dist/esm/index.js"
);

export const getMongoDBTool = () => {
    return {
        MongoDB: {
            transport: "stdio" as const,
            command: process.execPath,
            args: [mongoMcpEntry],
            defaultToolTimeout: 120_000,
            env: {
                DO_NOT_TRACK: process.env.DO_NOT_TRACK ?? "1",
                MDB_MCP_CONNECTION_STRING:
                    process.env.MDB_MCP_CONNECTION_STRING ??
                    "mongodb://localhost:27017/dataprocessing",
            },
        },
    };
};