import { spawnSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const envFile = join(root, '.env');
const testFile = join(root, 'test', 'e2e', 'chat.pipeline.e2e.test.ts');

const r = spawnSync(
  process.execPath,
  [
    '--env-file',
    envFile,
    '--experimental-strip-types',
    '--test-timeout=100000',
    '--test',
    testFile,
  ],
  {
    cwd: root,
    stdio: 'inherit',
    env: { ...process.env, RUN_FULL_E2E: '1' },
  },
);

process.exit(r.status ?? 1);
