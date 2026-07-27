import { getMCPTools, closeMcpConnections } from '../src/services/mcpService.ts';

const tools = await getMCPTools();
const customerTools = tools.filter((t) => t.name.includes('customer'));

console.log(`OK: ${tools.length} MCP tools loaded`);
console.log('Customer tools:', customerTools.map((t) => t.name).join(', '));

if (customerTools.length < 5) {
  console.error('Expected at least 5 customer tools');
  process.exit(1);
}

await closeMcpConnections();
console.log('validate:mcp-tools OK');
