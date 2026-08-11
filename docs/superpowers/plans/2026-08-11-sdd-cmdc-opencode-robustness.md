# sdd-cmdc-opencode Robustness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the canonical `sdd-cmdc-opencode` skill fail closed with actionable diagnostics for Windows launcher failures, invalid artifacts, Portuguese task headings, and installation drift, while preserving the primary execution cause.

**Architecture:** Keep the existing single-file adapter and shell wrapper; introduce small local helpers at the existing boundaries instead of a speculative architecture extraction. Both primary and recovery commands will pass through the same platform-normalization helper, and timeout diagnostics will retain immutable primary evidence while attaching recovery evidence. A deterministic parity checker will be an explicit audit tool, not an automatic overwrite of installed skill copies.

**Tech Stack:** Python 3, pytest, Bash/awk, Git worktrees, SHA-256 file manifests.

## Global Constraints

- The fixed CMDc model remains `deepseek/deepseek-v4-flash`; do not add model override or `/fast` behavior.
- CMDc-only, OCR-only, and fail-closed execution contracts remain unchanged.
- Missing, malformed, or out-of-bound artifacts produce structured `BLOCKED` output before any child process starts.
- A primary timeout/worker failure remains the top-level cause; recovery failures are attached evidence and never replace it.
- Existing tests and unrelated dirty files are preserved; no `.agents` or `.codex` installation is overwritten in this branch.
- Completion requires focused tests, the complete canonical skill suite, and a read-only parity audit against the installed copies.

---

### Task 1: Normalize Windows launch commands for primary and recovery

**Files:**
- Modify: `skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py` near `_platform_command`, `run_implementer`, and timeout recovery.
- Test: `skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py`.

**Interfaces:**
- ` _platform_command(command: list[str]) -> list[str]` remains the single logical-command-to-launch-command adapter.
- Recovery calls `_platform_command` on the command returned by `build_command` before `_run_cmdc_process`.
- Diagnostics expose `PRIMARY_BLOCKER_CODE`, `PRIMARY_PHASE`, `PRIMARY_COMMAND`, and `RECOVERY_ERROR` when recovery was attempted.

- [x] **Step 1: Write failing tests**

  Add tests that monkeypatch `MODULE.os.name` to `nt`, set `COMSPEC`, and assert `.cmd` becomes `[comspec, "/d", "/c", ...]`; assert `.ps1` uses the selected PowerShell launcher and `-File`. Add a timeout test whose first fake process raises `TimeoutExpired` after creating a partial file and whose recovery fake raises `FileNotFoundError`; assert the final output still contains `BLOCKER_CODE: TIMEOUT`, the original timeout evidence, and a separate `RECOVERY_ERROR` instead of `BLOCKER_CODE: CMD_NOT_FOUND`.

- [x] **Step 2: Run the focused tests and verify RED**

  Run `python -m pytest skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py -q -k "platform_command or recovery_error or primary"`. The pre-patch expectation is failure because recovery currently passes the logical `.cmd`/`.ps1` command directly and recovery currently mutates the primary diagnostic.

- [x] **Step 3: Implement the minimal fix**

  Keep `_platform_command` as the only launcher policy. Normalize the recovery command immediately before `_run_cmdc_process`. Capture the initial timeout diagnostic in `primary_diagnostic` and never replace it; add a recovery outcome/error field and phase/command evidence to the incomplete renderer. Classify return-code 8/`max turns` as `WORKER_TURN_LIMIT`, while watchdog `WALL_TIMEOUT` and `STALLED` retain their distinct blocker codes. Preserve the old `TIMEOUT` alias only where existing callers assert the stable legacy code, and include the more specific phase in the message/action.

- [x] **Step 4: Run the focused tests and verify GREEN**

  Run the same focused command, then run the existing timeout/recovery selection (`python -m pytest skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py -q -k "timeout or stall or recovery"`). All selected tests must pass.

- [x] **Step 5: Commit the task**

  Run `git add skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py` and commit with `git commit -m "fix: preserve cmdc timeout causes through recovery"`.

### Task 2: Validate prompt, report, and checkpoint artifacts before spawning CMDc

**Files:**
- Modify: `skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py` in `validate_execution_boundary` and `run_implementer`.
- Test: `skills/sdd-cmdc-opencode/tests/test_preflight_contract.py` and `skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py`.

**Interfaces:**
- Add `validate_artifact_path(path, git_root, code_prefix, ...) -> tuple[Path | None, dict[str, object] | None]` or an equivalent private helper returning either a resolved regular in-repository path or the existing `_preflight_blocked` payload.
- `run_implementer` reads `prompt_file` only after the structured preflight has accepted it.
- A prompt decode failure is rendered as `BLOCKED` with a stable `PROMPT_UNREADABLE` code; an outside/directory/missing report or checkpoint path has a stable artifact-specific code.

- [x] **Step 1: Write failing tests**

  Add public-path tests for a missing prompt, a prompt directory, an outside-repository prompt, invalid UTF-8 prompt, a report marker pointing outside the repository, and a checkpoint path outside the repository. Monkeypatch the process launcher to fail if called. Assert exit `1`, structured `STATUS: BLOCKED`, an artifact code/message, and no raw `FileNotFoundError` traceback.

- [x] **Step 2: Run the focused tests and verify RED**

  Run `python -m pytest skills/sdd-cmdc-opencode/tests/test_preflight_contract.py skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py -q -k "prompt or artifact or checkpoint"`. The pre-patch missing prompt path raises before preflight and the other paths are not validated consistently.

- [x] **Step 3: Implement the minimal fix**

  Resolve and validate `cwd`/Git root first, then validate `plan_file`, `prompt_file`, optional `checkpoint_file`, and the extracted report path as regular files or safe output paths inside that root. Catch `UnicodeDecodeError`, `PermissionError`, and `OSError` while reading the prompt and convert them to `_preflight_blocked` data. Do not create or truncate checkpoint/report files during validation. Reuse the same descendant check for all artifact paths and preserve the initial Git snapshot on later boundary blocks.

- [x] **Step 4: Run the focused tests and verify GREEN**

  Run the focused command again, then run `python -m pytest skills/sdd-cmdc-opencode/tests/test_preflight_contract.py -q`.

- [x] **Step 5: Commit the task**

  Run `git add skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py skills/sdd-cmdc-opencode/tests/test_preflight_contract.py skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py` and commit with `git commit -m "fix: preflight cmdc task artifacts"`.

### Task 3: Make `task-brief` bilingual and transactional

**Files:**
- Modify: `skills/sdd-cmdc-opencode/scripts/task-brief`.
- Test: create `skills/sdd-cmdc-opencode/tests/test_task_brief.py`.

**Interfaces:**
- The command-line interface remains `task-brief PLAN_FILE TASK_NUMBER [OUTFILE]`.
- Heading matching accepts `Task N` and `Tarefa N`, including numeric prefixes such as `## 8. Tarefa 7`.
- Extraction writes a temporary file beside the destination, checks it is non-empty, and atomically replaces the destination only on success.

- [x] **Step 1: Write failing tests**

  Add subprocess tests that locate `bash` and skip with an explicit reason only when Bash is unavailable. Cover Portuguese extraction, English extraction regression, and a missing task where an existing destination must retain its original bytes. Use a plan containing fenced code with fake headings to ensure fence handling remains unchanged.

- [x] **Step 2: Run the focused tests and verify RED**

  Run `python -m pytest skills/sdd-cmdc-opencode/tests/test_task_brief.py -q`; Portuguese extraction fails and the missing-task case currently truncates the destination.

- [x] **Step 3: Implement the minimal fix**

  Update the awk heading expression to accept `Task|Tarefa` after optional numeric-list prefixes, and derive the task-number comparison from the captured heading. Create a same-directory temporary path with `mktemp`, redirect extraction there, verify non-empty, then `mv` it over the destination. Trap cleanup on all failure paths and report the accepted heading forms in the error.

- [x] **Step 4: Run the focused tests and verify GREEN**

  Re-run `python -m pytest skills/sdd-cmdc-opencode/tests/test_task_brief.py -q`, then invoke the script manually once with both heading forms.

- [x] **Step 5: Commit the task**

  Run `git add skills/sdd-cmdc-opencode/scripts/task-brief skills/sdd-cmdc-opencode/tests/test_task_brief.py` and commit with `git commit -m "fix: extract bilingual task briefs atomically"`.

### Task 4: Add an explicit source-to-install parity audit

**Files:**
- Create: `skills/sdd-cmdc-opencode/scripts/verify-install-parity.py`.
- Modify: `skills/sdd-cmdc-opencode/tests/test_package_contract.py`.
- Test: `skills/sdd-cmdc-opencode/tests/test_package_contract.py`.

**Interfaces:**
- CLI: `python scripts/verify-install-parity.py SOURCE TARGET...` exits `0` only when every target has the same regular-file relative paths and SHA-256 bytes as `SOURCE`; it ignores only cache directories explicitly named in the tool contract (`__pycache__`, `.pytest_cache`, `.mypy_cache`).
- Output lists missing, extra, and changed paths without mutating either tree.

- [x] **Step 1: Write failing tests**

  Add unit tests that build temporary source/target trees and assert success for identical files, failure for changed bytes, failure for an extra `test_model_override.py`, and failure for a missing adapter. Assert the command never changes target contents.

- [x] **Step 2: Run the focused tests and verify RED**

  Run `python -m pytest skills/sdd-cmdc-opencode/tests/test_package_contract.py -q -k parity`; the tool does not yet exist.

- [x] **Step 3: Implement the minimal fix**

  Implement deterministic relative-file collection, cache filtering, SHA-256 comparison, stable sorted diagnostics, argument validation, and a nonzero exit code for any drift. Keep target paths caller-supplied; do not hard-code or automatically write `.agents`/`.codex`.

- [x] **Step 4: Run the focused tests and verify GREEN**

  Run the parity selection and execute a read-only audit against the current canonical source and both installed copies. Record drift in the handoff; do not delete the conflicting installed test or synchronize it in this branch.

- [x] **Step 5: Commit the task**

  Run `git add skills/sdd-cmdc-opencode/scripts/verify-install-parity.py skills/sdd-cmdc-opencode/tests/test_package_contract.py` and commit with `git commit -m "test: add skill installation parity audit"`.

### Task 5: Update the skill contract and close only completed issues

**Files:**
- Modify: `skills/sdd-cmdc-opencode/SKILL.md` and any source contract tests that assert its wording.
- Test: `skills/sdd-cmdc-opencode/tests/test_skill_contract.py` and the complete package suite.

**Interfaces:**
- Documentation explicitly names bilingual `Task/Tarefa` extraction, structured artifact preflight, primary/recovery diagnostic preservation, and the parity audit command.
- No documentation introduces `/fast`, model override, Luna fallback, or non-CMDc execution.

- [x] **Step 1: Write failing contract assertions**

  Add assertions for the new documented command/diagnostic terms while retaining fixed-model and CMDc-only assertions.

- [x] **Step 2: Run the focused contract tests and verify RED**

  Run `python -m pytest skills/sdd-cmdc-opencode/tests/test_skill_contract.py -q -k "artifact or recovery or task brief or parity"`.

- [x] **Step 3: Update the skill documentation**

  Add concise operational guidance and examples matching the implemented CLI and stable diagnostic fields. Keep the execution boundary and fixed model wording authoritative.

- [x] **Step 4: Run all verification**

  Run `python -m pytest skills/sdd-cmdc-opencode/tests -q`, inspect `git diff --check`, inspect the exact changed-file list, and run `python skills/sdd-cmdc-opencode/scripts/verify-install-parity.py skills/sdd-cmdc-opencode C:\\Users\\victor.bernardi\\.agents\\skills\\sdd-cmdc-opencode C:\\Users\\victor.bernardi\\.codex\\skills\\sdd-cmdc-opencode` from the isolated worktree. Treat any drift as a publication blocker, not as permission to overwrite installations.

- [x] **Step 5: Reconcile GitHub issue state**

  Re-fetch #129, #131, and #164. Keep #129 closed because its acceptance was already verified. Close #131 only if its timeout, prompt-preflight, and task-brief acceptance criteria are all covered by the merged/tested source. Close #164 only if Windows primary/recovery launcher behavior and cause-preserving diagnostics are covered by the merged/tested source. Otherwise leave the issue open with an evidence comment describing the remaining external/publication gate.

- [x] **Step 6: Commit the final documentation and verification changes**

  Run `git add skills/sdd-cmdc-opencode/SKILL.md skills/sdd-cmdc-opencode/tests/test_skill_contract.py` and commit with `git commit -m "docs: document cmdc recovery and artifact contracts"`.
