import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import z from "zod";
import type { CustomerService } from "../../application/customer-service.ts";
import type { TokenContext } from "../../domain/token-context.ts";
import { CustomerMutationSchema } from "../../domain/customer.ts";
import { withToolGuard } from "./tool-guard.ts";

export function registerDeleteCustomerTool(
    server: McpServer,
    service: CustomerService,
    tokenContext: TokenContext
): void {
    server.registerTool(
        "delete_customer",
        {
            description: "Delete a customer by their _id",
            inputSchema: {
                _id: z
                    .string()
                    .describe("MongoDB ObjectId of the customer to delete"),
            },
            outputSchema: CustomerMutationSchema.shape,
        },
        async ({ _id }) =>
            withToolGuard("delete_customer", tokenContext, async () => {
                const result = await service.deleteCustomer(_id);
                return {
                    content: [{ type: "text", text: result.message ?? "" }],
                    structuredContent: result,
                };
            })
    );
}
