import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import z from "zod";
import type { CustomerService } from "../../application/customer-service.ts";
import type { TokenContext } from "../../domain/token-context.ts";
import { CustomerMutationSchema } from "../../domain/customer.ts";
import { withToolGuard } from "./tool-guard.ts";

export function registerCreateCustomerTool(
    server: McpServer,
    service: CustomerService,
    tokenContext: TokenContext
): void {
    server.registerTool(
        "create_customer",
        {
            description: "Create a new customer",
            inputSchema: {
                name: z.string().describe("Full name of the customer"),
                phone: z.string().describe("Phone number of the customer"),
            },
            outputSchema: CustomerMutationSchema.shape,
        },
        async ({ name, phone }) =>
            withToolGuard("create_customer", tokenContext, async () => {
                const result = await service.createCustomer({ name, phone });
                return {
                    content: [{ type: "text", text: result.message ?? "" }],
                    structuredContent: result,
                };
            })
    );
}
