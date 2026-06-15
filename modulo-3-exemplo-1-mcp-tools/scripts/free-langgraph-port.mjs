import { execSync } from 'node:child_process';

const port = process.env.LANGGRAPH_PORT ?? '2024';

function killOnWindows() {
  let output = '';
  try {
    output = execSync(`netstat -ano | findstr :${port}`, { encoding: 'utf8' });
  } catch {
    return;
  }

  const pids = new Set();
  for (const line of output.split('\n')) {
    if (!line.includes('LISTENING')) continue;
    const pid = line.trim().split(/\s+/).at(-1);
    if (pid && pid !== '0') pids.add(pid);
  }

  for (const pid of pids) {
    try {
      execSync(`taskkill /F /PID ${pid}`, { stdio: 'ignore' });
      console.log(`Port ${port}: processo ${pid} encerrado`);
    } catch {
      // already gone
    }
  }
}

function killOnUnix() {
  try {
    execSync(`lsof -ti:${port} | xargs -r kill -9`, { stdio: 'ignore', shell: true });
    console.log(`Port ${port}: processos encerrados`);
  } catch {
    // port free
  }
}

if (process.platform === 'win32') {
  killOnWindows();
} else {
  killOnUnix();
}
