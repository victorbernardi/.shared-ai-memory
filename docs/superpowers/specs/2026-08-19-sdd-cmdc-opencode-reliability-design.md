# SDD Command Code reliability architecture

**Date:** 2026-08-19

**Status:** Approved for implementation planning

**Scope:** `skills/sdd-cmdc-opencode`

## Context

`sdd-cmdc-opencode` keeps Codex as the SDD Orchestrator and delegates implementation to local Command Code. Its current executor concentrates preflight, launcher resolution, process supervision, timeout and stall handling, recovery, report parsing, Git validation, and result rendering in `scripts/cmdc-implementer.py`. `scripts/review-session.py` independently implements part of the same process-tree lifecycle.

The resulting behavior is difficult to change safely. In particular, broad exception handling can classify cleanup failures as launcher failures, Windows cleanup depends on `wmic.exe`, continuation starts a fresh Command Code process without a durable session contract, scope protection is mostly instructional, and review polling does not have a persistent transaction identity.

This design incorporates the accepted improvement input and the current evidence from these issues:

- `victorbernardi/jd-bi-acs-telemetry#1` and `#2`;
- `victorbernardi/Inova#109`, `#128`, `#169`, `#170`, and `#171`;
- `victorbernardi/.shared-ai-memory#8`.

Closed fixes from `Inova#129`, `#131`, and `#164` remain regression requirements.

The domain vocabulary is defined in [`skills/sdd-cmdc-opencode/CONTEXT.md`](../../../skills/sdd-cmdc-opencode/CONTEXT.md).

## Decision summary

Refactor incrementally into a small number of deep Modules while keeping `scripts/cmdc-implementer.py` as a thin compatibility Adapter. Do not rewrite the runner wholesale. Do not introduce a generic backend Seam while `cmdc-local` is the only operational Adapter.

The work is split into three deliveries:

1. process and launcher reliability;
2. resumable Run transaction, mechanical scope, provenance, and evidence;
3. persistent Review Transaction.

Each delivery must preserve a runnable, tested compatibility path.

## Goals

- Remove all `wmic.exe` dependencies.
- Make process creation, termination, and cleanup proof reliable on native Windows.
- Separate launcher, spawn, runtime, termination, and cleanup errors.
- Persist explicit Run states without losing the primary failure cause.
- Capture a Command Code Session ID and resume the same session safely.
- Detect a worker that consumes its early budget without implementation progress.
- Enforce allowed and denied paths mechanically while preserving pre-existing changes.
- Replace prompt-derived operational facts with versioned JSON contracts and results.
- Accept external plans only with explicit, verifiable provenance.
- Derive test evidence from normalized tool events.
- Include Markdown in OCR review scope.
- Make `CHANGES REQUIRED` terminal unless Fix Rounds were explicitly authorized.
- Persist reviewer identity and resume polling without duplicate dispatch.
- Preserve current CLI behavior during migration.

## Non-goals

- Replacing local Command Code with a proxy, remote provider, or direct model call.
- Implementing `ProviderHarnessBackend` in these deliveries.
- Creating `backends/base.py` for a hypothetical future Adapter.
- Automatically resetting or deleting out-of-scope changes.
- Silently copying an external plan into the implementation repository.
- Automatically fixing review findings when `auto_fix_rounds` is zero.
- Publishing installed skill copies or changing GitHub issue state as part of implementation.

## Architectural shape

```text
scripts/cmdc-implementer.py                 compatibility Adapter
scripts/review-session.py                  review CLI Adapter
scripts/sdd_cmdc_opencode/
    execution_lifecycle.py                 deep Run lifecycle Module
    process_supervisor.py                  deep process lifecycle Module
    cmdc_local.py                          deep local Command Code Module
    run_record.py                          deep Run transaction Module
    review_transaction.py                  deep review lifecycle Module
    internal scope and Windows helpers     private Implementation only
```

The exact private file split may change during implementation. Callers and tests must depend on the five named Module Interfaces, not on private helpers.

### Compatibility Adapter

`scripts/cmdc-implementer.py` remains the documented executable so existing invocations do not break. It parses current options, supports explicit `start` and `resume --run-id` operations, normalizes legacy input into a Run Contract, invokes the lifecycle Module, and renders the existing human-readable summary from the structured Result.

It does not own state transitions, process control, path parsing, recovery, or result validation.

### Run lifecycle Module

The lifecycle Module owns preflight ordering, state transitions, failure precedence, progress policy, Recovery eligibility, and outcome status. The state machine is private Implementation rather than a separate shallow Module.

Its Interface accepts a validated Run Contract or verified Recovery request and produces one persisted outcome for each completed invocation. Callers do not manipulate individual transition functions.

### Process lifecycle Module

The process Module owns spawn, streaming, timeout notification, final output drain, tree termination, and proof of cleanup across platforms. Both implementation and review use this Module.

On Windows, Job Object setup is private Implementation. The supervisor establishes containment before useful child work can begin, enables kill-on-close behavior, and verifies active processes through Job Object information. It does not use process ancestry from WMIC. If containment or cleanup cannot be proven, the Module fails closed.

POSIX process-group behavior remains supported behind the same Interface.

### Local Command Code Module

`cmdc-local` owns installed launcher discovery, wrapper normalization, package entry-point resolution, the disposable smoke test, command construction, session identification, NDJSON translation, and resume invocation.

Supported launch forms include `.ps1`, `.cmd`, `.bat`, `.exe`, and a package-declared Node entry point. The Module must not depend on a hard-coded `dist/index.mjs` when package metadata declares the executable.

The smoke test runs in a temporary Git repository with a very small turn budget. It captures stdout, stderr, exit code, session evidence, and cleanup evidence. A missing capability blocks preflight; there is no proxy or provider fallback.

### Run transaction Module

The Run Record owns `contract.json`, event JSONL, checkpoints, baseline, provenance, session identity, Result, and all resume invariants. Prompt text is a rendering of the contract, not an operational authority.

The Module also owns canonical path normalization and final scope validation. Thin internal Adapters may expose that Implementation to the Command Code scope Mod without creating another public Module.

### Review lifecycle Module

The Review Transaction owns the exact Git range, review package, OCR coverage, reviewer identity, polling state, findings, Fix Round authorization, and terminal review result.

It never recalculates the range from `HEAD~1` and never treats a successful command exit alone as approval.

## Why there is no backend Seam yet

`cmdc-local` is the only Adapter that can currently satisfy session persistence, event normalization, scope enforcement, process cleanup, and evidence requirements. A base class plus an unavailable provider Adapter would make the Interface almost as complex as its only Implementation.

The deletion test therefore rejects `backends/base.py`: deleting it removes speculative complexity instead of forcing complexity to reappear across multiple callers. The Run Contract and Result still record `backend: "cmdc-local"` so a future second Adapter can be introduced deliberately without changing historical evidence.

## Run artifacts

Each task Run stores its artifacts below the existing plan-scoped SDD workspace. The default layout is:

```text
{plan-workspace}/runs/{run-id}/
    contract.json
    events.jsonl
    checkpoints.jsonl
    result.json
    scope-contract.json
```

The brief, Implementer Report, review package, and human Ledger remain at their existing plan-scoped paths. Existing explicit report and checkpoint options remain valid after canonical path validation.

### Run Contract

`contract.json` is immutable after the Run starts and is validated before launcher smoke or process creation.

```json
{
  "schema_version": 1,
  "run_id": "task-5-20260819-001",
  "task": {
    "id": 5,
    "heading": "Task 5",
    "brief_path": ".superpowers/sdd/task-5-brief.md",
    "brief_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "report_path": ".superpowers/sdd/task-5-report.md"
  },
  "plan": {
    "source_path": "C:/plans/source-repo/docs/feature-plan.md",
    "source_repository": "C:/plans/source-repo",
    "source_branch": "main",
    "source_head": "cccccccccccccccccccccccccccccccccccccccc",
    "sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
  },
  "workspace": {
    "repo_root": "C:/worktrees/feature-branch",
    "base_head": "dddddddddddddddddddddddddddddddddddddddd",
    "branch": "feat/feature-branch",
    "baseline_status": {}
  },
  "scope": {
    "allowed_paths": [],
    "denied_paths": []
  },
  "execution": {
    "backend": "cmdc-local",
    "model": "deepseek/deepseek-v4-flash",
    "max_turns": 100,
    "wall_timeout_seconds": 14400,
    "stall_timeout_seconds": 900,
    "progress_deadline_turns": 10,
    "max_resumes": 2,
    "no_skills": true,
    "yolo": true
  },
  "success": {
    "require_commit": true,
    "require_report": true,
    "require_test_evidence": true
  },
  "review": {
    "auto_fix_rounds": 0
  }
}
```

Legacy CLI values are normalized into this schema before execution. Operational paths and state are never rediscovered from free-form prompt text when their structured value is available.

### External plan provenance

An external plan is accepted only when its source repository, branch, commit, original path, file SHA-256, task heading, and extracted brief SHA-256 are recorded. The worker receives the local brief. The Run Record retains the relationship to the original plan.

The plan is not copied silently. A requested copy must be an explicit artifact operation with its own destination and provenance.

### Events and test evidence

Command Code NDJSON is translated into normalized domain events. Tool results retain command, exit code, stdout, stderr, timestamps, and tool identity.

```json
{
  "type": "tool_result",
  "tool": "shell",
  "command": "pytest tests/unit -q",
  "exit_code": 0,
  "stdout": "246 passed in 23.67s",
  "stderr": ""
}
```

The Result derives test evidence from these events rather than from the final assistant message. It recognizes zero-failure summaries such as `246 passed`, preserves the command exactly, and treats Windows command separators independently from shell output parsing.

### Result

`result.json` is the current authority for transactional approval. Markdown remains the human report. A completed invocation writes it atomically with status `COMPLETE`, `BLOCKED`, or `INCOMPLETE`; the append-only event and checkpoint streams retain every prior outcome when Recovery updates the current Result.

The Result records at least:

- schema version, Run ID, backend, and Command Code Session ID;
- status, primary blocker, and secondary blockers;
- base and final commits;
- scope validity and violating paths;
- report and test-evidence validity;
- process-tree cleanup proof;
- normalized tests;
- Recovery attempts and whether the same session was resumed;
- paths and hashes for contract, plan, brief, report, events, and checkpoints.

The compatibility Adapter renders the existing short textual contract from this object.

## Scope enforcement

Scope is mechanical and fail closed.

### Contract construction

An explicit `allowed_paths` list takes precedence. If it is absent, the Orchestrator may derive paths only from the task's declared `Files` section and records that derivation. If neither source provides deterministic paths, preflight returns `SCOPE_CONTRACT_MISSING`. The whole repository is never an implicit default.

`denied_paths` always overrides `allowed_paths`. Paths are canonical repository-relative paths after Windows separator, case, dot-segment, symlink, and absolute-path normalization.

### Pre-tool enforcement

`cmdc-local` loads a Run-specific Command Code Mod through `--mod`. The Mod source is packaged and immutable; its Run-specific configuration is a temporary validated JSON contract. It does not modify user or project Command Code settings.

The Mod blocks direct `write` and `edit` calls outside the allowlist before execution. A capability smoke test proves that the installed Command Code version loads the Mod and fires the hook. Missing Mod or hook support blocks preflight without degraded enforcement.

### Shell and final enforcement

After every shell tool call, the awaited Mod lifecycle checks Git status against the baseline before another turn can continue. An indirect effect outside scope terminates the Run with `SCOPE_VIOLATION`. The Python Run lifecycle independently repeats the check at checkpoints, Recovery, and final validation.

The runner never resets an out-of-scope path. It preserves the workspace for audit and reports all detected paths.

## Progress and Recovery

Implementation progress is observable when at least one of these occurs:

- a permitted write or edit;
- an allowed workspace change relative to baseline;
- a new task commit;
- a normalized test or shell event classified as directly related to implementation.

The default initial progress deadline is 20 percent of `max_turns`, capped at ten turns and never lower than one turn. The contract may set a stricter value. If the worker only explores or plans through that deadline, the Run terminates with `NO_IMPLEMENTATION_PROGRESS`.

Recovery policy:

- `WORKER_TURN_LIMIT` automatically resumes the same Command Code Session up to `max_resumes`;
- exhausting `max_resumes` produces `BLOCKED` with `WORKER_TURN_LIMIT` as the primary blocker and `RECOVERY_EXHAUSTED` as a secondary blocker;
- `STALLED` and `WALL_TIMEOUT` produce `INCOMPLETE`, preserve the session and Checkpoint, and require explicit `resume --run-id`;
- launcher failure, scope violation, cleanup failure, or unverifiable cleanup is not resumable;
- every Recovery requires the same `run_id`, `base_head`, contract hash, owned Checkpoint, known workspace fingerprint, and no unknown changes;
- the Recovery prompt is a short finalization instruction rendered from the same Run Contract;
- a Fix Round is not Recovery and always uses a new Command Code Session.

There is no generic `--allow-dirty` path around these checks.

## State model

The private state machine accepts only explicit transitions:

```text
PREFLIGHT -> SPAWN -> RUNNING
RUNNING -> CLEANUP_VERIFICATION -> COMPLETE
RUNNING -> WORKER_TURN_LIMIT -> CLEANUP_VERIFICATION -> RECOVERY
RECOVERY -> SPAWN -> RUNNING
RUNNING -> NO_IMPLEMENTATION_PROGRESS
        -> TERMINATING -> CLEANUP_VERIFICATION -> BLOCKED
RUNNING -> STALLED | WALL_TIMEOUT
        -> TERMINATING -> CLEANUP_VERIFICATION -> INCOMPLETE
INCOMPLETE -> RECOVERY -> SPAWN -> RUNNING
```

Scope violation, protocol failure, and unexpected runtime failure also pass through termination and cleanup verification when a process may exist. A controlled recoverable interruption may produce `INCOMPLETE`; an unclassified interruption fails closed.

## Error taxonomy and precedence

The lifecycle records errors at the narrowest Module that understands them.

| Phase | Codes |
|---|---|
| Resolution | `LAUNCHER_NOT_FOUND`, `LAUNCHER_UNSUPPORTED` |
| Smoke | `LAUNCHER_SMOKE_FAILED`, `LAUNCHER_SMOKE_CLEANUP_FAILED` |
| Spawn | `PROCESS_SPAWN_FAILED`, `PROCESS_JOB_ASSIGNMENT_FAILED` |
| Execution | `NO_IMPLEMENTATION_PROGRESS`, `STALLED`, `WALL_TIMEOUT`, `WORKER_TURN_LIMIT`, `CMD_CODE_PROTOCOL_ERROR` |
| Scope | `SCOPE_CONTRACT_MISSING`, `SCOPE_VIOLATION` |
| Termination | `PROCESS_TREE_TERMINATION_FAILED`, `PROCESS_CLEANUP_UNVERIFIABLE` |
| Recovery | `RESUME_INVARIANT_FAILED`, `RECOVERY_EXHAUSTED` |
| Result | `REPORT_INVALID`, `TEST_EVIDENCE_INVALID`, `COMMIT_REQUIREMENT_FAILED` |

The first causal error remains `primary_blocker`. Termination, cleanup, or persistence errors discovered afterward are appended to `secondary_blockers`. If no earlier cause exists, a cleanup failure becomes primary. Invalid transitions and unknown event shapes fail closed with phase diagnostics.

No Result can be `COMPLETE` until cleanup verification proves the process tree is empty.

## Review Transaction

Review begins only after a Run Result is `COMPLETE`.

1. Generate the review package for the exact base and head recorded by the Run.
2. Run delegated OCR preview and rules for every changed path.
3. Treat `.md` and `.markdown` as reviewable paths.
4. Return `REVIEW_UNSUPPORTED_FILE` for a truly unsupported extension; never convert exclusion into `REVIEW CLEAN`.
5. Persist `review_id`, exact range, shell, commands, and current state before polling.
6. Treat polling timeout as resumable `REVIEW_TIMEOUT`, retaining the same `review_id` and prohibiting duplicate dispatch.
7. Reserve `REVIEW_FAILED` for a confirmed terminal reviewer failure.
8. Require both specification-compliance and task-quality verdicts plus complete path coverage for `REVIEW CLEAN`.

`auto_fix_rounds` defaults to zero. With zero authorization, `CHANGES REQUIRED` is terminal. When the Run Contract explicitly authorizes a positive value, each Fix Round uses a new Command Code Session, retains links to the findings and original Review Transaction, reruns covering tests, and receives a scoped OCR re-review over the exact fix range. Exhausting the authorized rounds leaves `CHANGES REQUIRED`; findings are not silently parked or discarded.

OCR remains mandatory. Shell failure, incomplete preview, unresolved rules, reviewer timeout, or unsupported files never trigger an alternate review Adapter.

## Cross-platform helper behavior

Windows-native execution must not invoke a Bash helper with Python. Task brief extraction and other controller helpers receive explicit cross-platform entry points. Legacy extensionless helpers may remain as shell wrappers, but the SKILL documentation must invoke the correct entry for the current platform.

Legacy report-path parsing remains only in the compatibility Adapter. It normalizes spaces, quotes, backticks, Windows separators, and a marker separated from its path by a newline. New Runs use structured contract paths.

## Testing strategy

The Interface of each deep Module is its primary test surface. Existing tests that monkeypatch private functions move toward observable Module behavior; narrowly platform-specific private Implementation may retain focused internal tests.

### Unit and contract tests

- valid and invalid state transitions;
- primary and secondary blocker precedence;
- Run Contract and Result schema versioning;
- launcher and process error classification;
- Command Code event and Session ID normalization;
- progress deadline and `NO_IMPLEMENTATION_PROGRESS`;
- Recovery invariants and maximum resumes;
- allowed, denied, pre-existing, tracked, and untracked paths;
- external-plan and brief hashes;
- report paths containing spaces, quotes, backticks, Windows separators, and split markers;
- test summaries including `246 passed` and Windows commands containing `;`;
- Markdown review, unsupported files, reviewer identity, timeout resume, and Fix Round authorization.

### Process integration tests

A helper process creates child and grandchild processes. Tests prove timeout, termination, final output drain, and cleanup verification. Native Windows tests exercise Job Object behavior and run with `wmic.exe` absent. POSIX tests exercise process groups.

### Command Code tests

A fake executable emits deterministic NDJSON for success, protocol failure, Session ID capture, turn limit, stall, and resume. A separate local gate runs the real installed Command Code launcher smoke in a disposable repository and verifies no process remains.

### Scope tests

The Run-specific Mod blocks direct out-of-scope writes before execution. Shell integration tests create indirect changes and prove termination, preserved files, reported paths, and final Python revalidation.

### End-to-end integration

At least one deterministic integration test runs:

```text
start
  -> contract
  -> smoke
  -> execution
  -> checkpoint
  -> worker turn limit
  -> same-session Recovery
  -> execution
  -> scope validation
  -> Result
  -> Review Transaction
```

The fake Command Code and fake review Adapter remove model/network nondeterminism while the lifecycle, Run Record, scope policy, checkpoints, and review state remain real.

### Regression and package gates

- preserve behavior from closed issues `Inova#129`, `#131`, and `#164`;
- run `skills/sdd-cmdc-opencode/tests` from the skill directory;
- treat the former standalone `sdd-cmdc` suite as historical evidence only;
- verify the package manifest and tracked-file contract;
- report installation parity separately without overwriting installed copies.

The current governed baseline is `299 passed, 12 skipped` from
`skills/sdd-cmdc-opencode` on native Windows.

## Delivery sequence

### Delivery 1: process and launcher foundation

- extract the shared process lifecycle Module;
- use it from both implementation and review;
- implement Windows Job Object containment and cleanup proof;
- remove WMIC;
- extract the deep `cmdc-local` Module;
- add disposable launcher and Mod-capability smoke tests;
- classify resolution, spawn, runtime, termination, and cleanup separately;
- keep the compatibility Adapter and existing tests green.

### Delivery 2: resumable Run transaction

- add Run Contract, Run Record, event stream, checkpoints, and Result;
- render prompts from structured data;
- add external plan provenance;
- capture Session ID and implement safe same-session Recovery;
- add progress detection;
- add the Run-specific scope Mod and final scope verification;
- normalize test evidence and legacy Windows paths;
- add deterministic end-to-end integration.

### Delivery 3: Review Transaction

- add Markdown OCR coverage and explicit unsupported-file status;
- persist reviewer identity and polling state;
- resume polling without duplicate dispatch;
- make zero automatic Fix Rounds the default;
- use new sessions for explicitly authorized Fix Rounds;
- align SKILL instructions, prompts, ledger entries, and final review gates.

## Compatibility and rollout

- The old CLI invocation remains supported throughout migration.
- The textual implementer summary remains available but is rendered from `result.json`.
- Existing worktree, protected-branch, deployed-server, `--no-skills`, `--skip-onboarding`, `--yolo` consent, and OCR requirements remain fail closed.
- Every delivery updates tests and documentation with the code that changes behavior.
- Canonical source changes occur only in `skills/sdd-cmdc-opencode` plus its design and plan documents.
- Installation into `.agents` or `.codex`, remote publication, and issue closure remain separate authorized operations.

## Acceptance criteria

The design is implemented only when all of the following are true:

- no production path invokes WMIC;
- implementation and review share one process lifecycle Module;
- a launcher failure cannot be emitted for a cleanup exception;
- the real launcher smoke completes in a disposable repository with a clean process tree;
- a Run captures its Session ID and safely resumes the same session;
- a worker that does not implement within the early budget returns `NO_IMPLEMENTATION_PROGRESS`;
- direct and indirect out-of-scope changes are mechanically blocked or detected, preserved, and reported;
- pre-existing workspace changes remain distinguishable and untouched;
- external plan and local brief provenance are verifiable;
- `contract.json`, normalized events, checkpoints, and `result.json` form an auditable chain;
- tests are approved from normalized events rather than agent prose;
- Markdown receives OCR coverage;
- `CHANGES REQUIRED` is terminal by default;
- review timeout preserves one reviewer identity and supports explicit polling resume;
- scoped unit, integration, regression, package, and Windows gates pass;
- installed-copy parity is reported without unauthorized overwrite.
