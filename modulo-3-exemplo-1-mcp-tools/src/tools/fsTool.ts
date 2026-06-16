import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const fsMcpEntry = path.resolve(
    __dirname,
    "../../node_modules/@modelcontextprotocol/server-filesystem/dist/index.js"
);
const reportsDir = path.resolve(process.cwd(), "reports");

export const getFSTool = () => {
    return {
        filesystem: {
            transport: "stdio" as const,
            command: process.execPath,
            args: [fsMcpEntry, reportsDir],
            defaultToolTimeout: 120_000,
        },
    };
};
