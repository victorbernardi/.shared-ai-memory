# SDD Command Code Resumable Run Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace prompt-derived execution state with an auditable Run transaction that enforces scope, records provenance and normalized evidence, detects non-progress, and safely resumes the same Command Code Session.

**Architecture:** Add `run_record` as the structured transaction Module and `execution_lifecycle` as the deep Run lifecycle Module. Keep scope policy and the Command Code Mod private. The compatibility Adapter normalizes legacy arguments into a versioned Run Contract, while canonical `start` and `resume` operations consume persisted structured state. Recovery never creates a new Run or Session.

**Tech Stack:** Python 3 standard library, JSON/JSONL, Git plumbing commands, SHA-256, Command Code Mod hooks in TypeScript, pytest, the Delivery 1 `CmdcLocal` and `run_process` Interfaces.

## Global Constraints

- Begin only after every acceptance gate in `2026-08-19-sdd-cmdc-opencode-process-launcher.md` passes and its commits are present.
- Work only in the isolated feature worktree. Preserve unrelated and pre-existing changes; never reset or delete a violating path.
- Keep `cmdc-local` as the only implementation Adapter. Do not add `backends/base.py`, provider/proxy fallback, or a generic backend Seam.
- A Run Contract is immutable after start. Prompt text is rendered from it and never becomes authority for paths, scope, provenance, success, or Recovery.
- `allowed_paths` is explicit or deterministically derived from the task `Files` section. An absent/ambiguous scope is `SCOPE_CONTRACT_MISSING`; the repository root is never the default.
- `denied_paths` overrides `allowed_paths` after canonical, case-aware Windows path normalization and symlink checks.
- Preserve pre-existing changes byte-for-byte unless they are explicitly in scope. Dirty-worktree consent does not bypass scope or Recovery invariants.
- Use a Run-specific Command Code Mod through `--mod`; do not mutate user or project Command Code settings. Missing Mod/hook capability blocks preflight.
- Direct `write_file`/`edit_file` violations are blocked before execution. Indirect `shell_command` violations terminate after the awaited hook and are independently detected again by Python.
- `WORKER_TURN_LIMIT` may automatically Recovery the same Session up to `max_resumes`. `STALLED` and `WALL_TIMEOUT` require explicit `resume --run-id`. Launcher, protocol, scope, and cleanup failures are not resumable.
- A Fix Round is not Recovery. Delivery 2 records `review.auto_fix_rounds` but does not execute review correction policy.
- `COMPLETE` requires report, commit, test evidence, valid scope, final drain, and empty process tree when the corresponding success policy is true.
- Run tests from `skills/sdd-cmdc-opencode`; run the sibling `skills/sdd-cmdc` suite separately.
- Do not overwrite installed copies, publish, merge, push, or change issue state.

## Open-Issue and Regression Traceability

- [`Inova#169`](https://github.com/victorbernardi/Inova/issues/169): Tasks 1, 2, 5, and 7 cover Windows-native task extraction plus report paths containing spaces, quotes, backticks, split markers, and separators.
- [`Inova#170`](https://github.com/victorbernardi/Inova/issues/170): Task 3 enforces explicit/derived allowed paths, denied precedence, direct Mod blocking, post-shell termination, Recovery audit, and preserved violations.
- [`jd-bi-acs-telemetry#1`](https://github.com/victorbernardi/jd-bi-acs-telemetry/issues/1): Task 2 records authorized external-plan repository/branch/commit/path and plan/brief hashes without silently copying the plan.
- [`jd-bi-acs-telemetry#2`](https://github.com/victorbernardi/jd-bi-acs-telemetry/issues/2): Tasks 4 and 6 detect exploration-only non-progress and distinguish bounded same-session Recovery from a fresh Run.
- Closed `Inova#129`, `#131`, and `#164` remain explicit regression gates: timeout/partial-state observability and report discovery; required `plan_file`, preserved `MODE`/initial Git state, and explicit yolo consent; platform-normalized primary/Recovery launch with primary-cause preservation.
- Issue closure is outside this plan. Passing source tests is not publication, integration, operational smoke, review approval, or authority to close an issue.

---

## File Structure and Stable Interfaces

Add or change these paths:

```text
skills/sdd-cmdc-opencode/
  scripts/
    cmdc-implementer.py                         thin compatibility CLI Adapter
    task-brief                                 retained Bash compatibility wrapper
    task-brief.py                              cross-platform task/scope extractor
    sdd_cmdc_opencode/
      run_record.py                            deep Run transaction Module
      execution_lifecycle.py                   deep Run lifecycle Module
      _scope_guard.py                          private policy + JSON stdin CLI
      _scope_mod.ts                            immutable private Command Code Mod
  tests/
    test_task_brief.py
    test_run_record.py
    test_scope_guard.py
    test_execution_lifecycle.py
    test_run_integration.py
```

`run_record.py` uses these public values:

```python
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class RunStatus(str, Enum):
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"
    INCOMPLETE = "INCOMPLETE"


@dataclass(frozen=True)
class Blocker:
    code: str
    phase: str
    message: str


@dataclass(frozen=True)
class TestEvidence:
    command: str
    exit_code: int
    summary: str
    passed: int | None
    failed: int
    event_sequence: int


@dataclass(frozen=True)
class RecoveryEvidence:
    attempt: int
    trigger: str
    session_id: str
    checkpoint_sequence: int
    same_session: bool


@dataclass(frozen=True)
class RunLineage:
    kind: str
    parent_run_id: str
    parent_review_id: str
    parent_review_result_sha256: str
    parent_brief_sha256: str
    finding_ids: tuple[str, ...]
    findings_sha256: str


@dataclass(frozen=True)
class RunResult:
    schema_version: int
    run_id: str
    backend: str
    session_id: str | None
    status: RunStatus
    primary_blocker: Blocker | None
    secondary_blockers: tuple[Blocker, ...]
    base_head: str
    final_head: str
    scope_valid: bool
    violating_paths: tuple[str, ...]
    report_valid: bool
    test_evidence_valid: bool
    cleanup_verified: bool
    tests: tuple[TestEvidence, ...]
    recoveries: tuple[RecoveryEvidence, ...]
    artifact_hashes: Mapping[str, str]
```

The immutable `RunContract` is represented by frozen nested dataclasses matching the approved JSON keys: `TaskContract`, `PlanProvenance`, `WorkspaceContract`, `ScopeContract`, `ExecutionPolicy`, `SuccessPolicy`, and `ReviewPolicy`. It also accepts one known optional `RunLineage`; this field is absent for an initial task and has `kind: "fix-round"` plus the parent/finding hashes above for an explicitly authorized Fix Round. It exposes `RunContract.load(path)` and `RunContract.from_mapping(value)`; both reject unknown schema versions, missing required keys, unknown keys, wrong types, unsafe paths, unsupported backend values, and inconsistent limits.

`RunRecord` has this public Interface:

```text
RunRecord.create(run_dir: Path, contract: RunContract) -> RunRecord
RunRecord.load(run_dir: Path) -> RunRecord
RunRecord.locate(repo_root: Path, run_id: str) -> RunRecord
RunRecord.append_event(event: dict[str, object]) -> int
RunRecord.append_checkpoint(checkpoint: dict[str, object]) -> int
RunRecord.write_result(result: RunResult) -> None
RunRecord.read_result() -> RunResult | None
RunRecord.contract_sha256 -> str
RunRecord.run_dir -> Path
```

`execution_lifecycle.py` exposes one orchestration Interface:

```text
ExecutionLifecycle(record: RunRecord, cmdc: CmdcLocal)
ExecutionLifecycle.start() -> RunResult
ExecutionLifecycle.resume() -> RunResult
```

Callers cannot request individual state transitions. The state machine, progress classifier, evidence normalization, failure precedence, and Recovery prompt are private Implementation.

Canonical CLI forms are:

```text
python scripts/cmdc-implementer.py start --contract-file PATH
python scripts/cmdc-implementer.py resume --cwd REPOSITORY --run-id RUN_ID
```

The current flat invocation remains accepted and is normalized into a Run Contract before any launcher smoke or child process.

---

### Task 1: Add a cross-platform task brief and deterministic `Files` parser

**Files:**
- Create: `skills/sdd-cmdc-opencode/scripts/task-brief.py`
- Modify: `skills/sdd-cmdc-opencode/scripts/task-brief`
- Modify: `skills/sdd-cmdc-opencode/tests/test_task_brief.py`

**Interfaces:**

```text
extract_task(plan_text: str, task_number: int) -> tuple[str, str]
extract_declared_files(task_text: str) -> tuple[str, ...]
python scripts/task-brief.py PLAN_FILE TASK_NUMBER [OUTFILE] [--scope-json SCOPE_FILE]
```

`extract_task` returns the exact heading and task body. `extract_declared_files` accepts only repository-relative backtick paths under a task-local `Files`/`Arquivos` section with a recognized action label: `Create`, `Modify`, `Test`, `Delete`, `Criar`, `Modificar`, `Teste`, or `Excluir`.

- [ ] **Step 1: Add RED tests for Python extraction and strict scope derivation**

  Keep existing Bash tests and add Python-module/CLI coverage for:

  - `## Task 3`, `## Tarefa 3`, and `## 8. Tarefa 3`;
  - fenced code containing fake headings;
  - atomic preservation of an existing output when the task is missing;
  - `**Files:**` entries such as `- Modify: \`src/run.py\`` and `- Test: \`tests/test_run.py\``;
  - rejection of absolute paths, `..`, globs, bare prose, missing backticks, duplicate paths with conflicting spelling, and an absent `Files` section.

  Assert deterministic output:

  ```python
  assert extract_declared_files(task_text) == (
      "src/run.py",
      "tests/test_run.py",
  )
  ```

  Run `python -m pytest tests/test_task_brief.py -q`. Expected RED: `task-brief.py` is absent.

- [ ] **Step 2: Implement extraction without Bash dependency**

  Parse Markdown line-by-line while tracking fenced blocks. Match headings case-insensitively, require the requested integer, and stop at the next task heading of the same or higher level. Preserve task bytes except for normalized final newline.

  Write output through a same-directory temporary file, flush and `os.fsync`, then `os.replace`. Exit `2` for invalid input and `3` when the task is absent, matching the Bash contract.

- [ ] **Step 3: Implement strict file derivation and optional JSON output**

  Normalize `\` to `/`, collapse `.` segments, reject absolute/drive/UNC/parent paths and wildcard characters, preserve first-seen order, and deduplicate case-insensitively only on Windows. The scope JSON is:

  ```json
  {
    "source": "task-files-section",
    "task_heading": "Task 3",
    "allowed_paths": ["src/run.py", "tests/test_run.py"]
  }
  ```

  If deterministic paths cannot be produced, do not write `--scope-json` and exit with a stable error.

- [ ] **Step 4: Reduce the Bash helper to a compatibility wrapper**

  Keep `task-brief PLAN_FILE TASK_NUMBER [OUTFILE]`. Resolve `python`/`python3`, then execute the adjacent `task-brief.py` with the same arguments. SKILL documentation will select `task-brief.py` directly on Windows in Task 7.

- [ ] **Step 5: Run focused tests and commit**

  Run:

  ```powershell
  python -m pytest tests/test_task_brief.py -q
  python -m py_compile scripts/task-brief.py
  ```

  Stage Task 1 paths and commit:

  ```powershell
  git add skills/sdd-cmdc-opencode/scripts/task-brief.py skills/sdd-cmdc-opencode/scripts/task-brief skills/sdd-cmdc-opencode/tests/test_task_brief.py
  git commit -m "feat: extract task scope cross platform"
  ```

---

### Task 2: Persist the immutable Run Contract and append-only Run Record

**Files:**
- Create: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/run_record.py`
- Create: `skills/sdd-cmdc-opencode/tests/test_run_record.py`
- Modify: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/__init__.py`

**Interfaces:** Use the exact `RunStatus`, evidence values, `RunResult`, `RunContract`, and `RunRecord` Interfaces above.

- [ ] **Step 1: Write schema and immutability RED tests**

  Build the approved schema-version-1 contract with all fields from the design. Assert rejection of:

  - missing/extra fields and non-integer schema version;
  - backend other than `cmdc-local`;
  - `max_turns < 1`, negative timeouts, `max_resumes < 0`, or progress deadline above `max_turns`;
  - non-absolute repository/source-repository paths;
  - report/brief paths outside the target repository;
  - malformed 40-character commit IDs or 64-character SHA-256 values;
  - source file hash, task heading, or brief hash mismatches;
  - a `RunLineage` whose kind is not `fix-round`, whose parent Review Result hash is invalid, or whose finding IDs/hash do not match that parent.

  Assert `RunRecord.create` writes `contract.json` once and a second create cannot replace it.

  Run `python -m pytest tests/test_run_record.py -q -k "contract or immutable or provenance"`. Expected RED: Module absent.

- [ ] **Step 2: Implement frozen contract values and provenance verification**

  Resolve the external plan's Git root, branch, and exact source commit; verify the original path belongs to that source repository and the current file bytes match `plan.sha256`. For an initial task, re-extract `task.heading` and `task.brief_sha256`. For a Fix Round lineage, re-extract the original heading and `parent_brief_sha256`, verify the parent Review Result/finding hashes, then verify the derived Fix Round brief against the current `task.brief_sha256`. Record the original location; never copy the plan implicitly.

  For plans inside the implementation repository, apply the same fields rather than inventing a weaker internal-plan format.

- [ ] **Step 3: Write append-only stream and atomic Result RED tests**

  Assert every event/checkpoint line contains monotonically increasing `sequence`, `run_id`, `contract_sha256`, and UTC timestamp. Simulate an interrupted Result replacement and prove the previous `result.json` remains valid. Assert prior outcomes remain in events/checkpoints after a later Result replaces current authority.

  Assert `RunRecord.locate(repo, run_id)` scans only `.superpowers/sdd/*/runs/<run-id>`, rejects zero matches, rejects multiple matches, and never searches outside the repository.

- [ ] **Step 4: Implement durable Run artifacts**

  Use this exact layout:

  ```text
  {plan-workspace}/runs/{run-id}/
    contract.json
    events.jsonl
    checkpoints.jsonl
    result.json
    scope-contract.json
  ```

  Create `contract.json` with exclusive-create semantics and flush it before execution. Append each JSONL record with one write under an in-process lock, flush, and `fsync`. Write Result and scope contract through same-directory temporary files plus `os.replace`; never truncate current authority first.

  Reject an event/checkpoint whose supplied `run_id` or contract hash differs from the owning record.

- [ ] **Step 5: Add workspace fingerprints**

  A Checkpoint fingerprint records exact HEAD, branch, raw `git status --porcelain=v2 -z` SHA-256, and per-changed-path evidence. For tracked paths, hash `git diff --binary HEAD -- <path>`; for untracked regular files, hash bytes; record symlink target or missing state explicitly. This distinguishes an unchanged pre-existing dirty path from a new mutation to that path.

  Add tests for staged, unstaged, untracked, deleted, renamed, Unicode, `&`, and pre-existing dirty files.

- [ ] **Step 6: Run focused tests and commit**

  Run `python -m pytest tests/test_run_record.py -q` and `python -m py_compile scripts/sdd_cmdc_opencode/run_record.py`.

  Stage Task 2 paths and commit:

  ```powershell
  git add skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/run_record.py skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/__init__.py skills/sdd-cmdc-opencode/tests/test_run_record.py
  git commit -m "feat: persist auditable cmdc run records"
  ```

---

### Task 3: Enforce scope before direct tools and after shell effects

**Files:**
- Create: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/_scope_guard.py`
- Create: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/_scope_mod.ts`
- Create: `skills/sdd-cmdc-opencode/tests/test_scope_guard.py`
- Modify: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/cmdc_local.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_cmdc_local.py`

**Interfaces:** `_scope_guard.py` is private but has a stable JSON-stdin CLI used by the packaged Mod:

```text
python _scope_guard.py check-tool --contract SCOPE_CONTRACT
python _scope_guard.py audit-workspace --contract SCOPE_CONTRACT
```

Input is one JSON object on stdin. Output is one JSON object:

```json
{
  "decision": "allow",
  "code": "",
  "paths": [],
  "message": "path is inside the Run scope"
}
```

Violation decisions are `block` for direct tools and `terminate` for workspace audit, both with `code: "SCOPE_VIOLATION"`.

- [ ] **Step 1: Write canonical path-policy RED tests**

  Cover exact allowed files, explicit directory entries ending `/`, denied-over-allowed, absolute paths, drive-relative paths, UNC paths, mixed separators, `.`/`..`, Windows case folding, symlinks inside/outside root, missing future files, and Unicode normalization. Assert the returned violation paths are canonical repository-relative POSIX paths and sorted.

  Cover scope construction precedence:

  ```text
  explicit allowed_paths -> use and record explicit
  no explicit paths + deterministic Files paths -> use and record derived
  neither -> SCOPE_CONTRACT_MISSING before launcher smoke
  ```

  Run `python -m pytest tests/test_scope_guard.py -q -k "path or contract"`. Expected RED: private helper absent.

- [ ] **Step 2: Implement canonical scope policy and baseline-aware audit**

  Use Git's repository-relative paths as the canonical namespace, then validate resolved filesystem targets remain under the repository after symlink resolution. An exact file entry allows only that path; a normalized entry ending `/` allows its subtree. `denied_paths` wins at the same or broader prefix.

  Compare the current fingerprint to the baseline per path. An unchanged pre-existing out-of-scope path is preserved and accepted. Any content/index/status change to it is a new violation. Return all violations; never reset them.

- [ ] **Step 3: Write the immutable Mod with argument-array helper calls**

  Use the installed Command Code Mod contract and no interactive confirmation:

  ```typescript
  import {spawnSync} from 'node:child_process';
  import type {ModApi} from '@commandcode/harness';

  type Decision = {
    decision: 'allow' | 'block' | 'terminate';
    code: string;
    paths: string[];
    message: string;
  };

  const python = process.env.SDD_CMDC_SCOPE_PYTHON ?? '';
  const helper = process.env.SDD_CMDC_SCOPE_HELPER ?? '';
  const contract = process.env.SDD_CMDC_SCOPE_CONTRACT ?? '';

  function decide(operation: string, payload: object): Decision {
    const result = spawnSync(
      python,
      [helper, operation, '--contract', contract],
      {input: JSON.stringify(payload), encoding: 'utf8', shell: false},
    );
    if (result.status !== 0) {
      return {
        decision: 'terminate',
        code: 'SCOPE_GUARD_FAILED',
        paths: [],
        message: result.stderr || 'scope helper failed closed',
      };
    }
    return JSON.parse(result.stdout) as Decision;
  }

  export default function (cmd: ModApi) {
    cmd.hooks({
      beforeToolCall: async ({toolName, input}) => {
        if (toolName !== 'write_file' && toolName !== 'edit_file') return undefined;
        const result = decide('check-tool', {toolName, input});
        if (result.decision === 'allow') return undefined;
        return {block: true, terminate: true, additionalContext: result.message};
      },
      afterToolCall: async ({toolName, input, result, isError}) => {
        if (toolName !== 'shell_command') return undefined;
        const audit = decide('audit-workspace', {toolName, input, result, isError});
        if (audit.decision === 'allow') return undefined;
        return {terminate: true, isError: true, additionalContext: audit.message};
      },
    });
  }
  ```

  Validate the three required environment paths before Command Code starts. The Mod source is packaged and immutable; only `scope-contract.json` varies per Run.

- [ ] **Step 4: Add direct and indirect integration RED tests**

  Use a fake Command Code that executes the Mod contract or a small Node harness fixture. Prove:

  - out-of-scope `write_file` is blocked before file creation;
  - allowed write proceeds;
  - shell-created out-of-scope file remains on disk for audit, the run terminates, and the path is reported;
  - modification of a pre-existing dirty out-of-scope file is detected;
  - unchanged pre-existing dirty paths do not block;
  - a helper crash fails closed as `SCOPE_GUARD_FAILED`;
  - final Python audit catches a change even if no after-hook event arrives.

  Run `python -m pytest tests/test_scope_guard.py tests/test_cmdc_local.py -q -k "scope or mod"`. Expected RED until the Mod is wired.

- [ ] **Step 5: Wire Mod capability into `CmdcLocal`**

  Add `--mod <absolute _scope_mod.ts>` to both start and resume, pass only the three `SDD_CMDC_SCOPE_*` variables for the current Run, and require the Delivery 1 Mod hook smoke. A launcher without working Mod hooks fails preflight; there is no prompt-only degraded mode.

- [ ] **Step 6: Run focused tests and commit**

  Run:

  ```powershell
  python -m pytest tests/test_scope_guard.py tests/test_cmdc_local.py -q
  python -m py_compile scripts/sdd_cmdc_opencode/_scope_guard.py
  ```

  Stage Task 3 paths and commit:

  ```powershell
  git add skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/_scope_guard.py skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/_scope_mod.ts skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/cmdc_local.py skills/sdd-cmdc-opencode/tests/test_scope_guard.py skills/sdd-cmdc-opencode/tests/test_cmdc_local.py
  git commit -m "feat: enforce cmdc run scope mechanically"
  ```

---

### Task 4: Normalize evidence and detect implementation progress

**Files:**
- Create: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/execution_lifecycle.py`
- Create: `skills/sdd-cmdc-opencode/tests/test_execution_lifecycle.py`
- Modify: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/__init__.py`

**Interfaces:** Add the exact `ExecutionLifecycle(record, cmdc)`, `.start()`, and `.resume()` Interface. This task implements event/evidence/progress behavior first; Task 5 completes state orchestration.

- [ ] **Step 1: Write normalized test-evidence RED tests**

  Feed `CmdcEvent` sequences and assert a passing test requires a shell/tool result with exit code `0`, a recognized test command, a zero-failure summary, and raw stdout/stderr retained. Cover:

  ```text
  pytest tests/unit -q -> 246 passed in 23.67s
  python -m pytest tests/test_a.py -q; Write-Output done -> 12 passed
  npm test -> 31 passed, 0 failed
  dotnet test -> Failed: 0, Passed: 18
  pytest -> 245 passed, 1 failed
  assistant prose -> "all tests pass"
  ```

  The first four become normalized evidence; the failure and prose do not. Preserve the original command including `;`; never parse command separators as output.

  Run `python -m pytest tests/test_execution_lifecycle.py -q -k evidence`. Expected RED: Module absent.

- [ ] **Step 2: Implement conservative event and evidence normalization**

  Recognize test runners by executable/argument structure (`pytest`, `python -m pytest`, `npm test`, `npm run test`, `go test`, `cargo test`, `dotnet test`, Maven/Gradle test). Accept only zero-exit results without nonzero failure/error counts. Record the normalized summary, pass/fail counts when present, event sequence, and exact command.

  Unknown event shapes are appended to `events.jsonl` but cannot satisfy test evidence or progress.

- [ ] **Step 3: Write progress-deadline RED tests**

  Default deadline is:

  ```python
  min(10, max(1, (max_turns + 4) // 5))
  ```

  Cover exploration-only reads/status commands through the deadline, a permitted write, an allowed workspace fingerprint change, a new task commit, a recognized test/build/lint event, and an unrelated `git status`/directory listing. Assert only the approved signals set first progress and the exploration-only sequence becomes `NO_IMPLEMENTATION_PROGRESS`.

- [ ] **Step 4: Implement progress classification and checkpoint evidence**

  Treat these as progress: permitted write/edit event, allowed workspace delta, HEAD advance from a task commit, passing/failing recognized test execution, and a conservative build/lint command (`ruff`, `mypy`, `tsc`, `go build`, `cargo check`, `dotnet build`). Reads, searches, plan narration, `git status`, `git diff`, and arbitrary shell output do not count.

  Persist the first progress signal and turn in a Checkpoint. On deadline violation, terminate through the process supervisor, audit scope, preserve `NO_IMPLEMENTATION_PROGRESS` as primary, and record cleanup failures secondarily.

- [ ] **Step 5: Run focused tests and commit**

  Run `python -m pytest tests/test_execution_lifecycle.py -q -k "evidence or progress"`.

  Stage Task 4 paths and commit:

  ```powershell
  git add skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/execution_lifecycle.py skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/__init__.py skills/sdd-cmdc-opencode/tests/test_execution_lifecycle.py
  git commit -m "feat: normalize cmdc progress and test evidence"
  ```

---

### Task 5: Implement the private Run state machine and canonical `start`

**Files:**
- Modify: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/execution_lifecycle.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_execution_lifecycle.py`
- Modify: `skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_preflight_contract.py`

**Interfaces:** Implement `ExecutionLifecycle.start() -> RunResult` and `cmdc-implementer.py start --contract-file PATH`. Legacy flat arguments create the same contract and then call this path.

- [ ] **Step 1: Write state-transition and blocker-precedence RED tests**

  Exercise the approved transitions:

  ```text
  PREFLIGHT -> SPAWN -> RUNNING -> CLEANUP_VERIFICATION -> COMPLETE
  RUNNING -> NO_IMPLEMENTATION_PROGRESS -> TERMINATING -> CLEANUP_VERIFICATION -> BLOCKED
  RUNNING -> STALLED | WALL_TIMEOUT -> TERMINATING -> CLEANUP_VERIFICATION -> INCOMPLETE
  RUNNING -> protocol/scope/runtime failure -> TERMINATING -> CLEANUP_VERIFICATION -> BLOCKED
  ```

  Assert an invalid transition becomes a fail-closed lifecycle diagnostic. Assert first cause remains primary and later termination/cleanup/persistence causes retain order as secondary. Assert cleanup is primary only when no earlier cause exists.

  Run `python -m pytest tests/test_execution_lifecycle.py -q -k "transition or blocker"`. Expected RED until orchestration exists.

- [ ] **Step 2: Implement ordered preflight**

  Perform these gates before process creation:

  1. load and hash Run Contract;
  2. verify plan/brief provenance and report/checkpoint containment;
  3. verify repository root, branch, base HEAD, protected/deployed authorization, and baseline fingerprint;
  4. construct/validate scope or return `SCOPE_CONTRACT_MISSING`;
  5. write immutable contract and scope contract;
  6. resolve/smoke `cmdc-local`, including Mod hook capability;
  7. render prompt from structured contract and task brief.

  Resolution, smoke, spawn, execution, scope, termination, and result errors use only the approved taxonomy. Do not wrap the sequence in a broad launcher exception.

- [ ] **Step 3: Implement execution, checkpoints, and final transaction validation**

  Translate every `CmdcEvent` to append-only events, write Checkpoints on Session ID capture, first progress, workspace/HEAD changes, timeout/limit, and pre-final validation. A valid success must prove:

  - terminal Command Code subtype is success;
  - process cleanup and drain are verified;
  - scope final audit is valid;
  - final HEAD satisfies commit policy and is based on `base_head`;
  - Implementer Report exists at the contract path and hashes correctly;
  - normalized test evidence satisfies policy;
  - no new unknown workspace change exists.

  Fail with `REPORT_INVALID`, `TEST_EVIDENCE_INVALID`, or `COMMIT_REQUIREMENT_FAILED` at the Result phase. Write Result atomically for every completed invocation, including `BLOCKED` and `INCOMPLETE`.

- [ ] **Step 4: Add canonical start CLI while preserving legacy output**

  Add subcommand parsing without breaking the current flat form. `start --contract-file` prints the existing short key/value summary rendered from `RunResult`, followed by `RUN_ID`, `RESULT_FILE`, `EVENTS_FILE`, and `CHECKPOINTS_FILE`. Exit `0` only for `COMPLETE`; retain stable nonzero mappings for blocked/incomplete compatibility.

  Legacy report-marker parsing remains only in the Adapter. Add paths with spaces, quotes, backticks, Windows separators, and a marker whose path begins on the next line. New Runs always use `task.report_path` directly.

- [ ] **Step 5: Run start and compatibility tests**

  Run:

  ```powershell
  python -m pytest tests/test_execution_lifecycle.py tests/test_preflight_contract.py tests/test_cmdc_implementer.py -q -k "start or preflight or result or report or compatibility"
  ```

  Expected GREEN. Inspect `result.json`, event sequence, and unchanged legacy text in fixture assertions.

- [ ] **Step 6: Commit canonical start**

  Stage Task 5 paths and commit:

  ```powershell
  git add skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/execution_lifecycle.py skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py skills/sdd-cmdc-opencode/tests/test_execution_lifecycle.py skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py skills/sdd-cmdc-opencode/tests/test_preflight_contract.py
  git commit -m "feat: execute cmdc through resumable run contracts"
  ```

---

### Task 6: Resume the same Run and Command Code Session safely

**Files:**
- Modify: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/execution_lifecycle.py`
- Modify: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/run_record.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_execution_lifecycle.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_run_record.py`
- Modify: `skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py`

**Interfaces:** Implement `ExecutionLifecycle.resume() -> RunResult` and `cmdc-implementer.py resume --cwd REPOSITORY --run-id RUN_ID`.

- [ ] **Step 1: Write Recovery invariant RED tests**

  Recovery requires exact equality for:

  - `run_id` and contract SHA-256;
  - contract `workspace.base_head`;
  - Checkpoint ownership/sequence and captured Session ID;
  - expected current HEAD/branch;
  - known workspace fingerprint, including pre-existing changes;
  - no path outside the known baseline plus allowed Run changes.

  Change each invariant independently and assert `RESUME_INVARIANT_FAILED` before launcher/process creation. Assert zero or multiple `RunRecord.locate` matches fail closed.

  Run `python -m pytest tests/test_execution_lifecycle.py tests/test_run_record.py -q -k "resume or recovery or invariant"`. Expected RED.

- [ ] **Step 2: Implement exact same-session Recovery**

  Load the persisted record, never rebuild the contract from CLI text, validate the newest owned Checkpoint, and call:

  ```text
  cmdc -p --resume SESSION_ID FINALIZATION_PROMPT
  ```

  through `CmdcLocal.resume`. Include the same `--mod` and scope environment. The Recovery prompt is rendered from the same Run Contract and states only the remaining success obligations; it cannot change scope/model/policy.

  Append `RecoveryEvidence` with `same_session: true`. A different returned Session ID is `CMD_CODE_PROTOCOL_ERROR` and is not accepted as Recovery.

- [ ] **Step 3: Implement trigger-specific policy**

  - On `WORKER_TURN_LIMIT`, automatically Recovery while attempts are below `max_resumes` and cleanup was verified.
  - When attempts are exhausted, Result is `BLOCKED`; primary remains `WORKER_TURN_LIMIT`, secondary includes `RECOVERY_EXHAUSTED`.
  - On `STALLED` or `WALL_TIMEOUT`, write `INCOMPLETE` and require explicit CLI resume.
  - Launcher/smoke/spawn, protocol, scope, termination, cleanup, and unverifiable cleanup failures are non-resumable.
  - A controlled user interruption may be `INCOMPLETE` only with verified cleanup and a valid Checkpoint; an unclassified interruption is blocked.

- [ ] **Step 4: Add fake CLI sequence assertions**

  Make `fake_cmdc.py` log received argument arrays. First call emits Session ID and `max_turns`; second call must contain `--resume session-123`, the same Mod path, and no new-session flags. Assert one Run directory, one immutable contract, ordered Recovery events, current Result replacement, and preserved prior outcome records.

  Assert explicit resume after stall uses the same Session. Assert `--continue` never appears anywhere.

- [ ] **Step 5: Run Recovery tests and commit**

  Run:

  ```powershell
  python -m pytest tests/test_execution_lifecycle.py tests/test_run_record.py tests/test_cmdc_implementer.py tests/test_cmdc_local.py -q -k "resume or recovery or turn_limit or stalled or wall_timeout"
  ```

  Stage Task 6 paths and commit:

  ```powershell
  git add skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/execution_lifecycle.py skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/run_record.py skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py skills/sdd-cmdc-opencode/tests/test_execution_lifecycle.py skills/sdd-cmdc-opencode/tests/test_run_record.py skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py
  git commit -m "feat: recover the same command code session"
  ```

---

### Task 7: Prove the complete Run transaction and update the skill contract

**Files:**
- Create: `skills/sdd-cmdc-opencode/tests/test_run_integration.py`
- Modify: `skills/sdd-cmdc-opencode/SKILL.md`
- Modify: `skills/sdd-cmdc-opencode/tests/test_skill_contract.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_package_contract.py`
- Modify: `skills/sdd-cmdc-opencode/CONTEXT.md` only if implementation exposes a vocabulary mismatch

**Interfaces:** Documentation makes `start --contract-file` and `resume --run-id` canonical, keeps legacy compatibility explicit, and distinguishes Run, Command Code Session, Recovery, Result, Implementer Report, and Fix Round.

- [ ] **Step 1: Add the deterministic end-to-end test**

  In a temporary Git repository with a Unicode and `&` path, execute this real lifecycle with fake Command Code:

  ```text
  start
    -> immutable contract/provenance/scope
    -> fake launcher smoke + Mod probe
    -> Session ID capture
    -> allowed partial implementation
    -> Checkpoint
    -> worker turn limit
    -> automatic same-session Recovery
    -> passing test event (246 passed)
    -> commit + Implementer Report
    -> final scope/cleanup validation
    -> COMPLETE Result
  ```

  Assert exact artifacts, hashes, event/checkpoint ordering, one Session ID, one Run ID, preserved baseline changes, allowed diff only, normalized test evidence, and human summary rendered from Result.

- [ ] **Step 2: Add fail-closed end-to-end variants**

  Cover no progress, direct denied write, indirect shell violation, unknown workspace change before Recovery, report without commit, commit without report, agent prose without test event, malformed NDJSON, failed cleanup, and exhausted Recovery. Assert violating files remain present and no review artifact is created.

  Run `python -m pytest tests/test_run_integration.py -q`. Expected GREEN before documentation changes.

- [ ] **Step 3: Add RED skill/package contract assertions**

  Assert `SKILL.md` documents:

  - versioned Run Contract/Record/Result authority;
  - explicit/derived scope and `SCOPE_CONTRACT_MISSING`;
  - pre-tool Mod and post-shell/final audits;
  - `NO_IMPLEMENTATION_PROGRESS` deadline;
  - same-session Recovery rules and exact resume CLI;
  - external plan/brief provenance;
  - normalized test events rather than prose;
  - Windows `task-brief.py` entry;
  - no generic allow-dirty Recovery bypass.

  Assert new Python/TypeScript/package files are tracked and LF-only.

- [ ] **Step 4: Update documentation and examples**

  Replace prompt-as-authority instructions with contract construction and exact CLI examples. Keep `--yolo` consent, protected/deployed authorization, worktree isolation, fixed model, Command Code-only implementation, OCR-only review, and separate installation/publication gates.

  Make the Legacy section explicit: old flags normalize into schema v1 and use the same lifecycle; report-marker parsing exists only for old calls.

- [ ] **Step 5: Run Delivery 2 verification**

  From `skills/sdd-cmdc-opencode`:

  ```powershell
  python -m pytest tests/test_task_brief.py tests/test_run_record.py tests/test_scope_guard.py tests/test_execution_lifecycle.py tests/test_run_integration.py -q
  python -m pytest -q
  python -m py_compile scripts/task-brief.py scripts/cmdc-implementer.py scripts/sdd_cmdc_opencode/run_record.py scripts/sdd_cmdc_opencode/execution_lifecycle.py scripts/sdd_cmdc_opencode/_scope_guard.py
  ```

  From `skills/sdd-cmdc` separately:

  ```powershell
  python -m pytest -q
  ```

  From the worktree root:

  ```powershell
  git diff --check
  git status --short
  git diff --name-only origin/master...HEAD
  python skills/sdd-cmdc-opencode/scripts/verify-install-parity.py skills/sdd-cmdc-opencode C:\Users\victor.bernardi\.agents\skills\sdd-cmdc-opencode C:\Users\victor.bernardi\.codex\skills\sdd-cmdc-opencode
  ```

  Record scoped suite, sibling suite, optional real smoke, and parity as separate evidence states.

- [ ] **Step 6: Commit Delivery 2 documentation and integration tests**

  Stage only Task 7 paths and commit:

  ```powershell
  git add skills/sdd-cmdc-opencode/tests/test_run_integration.py skills/sdd-cmdc-opencode/SKILL.md skills/sdd-cmdc-opencode/tests/test_skill_contract.py skills/sdd-cmdc-opencode/tests/test_package_contract.py skills/sdd-cmdc-opencode/CONTEXT.md
  git commit -m "docs: define auditable resumable cmdc runs"
  ```

  If `CONTEXT.md` has no actual diff, omit it from the final staged set.

## Delivery 2 Acceptance Gate

Delivery 2 is complete only when all statements are evidenced:

- `contract.json` is immutable and validates plan, brief, workspace, scope, execution, success, and review data before spawn;
- external plans retain original repository/branch/commit/path and SHA-256 provenance without silent copying;
- events/checkpoints are append-only and `result.json` is atomically current;
- direct and indirect scope violations are mechanically blocked/detected, preserved, and reported;
- unchanged pre-existing changes are distinguishable and untouched;
- test approval comes only from normalized tool events, including the `246 passed` and Windows `;` regressions;
- exploration-only work reaches `NO_IMPLEMENTATION_PROGRESS` at the configured early deadline;
- `WORKER_TURN_LIMIT` automatically resumes the exact Session within budget;
- stall/wall timeout remain explicit `INCOMPLETE` until operator Recovery;
- every Recovery validates Run ID, base, contract, Checkpoint, fingerprint, scope, and Session ID;
- a valid Result cannot be `COMPLETE` without report/commit/test/scope/cleanup evidence required by policy;
- the deterministic end-to-end Run and regression suites pass;
- scoped, sibling, package, compile, diff, and read-only parity gates are reported separately.
