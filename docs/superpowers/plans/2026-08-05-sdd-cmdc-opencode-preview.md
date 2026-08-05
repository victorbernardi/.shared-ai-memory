# sdd-cmdc-opencode Preview Improvements Implementation Plan

> For agentic workers: REQUIRED SUB-SKILL: Use sdd-cmdc-opencode to execute this plan task-by-task. Each task is an independent commit and review gate. Keep the exact BASE recorded before the first edit of that task; never infer it with HEAD~1.

Goal: Transform the current sdd-cmdc-opencode package into a fail-closed, Windows-native, evidence-driven implementation workflow covering all P0 corrections, the essential P1 hardening, and the P2 metadata/clarity improvements described in preview.md.

Architecture: Keep Codex as the controller, Command Code as the fixed-model implementer, and delegated OCR as the mandatory reviewer. Move operational behavior into small Python helpers with explicit contracts, retain LF Bash compatibility wrappers while consumers migrate, and make workspace, report, ledger, review-range, cleanup, and state transitions independently verifiable. Keep the skill body short and load detailed governance/runtime material from first-level references.

Tech Stack: Python already supported by the repository, pytest, Git, native Windows process APIs through subprocess, PowerShell/CMD launchers only when required by Windows shims, and ocr delegate preview/rule for delegated review. Tests must not invoke Codex, Command Code, OCR, API review, or network services.

## Global Constraints

- Baseline is commit fc8522be2d4319be8b11454027462705e5f4b7ef (fc8522b), which already contains the source-backed issue-131 timeout alias and its CLI-boundary test.
- Work only in C:\Users\victor.bernardi\.shared-ai-memory.worktrees\feat-sdd-cmdc-opencode-preview on branch feat/sdd-cmdc-opencode-preview; do not merge, publish, synchronize local master, install globally, or modify the issue-131 worktree during this plan.
- Preserve the fixed Command Code model deepseek/deepseek-v4-flash; do not add a fallback model, fallback backend, ocr review, OCR API mode, OPENAI_API_KEY, SkillOpt, synthetic LLM evaluations, Claude-specific runtime instructions, or WSL2 requirements.
- Preserve pre-existing user changes. No command in this plan may clean, reset, overwrite, or recursively delete an unvalidated path. The cleanup helper is implemented and tested, but is not run against a real user workspace in this plan.
- The controller remains responsible for planning, reconciliation, state classification, review-range selection, finding decisions, and final completion. Command Code remains responsible for implementation commits and reports. Delegated OCR remains a prerequisite for review; an ordinary Codex review cannot substitute for it.
- Every implementation task starts from a recorded full commit BASE, uses a fresh Command Code dispatch through scripts/cmdc-implementer.py, commits before broad host verification, and receives a scoped ocr delegate preview plus ocr delegate rule review of the exact BASE..HEAD range.
- Every operational failure is fail-closed. A timeout, partial preview, missing report, stale report, incomplete OCR coverage, unresolved finding, or uncertain cleanup target is never converted into approval or completion.
- Machine tokens, states, blocker codes, ledger fields, and report fields use English stable identifiers. Portuguese remains allowed in user-facing explanations and remediation text.
- The current compatibility wrappers scripts/review-package, scripts/sdd-workspace, and scripts/task-brief are retained as LF launchers until all callers use the Python modules; no file is deleted merely to match the proposed target tree.
- The issue-131 --timeout-seconds alias remains an alias of --wall-timeout-seconds, with the same positive-value validation and finite watchdog semantics.

## Baseline File Map

The verified baseline contains these tracked package files:

- skills/sdd-cmdc-opencode/SKILL.md — 765-line controller workflow and governance contract.
- skills/sdd-cmdc-opencode/implementer-prompt.md — Command Code task prompt.
- skills/sdd-cmdc-opencode/task-reviewer-prompt.md and re-review-prompt.md — host review prompts.
- skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py — 1,493-line implementer adapter, watchdog, diagnostics, recovery, and CLI.
- skills/sdd-cmdc-opencode/scripts/review-session.py — clean host review launcher and report validator.
- skills/sdd-cmdc-opencode/scripts/review-package, sdd-workspace, and task-brief — CRLF Bash helpers whose contracts must be preserved while they are migrated.
- skills/sdd-cmdc-opencode/scripts/__init__.py — existing empty Python package marker.
- skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py, test_review_session.py, and test_skill_contract.py — current deterministic tests, with known digest/global-state coupling to be removed in the test-hardening task.
- skills/sdd-cmdc-opencode/tests/pressure/*.md — scenario fixtures for the contradictory pressure cases.
- skills/sdd-cmdc-opencode/audit_result.json — historical audit artifact that must not be treated as runtime quality evidence.

The intended target adds references/, agents/openai.yaml, Python helper modules, cleanup_workspace.py, ledger.py, state_contract.py, and a separated test layout while retaining compatibility wrappers during the migration.

## Dependency and Review Gates

The task order is deliberately sequential:

1. Package hygiene and platform normalization establish readable scripts and a clean artifact boundary.
2. Execution preflight and cmdc resolution protect the YOLO boundary before any child process can start.
3. Input, report, and Windows process contracts make failures observable and structured.
4. Cleanup, state, workspace, ledger, review, and retry contracts make recovery safe and idempotent.
5. Prompts, scenarios, progressive disclosure, and tests align the human contract with the runtime contract.
6. Audit/secrets/P2 metadata and final packaging close the release gate.

After each task commit, the controller must run the exact changed-task tests, the relevant full package suite, git diff --check, and the delegated OCR review. A task is not complete merely because its tests pass; its ledger entry must record the commit range, commands, exit codes, preview/rule coverage, findings, and decision.

---

### Task 1: Normalize package files and establish the release manifest

Files:
- Create: .gitattributes entries scoped to skills/sdd-cmdc-opencode/.
- Modify: .gitignore only if package-specific generated-artifact rules are absent; preserve all existing rules.
- Modify: skills/sdd-cmdc-opencode/scripts/review-package, sdd-workspace, and task-brief to LF-compatible wrappers.
- Modify: tracked Python and Markdown files under skills/sdd-cmdc-opencode/ to UTF-8/LF through controlled renormalization.
- Create: skills/sdd-cmdc-opencode/tests/test_package_contract.py.
- Test: test_package_contract.py and the existing package suite.

Interfaces:
- Produce a package manifest based on git ls-files, not on a recursive filesystem walk that accidentally includes ignored caches.
- Produce assert_lf_or_non_binary(path: Path), tracked_runtime_files(), and assert_no_generated_payload() test helpers for later packaging tasks.

- [ ] Step 1: Write the failing package tests.

Add tests that enumerate tracked files below skills/sdd-cmdc-opencode/ and assert:

    EXECUTABLE_SHELLS = {
        Path("scripts/review-package"),
        Path("scripts/sdd-workspace"),
        Path("scripts/task-brief"),
    }

    def test_shell_wrappers_have_lf_only_bytes() -> None:
        for relative in EXECUTABLE_SHELLS:
            data = (SKILL / relative).read_bytes()
            assert b"\r\n" not in data

    def test_tracked_package_has_sources_and_no_generated_payload() -> None:
        tracked = git_ls_files_under(SKILL)
        assert Path("scripts/__init__.py") in tracked
        assert all("__pycache__" not in path.parts and path.suffix != ".pyc" for path in tracked)

    def test_text_sources_decode_as_utf8() -> None:
        for path in tracked_text_files(SKILL):
            path.read_text(encoding="utf-8")

- [ ] Step 2: Run the package tests to capture RED.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_package_contract.py -q

Expected on baseline: the LF assertion fails for the three CRLF Bash scripts; the failure is evidence for P0-01, not a reason to alter unrelated repository files.

- [ ] Step 3: Add attributes and normalize only the scoped package.

Add these scoped rules without replacing existing repository attributes:

    skills/sdd-cmdc-opencode/**/*.py text eol=lf
    skills/sdd-cmdc-opencode/**/*.md text eol=lf
    skills/sdd-cmdc-opencode/scripts/review-package text eol=lf
    skills/sdd-cmdc-opencode/scripts/sdd-workspace text eol=lf
    skills/sdd-cmdc-opencode/scripts/task-brief text eol=lf

Convert the three wrappers and all scoped text sources to LF/UTF-8, then verify:

    git add .gitattributes .gitignore skills/sdd-cmdc-opencode
    git diff --cached --check
    bash -n skills/sdd-cmdc-opencode/scripts/review-package
    bash -n skills/sdd-cmdc-opencode/scripts/sdd-workspace
    bash -n skills/sdd-cmdc-opencode/scripts/task-brief

Do not stage __pycache__, .pytest_cache, or any ignored artifact.

- [ ] Step 4: Run GREEN and the package baseline.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_package_contract.py -q
    python -m pytest skills/sdd-cmdc-opencode/tests -q
    python -m pytest skills/sdd-cmdc/tests -q
    git diff --check

Expected: package contract passes; both suites remain green; git diff --check is silent.

- [ ] Step 5: Commit and review.

    git add .gitattributes .gitignore skills/sdd-cmdc-opencode
    git commit -m "chore: normalize sdd-cmdc-opencode package files"

Record the pre-edit BASE, commit, exact tests, bash -n results, and manifest. Generate the review package from that BASE to HEAD; run ocr delegate preview and ocr delegate rule for every reviewable file. Any CRLF or package-scope finding must be fixed by a fresh CMDc round.

### Task 2: Make the YOLO and repository boundary an explicit preflight

Files:
- Modify: skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py.
- Modify: skills/sdd-cmdc-opencode/SKILL.md and implementer-prompt.md.
- Create: skills/sdd-cmdc-opencode/tests/test_preflight_contract.py.
- Test: test_preflight_contract.py plus focused adapter tests in test_cmdc_implementer.py.

Interfaces:
- Add validate_execution_boundary(cwd: Path, plan_file: Path, *, allow_protected_branch: bool, ledger_file: Path | None) -> dict[str, object].
- Add capture_initial_git_state(cwd: Path) -> dict[str, object] containing canonical worktree, branch, HEAD, and exact git status --short lines.
- Add CLI options --plan-file, --allow-protected-branch, and --allow-cmdc-yolo; include --yolo in build_command() only when the explicit adapter option is present.
- Extend the persistent report/checkpoint context with the preflight snapshot; never erase or normalize pre-existing status lines.

- [ ] Step 1: Write failing boundary tests.

Cover a trusted feature branch, main, master, a missing plan, a plan outside the repository, an invalid cwd, a dirty worktree, and a trusted worktree with pre-existing changes. The protected-branch test must require an explicit ledger entry containing ALLOW_PROTECTED_BRANCH before continuing. Assert that the snapshot preserves each status line verbatim.

    def test_preflight_blocks_master_without_recorded_consent(tmp_path: Path) -> None:
        result = validate_execution_boundary(
            tmp_path,
            tmp_path / "plan.md",
            allow_protected_branch=False,
            ledger_file=None,
        )
        assert result["BLOCKER_CODE"] in {"CWD_INVALID", "BRANCH_PROTECTED"}

The fixture must use a real temporary Git repository and a committed plan; do not inspect the controller's current dirty checkout as a test fixture.

- [ ] Step 2: Run RED.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_preflight_contract.py -q

Expected: the new preflight API and explicit YOLO option are absent or the protected-branch cases fail against baseline.

- [ ] Step 3: Implement the preflight contract.

Validate in this order: canonical repository root, cwd directory and descendant relationship, plan regular file and descendant relationship, Git branch/HEAD/status, protected branch policy, and explicit YOLO consent. Record the initial state before spawning Command Code. Keep --yolo out of build_command() unless --allow-cmdc-yolo is true, and include the selected mode in the diagnostic/report.

The adapter must reject direct execution in deployed/server paths unless a separate explicit authorization flag is recorded in the ledger; that authorization is not added to the normal skill command.

- [ ] Step 4: Run GREEN and verify the command boundary.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_preflight_contract.py skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py -q
    python -m pytest skills/sdd-cmdc-opencode/tests -q
    git diff --check

Expected: boundary tests pass, build_command() contains --yolo only for explicit consent, and the normal suite remains green.

- [ ] Step 5: Commit and review.

    git add skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py skills/sdd-cmdc-opencode/SKILL.md skills/sdd-cmdc-opencode/implementer-prompt.md skills/sdd-cmdc-opencode/tests/test_preflight_contract.py
    git commit -m "feat: enforce explicit execution boundary preflight"

Review the exact BASE..HEAD range with delegated OCR. A review that cannot inspect the preflight or command-construction paths is incomplete.

### Task 3: Harden cmdc resolution against project-local hijacking

Files:
- Modify: skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py or extract the resolver to scripts/cmdc_resolution.py without changing its public resolve_cmdc() import path.
- Modify: skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py.
- Create: skills/sdd-cmdc-opencode/tests/test_cmdc_resolution.py.
- Modify: skills/sdd-cmdc-opencode/SKILL.md with the trusted-resolution contract.

Interfaces:
- Preserve resolve_cmdc(cmd_bin: str = "cmdc") -> Path for callers.
- Add optional trusted_dirs: Sequence[Path] = () and allowlist CLI wiring without allowing a local project file to win for the bare name cmdc.
- Add resolved_cmdc_path to the run snapshot and report, with secrets and unrelated environment values redacted.

- [ ] Step 1: Write failing resolution tests.

Use temporary directories and monkeypatched PATH, APPDATA, and platform launcher helpers. Cover: ./cmdc ignored for the bare name; a PATH executable selected; an explicit absolute path accepted; a path containing spaces and Unicode; APPDATA used only when absolute/non-empty on Windows; directory and nonexistent candidate rejected; symlink resolved; C:\Windows\System32\cmd.exe rejected; .cmd and .ps1 selected through the trusted directory.

    def test_bare_cmdc_does_not_select_project_local_file(tmp_path, monkeypatch):
        local = tmp_path / "cmdc"
        local.write_text("fake", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("PATH", "")
        monkeypatch.delenv("APPDATA", raising=False)
        with pytest.raises(FileNotFoundError):
            resolve_cmdc("cmdc")

- [ ] Step 2: Run RED.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_cmdc_resolution.py -q

Expected: baseline accepts the local cmdc or constructs an unsafe empty-APPDATA candidate.

- [ ] Step 3: Implement deterministic candidate policy.

For a one-component name, query shutil.which() first and inspect only trusted candidates. Treat a local path as explicit only when it is absolute or contains a directory separator. On Windows, consult APPDATA\npm only when the environment value is absolute and non-empty. Reject directories, missing files, unresolved ambiguous candidates, and the native System32\cmd.exe. Resolve symlinks before returning. Apply the optional allowlist to the final resolved parent directory and pass the selected path through _platform_command().

- [ ] Step 4: Run GREEN and Windows-compatible checks.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_cmdc_resolution.py skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py -q
    python -m pytest skills/sdd-cmdc-opencode/tests -q
    git diff --check

Expected: all candidate-policy tests pass on Windows; non-Windows tests use deterministic fakes rather than assuming Windows filesystem semantics.

- [ ] Step 5: Commit and review.

    git add skills/sdd-cmdc-opencode
    git commit -m "fix: prevent project-local cmdc resolution hijacking"

The OCR review must include the resolver, platform launcher, and every new test path.

### Task 4: Validate inputs and enforce the structured report contract

Files:
- Modify: skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py.
- Modify: skills/sdd-cmdc-opencode/scripts/review-session.py where report fields are shared.
- Modify: skills/sdd-cmdc-opencode/implementer-prompt.md, task-reviewer-prompt.md, and re-review-prompt.md.
- Create: skills/sdd-cmdc-opencode/scripts/report_contract.py.
- Create: skills/sdd-cmdc-opencode/tests/test_report_contract.py.
- Test: test_report_contract.py, test_cmdc_implementer.py, and test_review_session.py.

Interfaces:
- Create ReportSnapshot(exists: bool, size: int, mtime_ns: int | None, sha256: str | None).
- Create capture_report_snapshot(path: Path) -> ReportSnapshot.
- Create validate_report(path: Path, *, before: ReportSnapshot, task_id: str, round_id: str, require_change: bool) -> dict[str, object].
- Add explicit CLI option --report-file; stop deriving report identity from a free-form prompt sentence.
- Keep the seven-field diagnostic schema exactly: STATUS, BLOCKER_CODE, MESSAGE, COMMAND, EXIT_CODE, STDERR, ACTION.

- [ ] Step 1: Write failing validation tests.

Test all input and report classes from the preview: invalid cwd, cwd outside expected worktree, missing/non-UTF-8/empty/placeholder prompt, invalid/non-positive --max-turns, missing launcher, missing report, pre-existing unchanged report, changed report, fix-round report that changes hash without growing, empty report, missing required fields, invalid status, mismatched task/round, path traversal, and redaction of a token in stderr.

Use these exact required report headings:

    Status:
    Task:
    Round:
    Commit(s):
    Tests:
    Files changed:
    Concerns/Blockers:

The validator must return REPORT_STALE for an unchanged pre-existing report and REPORT_INVALID for an empty or semantically incomplete report.

- [ ] Step 2: Run RED.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_report_contract.py -q

Expected: baseline either accepts stale reports or lacks the explicit report-file contract.

- [ ] Step 3: Implement input/report validation.

Validate and resolve cwd, plan_file, prompt_file, and report_file before starting a child process. Require the report path to remain within the execution workspace. Snapshot it before execution; require creation/change afterward and, for a fix round, require hash or size change. Parse the worker short status separately and reject BLOCKED or IMPLEMENTATION INCOMPLETE even when the child exit code is zero. Redact bearer tokens, API-key-shaped values, passwords, connection strings, and credential-like environment values before including stderr in diagnostics, reports, or ledger entries. Catch PermissionError, OSError, UnicodeError, BrokenPipeError, and controlled interruption paths into the stable diagnostic schema.

Apply _positive_int to --max-turns and preserve the issue-131 timeout alias. The prompt contains task content, but adapter arguments are authoritative for report identity.

- [ ] Step 4: Run GREEN and verify no raw traceback is the only failure.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_report_contract.py skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py skills/sdd-cmdc-opencode/tests/test_review_session.py -q
    python -m pytest skills/sdd-cmdc-opencode/tests -q
    git diff --check

Expected: each known operational failure has one deterministic blocker code and no known path emits only an uncaught traceback.

- [ ] Step 5: Commit and review.

    git add skills/sdd-cmdc-opencode
    git commit -m "feat: validate implementer inputs and reports fail closed"

The delegated review must inspect report freshness, path containment, status parsing, redaction, and the seven-field output together.

### Task 5: Standardize Windows subprocesses, encoding, and timeout cleanup

Files:
- Modify: skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py.
- Modify: skills/sdd-cmdc-opencode/scripts/review-session.py.
- Create: skills/sdd-cmdc-opencode/tests/test_windows_process_contract.py.
- Modify: skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py and test_review_session.py.

Interfaces:
- Preserve _run_cmdc_process(...) -> subprocess.CompletedProcess[str] and _run_process(...) -> ProcessResult while making encoding, bounded capture, and cleanup behavior explicit.
- Add MAX_CAPTURE_BYTES and a deterministic _bounded_append()/stream policy; report truncation as evidence rather than silently dropping output.
- Add timeout reasons WALL_TIMEOUT, STALL_TIMEOUT, and MODEL_TURN_LIMIT while preserving blocker code TIMEOUT for finite timeout paths.

- [ ] Step 1: Write failing process tests.

Use fake Popen implementations and short-lived helper child processes. Cover UTF-8 prompt/output containing ç, ã, and Unicode paths with spaces; .cmd, .ps1, and native executable command construction; missing PowerShell launcher as LAUNCHER_NOT_FOUND; timeout termination of the leader and descendant; real non-zero exit-code preservation; bounded stdout/stderr capture; and distinction between a watchdog timeout and a Command Code max-turns message.

- [ ] Step 2: Run RED.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_windows_process_contract.py -q

Expected: at least launcher, bounded-output, or timeout-kind tests fail against the current unbounded/partially classified behavior.

- [ ] Step 3: Implement the process contract.

Pass stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", and errors="replace" on every text subprocess. Keep prompts on stdin. Use the existing process-tree/group helpers, verify the entire tree after termination, and raise a timeout carrying its reason and cleanup result. Drain streams continuously into bounded buffers and record a truncation marker. Preserve the child actual return code and classify launcher failures separately from Command Code failures.

- [ ] Step 4: Run GREEN and the full deterministic suites.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_windows_process_contract.py skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py skills/sdd-cmdc-opencode/tests/test_review_session.py -q
    python -m pytest skills/sdd-cmdc-opencode/tests -q
    python -m pytest skills/sdd-cmdc/tests -q
    git diff --check

- [ ] Step 5: Commit and review.

    git add skills/sdd-cmdc-opencode
    git commit -m "fix: harden Windows subprocess and timeout handling"

The OCR review must include both adapter paths and verify that timeout cleanup is not declared clean from a leader-only check.

### Task 6: Add a recoverable, path-restricted cleanup helper

Files:
- Create: skills/sdd-cmdc-opencode/scripts/cleanup_workspace.py.
- Modify: skills/sdd-cmdc-opencode/SKILL.md, implementer-prompt.md, and tests/test_skill_contract.py.
- Create: skills/sdd-cmdc-opencode/tests/test_cleanup_workspace.py.

Interfaces:
- Create validate_cleanup_target(repo_root: Path, target: Path, ledger_file: Path) -> Path.
- Create cleanup_workspace(repo_root: Path, target: Path, ledger_file: Path, *, permanent: bool = False) -> dict[str, object].
- Default behavior moves the validated direct child of <repo-root>/.superpowers/sdd/ into an explicit recoverable trash directory and writes an atomic removal record. Permanent deletion requires --permanent and still records the exact target.

- [ ] Step 1: Write failing safety tests.

Reject empty paths, unresolved paths, repo root, filesystem root, the .superpowers/sdd parent, ancestors, symlinks, non-direct descendants, a ledger for another plan, and targets outside the repo. Accept only a real direct plan directory whose ledger identity matches. Verify default cleanup is recoverable and the audit record contains canonical target, ledger hash, mode, and timestamp.

- [ ] Step 2: Run RED.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_cleanup_workspace.py -q

Expected: the helper does not exist on baseline.

- [ ] Step 3: Implement and document the restricted helper.

Resolve all paths before validation, reject symlinks at every component, require the target parent to be exactly <repo-root>/.superpowers/sdd, and require the ledger to identify the same plan/workspace. Never accept /, C:\, the repo root, the user profile, a blank variable, or a computed path that was not re-resolved. Do not call this helper from normal task completion; expose it only as an explicit, audited cleanup action.

- [ ] Step 4: Run GREEN without touching a real workspace.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_cleanup_workspace.py skills/sdd-cmdc-opencode/tests/test_skill_contract.py -q
    python -m pytest skills/sdd-cmdc-opencode/tests -q
    git diff --check

- [ ] Step 5: Commit and review.

    git add skills/sdd-cmdc-opencode
    git commit -m "feat: restrict cleanup to recoverable plan workspaces"

OCR review must inspect every path validation branch. No real worktree or user directory is cleaned during this task.

### Task 7: Define one canonical state machine and versioned ledger

Files:
- Create: skills/sdd-cmdc-opencode/scripts/state_contract.py.
- Create: skills/sdd-cmdc-opencode/scripts/ledger.py.
- Modify: skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py, review-session.py, SKILL.md, implementer-prompt.md, task-reviewer-prompt.md, and re-review-prompt.md.
- Create: skills/sdd-cmdc-opencode/tests/test_state_contract.py and test_ledger.py.

Interfaces:
- Define STATES = ("READY", "IMPLEMENTING", "NEEDS_CONTEXT", "IMPLEMENTATION_BLOCKED", "READY_FOR_REVIEW", "REVIEW_INCOMPLETE", "REVIEW_BLOCKED", "FIXING", "REVIEW_CLEAN", "COMPLETE_WITH_DEFERRED", "COMPLETE", "PLAN_BLOCKED").
- Define validate_transition(previous: str, current: str, evidence: Mapping[str, object]) -> None.
- Define LedgerEntry(version: int, plan_id: str, task: int, round_id: str, state: str, base: str, head: str | None, commits: tuple[str, ...], commands: tuple[str, ...], exit_codes: tuple[int, ...], findings: tuple[dict[str, object], ...], decision: str).
- Define append_ledger(path: Path, entry: LedgerEntry) -> None using a temporary file and atomic replace, and read_ledger(path: Path) -> list[LedgerEntry] with schema validation.

- [ ] Step 1: Write failing transition and ledger tests.

Test every allowed path from READY through COMPLETE, invalid skips, missing evidence, REVIEW_CLEAN with parked findings, COMPLETE_WITH_DEFERRED, load-bearing residual findings producing PLAN_BLOCKED, malformed JSONL, and atomic preservation of the prior ledger after a failed append.

    def test_parked_finding_cannot_be_review_clean():
        with pytest.raises(StateContractError):
            validate_transition(
                "READY_FOR_REVIEW",
                "REVIEW_CLEAN",
                {"findings": [{"severity": "Minor", "status": "deferred"}]},
            )

- [ ] Step 2: Run RED.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_state_contract.py skills/sdd-cmdc-opencode/tests/test_ledger.py -q

- [ ] Step 3: Implement the canonical contract.

Make the state table and finding policy executable. Critical/High findings enter FIXING; Medium findings enter the fix loop when they affect the requirement and otherwise remain visible for final decision; Minor findings are deferred; false positives require written justification; load-bearing residuals become PLAN_BLOCKED. Retry reconciliation must occur before any new state transition. Keep a human-readable progress.md if existing users depend on it, but make versioned JSONL ledger entries authoritative.

- [ ] Step 4: Run GREEN and migrate all emitters.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_state_contract.py skills/sdd-cmdc-opencode/tests/test_ledger.py skills/sdd-cmdc-opencode/tests/test_review_session.py -q
    python -m pytest skills/sdd-cmdc-opencode/tests -q
    git diff --check

- [ ] Step 5: Commit and review.

    git add skills/sdd-cmdc-opencode
    git commit -m "feat: enforce canonical workflow states and ledger transitions"

The delegated review must check the state table, finding severity decisions, and the rule that parked findings cannot be called REVIEW_CLEAN.

### Task 8: Make plan workspaces unique and helper writes atomic

Files:
- Create: skills/sdd-cmdc-opencode/scripts/sdd_workspace.py, task_brief.py, and review_package.py.
- Modify: compatibility wrappers scripts/sdd-workspace, scripts/task-brief, and scripts/review-package.
- Create: skills/sdd-cmdc-opencode/tests/test_helpers.py.
- Modify: skills/sdd-cmdc-opencode/tests/test_skill_contract.py and SKILL.md.

Interfaces:
- Define resolve_workspace(plan_file: Path, repo_root: Path | None = None) -> WorkspaceIdentity where the identity contains canonical plan path, relative path, readable slug, stable short hash, and workspace path.
- Define extract_task(plan_file: Path, task_number: int, out_file: Path) -> Path.
- Define build_review_package(plan_file: Path, base: str, head: str, out_file: Path | None = None) -> Path.
- Python modules own the contracts; Bash wrappers only resolve their own directory and exec the Python module with quoted arguments.

- [ ] Step 1: Write failing helper tests.

Cover two plans named implementation.md in different directories, plan outside repo, idempotent .superpowers/sdd/.gitignore preservation, Unicode/space paths, positive integer task IDs, Markdown headings, fenced code blocks using both backticks and tildes, correct structural task termination, empty/placeholder/wrong-task briefs, atomic output after an injected failure, complete BASE/HEAD resolution, non-ancestor BASE rejection, binary/rename/submodule/large-file manifest entries, and distinct review output files for different ranges.

- [ ] Step 2: Run RED.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_helpers.py -q
    bash -n skills/sdd-cmdc-opencode/scripts/sdd-workspace
    bash -n skills/sdd-cmdc-opencode/scripts/task-brief
    bash -n skills/sdd-cmdc-opencode/scripts/review-package

Expected: the Python modules do not exist and current Bash helpers still collide by basename or overwrite .gitignore.

- [ ] Step 3: Implement Python helpers and compatibility wrappers.

Use the canonical plan path relative to the repository plus a stable short SHA-256 component, for example implementation-4f6e2a1c, instead of basename alone. Reject plans outside the repo unless an explicit authorization is passed by the controller. Ensure .gitignore contains the required * rule without replacing existing content. Write briefs and review packages to a sibling temporary file in the same directory, flush and close it, then atomically replace the destination only after every Git/parser command succeeds. Include in the review package a manifest of changed paths, complete range, commit list, stat, and package SHA-256.

- [ ] Step 4: Run GREEN and wrapper compatibility checks.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_helpers.py skills/sdd-cmdc-opencode/tests/test_package_contract.py -q
    python -m pytest skills/sdd-cmdc-opencode/tests -q
    bash skills/sdd-cmdc-opencode/scripts/sdd-workspace docs/superpowers/plans/2026-08-05-sdd-cmdc-opencode-preview.md
    git diff --check

Expected: printed workspace includes path identity hash, existing ignore content survives, and no partial output remains after simulated failure.

- [ ] Step 5: Commit and review.

    git add skills/sdd-cmdc-opencode
    git commit -m "feat: make SDD helpers atomic and plan-unique"

The OCR review must include Python implementations and all three compatibility wrappers.

### Task 9: Make delegated review coverage measurable

Files:
- Modify: skills/sdd-cmdc-opencode/scripts/review_package.py and review-session.py.
- Create: skills/sdd-cmdc-opencode/scripts/review_contract.py.
- Modify: skills/sdd-cmdc-opencode/SKILL.md, task-reviewer-prompt.md, and re-review-prompt.md.
- Create: skills/sdd-cmdc-opencode/tests/test_review_contract.py.

Interfaces:
- Define ReviewManifest with base, head, merge_base, git_paths, package_paths, preview_paths, excluded_paths, and exclusion reasons.
- Define validate_review_coverage(manifest: ReviewManifest) -> None.
- Define render_review_finding(severity: str, path: str, lines: str, rule: str, evidence: str, recommendation: str, status: str) -> str.
- Keep the exact range supplied by the controller; do not infer it with HEAD~1.

- [ ] Step 1: Write failing coverage tests.

Test a complete Python/text preview, a deliberately excluded unsupported file with a recorded reason, a missing preview path, a missing rule resolution, a Git/package/preview path mismatch, a timeout/partial preview, and an OCR exit code zero without actual coverage. Assert that only complete coverage can produce a review-clean candidate.

- [ ] Step 2: Run RED.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_review_contract.py -q

- [ ] Step 3: Implement the manifest and delegated-review contract.

Have review_package.py publish its manifest only after the full range/package succeeds. Record BASE, FIX_BASE, HEAD, and MERGE_BASE as resolved full commit IDs, shell and OCR version, exact commands, exit codes, included paths, excluded paths, and reasons. Require ocr delegate preview to cover the Git manifest and require ocr delegate rule for every preview-reviewable path. Any difference is REVIEW_INCOMPLETE or REVIEW_BLOCKED, never REVIEW_CLEAN. Keep ocr review, API, OPENAI_API_KEY, and ordinary Codex review explicitly prohibited.

- [ ] Step 4: Run GREEN with deterministic fixtures.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_review_contract.py skills/sdd-cmdc-opencode/tests/test_review_session.py -q
    python -m pytest skills/sdd-cmdc-opencode/tests -q
    git diff --check

- [ ] Step 5: Commit and delegated-review the review contract itself.

    git add skills/sdd-cmdc-opencode
    git commit -m "feat: make delegated review coverage auditable"

The review of this task must itself use the new manifest and coverage checks; a missing path or missing rule output is a blocker.

### Task 10: Make retries and recovery idempotent

Files:
- Modify: skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py.
- Create: skills/sdd-cmdc-opencode/scripts/recovery.py and tests/test_recovery.py.
- Modify: SKILL.md, implementer-prompt.md, and ledger.py.

Interfaces:
- Define reconcile_before_retry(cwd: Path, base: str, report_file: Path, ledger_file: Path) -> dict[str, object].
- Define ExecutionLock(path: Path) with acquire(), release(), and recover_stale(); active locks are never removed by another run.
- Define recovery_id(task: int, round_id: str, attempt: int) -> str and persist it in checkpoint, report, and ledger context.

- [ ] Step 1: Write failing recovery tests.

Use temporary Git repositories to cover timeout before commit, timeout after commit, partial working-tree edits, a valid report with a completed commit, an existing DONE/READY_FOR_REVIEW state, active lock, stale lock whose PID is gone, lock with a live PID, duplicate redispatch prevention, and recovery context limited to the persistent artifacts required by the next implementer.

- [ ] Step 2: Run RED.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_recovery.py -q

- [ ] Step 3: Implement reconciliation and locking.

Before every retry, collect current HEAD, commits after BASE, git status --short, report snapshot/content, ledger state, and checkpoint. If the task is already committed and report/review state is sufficient, return a non-dispatch decision. If partial work exists, pass exact persistent context to a fresh implementer instead of presenting an empty task. Acquire a lock atomically with owner PID, branch, HEAD, plan identity, and timestamp. Recover only a stale lock whose owner is demonstrably gone and whose identity matches; never remove a live lock.

- [ ] Step 4: Run GREEN and simulate both prior timeout outcomes.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_recovery.py skills/sdd-cmdc-opencode/tests/test_state_contract.py -q
    python -m pytest skills/sdd-cmdc-opencode/tests -q
    git diff --check

- [ ] Step 5: Commit and review.

    git add skills/sdd-cmdc-opencode
    git commit -m "fix: make implementer retries idempotent"

The delegated review must verify that timeout recovery cannot duplicate commits or dispatch concurrently.

### Task 11: Align prompts and all pressure scenarios with canonical contracts

Files:
- Modify: skills/sdd-cmdc-opencode/SKILL.md only for references to canonical states/contracts in this task; the large disclosure split is Task 12.
- Modify: implementer-prompt.md, task-reviewer-prompt.md, and re-review-prompt.md.
- Modify: tests/pressure/api-key-fallback.md, dirty-workspace.md, finding-fix-round.md, ocr-timeout.md, and partial-preview.md.
- Create: skills/sdd-cmdc-opencode/tests/test_scenario_contract.py.

Interfaces:
- Prompts accept explicit --report-file, task ID, round ID, BASE, worktree/branch, and plan identity from the controller.
- Prompt statuses and reports use the state/ledger names from Task 7.
- Scenario fixtures remain documentation test inputs; they do not call external tools.

- [ ] Step 1: Write failing document-contract tests.

Parse prompts and scenarios structurally. Assert that report path is an argument contract, placeholders are rejected, pre-existing partial work has a defined action, and the five scenarios use canonical states and blocker codes. Assert specifically that api-key-fallback.md rejects ocr review/API configuration but permits delegated preview/rule; dirty-workspace.md allows exact-range review when coverage is complete; finding-fix-round.md records round, resolved/open findings, and commit range; ocr-timeout.md distinguishes bounded retry from escalation; and partial-preview.md compares Git paths against preview paths. Catch the literal typo restrto.

- [ ] Step 2: Run RED.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_scenario_contract.py -q

- [ ] Step 3: Update the prompt/scenario contracts.

Make report schema and state transitions executable in the text. Keep the implementer prompt short and require focused tests, commit, and report before host-owned broad verification. Require a fresh worker for every fix round, but make partial-commit recovery explicit. Do not add any suggestion to configure OPENAI_API_KEY, run ocr review, or use a common Codex review as fallback.

- [ ] Step 4: Run GREEN and contract scans.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_scenario_contract.py skills/sdd-cmdc-opencode/tests/test_skill_contract.py -q
    python -m pytest skills/sdd-cmdc-opencode/tests -q
    git diff --check

- [ ] Step 5: Commit and review.

    git add skills/sdd-cmdc-opencode
    git commit -m "docs: align prompts and pressure scenarios with contracts"

OCR review must include every changed prompt and scenario; unsupported Markdown paths must still be read manually and recorded as excluded if delegated preview cannot review them.

### Task 12: Reduce SKILL.md and make trigger/dependencies explicit

Files:
- Modify: skills/sdd-cmdc-opencode/SKILL.md.
- Create: skills/sdd-cmdc-opencode/references/workflow.md, review-governance.md, ledger-contract.md, windows-runtime.md, and failure-recovery.md.
- Modify: skills/sdd-cmdc-opencode/tests/test_skill_contract.py.
- Create: skills/sdd-cmdc-opencode/tests/test_reference_contract.py.

Interfaces:
- SKILL.md frontmatter contains only name and description.
- The description explicitly names approved implementation-plan execution, mostly independent/sequential tasks, Codex controller, Command Code implementer, mandatory delegated OCR, isolated branch/worktree, and exclusions for brainstorming, plan authoring, strongly coupled work, or missing dependencies.
- The body remains below 500 lines and names the exact reference to read for each stage.
- References are first-level only; any reference longer than 100 lines starts with a summary.

- [ ] Step 1: Write failing structure tests.

Assert frontmatter keys, trigger phrases and exclusions, body line count, first-level reference links, no duplicated full policy between body and references, summary presence for long references, consistent controller Codex/implementador Command Code terminology, and one dependency preflight containing Git, Python, authenticated Command Code, fixed model, OCR CLI, open-code-review-delegate, conditional Git Bash, and worktree support.

- [ ] Step 2: Run RED.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_reference_contract.py -q

Expected: current 765-line body and current frontmatter fail the size/trigger/reference assertions.

- [ ] Step 3: Move detail without changing behavior.

Keep in SKILL.md only trigger, global safety constraints, dependency preflight, task-loop outline, review gate, state summary, and reference-routing instructions. Move detailed workflow to workflow.md, review rules to review-governance.md, machine states/ledger schema to ledger-contract.md, Windows launcher/encoding/process details to windows-runtime.md, and recovery/report/cleanup details to failure-recovery.md. Remove duplicated DOT diagrams and repeated rationalizations. Do not move the preview/history document into the distributed skill package.

- [ ] Step 4: Run GREEN and inspect the rendered structure.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_reference_contract.py skills/sdd-cmdc-opencode/tests/test_skill_contract.py -q
    python -m pytest skills/sdd-cmdc-opencode/tests -q
    git diff --check

Expected: SKILL.md is below 500 lines, references are reachable in one hop, and existing mandatory review/no-fallback contracts remain present.

- [ ] Step 5: Commit and review.

    git add skills/sdd-cmdc-opencode
    git commit -m "refactor: apply progressive disclosure to sdd-cmdc-opencode"

The delegated review must read SKILL.md and every changed reference. A preview that excludes Markdown must be recorded as excluded rather than silently treated as covered.

### Task 13: Repair test architecture and add the deterministic P1 matrix

Files:
- Modify: skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py and test_skill_contract.py.
- Modify: skills/sdd-cmdc-opencode/tests/test_review_session.py.
- Create: skills/sdd-cmdc-opencode/tests/test_helpers.py, test_preflight_contract.py, test_report_contract.py, test_windows_process_contract.py, test_cleanup_workspace.py, test_state_contract.py, test_ledger.py, test_review_contract.py, test_recovery.py, test_scenario_contract.py, and test_reference_contract.py where not already created by earlier tasks.
- Create: skills/sdd-cmdc-opencode/tests/regression_cases/ with one fixture per confirmed incident, using redacted local data only.

Interfaces:
- Unit tests import implementation under skills/sdd-cmdc-opencode/scripts/, never the sibling skills/sdd-cmdc implementation.
- Contract tests inspect skill text and package structure only.
- Registry/integration tests remain separate from runtime unit tests.
- Regression tests execute local fixtures and never invoke external model/tool CLIs by default.

- [ ] Step 1: Write failing architecture guards.

Assert that test_cmdc_implementer.py loads skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py, no test relies on a clean global source worktree, digest equality is not required for files intentionally owned by this skill, fallback checks match semantic prohibitions rather than incidental sentences, and each P1-10 item has a named deterministic test.

- [ ] Step 2: Run RED against the current test organization.

    python -m pytest skills/sdd-cmdc-opencode/tests -q

Expected: the new import/digest/coverage guards identify known sibling import, digest coupling, global-worktree check, or missing deterministic cases before the architecture rewrite.

- [ ] Step 3: Refactor tests and add the minimum matrix.

Remove the sibling implementation import and byte-digest coupling where the opencode skill intentionally diverges. Replace substring-only assertions with parsed paragraphs/sections and behavior checks. Isolate registry tests. Add deterministic tests for: trusted cmdc resolution; .cmd/.ps1/Unicode paths; UTF-8 streams; timeout and child termination; prompt invalidity; max-turns; report lifecycle; every blocker code; same-basename workspace identity; ledger isolation; fenced-heading extraction; atomic review packages; non-ancestor BASE; manifest/preview divergence; cleanup danger paths; CRLF; generated artifacts; frontmatter/references; fallback prohibition; and state transitions.

- [ ] Step 4: Run the complete no-token verification matrix.

    python -m compileall -q skills/sdd-cmdc-opencode/scripts skills/sdd-cmdc-opencode/tests
    python -m pytest skills/sdd-cmdc-opencode/tests -q
    python -m pytest skills/sdd-cmdc/tests -q
    git diff --check

Expected: every test is deterministic and no test starts Command Code, Codex, OCR, or a network client.

- [ ] Step 5: Commit and review.

    git add skills/sdd-cmdc-opencode
    git commit -m "test: harden deterministic sdd-cmdc-opencode coverage"

The review must include the tests themselves; a green suite is not evidence that an unrelated implementation was imported.

### Task 14: Reevaluate audit evidence and protect sensitive process data

Files:
- Modify or move out of runtime packaging: skills/sdd-cmdc-opencode/audit_result.json; preserve historical evidence outside the distributed runtime if retained.
- Modify: skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py, review-session.py, report_contract.py, and ledger.py.
- Modify: SKILL.md or references/failure-recovery.md with environment/redaction policy.
- Create: skills/sdd-cmdc-opencode/tests/test_sensitive_data_contract.py.

Interfaces:
- Define build_child_environment(parent: Mapping[str, str]) -> dict[str, str] with an explicit allowlist/denylist policy that preserves Command Code authentication variables without copying unrelated secrets.
- Define redact_sensitive(text: str) -> str and apply it before stderr, report, checkpoint, or ledger persistence.
- Define audit_overlap_report(...) only as an analysis artifact; it cannot produce runtime approval by itself.

- [ ] Step 1: Write failing secret/audit tests.

Test redaction of bearer tokens, API-key-shaped values, passwords, connection strings, and .env content; preservation of the fixed model/authentication path; absence of secret values in report/checkpoint/ledger strings; and rejection of audit_result.json as sole quality evidence. Test semantic overlap review against sdd-cmdc, executing-plans, subagent-driven-development, worktree/review/verification skills and record the actual differential responsibility.

- [ ] Step 2: Run RED.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_sensitive_data_contract.py -q

- [ ] Step 3: Implement data policy and audit disposition.

Pass only the environment needed for Command Code and explicitly document any required authentication variables. Redact before writing or rendering every persisted operational artifact. Move historical audit data out of the runtime package if it cannot be recomputed and semantically reviewed; do not claim APPROVED from a stale overlap result. Document that Command Code implements, delegated OCR reviews, and Codex coordinates.

- [ ] Step 4: Run GREEN and inspect generated evidence.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_sensitive_data_contract.py skills/sdd-cmdc-opencode/tests -q
    git diff --check

Use only synthetic secrets in fixtures and verify they do not occur in any generated ignored report/checkpoint.

- [ ] Step 5: Commit and review.

    git add skills/sdd-cmdc-opencode
    git commit -m "fix: redact sensitive runtime evidence and qualify audit results"

### Task 15: Add P2 interface metadata, stable language, and dependency versions

Files:
- Create: skills/sdd-cmdc-opencode/agents/openai.yaml.
- Modify: skills/sdd-cmdc-opencode/SKILL.md and first-level references.
- Modify: skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py preflight version snapshot.
- Create: skills/sdd-cmdc-opencode/tests/test_metadata_contract.py.

Interfaces:
- agents/openai.yaml contains display_name, short_description, and default_prompt consistent with final frontmatter and no executable model/API configuration.
- Preflight reports Python, Git, Command Code, OCR CLI, and delegate skill versions without pinning them.

- [ ] Step 1: Write failing metadata/version tests.

Validate YAML keys and text consistency, machine-language stability, no executable LLM configuration, and deterministic version capture with fake command outputs.

- [ ] Step 2: Run RED.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_metadata_contract.py -q

- [ ] Step 3: Add metadata and version evidence.

Generate interface metadata from final skill wording. Add version commands to preflight with bounded, redacted output and preserve the rule that versions are recorded for correlation but not pinned without a reproduced incompatibility.

- [ ] Step 4: Run GREEN and package checks.

    python -m pytest skills/sdd-cmdc-opencode/tests/test_metadata_contract.py skills/sdd-cmdc-opencode/tests -q
    python -m pytest skills/sdd-cmdc/tests -q
    git diff --check

- [ ] Step 5: Commit and review.

    git add skills/sdd-cmdc-opencode
    git commit -m "feat: add skill metadata and runtime version evidence"

### Task 16: Validate the final package and perform the controlled real-use gate

Files:
- Modify: skills/sdd-cmdc-opencode/tests/test_package_contract.py and final package manifest tests.
- Modify: this plan only if an implementation decision changes the recorded contract; do not copy this plan into the distributed skill.
- Create: an ignored final validation report under the plan workspace resolved by scripts/sdd_workspace.py.

Interfaces:
- Final validation consumes the exact package manifest, test results, state/ledger evidence, review manifests, and a controlled real-task report.
- The real-use gate runs only in a trusted, reversible branch/worktree selected explicitly by the controller; it must not run on the skill repository master or on a deployed server.

- [ ] Step 1: Run the complete local release matrix.

    python -m compileall -q skills/sdd-cmdc-opencode/scripts skills/sdd-cmdc-opencode/tests
    python -m pytest skills/sdd-cmdc-opencode/tests -q
    python -m pytest skills/sdd-cmdc/tests -q
    git diff --check
    git status --short
    git ls-files skills/sdd-cmdc-opencode | Select-String -Pattern '__pycache__|\.pyc$|\.pytest_cache'

Expected: both suites pass; git diff --check is silent; the generated-artifact query returns no tracked files; the package manifest contains all required sources and no runtime cache.

- [ ] Step 2: Verify all general acceptance criteria.

Check every item from preview.md section 12: no CRLF Bash, no generated payload, complete sources, no local cmdc hijack, Unicode/space paths, UTF-8 stdin/stdout/stderr, structured failures, stale/empty/invalid report rejection, unique workspaces, atomic writes, restricted cleanup, coherent states, explicit Medium/Minor/deferred/load-bearing decisions, identical Git/package/OCR path sets, no approval from partial review, correct test imports, semantic fallback checks, no external calls in deterministic tests, concise skill/reference routing, explicit trigger/dependencies, no Claude/WSL2/API-key requirement, preserved user changes, and reversible first use.

- [ ] Step 3: Run the controlled real-use gate.

Use a small reversible task in a trusted project worktree only after the controller records project, branch, initial HEAD, initial status, plan identity, tool versions, and authorization. Run the implementer with the fixed model and explicit report path, reconcile the resulting commit/report/ledger, build the exact review package, run delegated preview/rule, and verify that the final state is REVIEW_CLEAN or COMPLETE_WITH_DEFERRED according to the recorded finding decision. Do not publish or merge as part of this task.

- [ ] Step 4: Record the final decision and stop at the release gate.

The final report must list every P0/P1/P2 item as implemented, deferred, or blocked with evidence. If any P0 or load-bearing P1 remains open, record PLAN_BLOCKED; do not call the package complete. If the local package is ready but a real-use authorization or target is missing, record the package as ready for controlled use and stop without inventing authorization.

## Acceptance Mapping

| Preview item | Plan task | Completion evidence |
| --- | --- | --- |
| P0-01 line endings/platform | 1 | LF tests, .gitattributes, bash -n, UTF-8 checks |
| P0-02 YOLO boundary | 2 | preflight tests, branch/status snapshot, explicit consent |
| P0-03 cmdc hijacking | 3 | resolver candidate tests and resolved-path evidence |
| P0-04 structured input/failures | 4 | blocker-code and redaction matrix |
| P0-05 report freshness/validity | 4 | stale/empty/invalid/change/schema tests |
| P0-06 Windows subprocesses | 5 | launcher, encoding, timeout, tree-cleanup tests |
| P0-07 cleanup safety | 6 | dangerous-target rejection and recoverable cleanup tests |
| P0-08 state machine | 7 | transition table and ledger validation |
| P0-09 scenarios | 11 | five scenario contract tests |
| P0-10 package composition | 1 and 16 | manifest/source/cache validation |
| P1-01 frontmatter | 12 | parsed frontmatter/trigger tests |
| P1-02 progressive disclosure | 12 | body size/reference routing tests |
| P1-03 terminology/dependencies | 11 and 12 | terminology and preflight contract tests |
| P1-04 unique workspace | 8 | same-basename/hash identity tests |
| P1-05 atomic helpers/ledger | 7 and 8 | injected-failure atomicity tests |
| P1-06 implementer prompt | 4 and 11 | explicit report/context/status tests |
| P1-07 measurable delegated review | 9 | manifest/preview/rule equality tests |
| P1-08 idempotent retries/locks | 10 | partial-commit/active-lock/stale-lock tests |
| P1-09 test architecture | 13 | correct imports, no digest/global-state coupling |
| P1-10 deterministic minimum | 13 | complete no-token matrix |
| P1-11 audit artifact | 14 | qualified/remediated audit evidence |
| P1-12 secrets | 14 | environment and redaction tests |
| P2-01 interface metadata | 15 | agents/openai.yaml contract |
| P2-02 language/contracts | 11, 12, 15 | stable machine tokens and parsed docs |
| P2-03 rationalizations/examples | 12 | concise body and reference routing |
| P2-04 dependency versions | 15 | preflight version snapshot |

## Self-Review

- Spec coverage: every P0, P1, P2 item and each of the five recommended implementation phases has a named task and acceptance evidence in the mapping above.
- Scope check: the preview spans runtime safety, state/recovery, package structure, documentation, tests, and metadata. They are separated into independently reviewable tasks with explicit commit/review gates; no task requires a hidden cross-task edit.
- Placeholder scan: every task names files, interfaces, test commands, expected outcomes, and commit messages; no step relies on an unspecified implementation action.
- Type consistency: ReportSnapshot, validate_report, WorkspaceIdentity, ReviewManifest, LedgerEntry, validate_transition, reconcile_before_retry, ExecutionLock, build_child_environment, and redact_sensitive are defined once and reused by later tasks with the same names and argument shapes.
- Rollback: each task is one commit from a recorded BASE. A failed task remains in its own branch state for inspection; no reset or deletion is part of recovery. The previous stable branch remains feat/sdd-cmdc-opencode-issue-131 at fc8522b.

## Definition of Done

The preview implementation is complete only when all P0 items, all P1 items in the acceptance mapping, and the P2 metadata/clarity items have passing deterministic evidence; every task range has a clean delegated review; the final package has no generated payload; and a controlled real task has produced a new valid report, correct commit/range, complete preview/rule/diff coverage, coherent review status, recoverable ledger, and no out-of-scope changes. Until those conditions hold, the final state is PLAN_BLOCKED or an explicitly named intermediate state, never approval by timeout or by a green broad suite alone.
