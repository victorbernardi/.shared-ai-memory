# SDD Command Code Review Transaction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make delegated OCR review a persistent transaction over the exact successful Run range, with real Markdown coverage, one durable reviewer identity per review cycle, resumable polling, and no automatic Fix Round unless the Run Contract explicitly authorizes it.

**Architecture:** Add `review_transaction` as the deep review lifecycle Module. It owns exact range/package/OCR evidence, state, reviewer binding, report validation, findings, and Fix Round authorization. `review-session.py` becomes the CLI Adapter for transaction operations while retaining its legacy clean-host positional form. Codex remains the Orchestrator and performs reasoning after deterministic OCR delegation; Python records dispatch/polling state but never invokes collaboration tools or substitutes another reviewer.

**Tech Stack:** Python 3 standard library, JSON/JSONL, Git, Alibaba Open Code Review delegation CLI, pytest, the Delivery 1 process supervisor, and the Delivery 2 Run Record/Result.

## Global Constraints

- Begin only after the complete acceptance gates in both earlier 2026-08-19 plans pass.
- Review starts only from a persisted Run Result whose status is `COMPLETE`. A text report, green tests, or exit code zero cannot bypass this gate.
- Use the exact `base_head` and `final_head` recorded in the Run Result. Never derive review scope from `HEAD~1`, current checkout drift, or prompt text.
- OCR delegation remains mandatory: `ocr delegate preview` then `ocr delegate rule`. Do not use `ocr review`, configure an OCR LLM endpoint/API key, or add a Codex-only fallback.
- Keep Codex as Orchestrator/reviewer and Command Code as implementer only. Python must not spawn an agent or pretend to poll collaboration state.
- Admit `.md` and `.markdown` with an explicit OCR rule and verify the preview actually returns them as reviewable. Unsupported or omitted changed paths never become `REVIEW CLEAN`.
- Persist local `review_id` and transaction state before reviewer dispatch. Bind the actual reviewer agent ID exactly once per review cycle.
- Poll timeout is resumable `REVIEW_TIMEOUT`. Resume waits on the recorded reviewer identity and never dispatches a duplicate.
- Reserve `REVIEW_FAILED` for a confirmed terminal reviewer failure/abort. Preparation/OCR/report incompleteness uses `REVIEW INCOMPLETE` with a precise blocker; unsupported extension uses `REVIEW_UNSUPPORTED_FILE`.
- `auto_fix_rounds` defaults to `0`. With zero, `CHANGES REQUIRED` is terminal. A positive value must already exist in the immutable Run Contract.
- Each authorized Fix Round is a new Run and a new Command Code Session. Recovery APIs are forbidden for Fix Rounds.
- Keep existing protected/deployed/worktree/scope/cleanup gates. Never overwrite installed copies, publish, push, merge, or change issue state.
- Run source and sibling tests separately from their skill directories.

## Open-Issue Traceability

- [`Inova#109`](https://github.com/victorbernardi/Inova/issues/109), “stabilize requesting-code-review dispatch and wait”: Tasks 1 and 4 persist review/reviewer identity, distinguish timeout from terminal failure, and resume polling without redispatch.
- [`Inova#128`](https://github.com/victorbernardi/Inova/issues/128), “block review loops in skills and commands”: Tasks 5 and 6 make `CHANGES REQUIRED` terminal by default and place a hard immutable bound on explicitly authorized Fix Rounds.
- [`.shared-ai-memory#8`](https://github.com/victorbernardi/.shared-ai-memory/issues/8), “Support Markdown files in delegated OCR preview”: Task 3 admits Markdown with a packaged include rule and verifies actual preview/rule coverage before dispatch.
- These tasks create source evidence only. Issue closure remains a later, explicit reconciliation after review, integration/publication, and operational verification.

## Verified OCR Dependency Behavior

- The planning probe used the installed `open-code-review v1.9.7` against the exact design commit range. Without a custom rule both Markdown files were excluded as `unsupported_ext`; with the rule specified in Task 3 the preview returned `reviewable_count: 2` and `excluded_count: 0`.
- Alibaba's merged [include-before-allowlist fix](https://github.com/alibaba/open-code-review/pull/378) establishes that an explicit user include can admit an otherwise non-allowlisted extension.
- Alibaba's maintainer [custom-extension example](https://github.com/alibaba/open-code-review/discussions/440) documents the same `include` plus path-rule shape used here.
- Implementation still uses a behavioral capability probe instead of trusting a minimum version string. A later binary that reports a compatible version but omits Markdown remains fail closed.

---

## File Structure and Stable Interfaces

Add or change these paths:

```text
skills/sdd-cmdc-opencode/
  scripts/
    review-session.py                          transaction + legacy CLI Adapter
    review-package                            retained Bash compatibility wrapper
    review-package.py                         cross-platform exact-range packager
    sdd_cmdc_opencode/
      review_transaction.py                   deep review lifecycle Module
      ocr-delegation-rule.json                immutable Markdown include/rule
  task-reviewer-prompt.md                     initial review contract
  re-review-prompt.md                         finding-disposition contract
  tests/
    helpers/fake_ocr.py
    test_review_package.py
    test_review_transaction.py
    test_review_session.py
    test_review_integration.py
```

`review_transaction.py` exposes these public values:

```python
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ReviewState(str, Enum):
    CREATED = "CREATED"
    PREPARING = "PREPARING"
    READY_TO_DISPATCH = "READY_TO_DISPATCH"
    RUNNING = "RUNNING"
    REVIEW_TIMEOUT = "REVIEW_TIMEOUT"
    REVIEW_INCOMPLETE = "REVIEW INCOMPLETE"
    REVIEW_CLEAN = "REVIEW CLEAN"
    CHANGES_REQUIRED = "CHANGES REQUIRED"
    REVIEW_FAILED = "REVIEW_FAILED"
    REVIEW_UNSUPPORTED_FILE = "REVIEW_UNSUPPORTED_FILE"


@dataclass(frozen=True)
class ReviewContract:
    schema_version: int
    review_id: str
    run_id: str
    repo_root: Path
    base: str
    head: str
    package_path: Path
    report_path: Path
    auto_fix_rounds: int
    fix_round: int


@dataclass(frozen=True)
class ReviewerBinding:
    cycle: str
    reviewer_agent_id: str
    model: str
    effort: str
    bound_at: str


@dataclass(frozen=True)
class ReviewFinding:
    finding_id: str
    severity: str
    path: str
    start_line: int
    end_line: int
    summary: str
    disposition: str | None


@dataclass(frozen=True)
class ReviewResult:
    schema_version: int
    review_id: str
    state: ReviewState
    blocker_code: str | None
    base: str
    head: str
    reviewable_paths: tuple[str, ...]
    excluded_paths: tuple[str, ...]
    reviewer: ReviewerBinding | None
    findings: tuple[ReviewFinding, ...]
    specification_compliance: str | None
    task_quality: str | None
    fix_rounds_used: int
    artifact_hashes: Mapping[str, str]
```

`ReviewTransaction` has this public Interface:

```text
ReviewTransaction.create(review_dir: Path, run_result_path: Path) -> ReviewTransaction
ReviewTransaction.load(review_dir: Path) -> ReviewTransaction
ReviewTransaction.prepare() -> ReviewResult
ReviewTransaction.bind_reviewer(binding: ReviewerBinding) -> ReviewResult
ReviewTransaction.record_poll_timeout(observed_at: str) -> ReviewResult
ReviewTransaction.resume_polling() -> ReviewerBinding
ReviewTransaction.record_reviewer_failure(payload: dict[str, object]) -> ReviewResult
ReviewTransaction.complete(report_path: Path) -> ReviewResult
ReviewTransaction.create_fix_round_contract(destination: Path) -> Path
ReviewTransaction.record_fix_run(result_path: Path) -> ReviewResult
ReviewTransaction.read_result() -> ReviewResult
```

The immutable transaction contract, append-only events, and current Result use:

```text
{plan-workspace}/reviews/{review-id}/
  contract.json
  events.jsonl
  result.json
  review-package.md
  review-package.json
  ocr-preview.json
  ocr-rules.json
  reviewer-report.md
```

Canonical transaction CLI forms are:

```text
python scripts/review-session.py transaction create --run-result PATH --review-dir DIRECTORY
python scripts/review-session.py transaction prepare --review-dir DIRECTORY
python scripts/review-session.py transaction bind --review-dir DIRECTORY --cycle initial --reviewer-agent-id ID --model MODEL --effort EFFORT
python scripts/review-session.py transaction timeout --review-dir DIRECTORY --observed-at ISO8601
python scripts/review-session.py transaction resume --review-dir DIRECTORY
python scripts/review-session.py transaction fail --review-dir DIRECTORY --payload-file PATH
python scripts/review-session.py transaction complete --review-dir DIRECTORY --report-file PATH
```

The existing positional `review-session.py PLAN BASE HEAD PROMPT REPORT` form remains supported as a compatibility path and uses the Delivery 1 process supervisor.

---

### Task 1: Persist the Review Transaction and exact successful Run range

**Files:**
- Create: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/review_transaction.py`
- Create: `skills/sdd-cmdc-opencode/tests/test_review_transaction.py`
- Modify: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/__init__.py`

**Interfaces:** Use the exact public values and `ReviewTransaction` operations above. Internal transition helpers remain private.

- [ ] **Step 1: Write creation-gate RED tests**

  Build persisted Run Results for `COMPLETE`, `BLOCKED`, and `INCOMPLETE`. Assert only `COMPLETE` creates a transaction. Also reject:

  - missing or malformed Run Result;
  - mismatched Run ID/artifact hash;
  - missing cleanup/scope/report/test/commit evidence required by the Run Contract;
  - repository root mismatch;
  - base/head not resolvable to the exact recorded commits;
  - a Run Result whose final HEAD is no longer a descendant of base.

  Run `python -m pytest tests/test_review_transaction.py -q -k "create or run_gate or range"`. Expected RED: Module absent.

- [ ] **Step 2: Implement immutable contract creation**

  Allocate `review_id` before any OCR or reviewer work, copy no mutable Run facts from prose, and write the immutable contract with exclusive-create semantics. Use the Run's exact `base_head`, `final_head`, repository, Run ID, review policy, and plan workspace. Set state `CREATED` and append a creation event containing the Run Result hash.

  A second create at the same directory cannot replace contract or identity. Loading verifies contract hash, paths, exact refs, and schema version.

- [ ] **Step 3: Write transition/atomicity RED tests**

  Assert this transition graph:

  ```text
  CREATED -> PREPARING -> READY_TO_DISPATCH -> RUNNING
  RUNNING -> REVIEW_TIMEOUT -> RUNNING
  RUNNING -> REVIEW_CLEAN | CHANGES_REQUIRED | REVIEW_FAILED | REVIEW INCOMPLETE
  PREPARING -> REVIEW_UNSUPPORTED_FILE | REVIEW INCOMPLETE
  CHANGES REQUIRED -> PREPARING only for an explicitly authorized Fix Round
  ```

  Invalid transitions fail closed and append diagnostics. Simulate interrupted Result replacement and prove the prior result remains parseable; events remain append-only with sequence, review ID, contract hash, cycle, and UTC timestamp.

- [ ] **Step 4: Implement persistence and failure precedence**

  Reuse the Run Record's atomic JSON/append-only conventions without coupling to its private helpers. Preserve the first preparation/reviewer cause as blocker; add later process/evidence-write failures as secondary event details. Do not let an evidence write error change `REVIEW_TIMEOUT` into a reviewer failure.

- [ ] **Step 5: Run focused tests and commit**

  Run:

  ```powershell
  python -m pytest tests/test_review_transaction.py -q -k "create or range or transition or atomic"
  python -m py_compile scripts/sdd_cmdc_opencode/review_transaction.py
  ```

  Stage Task 1 paths and commit:

  ```powershell
  git add skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/review_transaction.py skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/__init__.py skills/sdd-cmdc-opencode/tests/test_review_transaction.py
  git commit -m "feat: persist exact-range review transactions"
  ```

---

### Task 2: Replace the Bash-only review packager with an exact cross-platform entry

**Files:**
- Create: `skills/sdd-cmdc-opencode/scripts/review-package.py`
- Modify: `skills/sdd-cmdc-opencode/scripts/review-package`
- Create: `skills/sdd-cmdc-opencode/tests/test_review_package.py`
- Modify: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/review_transaction.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_review_transaction.py`

**Interfaces:**

```text
build_review_package(repo: Path, base: str, head: str, markdown_path: Path, manifest_path: Path) -> dict[str, object]
python scripts/review-package.py --repo REPOSITORY --base BASE --head HEAD --markdown OUT_MD --manifest OUT_JSON
```

- [ ] **Step 1: Write exact-range packager RED tests**

  In a temporary repository, create multiple commits and assert the package uses the supplied base/head full hashes, not current HEAD. Cover added, modified, deleted, renamed, binary, Markdown, Unicode, spaces, and `&` paths. Change HEAD after choosing the range and prove package bytes/range remain tied to the original refs.

  Manifest assertions include:

  ```json
  {
    "schema_version": 1,
    "base": "1111111111111111111111111111111111111111",
    "head": "2222222222222222222222222222222222222222",
    "merge_base": "1111111111111111111111111111111111111111",
    "paths": ["docs/guide.md", "src/app.py"],
    "commands": []
  }
  ```

  The test supplies real hashes rather than the illustrative values above.

  Run `python -m pytest tests/test_review_package.py -q`. Expected RED: Python packager absent.

- [ ] **Step 2: Implement Git argument-array packaging**

  Resolve refs with `git rev-parse --verify <ref>^{commit}`, verify base ancestry, and collect paths with NUL-delimited Git output. Record exact argument arrays and exit codes. The Markdown contains range metadata, name-status, stat, and exact diff; the JSON manifest contains normalized paths, statuses, counts, command evidence, and SHA-256 of the Markdown.

  Never invoke a shell, reconstruct pathspec strings, or use `HEAD~1`.

- [ ] **Step 3: Make the extensionless helper a wrapper and wire prepare**

  Keep its existing argument form when feasible, translate it to the Python CLI, and document the Windows-native Python form. `ReviewTransaction.prepare()` writes package outputs only inside its own directory and verifies both hashes before OCR.

- [ ] **Step 4: Run focused tests and commit**

  Run:

  ```powershell
  python -m pytest tests/test_review_package.py tests/test_review_transaction.py -q -k "package or exact_range"
  python -m py_compile scripts/review-package.py
  ```

  Stage Task 2 paths and commit:

  ```powershell
  git add skills/sdd-cmdc-opencode/scripts/review-package.py skills/sdd-cmdc-opencode/scripts/review-package skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/review_transaction.py skills/sdd-cmdc-opencode/tests/test_review_package.py skills/sdd-cmdc-opencode/tests/test_review_transaction.py
  git commit -m "feat: package exact review ranges cross platform"
  ```

---

### Task 3: Make Markdown reviewable and fail closed on OCR coverage gaps

**Files:**
- Create: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/ocr-delegation-rule.json`
- Create: `skills/sdd-cmdc-opencode/tests/helpers/fake_ocr.py`
- Modify: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/review_transaction.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_review_transaction.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_package_contract.py`

**Interfaces:** `ReviewTransaction.prepare()` runs OCR preview/rules through the shared process supervisor and transitions to `READY_TO_DISPATCH` only after complete deterministic coverage.

- [ ] **Step 1: Add the immutable OCR rule asset**

  Create this exact JSON:

  ```json
  {
    "include": [
      "**/*.md",
      "**/*.markdown"
    ],
    "rules": [
      {
        "path": "**/*.{md,markdown}",
        "rule": "Review documentation for correctness, internal consistency, executable commands, paths, and governance requirements."
      }
    ]
  }
  ```

  Add package tests that parse it, require both include patterns, and prohibit user/project OCR setting mutation.

- [ ] **Step 2: Write OCR preview/rule RED tests with a fake executable**

  `fake_ocr.py` records argument arrays and emits deterministic JSON for:

  - all changed code/Markdown paths reviewable;
  - Markdown excluded as `unsupported_ext`;
  - another unsupported extension;
  - a changed binary path excluded by OCR;
  - missing changed path from preview;
  - unresolved/empty rule output;
  - nonzero preview/rule exit;
  - timeout with verified cleanup;
  - malformed JSON.

  Assert exact commands contain `delegate preview`, `delegate rule`, `--repo`, full `--from`/`--to` refs, `--rule` asset, and `--format json`. Assert no command contains `ocr review` or an LLM configuration call.

  Run `python -m pytest tests/test_review_transaction.py -q -k ocr`. Expected RED until prepare invokes OCR.

- [ ] **Step 3: Resolve a clean Git executable environment for OCR**

  On Windows, enumerate Git candidates and choose a real `.exe`, rejecting `.cmd`, `.bat`, `.ps1`, aliases, and wrappers whose `rev-parse` output contains extra lines. Prepend the validated executable directory to the OCR child `PATH`. On POSIX, validate the resolved executable similarly.

  This prevents wrapper banners from corrupting OCR repository/ref parsing. Record resolved Git/OCR paths and versions in preparation events without making a version string the capability authority.

- [ ] **Step 4: Implement preview, capability validation, and rules**

  Run preview first and require every manifest path to be reviewable. If `.md`/`.markdown` is not reviewable with the packaged include rule, transition to `REVIEW_UNSUPPORTED_FILE`. Any changed path excluded as `unsupported_ext` or binary uses the same state and is listed; user-excluded or missing paths, malformed output, timeout, nonzero exit, or empty rules transition to `REVIEW INCOMPLETE` with a precise blocker. No explicit exclusion is sufficient for `REVIEW CLEAN`.

  Run `delegate rule` for every reviewable path in one argument array, persist raw JSON and SHA-256, and confirm every path has resolved rule content. Only then transition to `READY_TO_DISPATCH`.

- [ ] **Step 5: Add an opt-in real local OCR capability gate**

  Skip unless `SDD_CMDC_REAL_OCR_SMOKE=1`. In a disposable repository, commit a `.py` and `.md` change, run exact-range preview/rules with the packaged asset, and assert `reviewable_count == 2`, zero unsupported files, and verified process cleanup.

  Run deterministic and optional real gates separately:

  ```powershell
  python -m pytest tests/test_review_transaction.py -q -k "ocr and not real_ocr_capability"
  $env:SDD_CMDC_REAL_OCR_SMOKE = "1"
  python -m pytest tests/test_review_transaction.py -q -k real_ocr_capability
  Remove-Item Env:SDD_CMDC_REAL_OCR_SMOKE
  ```

  A skip is reported as no current operational proof, not as a pass.

- [ ] **Step 6: Commit OCR coverage**

  Stage Task 3 paths and commit:

  ```powershell
  git add skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/ocr-delegation-rule.json skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/review_transaction.py skills/sdd-cmdc-opencode/tests/helpers/fake_ocr.py skills/sdd-cmdc-opencode/tests/test_review_transaction.py skills/sdd-cmdc-opencode/tests/test_package_contract.py
  git commit -m "fix: include markdown in delegated ocr coverage"
  ```

---

### Task 4: Persist reviewer identity and resume polling without redispatch

**Files:**
- Modify: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/review_transaction.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_review_transaction.py`
- Modify: `skills/sdd-cmdc-opencode/scripts/review-session.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_review_session.py`

**Interfaces:** Implement `bind_reviewer`, `record_poll_timeout`, `resume_polling`, `record_reviewer_failure`, and the canonical transaction CLI forms.

- [ ] **Step 1: Write identity and timeout RED tests**

  Assert:

  - binding before `READY_TO_DISPATCH` is rejected;
  - the first binding records cycle, agent ID, model, effort, and timestamp and transitions to `RUNNING`;
  - rebinding the same cycle to another ID is rejected;
  - polling timeout preserves the binding and transitions to `REVIEW_TIMEOUT`;
  - `resume_polling()` returns the same binding and transitions back to `RUNNING` without an event named dispatch;
  - repeated timeout/resume retains one identity;
  - only a terminal failure payload produces `REVIEW_FAILED`;
  - timeout, missing mailbox update, or no report never produces `REVIEW_FAILED` or `REVIEW CLEAN`.

  Run `python -m pytest tests/test_review_transaction.py -q -k "reviewer or polling or timeout"`. Expected RED.

- [ ] **Step 2: Implement durable cycle bindings**

  Persist the transaction Result before the Orchestrator calls `spawn_agent`. After dispatch, bind the returned agent ID exactly once. A cycle key is `initial` or `fix-N-review`; it prevents duplicate dispatch while permitting a distinct reviewer identity for a later authorized re-review.

  `resume_polling()` is read/transition logic only. It emits JSON containing `review_id`, `cycle`, `reviewer_agent_id`, and action `WAIT_EXISTING_REVIEWER`; it has no code path that starts a process or agent.

- [ ] **Step 3: Add transaction subcommands to the CLI Adapter**

  Dispatch on the literal first arguments `transaction create|prepare|bind|timeout|resume|fail|complete`. Keep legacy positional parsing when the first argument is not `transaction`. Every transaction command prints one JSON Result and returns nonzero for invalid transition/evidence.

  Add subprocess tests that invoke the CLI and reload files, proving state survives a new Python process.

- [ ] **Step 4: Add the Orchestrator contract to CLI output**

  `prepare` returns `DISPATCH_REVIEWER` only after OCR coverage. `bind` returns `WAIT_REVIEWER`. `timeout` returns `REVIEW_TIMEOUT` plus the same ID. `resume` returns `WAIT_EXISTING_REVIEWER` and never `DISPATCH_REVIEWER`. `fail` requires a terminal collaboration payload with the bound ID.

- [ ] **Step 5: Run focused tests and commit**

  Run:

  ```powershell
  python -m pytest tests/test_review_transaction.py tests/test_review_session.py -q -k "transaction or reviewer or polling or timeout or legacy"
  python -m py_compile scripts/review-session.py scripts/sdd_cmdc_opencode/review_transaction.py
  ```

  Stage Task 4 paths and commit:

  ```powershell
  git add skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/review_transaction.py skills/sdd-cmdc-opencode/scripts/review-session.py skills/sdd-cmdc-opencode/tests/test_review_transaction.py skills/sdd-cmdc-opencode/tests/test_review_session.py
  git commit -m "feat: resume review polling by stable identity"
  ```

---

### Task 5: Validate dual-axis review reports and make changes terminal by default

**Files:**
- Modify: `skills/sdd-cmdc-opencode/task-reviewer-prompt.md`
- Modify: `skills/sdd-cmdc-opencode/re-review-prompt.md`
- Modify: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/review_transaction.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_review_transaction.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_review_session.py`

**Interfaces:** `complete(report_path)` validates one reviewer report for the bound cycle and produces only `REVIEW CLEAN`, `CHANGES REQUIRED`, or fail-closed `REVIEW INCOMPLETE`.

- [ ] **Step 1: Write report-validation RED tests**

  Require these report fields:

  ```text
  Review ID
  Cycle
  Range
  Files reviewed
  Excluded files
  Specification compliance: PASS | FAIL
  Task quality: PASS | FAIL
  Findings
  Verdict: REVIEW CLEAN | CHANGES REQUIRED
  ```

  Each actionable finding has stable ID, severity, path, start/end line, and summary. Assert:

  - both axes PASS, full path coverage, no actionable findings, exact identity/range -> `REVIEW CLEAN`;
  - either axis FAIL or any actionable finding -> `CHANGES REQUIRED`;
  - missing/duplicate path, wrong review ID/cycle/range, unknown verdict, inconsistent finding/verdict, or invalid line span -> `REVIEW INCOMPLETE`;
  - OCR-excluded unsupported path cannot be cured by reviewer prose.

  Run `python -m pytest tests/test_review_transaction.py -q -k "report or verdict or finding"`. Expected RED.

- [ ] **Step 2: Update initial and re-review prompts**

  Initial prompt includes immutable Review ID, exact range, package/preview/rule paths and hashes, and asks for independent specification-compliance plus task-quality conclusions. It forbids edits, Command Code, API review, GitHub comments, and range recalculation.

  Re-review prompt includes exact fix range and every previous finding. It requires `ADDRESSED` or `NOT ADDRESSED` per finding and may add new findings. It cannot silently omit or mark findings resolved without evidence.

- [ ] **Step 3: Implement strict report parsing and hashing**

  Parse Markdown deterministically, normalize repository-relative paths through the same canonical policy, require exact coverage of OCR reviewable paths, and persist report SHA-256. Do not infer clean from exit code or a phrase outside the structured verdict field.

- [ ] **Step 4: Enforce zero Fix Rounds as the default terminal policy**

  When `auto_fix_rounds == 0`, `CHANGES REQUIRED` is terminal. The Result action is `RETURN_FINDINGS_TO_OPERATOR`; no Run Contract is created, no Command Code command is built, and no re-review cycle appears. Add a regression against the current five-round automatic loop in `SKILL.md`/tests.

- [ ] **Step 5: Run focused tests and commit**

  Run:

  ```powershell
  python -m pytest tests/test_review_transaction.py tests/test_review_session.py -q -k "report or verdict or finding or zero_fix"
  ```

  Stage Task 5 paths and commit:

  ```powershell
  git add skills/sdd-cmdc-opencode/task-reviewer-prompt.md skills/sdd-cmdc-opencode/re-review-prompt.md skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/review_transaction.py skills/sdd-cmdc-opencode/tests/test_review_transaction.py skills/sdd-cmdc-opencode/tests/test_review_session.py
  git commit -m "fix: make review changes terminal by default"
  ```

---

### Task 6: Create explicitly authorized Fix Rounds as new Runs and Sessions

**Files:**
- Modify: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/review_transaction.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_review_transaction.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_execution_lifecycle.py`
- Modify: `skills/sdd-cmdc-opencode/tests/helpers/fake_cmdc.py`

**Interfaces:** Implement `create_fix_round_contract(destination)` and `record_fix_run(result_path)`. They operate only when immutable `auto_fix_rounds > fix_rounds_used` and current state is `CHANGES REQUIRED`.

- [ ] **Step 1: Write authorization and new-session RED tests**

  Assert contract creation is rejected when:

  - authorization is zero or exhausted;
  - current review is not `CHANGES REQUIRED`;
  - findings reference paths outside the original Run scope;
  - the reviewed HEAD/workspace no longer matches;
  - a prior Fix Round Run is still incomplete.

  For authorization `1`, assert the generated contract has a new Run ID, `base_head` equal to the previously reviewed head, allowed paths narrowed to in-scope finding paths, a validated `RunLineage` linking the parent Review Result/finding hashes, and no Session ID copied from the original Run.

  Run `python -m pytest tests/test_review_transaction.py tests/test_execution_lifecycle.py -q -k fix_round`. Expected RED.

- [ ] **Step 2: Implement Fix Round contract generation**

  Derive a new task brief that lists exact findings and success obligations. Preserve original plan provenance and record the original brief hash as `RunLineage.parent_brief_sha256`; hash the derived Fix Round brief as the new `task.brief_sha256`. Persist parent Review ID/Result hash and finding IDs/hash in `RunLineage`. Preserve original denied paths, fixed model, process/scope policies, and the explicitly authorized total. Do not widen original scope. Require normal `ExecutionLifecycle.start()`; never call Recovery or `CmdcLocal.resume`.

- [ ] **Step 3: Record Fix Round outcome and exact re-review range**

  Accept only a `COMPLETE` Fix Round Result with a different Command Code Session ID from every prior Run in the transaction. Set re-review range to previous reviewed head through new Fix Run final head, regenerate package/OCR evidence, and allocate cycle `fix-N-review` before dispatch.

  A blocked/incomplete Fix Run leaves `CHANGES REQUIRED` current and records its Result; it does not consume an unbounded retry. Exhausting the authorized count leaves `CHANGES REQUIRED` terminal.

- [ ] **Step 4: Add finding-disposition re-review tests**

  Require each old finding to be `ADDRESSED` or `NOT ADDRESSED`, retain unresolved findings, accept new findings, and transition to `REVIEW CLEAN` only when both axes pass, all old findings are addressed, no new actionable finding exists, and exact fix-range coverage is complete.

- [ ] **Step 5: Run focused tests and commit**

  Run:

  ```powershell
  python -m pytest tests/test_review_transaction.py tests/test_execution_lifecycle.py tests/test_cmdc_local.py -q -k "fix_round or new_session or disposition"
  ```

  Stage Task 6 paths and commit:

  ```powershell
  git add skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/review_transaction.py skills/sdd-cmdc-opencode/tests/test_review_transaction.py skills/sdd-cmdc-opencode/tests/test_execution_lifecycle.py skills/sdd-cmdc-opencode/tests/helpers/fake_cmdc.py
  git commit -m "feat: gate fix rounds behind explicit authorization"
  ```

---

### Task 7: Integrate the review lifecycle into the skill and prove end to end

**Files:**
- Create: `skills/sdd-cmdc-opencode/tests/test_review_integration.py`
- Modify: `skills/sdd-cmdc-opencode/SKILL.md`
- Modify: `skills/sdd-cmdc-opencode/CONTEXT.md` only for actual vocabulary drift
- Modify: `skills/sdd-cmdc-opencode/tests/test_skill_contract.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_package_contract.py`
- Modify: `skills/sdd-cmdc-opencode/tests/pressure/ocr-timeout.md`
- Modify: `skills/sdd-cmdc-opencode/tests/pressure/partial-preview.md`
- Modify: `skills/sdd-cmdc-opencode/tests/pressure/finding-fix-round.md`
- Modify: `skills/sdd-cmdc-opencode/tests/pressure/clean-review-session.md`

**Interfaces:** The SKILL workflow creates/prepares a transaction, dispatches exactly once, persists the returned reviewer ID, waits, records timeout/failure/report, and advances only on `REVIEW CLEAN`.

- [ ] **Step 1: Add deterministic initial-review integration**

  Use a real temporary Git repository, persisted `COMPLETE` Run Result, real package/transaction logic, fake OCR, and a fake reviewer report. Execute:

  ```text
  COMPLETE Run
    -> Review Transaction create
    -> exact package
    -> Markdown/code OCR preview + rules
    -> READY_TO_DISPATCH
    -> reviewer binding
    -> REVIEW_TIMEOUT
    -> resume same reviewer ID
    -> complete report
    -> REVIEW CLEAN
  ```

  Assert one review ID, one initial reviewer binding, exact range, complete path coverage, append-only timeout/resume evidence, no duplicate dispatch action, and no workspace mutation.

- [ ] **Step 2: Add deterministic changes/fix integration**

  With `auto_fix_rounds: 0`, assert `CHANGES REQUIRED` returns findings and stops. With `auto_fix_rounds: 1`, run a new fake Command Code Session, produce a fix commit/test/report, package/OCR the exact fix range, re-review finding dispositions, and reach clean. Assert original Session ID is never resumed and authorization cannot produce a second Fix Round.

  Run `python -m pytest tests/test_review_integration.py -q`. Expected GREEN before documentation updates.

- [ ] **Step 3: Add RED skill and pressure-contract assertions**

  Require the documented sequence and terms:

  - Run Result `COMPLETE` prerequisite;
  - exact recorded base/head;
  - `ocr delegate preview` and `ocr delegate rule` with Markdown rule;
  - `REVIEW_UNSUPPORTED_FILE` and `REVIEW INCOMPLETE` fail closed;
  - transaction/reviewer ID persisted before polling;
  - `REVIEW_TIMEOUT` resumes the same identity without dispatch;
  - `REVIEW_FAILED` only for terminal reviewer failure;
  - dual-axis report and complete coverage;
  - `auto_fix_rounds: 0` default;
  - new Session for authorized Fix Round;
  - no `ocr review`, API fallback, silent findings, or five-round default loop.

- [ ] **Step 4: Update SKILL, CONTEXT, and pressure scenarios**

  Replace the current automatic five-round loop with the transaction state machine and exact CLI/Orchestrator actions. Document that collaboration dispatch/wait occurs in Codex, while Python only persists/validates state. Explain how a new session resumes polling from review directory and reviewer ID.

  Update pressure scenarios so timeout, partial preview, unsupported Markdown, report mismatch, no-fix findings, authorized fix, and clean review all have explicit terminal states and stop criteria.

- [ ] **Step 5: Run Delivery 3 and complete source gates**

  From `skills/sdd-cmdc-opencode`:

  ```powershell
  python -m pytest tests/test_review_package.py tests/test_review_transaction.py tests/test_review_session.py tests/test_review_integration.py -q
  python -m pytest -q
  python -m py_compile scripts/review-package.py scripts/review-session.py scripts/sdd_cmdc_opencode/review_transaction.py
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

  Run the real OCR capability gate separately if available; report it independently from deterministic tests and review approval.

- [ ] **Step 6: Commit Delivery 3 documentation and integration tests**

  Stage only Task 7 paths and commit:

  ```powershell
  git add skills/sdd-cmdc-opencode/tests/test_review_integration.py skills/sdd-cmdc-opencode/SKILL.md skills/sdd-cmdc-opencode/CONTEXT.md skills/sdd-cmdc-opencode/tests/test_skill_contract.py skills/sdd-cmdc-opencode/tests/test_package_contract.py skills/sdd-cmdc-opencode/tests/pressure/ocr-timeout.md skills/sdd-cmdc-opencode/tests/pressure/partial-preview.md skills/sdd-cmdc-opencode/tests/pressure/finding-fix-round.md skills/sdd-cmdc-opencode/tests/pressure/clean-review-session.md
  git commit -m "docs: define persistent delegated review transactions"
  ```

  If `CONTEXT.md` has no actual diff, omit it from the final staged set.

## Delivery 3 Acceptance Gate

Delivery 3 is complete only when all statements are evidenced:

- a Review Transaction can be created only from a fully valid `COMPLETE` Run Result;
- package, OCR, reviewer, and report all use the exact recorded base/head range;
- `.md` and `.markdown` appear in actual OCR reviewable paths with the packaged include rule;
- any unsupported, omitted, malformed, timed-out, or unresolved OCR path fails closed and never becomes clean;
- transaction identity is persisted before dispatch and actual reviewer identity is bound once per cycle;
- polling timeout retains that identity and resume emits only `WAIT_EXISTING_REVIEWER`;
- terminal reviewer failure is distinct from timeout/incomplete evidence;
- `REVIEW CLEAN` requires both specification compliance and task quality plus complete path coverage;
- `CHANGES REQUIRED` is terminal when `auto_fix_rounds` is zero;
- every authorized Fix Round has a new Run ID and Command Code Session and receives an exact-range OCR re-review;
- exhausted authorization remains `CHANGES REQUIRED` with findings intact;
- deterministic initial/fix integration, complete source suite, sibling suite, package, compile, diff, and read-only parity gates pass;
- installation synchronization, publication, merge, issue closure, and operational use remain separate authorized actions.
