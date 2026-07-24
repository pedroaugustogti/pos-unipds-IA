import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { CustomerService } from "../../application/customer-service.ts";
import type { TokenContext } from "../../domain/token-context.ts";
import { CustomerMutationSchema, CustomerUpdateSchema } from "../../domain/customer.ts";
import { withToolGuard } from "./tool-guard.ts";

export function registerUpdateCustomerTool(
    server: McpServer,
    service: CustomerService,
    tokenContext: TokenContext
): void {
    server.registerTool(
        "update_customer",
        {
            description:
                "Update an existing customer's name and/or phone number by their _id",
            inputSchema: CustomerUpdateSchema.shape,
            outputSchema: CustomerMutationSchema.shape,
        },
        async ({ _id, name, phone }) =>
            withToolGuard("update_customer", tokenContext, async () => {
                const result = await service.updateCustomer(_id, {
                    name,
                    phone,
                });
                return {
                    content: [{ type: "text", text: result.message ?? "" }],
                    structuredContent: result,
                };
            })
    );
}
