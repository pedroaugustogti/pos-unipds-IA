import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'
import type { ServiceTokenMetadata } from '../src/domain/token-context.ts'

const API_URL = process.env.CUSTOMERS_API_URL ?? 'http://127.0.0.1:9999/v1'

export interface ServiceTokenCredentials {
  username: string
  password: string
  adminSuperSecret?: string
}

export interface TestClientOptions {
  rateLimitMax?: number
  rateLimitWindowMs?: number
}

const DEFAULT_CREDENTIALS: ServiceTokenCredentials = {
  username: 'erickwendel',
  password: '123123',
  adminSuperSecret: 'AM I THE BOSS?',
}

let cachedAdminToken: ServiceTokenMetadata | null = null

export async function getServiceToken(
  credentials: ServiceTokenCredentials = DEFAULT_CREDENTIALS
): Promise<ServiceTokenMetadata> {
  const res = await fetch(`${API_URL}/auth/service-token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: credentials.username,
      password: credentials.password,
      adminSuperSecret: credentials.adminSuperSecret ?? 'AM I THE BOSS?',
    }),
  })
  if (!res.ok) throw new Error(`Failed to get service token: ${res.status}`)
  const payload = await res.json() as ServiceTokenMetadata
  return payload
}

export async function getCachedAdminToken(): Promise<ServiceTokenMetadata> {
  if (!cachedAdminToken) {
    cachedAdminToken = await getServiceToken()
  }
  return cachedAdminToken
}

export async function createTestClient(
  metadata: ServiceTokenMetadata,
  options: TestClientOptions = {}
) {
  const transport = new StdioClientTransport({
    command: 'node',
    args: ['--experimental-strip-types', 'src/index.ts'],
    env: {
      ...process.env,
      SERVICE_TOKEN: metadata.serviceToken,
      SERVICE_TOKEN_ROLE: metadata.role,
      SERVICE_TOKEN_DEPARTMENT: metadata.department,
      RATE_LIMIT_MAX_REQUESTS: String(options.rateLimitMax ?? process.env.RATE_LIMIT_MAX_REQUESTS ?? 90),
      RATE_LIMIT_WINDOW_MS: String(options.rateLimitWindowMs ?? process.env.RATE_LIMIT_WINDOW_MS ?? 60_000),
    },
  })

  const client = new Client({
    name: 'test-client',
    version: '1.0.0'
  }, {
    capabilities: {}
  })

  await client.connect(transport)
  return client
}
