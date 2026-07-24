import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { CustomerService } from "../../application/customer-service.ts";
import type { TokenContext } from "../../domain/token-context.ts";
import { CustomerMutationSchema } from "../../domain/customer.ts";
import { withToolGuard } from "./tool-guard.ts";

export function registerListCustomersTool(
    server: McpServer,
    service: CustomerService,
    tokenContext: TokenContext
): void {
    server.registerTool(
        "list_customers",
        {
            description: "List all customers",
            inputSchema: {},
            outputSchema: CustomerMutationSchema.shape,
        },
        async () =>
            withToolGuard("list_customers", tokenContext, async () => {
                const customers = await service.listCustomers();
                return {
                    content: [{ type: "text", text: JSON.stringify(customers, null, 2) }],
                    structuredContent: { customers },
                };
            })
    );
}
