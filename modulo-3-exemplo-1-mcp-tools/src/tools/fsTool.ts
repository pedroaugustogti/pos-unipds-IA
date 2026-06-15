import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const fsMcpEntry = path.resolve(
    __dirname,
    "../../node_modules/@modelcontextprotocol/server-filesystem/dist/index.js"
);

export const getFSTool = () => {
    return {
        filesystem: {
            transport: "stdio" as const,
            command: process.execPath,
            args: [fsMcpEntry, process.cwd()],
            defaultToolTimeout: 120_000,
        },
    };
};
