import { type McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { CustomerService } from "../../application/customerService.ts";
import z from "zod";
import { CustomerSchema } from "../../domain/customer.ts";
import { formatPhoneMask } from "../../domain/phoneMask.ts";

const CustomerWithMaskedPhoneSchema = CustomerSchema.extend({
    phone: z.string().describe("Phone formatted as (99) 99999-9999"),
});

export function registerListCustomersMaskedPhoneTool(
    server: McpServer,
    service: CustomerService
) {
    server.registerTool(
        "list_customers_masked_phone",
        {
            description: "List all customers with phone numbers formatted as (99) 99999-9999, padding missing digits with 0",
            inputSchema: {},
            outputSchema: {
                customers: z.array(CustomerWithMaskedPhoneSchema)
                    .describe("Customers with masked phone numbers"),
            },
        },
        async () => {
            try {
                const customers = await service.listCustomers();
                const maskedCustomers = customers.map((customer) => ({
                    ...customer,
                    phone: formatPhoneMask(customer.phone),
                }));

                return {
                    content: [
                        {
                            type: "text",
                            text: JSON.stringify(maskedCustomers, null, 2),
                        },
                    ],
                    structuredContent: { customers: maskedCustomers },
                };
            } catch (error) {
                return {
                    isError: true,
                    content: [
                        {
                            type: "text",
                            text: `Failed to list customers with masked phone. Error: ${error instanceof Error ? error.message : String(error)}`,
                        },
                    ],
                };
            }
        }
    );
}
