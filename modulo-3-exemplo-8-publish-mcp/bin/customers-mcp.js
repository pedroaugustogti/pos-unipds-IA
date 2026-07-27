#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const pkgRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const require = createRequire(import.meta.url);
const tsxCli = require.resolve('tsx/cli', { paths: [pkgRoot] });
const entry = join(pkgRoot, 'src/index.ts');

const result = spawnSync(process.execPath, [tsxCli, entry], {
  stdio: 'inherit',
  env: process.env,
});

process.exit(result.status ?? 1);
