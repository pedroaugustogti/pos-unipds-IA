import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { CustomerService } from "../application/customer-service.ts";
import { parseTokenContextFromEnv } from "../domain/token-context.ts";
import { registerListCustomersTool } from "./tools/list-customers.ts";
import { registerGetCustomerTool } from "./tools/get-customer.ts";
import { registerCreateCustomerTool } from "./tools/create-customer.ts";
import { registerUpdateCustomerTool } from "./tools/update-customer.ts";
import { registerDeleteCustomerTool } from "./tools/delete-customer.ts";
import { registerApiInfoResource } from "./resources/api-info.ts";
import { registerFindCustomerPrompt } from "./prompts/findCustomer.ts";

const BASE_URL = "http://127.0.0.1:9999/v1";
const SERVICE_TOKEN = process.env.SERVICE_TOKEN!;
const tokenContext = parseTokenContextFromEnv();
const service = new CustomerService(BASE_URL, SERVICE_TOKEN);

export const server = new McpServer({
    name: "@erickwendel/ew-customers-mcp",
    version: "0.0.1",
});

registerListCustomersTool(server, service, tokenContext);
registerGetCustomerTool(server, service, tokenContext);
registerCreateCustomerTool(server, service, tokenContext);
registerUpdateCustomerTool(server, service, tokenContext);
registerDeleteCustomerTool(server, service, tokenContext);
registerApiInfoResource(server, BASE_URL, tokenContext);
registerFindCustomerPrompt(server);
