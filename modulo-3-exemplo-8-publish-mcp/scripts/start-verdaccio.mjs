import { spawn } from 'node:child_process';
import { existsSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';

const REGISTRY = 'http://localhost:4873';
const PID_FILE = resolve('.verdaccio.pid');

async function isRegistryUp() {
  try {
    const res = await fetch(REGISTRY);
    return res.ok;
  } catch {
    return false;
  }
}

async function main() {
  if (await isRegistryUp()) {
    console.log(`Verdaccio already running at ${REGISTRY}`);
    return;
  }

  const configPath = resolve('verdaccio/config.yaml');
  const child = spawn(
    process.platform === 'win32' ? 'npx.cmd' : 'npx',
    ['verdaccio', '-c', configPath, '-l', REGISTRY],
    {
      detached: true,
      stdio: 'ignore',
      shell: true,
    },
  );

  child.unref();
  writeFileSync(PID_FILE, String(child.pid), 'utf8');

  for (let i = 0; i < 30; i++) {
    if (await isRegistryUp()) {
      console.log(`Verdaccio started at ${REGISTRY} (pid ${child.pid})`);
      return;
    }
    await delay(1000);
  }

  throw new Error('Verdaccio failed to start within 30s');
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
