import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export function registerCreateCustomerPrompt(server: McpServer) {
    server.registerPrompt(
        "create_customer_prompt",
        {
            description: "Prompt to register a new customer using the create_customer tool",
            argsSchema: {
                name: z.string().describe("Full name of the customer"),
                phone: z.string().describe("Phone number of the customer"),
            },
        },
        ({ name, phone }) => ({
            messages: [
                {
                    role: "user",
                    content: {
                        type: "text",
                        text: `Please create a new customer using the create_customer tool.\nName: ${name}\nPhone: ${phone}`,
                    },
                },
            ],
        })
    );
}
