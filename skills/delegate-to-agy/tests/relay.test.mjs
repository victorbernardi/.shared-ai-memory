import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { tmpdir } from 'node:os';

const relayScript = resolve('skills/delegate-to-agy/scripts/relay.mjs');
const tempRoot = join(tmpdir(), 'relay-test-' + Date.now());
mkdirSync(tempRoot, { recursive: true });

let failures = 0;
function test(name, fn) {
  try {
    fn();
    console.log('PASS: ' + name);
  } catch (err) {
    failures++;
    console.error('FAIL: ' + name + ' -> ' + err.message);
  }
}

try {
  test('relay.mjs prints help and exits 0', () => {
    const res = spawnSync(process.execPath, [relayScript, '--help'], { encoding: 'utf8' });
    if (res.status !== 0) throw new Error('Expected exit 0, got ' + res.status);
    if (!res.stdout.includes('delegate-skills')) throw new Error('Expected help header in stdout');
  });

  test('relay.mjs rejects unknown option with exit 2', () => {
    const res = spawnSync(process.execPath, [relayScript, '--bogus-flag'], { encoding: 'utf8' });
    if (res.status !== 2) throw new Error('Expected exit 2, got ' + res.status);
    if (!res.stderr.includes('unknown option')) throw new Error('Expected error message in stderr');
  });

  test('relay.mjs rejects missing value with exit 2', () => {
    const res = spawnSync(process.execPath, [relayScript, '--model'], { encoding: 'utf8' });
    if (res.status !== 2) throw new Error('Expected exit 2, got ' + res.status);
  });

  test('relay.mjs rejects mutually exclusive flags with exit 2', () => {
    const res = spawnSync(process.execPath, [relayScript, '--read-only', '--dangerously-skip-permissions'], { encoding: 'utf8' });
    if (res.status !== 2) throw new Error('Expected exit 2, got ' + res.status);
    if (!res.stderr.includes('mutually exclusive')) throw new Error('Expected mutually exclusive error');
  });

  test('relay.mjs rejects invalid effort with exit 2', () => {
    const res = spawnSync(process.execPath, [relayScript, '--effort', 'extreme'], { encoding: 'utf8' });
    if (res.status !== 2) throw new Error('Expected exit 2, got ' + res.status);
  });

  test('relay.mjs live probe (read-only) produces valid result.json', () => {
    const briefPath = join(tempRoot, 'smoke-brief.txt');
    const outDir = join(tempRoot, 'out');
    mkdirSync(outDir, { recursive: true });
    writeFileSync(briefPath, 'AGY PREFLIGHT PROBE: no writes. Responda apenas: PONG_RELAY_OK', 'utf8');

    const res = spawnSync(process.execPath, [
      relayScript,
      '--brief', briefPath,
      '--read-only',
      '--timeout', '3m',
      '--out-dir', outDir,
    ], { encoding: 'utf8', timeout: 180000 });

    const resultPath = join(outDir, 'result.json');
    if (!existsSync(resultPath)) {
      throw new Error('result.json was not created; exit=' + res.status + '; stderr=' + res.stderr);
    }

    const result = JSON.parse(readFileSync(resultPath, 'utf8'));
    if (!result.conversationId) throw new Error('Expected conversationId in result.json');
    if (!result.agyVersion) throw new Error('Expected agyVersion in result.json');

    if (res.status === 0) {
      if (result.status !== 'completed') throw new Error('Expected status completed, got ' + result.status);
      if (result.exitCode !== 0) throw new Error('Expected exitCode 0, got ' + result.exitCode);
      if (!result.finalMessage.includes('PONG_RELAY_OK')) {
        throw new Error('Expected PONG_RELAY_OK in finalMessage, got: ' + result.finalMessage);
      }
    } else {
      if (result.status !== 'failed') throw new Error('Expected status failed, got ' + result.status);
      console.log('  (Live probe: agy returned non-zero ' + res.status + ', relay cleanly captured result.json)');
    }
  });

} finally {
  try { rmSync(tempRoot, { recursive: true, force: true }); } catch {}
}

if (failures > 0) {
  console.error(failures + ' test(s) failed');
  process.exit(1);
} else {
  console.log('All relay tests passed successfully!');
}
