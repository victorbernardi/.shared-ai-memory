import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import { cpSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { test } from 'node:test';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { detectText } from '../scripts/detector/engines/regex/detect-text.mjs';

const skillRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const detectorEntry = path.join(
  skillRoot,
  'scripts',
  'detector',
  'engines',
  'static-html',
  'detect-html.mjs',
);
const detectorScript = path.join(skillRoot, 'scripts', 'detect.mjs');
const fixture = path.join(import.meta.dirname, 'fixtures', 'static-runtime.html');
const commentedGlowFixture = path.join(import.meta.dirname, 'fixtures', 'commented-glow.html');
const staticRuntimePackages = ['htmlparser2', 'css-select', 'css-tree', 'domutils'];

function assertPackagedResolutions(detectorPath, runtimeRoot) {
  const requireFromDetector = createRequire(detectorPath);
  const resolvedRoot = path.resolve(runtimeRoot);

  for (const packageName of staticRuntimePackages) {
    const resolved = requireFromDetector.resolve(packageName);
    const relative = path.relative(resolvedRoot, path.resolve(resolved));
    assert.ok(
      relative && !relative.startsWith('..') && !path.isAbsolute(relative),
      `${packageName} resolved outside the packaged runtime: ${resolved}`,
    );
  }
}

function assertRealScanIsNotDegraded(root, target = fixture) {
  const result = spawnSync(process.execPath, [path.join(root, 'scripts', 'detect.mjs'), target], {
    cwd: root,
    encoding: 'utf8',
  });

  assert.equal(result.error, undefined, result.error?.message);
  assert.ok([0, 2].includes(result.status), `unexpected detector exit code: ${result.status}`);
  assert.doesNotMatch(result.stderr, /DEGRADED - HTML parser modules unavailable/);
}

test('the packaged detector resolves every static HTML runtime package', () => {
  assertPackagedResolutions(detectorEntry, path.join(skillRoot, 'scripts', 'node_modules'));
});

test('a real HTML scan does not fall back to the degraded regex engine', () => {
  assertRealScanIsNotDegraded(skillRoot);
});

test('a copied skill payload keeps the static detector runtime self-contained', () => {
  const stagingRoot = mkdtempSync(path.join(os.tmpdir(), 'impeccable-skill-'));
  const stagedSkillRoot = path.join(stagingRoot, 'impeccable');

  try {
    cpSync(skillRoot, stagedSkillRoot, { recursive: true });
    const stagedDetectorEntry = path.join(
      stagedSkillRoot,
      'scripts',
      'detector',
      'engines',
      'static-html',
      'detect-html.mjs',
    );
    assertPackagedResolutions(
      stagedDetectorEntry,
      path.join(stagedSkillRoot, 'scripts', 'node_modules'),
    );
    assertRealScanIsNotDegraded(stagedSkillRoot);
  } finally {
    rmSync(stagingRoot, { recursive: true, force: true });
  }
});

test('comment-only CSS does not produce a dark-glow finding in the regex fallback', () => {
  const content = readFileSync(commentedGlowFixture, 'utf8');
  const findings = detectText(content, commentedGlowFixture);

  assert.deepEqual(
    findings.filter(({ antipattern }) => antipattern === 'dark-glow'),
    [],
  );
});
