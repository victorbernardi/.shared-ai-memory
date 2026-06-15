'use strict';
const http = require('http');
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

function fetchContext(project) {
  return new Promise((resolve) => {
    const url = `http://localhost:37777/api/context/inject?project=${encodeURIComponent(project)}`;
    const req = http.get(url, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => resolve(body.trim() || null));
    });
    req.on('error', () => resolve(null));
    req.setTimeout(4000, () => { req.destroy(); resolve(null); });
  });
}

async function main() {
  try {
    const raw = await readStdin();
    const input = JSON.parse(raw);

    // Inject only on the first invocation to avoid repeating every turn
    if ((input.invocationNum || 0) > 0) {
      process.stdout.write('{}');
      return;
    }

    const workspacePath = (input.workspacePaths || [])[0] || process.cwd();
    const project = path.basename(workspacePath);

    const context = await fetchContext(project);

    if (context && context.length > 80) {
      process.stdout.write(JSON.stringify({
        injectSteps: [{ ephemeralMessage: context }]
      }));
    } else {
      process.stdout.write('{}');
    }
  } catch {
    process.stdout.write('{}');
  }
}

main();
