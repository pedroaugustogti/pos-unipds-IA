import { describe, it, after, before } from 'node:test'
import assert from 'node:assert'
import { createTestClient, getCachedAdminToken, getServiceToken } from '../helpers.ts'
import { Client } from '@modelcontextprotocol/sdk/client'
import type { Customer, CustomerMutation } from '../../src/domain/customer.ts'

type CustomerResult = { structuredContent: { customer?: Customer | null, isError: boolean, message?: string } }
type CustomersResult = { structuredContent: { customers?: Customer[], isError: boolean, message?: string } }
type MutationToolResult = { structuredContent: CustomerMutation }

const FAST_RATE_LIMIT = { rateLimitMax: 5, rateLimitWindowMs: 60_000 }

describe('Customer Tools CRUD', () => {
  let client: Client
  let createdId: string

  before(async () => {
    client = await createTestClient(await getCachedAdminToken())
  })

  after(async () => {
    await client.close()
  })

  it('should list all customers', async () => {
    const result = await client.callTool({
      name: 'list_customers',
      arguments: {},
    }) as unknown as CustomersResult

    assert.ok(Array.isArray(result.structuredContent.customers), 'Should return an array of customers')
  })

  it('should create a customer', async () => {
    const result = await client.callTool({
      name: 'create_customer',
      arguments: { name: 'Test MCP User', phone: '999-000-0001' },
    }) as unknown as MutationToolResult

    assert.ok(result.structuredContent.id, 'Should return the new customer id')
    assert.ok(result.structuredContent.message?.includes('Test MCP User'), 'Confirmation message should include customer name')
    createdId = result.structuredContent.id
  })

  it('should get a customer by _id', async () => {
    const result = await client.callTool({
      name: 'get_customer',
      arguments: { _id: createdId },
    }) as unknown as CustomerResult

    assert.ok(result.structuredContent.customer, 'Should return a customer object')
    assert.strictEqual(result.structuredContent.customer!.name, 'Test MCP User')
  })

  it('should get a customer by name', async () => {
    const result = await client.callTool({
      name: 'get_customer',
      arguments: { name: 'Test MCP User' },
    }) as unknown as CustomerResult

    assert.ok(result.structuredContent.customer, 'Should return a customer matching the name')
    assert.strictEqual(result.structuredContent.customer!.phone, '999-000-0001')
  })

  it('should update a customer', async () => {
    const result = await client.callTool({
      name: 'update_customer',
      arguments: { _id: createdId, name: 'Test MCP User Updated', phone: '999-000-0002' },
    }) as unknown as MutationToolResult

    assert.ok(result.structuredContent.message, 'Should return a confirmation message')
    assert.strictEqual(result.structuredContent.id, createdId)
  })

  it('should reflect the update when getting by id', async () => {
    const result = await client.callTool({
      name: 'get_customer',
      arguments: { _id: createdId },
    }) as unknown as CustomerResult

    assert.strictEqual(result.structuredContent.customer!.name, 'Test MCP User Updated')
    assert.strictEqual(result.structuredContent.customer!.phone, '999-000-0002')
  })

  it('should delete a customer', async () => {
    const result = await client.callTool({
      name: 'delete_customer',
      arguments: { _id: createdId },
    }) as unknown as MutationToolResult

    assert.ok(result.structuredContent.message, 'Should return a confirmation message')
  })

  it('should return null when getting a deleted customer by name', async () => {
    const result = await client.callTool({
      name: 'get_customer',
      arguments: { name: 'Test MCP User Updated' },
    }) as unknown as CustomerResult

    assert.ok(!result.structuredContent?.customer, 'Deleted customer should not be found')
  })

  it('should return isError when deleting with an invalid id', async () => {
    const result = await client.callTool({
      name: 'delete_customer',
      arguments: { _id: 'not-a-valid-id' },
    }) as unknown as CustomerResult

    assert.ok(result.structuredContent.isError, 'Should return isError: true for invalid id')
    assert.strictEqual(result.structuredContent.message, 'Failed to delete customer. Error: HTTP 400 - Bad Request - {"message":"the id is invalid!","id":"not-a-valid-id"}', 'Error message should indicate full error message')
  })
})

describe('Customer Tools auth', () => {
  it('should return isError when service token is invalid (list_customers)', async () => {
    const client = await createTestClient({
      serviceToken: 'invalid-token-that-does-not-exist',
      role: 'admin',
      department: 'sales',
    })

    try {
      const result = await client.callTool({
        name: 'list_customers',
        arguments: {},
      }) as unknown as CustomersResult

      assert.strictEqual(result.structuredContent.isError, true, 'Should return isError: true for invalid token')
      assert.ok(
        result.structuredContent.message!.toLowerCase().includes('unauthorized'),
        `Error message should mention "unauthorized", got: ${result.structuredContent.message}`
      )
    } finally {
      await client.close()
    }
  })

  it('should block create_customer for member from support department', async () => {
    const memberClient = await createTestClient(await getServiceToken({
      username: 'ananeri',
      password: '1234',
    }))

    try {
      const result = await memberClient.callTool({
        name: 'create_customer',
        arguments: { name: 'Blocked User', phone: '111-222-3333' },
      }) as unknown as CustomerResult

      assert.strictEqual(result.structuredContent.isError, true)
      assert.match(
        result.structuredContent.message!,
        /role 'member' cannot execute 'create_customer'/
      )
    } finally {
      await memberClient.close()
    }
  })

  it('should block delete_customer for admin outside sales department', async () => {
    const adminSupportClient = await createTestClient({
      serviceToken: (await getCachedAdminToken()).serviceToken,
      role: 'admin',
      department: 'support',
    })

    try {
      const result = await adminSupportClient.callTool({
        name: 'delete_customer',
        arguments: { _id: '507f1f77bcf86cd799439011' },
      }) as unknown as CustomerResult

      assert.strictEqual(result.structuredContent.isError, true)
      assert.match(
        result.structuredContent.message!,
        /department 'support' cannot execute 'delete_customer'/
      )
    } finally {
      await adminSupportClient.close()
    }
  })
})

describe('Customer Tools rate limit', () => {
  let client: Client

  before(async () => {
    client = await createTestClient(await getServiceToken(), FAST_RATE_LIMIT)
  })

  after(async () => {
    await client.close()
  })

  it('should reach rate limit under DDoS-like burst', async () => {
    let result: CustomersResult = { structuredContent: { isError: false, message: '' } }
    const maxAttempts = 8

    for (let index = 0; index < maxAttempts; index++) {
      result = await client.callTool({
        name: 'list_customers',
        arguments: {},
      }) as unknown as CustomersResult

      if (result.structuredContent.isError) {
        break
      }
    }

    assert.ok(result.structuredContent.isError, 'Should return isError: true for rate limit exceeded')
    assert.strictEqual(
      result.structuredContent.message,
      'Failed to list customers. Error: Rate limit exceeded. Please try again later.',
      'Error message should indicate full error message'
    )
  })
})
