import { describe, it, after, before } from 'node:test'
import assert from 'node:assert'
import { createTestClient } from '../helpers.ts'
import { Client } from '@modelcontextprotocol/sdk/client'

describe('Customer Resources', () => {
    let client: Client

    before(async () => {
        client = await createTestClient()
    })
    after(async () => {
        await client.close()
    })

    it('should list the customers://api-info resource', async () => {
        const { resources } = await client.listResources()
        const info = resources.find(r => r.uri === 'customers://api-info')
        assert.ok(
            info,
            'customers://api-info should exists'
        )

        assert.deepStrictEqual(
            info.description,
            'describes the customers rest API that this MCP server wraps',
            "description should be correct"
        )
    })

    it('should read customers://api-info with legacy API contract', async () => {
        const resource = await client.readResource({ uri: 'customers://api-info' })
        const text = resource.contents?.[0]?.text ?? ''

        assert.ok(text.includes('Customers API'), 'resource should describe the API')
        assert.ok(text.includes('DELETE /customers/:id'), 'resource should document delete endpoint')
        assert.ok(text.includes('{ _id: string, name: string, phone: string }'), 'resource should document customer shape')
    })
})