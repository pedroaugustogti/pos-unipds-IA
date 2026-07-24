import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import z from "zod";
import type { CustomerService } from "../../application/customer-service.ts";
import type { TokenContext } from "../../domain/token-context.ts";
import { CustomerMutationSchema, CustomerQuerySchema } from "../../domain/customer.ts";
import { withToolGuard } from "./tool-guard.ts";

export function registerGetCustomerTool(
    server: McpServer,
    service: CustomerService,
    tokenContext: TokenContext
): void {
    server.registerTool(
        "get_customer",
        {
            description: "Find a customer by _id, name, or phone number",
            inputSchema: CustomerQuerySchema,
            outputSchema: CustomerMutationSchema.shape,
        },
        async (query) =>
            withToolGuard("get_customer", tokenContext, async () => {
                const customer = await service.findCustomer(query);
                return {
                    content: [{ type: "text", text: JSON.stringify(customer, null, 2) }],
                    structuredContent: { customer },
                };
            })
    );
}
