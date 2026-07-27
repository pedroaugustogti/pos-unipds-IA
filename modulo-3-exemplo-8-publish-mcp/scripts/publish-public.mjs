import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';

process.env.NODE_OPTIONS = [process.env.NODE_OPTIONS, '--use-system-ca'].filter(Boolean).join(' ');

const REGISTRY = 'https://registry.npmjs.org/';
const PACKAGE = '@gorgan/customers-mcp';
const npm = process.platform === 'win32' ? 'npm.cmd' : 'npm';

function hasAuth() {
  if (process.env.NPM_TOKEN?.trim()) return true;
  try {
    const npmrc = readFileSync(join(homedir(), '.npmrc'), 'utf8');
    return npmrc.includes('//registry.npmjs.org/:_authToken=');
  } catch {
    return false;
  }
}

function run(args) {
  const result = spawnSync(npm, args, {
    encoding: 'utf8',
    shell: true,
    env: process.env,
  });

  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);

  if (result.status !== 0) {
    process.exit(result.status ?? 1);
  }
}

if (!hasAuth()) {
  console.error('npm not authenticated. Create a token at:');
  console.error('  https://www.npmjs.com/settings/gorgan/tokens');
  console.error('Then run:');
  console.error('  $env:NPM_TOKEN="npm_..."');
  console.error('  npm run registry:login:public');
  console.error('  npm run release:public');
  process.exit(1);
}

if (process.env.NPM_TOKEN?.trim()) {
  run(['config', 'set', '//registry.npmjs.org/:_authToken', process.env.NPM_TOKEN.trim(), '--location', 'user']);
}

const whoami = spawnSync(npm, ['whoami', '--registry', REGISTRY], {
  encoding: 'utf8',
  shell: true,
  env: process.env,
});

if (whoami.status !== 0) {
  console.error('Authentication failed:', whoami.stderr);
  process.exit(1);
}

console.log(`Logged in as ${whoami.stdout.trim()}`);
console.log(`Publishing ${PACKAGE} to npm public registry...`);
run(['version', 'patch', '--no-git-tag-version']);
run(['publish', '--access', 'public', '--registry', REGISTRY]);
console.log(`Published: https://www.npmjs.com/package/${PACKAGE.replace('/', '%2F')}`);
