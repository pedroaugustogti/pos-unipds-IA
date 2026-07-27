import { spawn } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const moduleRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');

process.env.NODE_OPTIONS = [process.env.NODE_OPTIONS, '--use-system-ca'].filter(Boolean).join(' ');

const port = process.env.LANGGRAPH_PORT ?? '2024';
const cli = resolve(moduleRoot, 'node_modules/.bin/langgraphjs');

const child = spawn(
  process.execPath,
  ['--use-system-ca', '--env-file', '.env', cli, 'dev', '--port', port],
  {
    cwd: moduleRoot,
    stdio: 'inherit',
    env: process.env,
    shell: false,
  },
);

child.on('exit', (code) => process.exit(code ?? 0));
