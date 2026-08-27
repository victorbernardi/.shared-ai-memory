# Impeccable Plugin Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the Impeccable 4.1.2 skill with the static detector runtime packaged so plugin installs resolve HTML/CSS parser dependencies instead of silently falling back to regex.

**Architecture:** Keep the upstream skill scripts intact, add a private runtime manifest beside them, and vendor its production dependency tree under `scripts/node_modules/`, which is inside the path copied by plugin/skill installers. Validate module resolution from the detector entrypoint and run a real HTML scan before deploying the same payload to the user-wide `.agents` skill directory.

**Tech Stack:** Node.js 24, npm, ECMAScript modules, Node's built-in `node:test`, GitHub skill installer.

## Global Constraints

- The installed skill must be Impeccable `4.1.2`, not the existing `4.1.1` copy.
- The static detector must resolve `htmlparser2`, `css-select`, `css-tree`, and `domutils` from its installed path.
- The packaged runtime must not require the user to run `npm install` after a plugin/skill installation.
- URL/browser scanning remains outside this fix because Puppeteer is optional and is not required for the reported static-HTML degradation.
- Preserve the existing worktree and repair only the existing plugin cache version `4.1.2`; do not modify other versions or plugins.

---

### Task 1: Add the failing detector-runtime regression test

**Files:**
- Create: `skills/impeccable/tests/detector-runtime.test.mjs`
- Create: `skills/impeccable/tests/fixtures/static-runtime.html`

**Interfaces:**
- Consumes: `skills/impeccable/scripts/detect.mjs` and the four static detector packages.
- Produces: A repeatable test proving the installed detector has parser modules and does not emit the `DEGRADED` fallback warning.

- [x] **Step 1: Write the failing test**

Create a Node test that resolves every parser package with `createRequire()` anchored at `scripts/detector/engines/static-html/detect-html.mjs`, asserts each result is inside `scripts/node_modules`, copies the full skill to a temporary staged directory, then runs `node scripts/detect.mjs <fixture>` from both payloads and asserts stderr does not contain `DEGRADED`.

- [x] **Step 2: Run the test to verify it fails**

Run:

```powershell
node --test skills/impeccable/tests/detector-runtime.test.mjs
```

Expected: FAIL because the current 4.1.1 skill has no `scripts/node_modules` and Node cannot resolve at least one required parser package.

Observed: both the direct resolution test and the real HTML scan failed with the expected missing-module/degraded-engine evidence.

### Task 2: Update the source payload to Impeccable 4.1.2

**Files:**
- Modify: `skills/impeccable/SKILL.md`
- Modify: `skills/impeccable/agents/*`
- Modify: `skills/impeccable/reference/*`
- Modify: `skills/impeccable/scripts/*`

**Interfaces:**
- Consumes: The verified GitHub `main/.agents/skills/impeccable` payload.
- Produces: The same skill payload at version 4.1.2, including the four upstream agent definitions.

- [x] **Step 1: Synchronize the tracked skill payload**

Copy the already downloaded and verified GitHub 4.1.2 skill payload into `skills/impeccable/`, retaining the repository's tracked layout and not touching unrelated skills.

- [x] **Step 2: Verify the version and syntax**

Run:

```powershell
Select-String -LiteralPath skills/impeccable/SKILL.md -Pattern '^version: 4\.1\.2$'
Get-ChildItem skills/impeccable/scripts -Recurse -File -Filter '*.mjs' | ForEach-Object { node --check $_.FullName }
```

Expected: The version assertion matches and every JavaScript module exits 0 from syntax checking.

Observed: the verified GitHub payload comparison matched all 153 upstream files; the tracked skill reports 4.1.2.

### Task 3: Package the static detector runtime

**Files:**
- Modify: `.gitignore`
- Create: `skills/impeccable/scripts/package.json`
- Create: `skills/impeccable/scripts/package-lock.json`
- Create: `skills/impeccable/scripts/node_modules/*`

**Interfaces:**
- Consumes: The direct runtime versions declared by Impeccable: `css-select@7.0.0`, `css-tree@3.2.1`, `domutils@4.0.2`, and `htmlparser2@12.0.0`.
- Produces: A self-contained `scripts/` package whose transitive runtime tree is copied with the skill and resolves from the detector entrypoint.

- [x] **Step 1: Declare the runtime contract**

Add a private ES-module manifest under `skills/impeccable/scripts/` with those four exact production dependencies and no install-time script.

- [x] **Step 2: Install the vendored dependency tree**

Run `npm.cmd install --ignore-scripts --save-exact` in `skills/impeccable/scripts/`, then verify the four packages and all transitive packages are regular directories with no symbolic links.

- [x] **Step 3: Make the vendor tree trackable**

Add narrowly scoped negations to `.gitignore` for `skills/impeccable/scripts/node_modules/` and its contents, keeping all other `node_modules` directories ignored by global or repository rules.

- [x] **Step 4: Run the regression test to verify it passes**

Run:

```powershell
node --test skills/impeccable/tests/detector-runtime.test.mjs
```

Expected: PASS; the scan resolves all four packages and does not emit the degraded warning.

Observed: 3/3 tests passed; npm resolved 13 production packages and reported zero vulnerabilities.

### Task 4: Deploy and verify the user-wide skill

**Files:**
- Modify: `C:/Users/victor.bernardi/.agents/skills/impeccable/*`
- Modify: `C:/Users/victor.bernardi/.codex/plugins/cache/impeccable/impeccable/4.1.2/skills/impeccable/scripts/*`

**Interfaces:**
- Consumes: The tracked 4.1.2 skill plus its packaged `scripts/node_modules` tree.
- Produces: A user-wide `.agents/skills/impeccable` installation with the same version, files, and runtime behavior.

- [x] **Step 1: Replace only the existing Impeccable installation**

After verifying the exact destinations, deploy the repository payload to `C:\Users\victor.bernardi\.agents\skills\impeccable` and copy only the runtime manifest, lockfile, and vendor tree into the existing `C:\Users\victor.bernardi\.codex\plugins\cache\impeccable\impeccable\4.1.2\skills\impeccable\scripts`, preserving all other user skills and plugin versions.

- [x] **Step 2: Verify installed parity and runtime behavior**

Run the version check, module-resolution test, and a real detector scan against the installed path. Confirm the result contains no `DEGRADED` warning and report any findings separately from the runtime status.

Observed: `.agents` and the exact plugin cache both report version 4.1.2, resolve all four packages from their local vendor trees, and exit 0 with empty stderr on the fixture scan.

- [x] **Step 3: Run final repository checks**

Run the first-party repository checks (the published vendor payload is kept
byte-for-byte so dependency contents are not silently rewritten):

```powershell
git diff --check -- . ':(exclude)skills/impeccable/scripts/node_modules/**'
git status --short
node --test skills/impeccable/tests/detector-runtime.test.mjs
```

Expected: no whitespace errors in first-party files, only scoped Impeccable
changes, and the runtime regression test passes.

Observed: the first-party diff check passes, no out-of-scope paths were found,
and the regression suite passes 4/4. The unfiltered range check reports 18
whitespace findings in 14 published dependency files under
`skills/impeccable/scripts/node_modules/` (including trailing whitespace and
blank lines at EOF); those vendor bytes are intentionally preserved rather
than normalized.
