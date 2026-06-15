'use strict';
const { execFileSync } = require('child_process');
const os = require('os');
const path = require('path');

function readStdin() {
  return new Promise((resolve) => {
    let data = '';
    if (process.stdin.isTTY) { resolve('{}'); return; }
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', chunk => data += chunk);
    process.stdin.on('end', () => resolve(data || '{}'));
    setTimeout(() => resolve(data || '{}'), 3000);
  });
}

async function main() {
  try {
    const raw = await readStdin();
    const bunExe = path.join(os.homedir(), '.bun', 'bin', 'bun.exe');
    const workerScript = path.join(
      os.homedir(), '.claude', 'plugins', 'marketplaces',
      'thedotmack', 'plugin', 'scripts', 'worker-service.cjs'
    );

    execFileSync(bunExe, [workerScript, 'hook', 'gemini-cli', 'summarize'], {
      input: raw,
      timeout: 20000,
      stdio: ['pipe', 'pipe', 'pipe']
    });
  } catch { /* non-fatal */ }

  // Empty decision = default stop behavior (não continua o loop)
  process.stdout.write('{"decision": ""}');
}

main();
