import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { TokenContext } from "../../domain/token-context.ts";

export function registerApiInfoResource(
    server: McpServer,
    baseUrl: string,
    tokenContext: TokenContext
): void {
    server.registerResource(
        "customers://api-info",
        "customers://api-info",
        { description: "Describes the Customers REST API that this MCP server wraps." },
        async () => ({
            contents: [
                {
                    uri: "customers://api-info",
                    mimeType: "text/plain",
                    text: `
Customers API
  Base URL : ${baseUrl}
  Token context:
    role       : ${tokenContext.role}
    department : ${tokenContext.department}
  Endpoints:
    GET    /customers          — list all customers
    GET    /customers/:id      — get customer by id
    POST   /customers          — create customer  { name, phone }  [admin + sales]
    PUT    /customers/:id      — update customer  { name, phone }  [admin/sales/support]
    DELETE /customers/:id      — delete customer  [admin + sales]

  Customer shape: { _id: string, name: string, phone: string }
`.trim(),
                },
            ],
        })
    );
}
