import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { setTimeout as delay } from 'node:timers/promises';

const moduleRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const dataDir = resolve(moduleRoot, 'data');
const port = process.env.LANGGRAPH_PORT ?? '2024';
const apiHost = process.env.LANGGRAPH_HOST ?? 'localhost';
const apiUrl = `http://${apiHost}:${port}`;
const prompt =
  'Crie 10 clientes de teste usando as tools de customer (nomes e telefones unicos). Depois liste todos com list_customers e mostre o resultado.';

process.env.NODE_OPTIONS = [process.env.NODE_OPTIONS, '--use-system-ca'].filter(Boolean).join(' ');

async function waitForApi(retries = 90) {
  for (let i = 0; i < retries; i++) {
    try {
      const res = await fetch(`${apiUrl}/info`);
      if (res.ok) return;
    } catch {
      // retry
    }
    await delay(2000);
  }
  throw new Error(`LangGraph API not reachable at ${apiUrl}`);
}

async function invokeGraph() {
  const assistantsRes = await fetch(`${apiUrl}/assistants/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ limit: 10, offset: 0 }),
  });

  if (!assistantsRes.ok) {
    throw new Error(`assistants/search failed (${assistantsRes.status})`);
  }

  const assistants = await assistantsRes.json();
  const assistant = assistants.find((a) => a.graph_id === 'multiple_mcp_tools') ?? assistants[0];
  if (!assistant) throw new Error('Assistant multiple_mcp_tools not found');

  const threadRes = await fetch(`${apiUrl}/threads`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({}),
  });
  const thread = await threadRes.json();

  console.log(`Thread: ${thread.thread_id}`);
  console.log('Invoking graph (pode levar varios minutos)...');

  const runRes = await fetch(`${apiUrl}/threads/${thread.thread_id}/runs/wait`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      assistant_id: assistant.assistant_id,
      input: { messages: [{ type: 'human', content: prompt }] },
    }),
    signal: AbortSignal.timeout(600_000),
  });

  if (!runRes.ok) {
    throw new Error(`run failed (${runRes.status}): ${(await runRes.text()).slice(0, 800)}`);
  }

  return runRes.json();
}

function collectText(result) {
  const parts = [];
  const walk = (value) => {
    if (!value) return;
    if (typeof value === 'string') {
      parts.push(value);
      return;
    }
    if (Array.isArray(value)) {
      value.forEach(walk);
      return;
    }
    if (typeof value === 'object') {
      if (typeof value.content === 'string') parts.push(value.content);
      if (Array.isArray(value.content)) {
        value.content.forEach((c) => {
          if (typeof c === 'string') parts.push(c);
          if (c?.text) parts.push(c.text);
        });
      }
      if (value.text) parts.push(value.text);
      if (value.answer) parts.push(value.answer);
      Object.values(value).forEach(walk);
    }
  };
  walk(result);
  return parts.join('\n');
}

let langgraph;
let startedHere = false;

try {
  await waitForApi(3);
  console.log(`LangGraph API: ${apiUrl}`);
} catch {
  startedHere = true;
  console.log('Starting LangGraph dev server...');
  langgraph = spawn('npx', ['@langchain/langgraph-cli', 'dev', '--port', port], {
    cwd: moduleRoot,
    shell: true,
    stdio: 'pipe',
    env: process.env,
  });
  langgraph.stdout?.on('data', (c) => process.stdout.write(c));
  langgraph.stderr?.on('data', (c) => process.stderr.write(c));
  await waitForApi();
  console.log(`LangGraph API started: ${apiUrl}`);
}

try {
  const result = await invokeGraph();
  const text = collectText(result);
  const lower = text.toLowerCase();

  mkdirSync(dataDir, { recursive: true });
  writeFileSync(resolve(dataDir, 'validation-run.json'), JSON.stringify({ prompt, result, text }, null, 2));

  console.log('\n--- Result preview ---');
  console.log(text.slice(0, 2500) || JSON.stringify(result).slice(0, 2500));

  if (lower.includes('sorry, an error occurred') || lower.includes('model_not_found')) {
    console.error('\nLangGraph run returned an error');
    process.exit(1);
  }

  if (!lower.includes('customer') && !lower.includes('cliente')) {
    console.warn('\nWarning: output may not include customer listing');
  } else {
    console.log('\nvalidate:langgraph:api OK');
  }
} finally {
  if (startedHere) langgraph?.kill();
}
