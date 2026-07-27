import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { HumanMessage } from '@langchain/core/messages';
import { buildGraph } from '../src/graph/factory.ts';
import { closeMcpConnections } from '../src/services/mcpService.ts';

const moduleRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const prompt =
  'Crie 10 clientes de teste usando as tools de customer (nomes e telefones unicos). Depois liste todos com list_customers e mostre o resultado.';

console.log('Building graph...');
const graph = await buildGraph();

console.log('Invoking graph (pode levar varios minutos)...');
const result = await graph.invoke({
  messages: [new HumanMessage(prompt)],
});

const text = [
  result.answer,
  ...result.messages.map((m) => m.text).filter(Boolean),
].filter(Boolean).join('\n');

mkdirSync(resolve(moduleRoot, 'data'), { recursive: true });
writeFileSync(
  resolve(moduleRoot, 'data/validation-run.json'),
  JSON.stringify({ prompt, result, text }, null, 2),
);

console.log('\n--- Result preview ---');
console.log(text.slice(0, 2500) || JSON.stringify(result).slice(0, 2500));

const lower = text.toLowerCase();
if (lower.includes('sorry, an error occurred') || lower.includes('connection error')) {
  console.error('\nGraph returned an error');
  await closeMcpConnections();
  process.exit(1);
}

if (!lower.includes('customer') && !lower.includes('cliente')) {
  console.warn('\nWarning: output may not include customer listing');
} else {
  console.log('\nvalidate:langgraph OK');
}

await closeMcpConnections();
