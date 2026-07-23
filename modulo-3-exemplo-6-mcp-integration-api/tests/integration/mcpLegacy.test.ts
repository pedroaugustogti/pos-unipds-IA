import { describe, it, after, before } from "node:test";
import assert from "node:assert";
import { createTestClient } from "../helpers.ts";
import { Client } from "@modelcontextprotocol/sdk/client";

type CustomerMutationResult = {
    structuredContent: { id: string; message: string };
};

type CustomerResult = {
    structuredContent: { customer: { _id?: string; name: string; phone: string } | null };
};

type CustomersResult = {
    structuredContent: { customers: Array<{ _id?: string; name: string; phone: string }> };
};

describe("MCP + Legacy API integration", () => {
    let client: Client;
    const uniqueName = `Integracao-${Date.now()}`;
    const phone = "11955554444";
    let createdId = "";

    before(async () => {
        client = await createTestClient();
    });

    after(async () => {
        if (createdId) {
            await client.callTool({
                name: "delete_customer",
                arguments: { _id: createdId },
            });
        }
        await client.close();
    });

    it("should read customers://api-info resource with legacy API endpoints", async () => {
        const resource = await client.readResource({ uri: "customers://api-info" });
        const text = resource.contents?.[0]?.text ?? "";

        assert.ok(text.includes("GET    /customers"), "resource must document list endpoint");
        assert.ok(text.includes("POST   /customers"), "resource must document create endpoint");
        assert.ok(text.includes("http://127.0.0.1:9999/v1"), "resource must expose legacy base URL");
    });

    it("should return find_customer_prompt referencing get_customer tool", async () => {
        const result = await client.getPrompt({
            name: "find_customer_prompt",
            arguments: { name: uniqueName },
        });

        const content = result.messages[0]?.content as { text: string };
        assert.ok(content.text.includes("get_customer"), "prompt should reference get_customer");
        assert.ok(content.text.includes(uniqueName), "prompt should include query value");
    });

    it("should return create_customer_prompt referencing create_customer tool", async () => {
        const result = await client.getPrompt({
            name: "create_customer_prompt",
            arguments: { name: uniqueName, phone },
        });

        const content = result.messages[0]?.content as { text: string };
        assert.ok(content.text.includes("create_customer"), "prompt should reference create_customer");
        assert.ok(content.text.includes(uniqueName), "prompt should include customer name");
        assert.ok(content.text.includes(phone), "prompt should include customer phone");
    });

    it("should create a customer via MCP against the legacy API", async () => {
        const result = (await client.callTool({
            name: "create_customer",
            arguments: { name: uniqueName, phone },
        })) as unknown as CustomerMutationResult;

        assert.ok(result.structuredContent.id, "create should return MongoDB id");
        assert.match(result.structuredContent.message, /created/i, "create should confirm success");
        createdId = result.structuredContent.id;
    });

    it("should find the created customer by name via get_customer", async () => {
        const result = (await client.callTool({
            name: "get_customer",
            arguments: { name: uniqueName },
        })) as unknown as CustomerResult;

        assert.ok(result.structuredContent.customer, "customer should be found");
        assert.strictEqual(result.structuredContent.customer?.name, uniqueName);
        assert.strictEqual(result.structuredContent.customer?.phone, phone);
    });

    it("should list customers including the one created via MCP", async () => {
        const result = (await client.callTool({
            name: "list_customers",
            arguments: {},
        })) as unknown as CustomersResult;

        const found = result.structuredContent.customers.some(
            (customer) => customer.name === uniqueName
        );
        assert.ok(found, "list_customers should include MCP-created customer");
    });

    it("should return null when customer is not found", async () => {
        const result = (await client.callTool({
            name: "get_customer",
            arguments: { name: "Cliente-Inexistente-XYZ-999" },
        })) as unknown as CustomerResult;

        assert.strictEqual(result.structuredContent.customer, null);
    });
});
