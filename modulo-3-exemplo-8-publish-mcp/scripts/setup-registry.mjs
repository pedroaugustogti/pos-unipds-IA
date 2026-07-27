import { spawnSync } from 'node:child_process';
import { writeFileSync } from 'node:fs';
import { setTimeout as delay } from 'node:timers/promises';

const REGISTRY = process.env.NPM_REGISTRY ?? 'http://localhost:4873';
const USERNAME = process.env.NPM_USER ?? 'pedroaugusto';
const PASSWORD = process.env.NPM_PASSWORD ?? '123456';

async function waitForRegistry(retries = 30) {
  for (let i = 0; i < retries; i++) {
    try {
      const res = await fetch(REGISTRY);
      if (res.ok) return;
    } catch {
      // retry
    }
    await delay(1000);
  }
  throw new Error(`Registry not reachable at ${REGISTRY}`);
}

function ensureUser() {
  const register = spawnSync(
    'curl',
    [
      '-s',
      '-X', 'PUT',
      `${REGISTRY}/-/user/org.couchdb.user:${USERNAME}`,
      '-H', 'Content-Type: application/json',
      '-d', JSON.stringify({ name: USERNAME, password: PASSWORD }),
    ],
    { encoding: 'utf8', shell: true },
  );

  if (register.status !== 0 && !String(register.stderr).includes('already')) {
    console.warn('User registration note:', register.stderr || register.stdout);
  }

  const auth = Buffer.from(`${USERNAME}:${PASSWORD}`).toString('base64');
  writeFileSync(
    '.npmrc',
    `@pedroaugusto:registry=${REGISTRY}/\n//localhost:4873/:_auth=${auth}\n//localhost:4873/:always-auth=true\n`,
    'utf8',
  );
}

async function main() {
  console.log(`Waiting for Verdaccio at ${REGISTRY}...`);
  await waitForRegistry();
  ensureUser();

  const whoami = spawnSync('npm', ['whoami', '--registry', REGISTRY], {
    encoding: 'utf8',
    shell: true,
  });

  if (whoami.status !== 0) {
    throw new Error(whoami.stderr || 'npm whoami failed');
  }

  console.log(`Logged in as ${whoami.stdout.trim()} at ${REGISTRY}`);
  console.log('Wrote .npmrc for scoped publish.');
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
