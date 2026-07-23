import { describe, it, after, before } from "node:test";
import assert from "node:assert";
import { createTestClient } from "../helpers.ts";
import { Client } from "@modelcontextprotocol/sdk/client";

type MaskedCustomersResult = {
    structuredContent: {
        customers: Array<{ _id?: string; name: string; phone: string }>;
    };
};

const PHONE_MASK_REGEX = /^\(\d{2}\) \d{5}-\d{4}$/;

describe("list_customers_masked_phone tool", () => {
    let client: Client;

    before(async () => {
        client = await createTestClient();
    });

    after(async () => {
        await client.close();
    });

    it("should list customers with masked phone numbers", async () => {
        const result = (await client.callTool({
            name: "list_customers_masked_phone",
            arguments: {},
        })) as unknown as MaskedCustomersResult;

        assert.ok(Array.isArray(result.structuredContent.customers));
        assert.ok(result.structuredContent.customers.length > 0);

        for (const customer of result.structuredContent.customers) {
            assert.match(
                customer.phone,
                PHONE_MASK_REGEX,
                `phone should match mask (99) 99999-9999, got ${customer.phone}`
            );
        }
    });

    it("should mask known test data phone 999-000-111", async () => {
        const result = (await client.callTool({
            name: "list_customers_masked_phone",
            arguments: {},
        })) as unknown as MaskedCustomersResult;

        const ana = result.structuredContent.customers.find(
            (customer) => customer.name === "Ana"
        );

        assert.ok(ana, "Ana should exist in customer list");
        assert.strictEqual(ana.phone, "(00) 99900-0111");
    });
});
