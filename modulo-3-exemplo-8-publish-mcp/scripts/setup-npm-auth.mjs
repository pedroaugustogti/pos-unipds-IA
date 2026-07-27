import { spawnSync } from 'node:child_process';

process.env.NODE_OPTIONS = [process.env.NODE_OPTIONS, '--use-system-ca'].filter(Boolean).join(' ');

const token = process.env.NPM_TOKEN?.trim();
if (!token) {
  console.error('Set NPM_TOKEN with your granular access token from npmjs.com:');
  console.error('  $env:NPM_TOKEN="npm_..."');
  console.error('  npm run registry:login:public');
  process.exit(1);
}

const npm = process.platform === 'win32' ? 'npm.cmd' : 'npm';
const result = spawnSync(
  npm,
  ['config', 'set', '//registry.npmjs.org/:_authToken', token, '--location', 'user'],
  { encoding: 'utf8', shell: true, env: process.env },
);

if (result.stdout) process.stdout.write(result.stdout);
if (result.stderr) process.stderr.write(result.stderr);

if (result.status !== 0) {
  process.exit(result.status ?? 1);
}

const whoami = spawnSync(npm, ['whoami', '--registry', 'https://registry.npmjs.org/'], {
  encoding: 'utf8',
  shell: true,
  env: process.env,
});

if (whoami.status !== 0) {
  console.error('Token saved but whoami failed:', whoami.stderr);
  process.exit(1);
}

console.log(`npm authenticated as ${whoami.stdout.trim()}`);
