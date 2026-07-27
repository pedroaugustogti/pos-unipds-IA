import { spawnSync } from 'node:child_process';

process.env.NODE_OPTIONS = [process.env.NODE_OPTIONS, '--use-system-ca'].filter(Boolean).join(' ');

const REGISTRY = 'https://registry.npmjs.org/';
const npm = process.platform === 'win32' ? 'npm.cmd' : 'npm';

function run(args, { capture = false } = {}) {
  const result = spawnSync(npm, args, {
    encoding: 'utf8',
    shell: true,
    env: process.env,
  });

  if (!capture) {
    if (result.stdout) process.stdout.write(result.stdout);
    if (result.stderr) process.stderr.write(result.stderr);
  }

  if (result.status !== 0) {
    throw new Error(result.stderr || result.stdout || `npm ${args.join(' ')} failed`);
  }

  return result.stdout?.trim() ?? '';
}

function extractTokenFromBrowser() {
  const read = spawnSync(
    'npx',
    ['agent-browser', '--session', 'npm-publish', 'read'],
    { encoding: 'utf8', shell: true, env: process.env },
  );

  const output = `${read.stdout}\n${read.stderr}`;
  const match = output.match(/npm_[A-Za-z0-9]+/);
  if (!match) {
    throw new Error('Token not found in agent-browser session output');
  }
  return match[0];
}

const token = extractTokenFromBrowser();
run(['config', 'set', '//registry.npmjs.org/:_authToken', token, '--location', 'user']);
const user = run(['whoami', '--registry', REGISTRY], { capture: true });
console.log(`Authenticated as ${user}`);
console.log('Publishing @gorgan/customers-mcp...');
run(['version', 'patch', '--no-git-tag-version']);
run(['publish', '--access', 'public', '--registry', REGISTRY]);
console.log('Published: https://www.npmjs.com/package/@gorgan/customers-mcp');
