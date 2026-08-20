# SDD Command Code Process and Launcher Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give implementation and review one reliable process lifecycle, remove WMIC/process-ancestry cleanup, and isolate local Command Code discovery and NDJSON handling behind a deep `cmdc-local` Module without breaking either existing CLI.

**Architecture:** Add two public Modules under `scripts/sdd_cmdc_opencode`: `process_supervisor` owns spawn, streaming, timeout, termination, drain, and cleanup proof; `cmdc_local` owns the installed Command Code launcher, commands, smoke, Session ID, and NDJSON translation. Windows containment is private Implementation built around a Job Object and a blocked bootstrap process. `cmdc-implementer.py` and `review-session.py` remain compatibility Adapters and delegate to these Modules.

**Tech Stack:** Python 3 standard library, `ctypes` Win32 Job Objects, POSIX process groups, pytest, local Command Code 1.28-compatible NDJSON.

## Global Constraints

- Execute this plan before `2026-08-19-sdd-cmdc-opencode-resumable-run.md`; Delivery 2 depends on the Interfaces defined here.
- Work only in the isolated feature worktree and preserve unrelated changes. Do not reset, clean, merge, push, publish, close issues, or overwrite `.agents`/`.codex` installations.
- Run tests from `skills/sdd-cmdc-opencode`; run `skills/sdd-cmdc/tests` separately from its own directory to avoid `tests.*` import collisions.
- Keep `deepseek/deepseek-v4-flash`, `--no-skills`, `--trust`, `--skip-onboarding`, and explicit `--yolo` consent unchanged.
- Keep local Command Code as the only implementation Adapter. Do not add `backends/base.py`, `ProviderHarnessBackend`, proxy fallback, API-key fallback, or a generic backend protocol.
- Keep the existing positional/flat CLIs and textual output stable while the Adapters begin delegating internally.
- A successful child exit is not sufficient: final stream drain and an empty contained process tree are required.
- Preserve the first causal failure as `primary_failure`; append termination, drain, cleanup, or persistence failures as `secondary_failures`.
- No production path may call `wmic`, CIM process ancestry, or `tasklist` to prove cleanup. Windows Job Object accounting is authoritative.
- Use argument arrays with `shell=False`. Wrapper normalization may invoke `.cmd`/`.bat` through `COMSPEC /d /s /c` and `.ps1` through PowerShell `-File`; never interpolate a shell command string.
- The real launcher smoke is a separate local capability gate. Deterministic unit/integration tests must not require network access, authentication, or model output.

## Open-Issue Traceability

- [`Inova#171`](https://github.com/victorbernardi/Inova/issues/171), “fail fast and clean up Windows launcher failures”: Tasks 1–4 separate resolution/spawn/runtime/cleanup causes, establish containment before target work, and prove an empty Job Object.
- [`Inova#169`](https://github.com/victorbernardi/Inova/issues/169), “harden Windows task/report path handling”: Task 3 centralizes launcher/wrapper argument arrays; the remaining task/report parsing acceptance is completed in Delivery 2.
- This delivery does not close either issue. Closure requires the later Run gates, complete verification, review, integration/publication, and explicit issue reconciliation.

---

## File Structure and Stable Interfaces

Create this structure during Delivery 1:

```text
skills/sdd-cmdc-opencode/
  scripts/
    cmdc-implementer.py                         compatibility Adapter
    review-session.py                          compatibility Adapter
    sdd_cmdc_opencode/
      __init__.py                              public exports
      process_supervisor.py                    deep process lifecycle Module
      cmdc_local.py                            deep local Command Code Module
      _windows_job.py                          private Job Object Implementation
      _job_bootstrap.py                        private blocked child bootstrap
      _mod_probe.ts                            private Command Code hook probe
  tests/
    conftest.py                                adds scripts/ to test import path
    helpers/
      __init__.py
      fake_cmdc.py                             deterministic NDJSON executable
      process_tree.py                          child/grandchild fixture
    test_process_supervisor.py
    test_cmdc_local.py
```

`process_supervisor.py` exposes exactly these public value types and operation:

```python
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Literal


class ProcessStatus(str, Enum):
    EXITED = "EXITED"
    SPAWN_FAILED = "SPAWN_FAILED"
    WALL_TIMEOUT = "WALL_TIMEOUT"
    STALLED = "STALLED"
    INTERRUPTED = "INTERRUPTED"


@dataclass(frozen=True)
class ProcessFailure:
    code: str
    phase: str
    message: str


@dataclass(frozen=True)
class ProcessRequest:
    command: tuple[str, ...]
    cwd: Path
    stdin_text: str = ""
    wall_timeout_seconds: float = 0
    stall_timeout_seconds: float = 0
    env: Mapping[str, str] | None = None


@dataclass(frozen=True)
class StreamEvent:
    stream: Literal["stdout", "stderr"]
    text: str
    elapsed_seconds: float


@dataclass(frozen=True)
class ProcessOutcome:
    pid: int | None
    returncode: int | None
    stdout: str
    stderr: str
    status: ProcessStatus
    containment: str
    cleanup_verified: bool
    drain_verified: bool
    primary_failure: ProcessFailure | None
    secondary_failures: tuple[ProcessFailure, ...]


def run_process(
    request: ProcessRequest,
    *,
    on_output: Callable[[StreamEvent], None] | None = None,
    activity_clock: Callable[[], float] | None = None,
) -> ProcessOutcome:
    """Run one contained process and return only after drain and cleanup proof."""
```

`cmdc_local.py` exposes one concrete local Adapter, not a base class:

```python
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from .process_supervisor import ProcessOutcome


@dataclass(frozen=True)
class CmdcEvent:
    type: str
    session_id: str | None = None
    turn_number: int | None = None
    tool: str | None = None
    command: str | None = None
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    raw: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class CmdcRequest:
    cwd: Path
    prompt: str
    max_turns: int
    allow_yolo: bool
    wall_timeout_seconds: float
    stall_timeout_seconds: float
    mod_path: Path | None = None
    env: Mapping[str, str] | None = None


@dataclass(frozen=True)
class CmdcOutcome:
    process: ProcessOutcome
    subtype: str | None
    stop_reason: str | None
    session_id: str | None
    final_text: str
    events: tuple[CmdcEvent, ...]


@dataclass(frozen=True)
class CmdcPreflight:
    launcher: Path
    command: tuple[str, ...]
    smoke: CmdcOutcome
    mod_hook_verified: bool
```

`CmdcLocal` exposes these concrete method signatures:

```text
CmdcLocal(cmd_bin: str = "cmdc")
CmdcLocal.resolve_launcher() -> Path
CmdcLocal.build_start_command(request: CmdcRequest) -> tuple[str, ...]
CmdcLocal.build_resume_command(session_id: str, request: CmdcRequest) -> tuple[str, ...]
CmdcLocal.smoke_test(cwd: Path, require_mod_hook: bool) -> CmdcPreflight
CmdcLocal.start(request: CmdcRequest) -> CmdcOutcome
CmdcLocal.resume(session_id: str, request: CmdcRequest) -> CmdcOutcome
```

---

### Task 1: Add the package and shared process supervisor

**Files:**
- Create: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/__init__.py`
- Create: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/process_supervisor.py`
- Create: `skills/sdd-cmdc-opencode/tests/conftest.py`
- Create: `skills/sdd-cmdc-opencode/tests/helpers/__init__.py`
- Create: `skills/sdd-cmdc-opencode/tests/helpers/process_tree.py`
- Create: `skills/sdd-cmdc-opencode/tests/test_process_supervisor.py`

**Interfaces:** Use the exact `ProcessStatus`, `ProcessFailure`, `ProcessRequest`, `StreamEvent`, `ProcessOutcome`, and `run_process` Interface above. Private functions may change without callers importing them.

- [ ] **Step 1: Make package imports fail for the new Interface**

  Add `tests/conftest.py` with the skill-local import path:

  ```python
  from __future__ import annotations

  import sys
  from pathlib import Path

  SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
  if str(SCRIPTS) not in sys.path:
      sys.path.insert(0, str(SCRIPTS))
  ```

  Start `test_process_supervisor.py` with the frozen-value assertion:

  ```python
  from __future__ import annotations

  import sys
  from dataclasses import FrozenInstanceError
  from pathlib import Path

  import pytest


  def test_process_request_is_immutable(tmp_path: Path) -> None:
      from sdd_cmdc_opencode.process_supervisor import ProcessRequest

      request = ProcessRequest(command=(sys.executable, "-V"), cwd=tmp_path)
      with pytest.raises(FrozenInstanceError):
          request.cwd = tmp_path.parent  # type: ignore[misc]
  ```

  Run `python -m pytest tests/test_process_supervisor.py -q`. Expected RED: `ModuleNotFoundError: No module named 'sdd_cmdc_opencode'`.

- [ ] **Step 2: Add the stable value types and package exports**

  Create the Interface exactly as specified and export only the public names from `__init__.py`. Do not export `_windows_job`, `_job_bootstrap`, stream-thread helpers, or platform launch helpers.

  Run `python -m pytest tests/test_process_supervisor.py -q`. The import/frozen test must pass before process behavior is added.

- [ ] **Step 3: Add RED tests for normal exit, streaming, spawn failure, wall timeout, and stall**

  Use `sys.executable` and argument arrays. The fixture process must print one stdout line and one stderr line, flush both, optionally wait, and optionally create descendants. Assert:

  ```python
  assert outcome.status is ProcessStatus.EXITED
  assert outcome.returncode == 0
  assert outcome.stdout == "out-one\n"
  assert outcome.stderr == "err-one\n"
  assert [event.stream for event in seen] == ["stdout", "stderr"]
  assert outcome.drain_verified is True
  assert outcome.cleanup_verified is True
  assert outcome.primary_failure is None
  ```

  For a missing executable, assert `SPAWN_FAILED`, `PROCESS_SPAWN_FAILED`, `pid is None`, and no cleanup failure. For wall timeout and stall, assert the precise status/code and that output already emitted remains present.

  Run `python -m pytest tests/test_process_supervisor.py -q`. Expected RED: `run_process` is absent or does not satisfy the behavior.

- [ ] **Step 4: Implement the cross-platform supervisor core and POSIX containment**

  Implement `Popen` with text UTF-8 replacement, one reader thread per stream, monotonic deadlines, and `start_new_session=True` on POSIX. A single supervision loop must:

  1. dispatch `StreamEvent` without swallowing callback exceptions;
  2. refresh output activity internally and combine it with `activity_clock` when supplied;
  3. set the first causal timeout/stall/interruption as primary;
  4. terminate the process group with `SIGTERM`, escalate to `SIGKILL` after a bounded grace period, then join readers;
  5. verify the captured process group has no live members;
  6. append drain or cleanup failures as secondary.

  Normal exit must also join readers and prove the group is empty. Do not use leader exit as cleanup proof.

- [ ] **Step 5: Run focused tests and commit the portable slice**

  Run:

  ```powershell
  python -m pytest tests/test_process_supervisor.py -q -k "not windows_job"
  python -m py_compile scripts/sdd_cmdc_opencode/process_supervisor.py
  ```

  Expected GREEN: portable tests pass; the native Windows Job test remains absent or skipped until Task 2.

  From the worktree root, stage the six Task 1 paths explicitly and commit:

  ```powershell
  git add skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/__init__.py skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/process_supervisor.py skills/sdd-cmdc-opencode/tests/conftest.py skills/sdd-cmdc-opencode/tests/helpers/__init__.py skills/sdd-cmdc-opencode/tests/helpers/process_tree.py skills/sdd-cmdc-opencode/tests/test_process_supervisor.py
  git commit -m "refactor: add shared process supervisor"
  ```

---

### Task 2: Contain native Windows trees with a Job Object before useful work

**Files:**
- Create: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/_windows_job.py`
- Create: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/_job_bootstrap.py`
- Modify: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/process_supervisor.py`
- Modify: `skills/sdd-cmdc-opencode/tests/helpers/process_tree.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_process_supervisor.py`

**Interfaces:** Keep the public Interface unchanged. `_windows_job.Job` is private and owns `CreateJobObjectW`, `SetInformationJobObject`, `AssignProcessToJobObject`, `TerminateJobObject`, `QueryInformationJobObject`, and handle closure.

- [ ] **Step 1: Write the native child/grandchild RED test**

  Make `tests/helpers/process_tree.py` start a child that starts a grandchild, writes all three PIDs to a JSON file, prints a final flushed line, and blocks. On native Windows, run it with a short wall timeout and assert:

  ```python
  assert outcome.status is ProcessStatus.WALL_TIMEOUT
  assert outcome.containment == "windows-job"
  assert outcome.cleanup_verified is True
  assert outcome.drain_verified is True
  assert "grandchild-ready" in outcome.stdout
  assert all(not windows_pid_exists(pid) for pid in recorded_pids)
  ```

  The test helper may use `OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)` plus `GetExitCodeProcess`; production code must use Job Object accounting.

  Run `python -m pytest tests/test_process_supervisor.py -q -k windows_job`. Expected RED: containment is not `windows-job` or a descendant survives.

- [ ] **Step 2: Implement the private Job Object wrapper**

  Define the required Win32 structures with `ctypes`, set `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, and make every API failure raise a private exception carrying `ctypes.get_last_error()`. `Job.active_processes()` must return `ActiveProcesses` from `JOBOBJECT_BASIC_ACCOUNTING_INFORMATION`; an API error is not equivalent to zero.

  Use a context manager that does not close the handle until cleanup was verified. `terminate(exit_code)` calls `TerminateJobObject`; `close()` is idempotent.

- [ ] **Step 3: Implement the blocked bootstrap handshake**

  `_job_bootstrap.py` must start no target until it reads exactly `SDD_CMDC_GO\n`. The parent sequence is fixed:

  1. spawn the Python bootstrap with pipes and the target argument array after `--`;
  2. assign the bootstrap PID to the Job Object;
  3. write only the GO line and flush;
  4. wait for a structured `target_spawned` bootstrap event;
  5. write the requested stdin and close the input pipe.

  The bootstrap starts the target with its own stdin stream and inherited stdout/stderr pipes, emits one JSON sentinel containing the target PID, then waits and returns the target exit code. A target spawn error emits a `target_spawn_failed` sentinel and exits `127`.

  If Job assignment fails, terminate the still-blocked bootstrap before GO and return primary `PROCESS_JOB_ASSIGNMENT_FAILED`; no target may have started.

- [ ] **Step 4: Wire Job accounting into every Windows outcome**

  On timeout/stall/interruption, call `TerminateJobObject`, wait for `active_processes() == 0`, join stream readers, then close the job. On normal exit, still require `active_processes() == 0`. Map unverifiable accounting to `PROCESS_CLEANUP_UNVERIFIABLE` and a non-empty job after bounded termination to `PROCESS_TREE_TERMINATION_FAILED`.

  Preserve the runtime timeout/stall as primary when cleanup also fails. Use cleanup as primary only when no earlier failure exists.

- [ ] **Step 5: Prove native Windows behavior and the absence of ancestry tools**

  Run:

  ```powershell
  python -m pytest tests/test_process_supervisor.py -q
  rg -n -i "wmic|Get-CimInstance|tasklist" scripts/sdd_cmdc_opencode scripts/cmdc-implementer.py scripts/review-session.py
  ```

  Expected GREEN: process tests pass. The `rg` command may still find legacy Adapter code before Task 4, but it must find nothing in `scripts/sdd_cmdc_opencode`.

- [ ] **Step 6: Commit the Windows containment slice**

  Stage only Task 2 files and commit:

  ```powershell
  git add skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/_windows_job.py skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/_job_bootstrap.py skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/process_supervisor.py skills/sdd-cmdc-opencode/tests/helpers/process_tree.py skills/sdd-cmdc-opencode/tests/test_process_supervisor.py
  git commit -m "fix: contain windows process trees with job objects"
  ```

---

### Task 3: Extract the concrete local Command Code Module

**Files:**
- Create: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/cmdc_local.py`
- Create: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/_mod_probe.ts`
- Create: `skills/sdd-cmdc-opencode/tests/helpers/fake_cmdc.py`
- Create: `skills/sdd-cmdc-opencode/tests/test_cmdc_local.py`
- Modify: `skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/__init__.py`

**Interfaces:** Use the concrete `CmdcEvent`, `CmdcRequest`, `CmdcOutcome`, `CmdcPreflight`, and `CmdcLocal` Interface above. No inheritance or backend registry is permitted.

- [ ] **Step 1: Write launcher and command-construction RED tests**

  Cover direct executable, `.ps1`, `.cmd`, `.bat`, `.exe`, the package-declared Node `bin` entry, native `cmd.exe` rejection, unsupported suffix, and missing launcher. Assert the logical start arguments in order:

  ```python
  assert command[1:] == (
      "-p",
      "--model", "deepseek/deepseek-v4-flash",
      "--max-turns", "12",
      "--output-format", "json",
      "--no-skills",
      "--trust",
      "--skip-onboarding",
  )
  ```

  Assert `--yolo` appears only with `allow_yolo=True`; `--mod ABSOLUTE_PATH` appears only when a validated Mod path is present. Assert resume contains `-p --resume session-123` and never `--continue`.

  Run `python -m pytest tests/test_cmdc_local.py -q -k "launcher or command or resume"`. Expected RED: the Module does not exist.

- [ ] **Step 2: Implement launcher discovery and wrapper normalization**

  Resolve explicit files first, then `PATH`, then the Windows npm directory. Reject Windows `System32\cmd.exe`. For an npm JavaScript wrapper, read its adjacent package metadata and use the declared `bin` entry; do not hard-code `dist/index.mjs` when metadata supplies another entry.

  Convert logical commands into platform argument arrays in this Module. Return `LAUNCHER_NOT_FOUND` and `LAUNCHER_UNSUPPORTED` only from resolution/normalization; never use those codes for spawn, runtime, or cleanup exceptions.

- [ ] **Step 3: Add deterministic NDJSON RED tests**

  `tests/helpers/fake_cmdc.py` must accept the relevant flags and emit one JSON object per line. Cover:

  ```jsonl
  {"type":"event","event":{"type":"assistant_progress","turnNumber":1}}
  {"type":"result","subtype":"success","sessionId":"session-123","stopReason":"end_turn","result":"done"}
  ```

  Add variants for `subtype: "error"`, `subtype: "max_turns"`, malformed JSON between valid events, result without Session ID, stderr, stall, and resume. Assert raw objects are retained, final fields are normalized, and a malformed protocol produces `CMD_CODE_PROTOCOL_ERROR` without disguising process cleanup evidence.

  Run `python -m pytest tests/test_cmdc_local.py -q -k "ndjson or session or protocol"`. Expected RED until parsing and process integration exist.

- [ ] **Step 4: Implement NDJSON translation and concrete start/resume**

  Feed the command through `run_process`, parse complete stdout lines, preserve unknown event shapes in `CmdcEvent.raw`, and require exactly one terminal result. Capture `sessionId`, `subtype`, `stopReason`, and final result text from the terminal object. If the process fails before a valid terminal object, retain the process failure as primary and append protocol diagnostics secondarily; if the process exits cleanly with invalid NDJSON, make `CMD_CODE_PROTOCOL_ERROR` primary.

- [ ] **Step 5: Add fake and opt-in real smoke coverage**

  The fake smoke creates a disposable Git repository, verifies `--output-format json`, a bounded turn count, and no surviving process. `_mod_probe.ts` registers `beforeToolCall` and blocks a harmless sentinel shell request with the marker `SDD_CMDC_MOD_HOOK_OK`; `smoke_test(cwd, require_mod_hook=True)` succeeds only if the emitted event proves the hook fired.

  Add an opt-in local test skipped unless `SDD_CMDC_REAL_SMOKE=1`. It uses the installed launcher in a temporary Git repository, a maximum of two turns, the packaged Mod probe, and asserts Session ID, hook evidence, `cleanup_verified`, and `drain_verified`.

  Run deterministic tests:

  ```powershell
  python -m pytest tests/test_cmdc_local.py -q -k "not real_launcher_smoke"
  ```

  Then run the real gate only when authentication and local execution are available:

  ```powershell
  $env:SDD_CMDC_REAL_SMOKE = "1"
  python -m pytest tests/test_cmdc_local.py -q -k real_launcher_smoke
  Remove-Item Env:SDD_CMDC_REAL_SMOKE
  ```

  A skipped real gate is reported separately; it does not turn deterministic tests into an operational smoke success.

- [ ] **Step 6: Commit the `cmdc-local` slice**

  Stage only Task 3 files and commit:

  ```powershell
  git add skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/cmdc_local.py skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/_mod_probe.ts skills/sdd-cmdc-opencode/scripts/sdd_cmdc_opencode/__init__.py skills/sdd-cmdc-opencode/tests/helpers/fake_cmdc.py skills/sdd-cmdc-opencode/tests/test_cmdc_local.py
  git commit -m "refactor: isolate local command code protocol"
  ```

---

### Task 4: Migrate both compatibility Adapters to the shared Modules

**Files:**
- Modify: `skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py`
- Modify: `skills/sdd-cmdc-opencode/scripts/review-session.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_review_session.py`

**Interfaces:** Existing public functions and CLIs remain callable. New code imports `CmdcLocal` and `run_process`; tests assert Adapter output, not former private process helpers.

- [ ] **Step 1: Add compatibility characterization tests before deletion**

  Pin the current success, `BLOCKED`, `REVIEW INCOMPLETE`, timeout exit `124`, initial Git snapshot, command rendering, stdout/stderr evidence, and report validation outputs. Replace monkeypatches of `_terminate_process_tree`, `_windows_parent_pid`, `_windows_process_parents`, or `_process_tree_alive` with fake `ProcessOutcome` objects at the Module Interface.

  Run:

  ```powershell
  python -m pytest tests/test_cmdc_implementer.py tests/test_review_session.py -q -k "process or timeout or cleanup or launcher"
  ```

  Expected GREEN before migration. These are compatibility guards, not new behavior.

- [ ] **Step 2: Route implementation through `CmdcLocal`**

  Replace launcher resolution, platform command construction, stream threads, process-tree termination, and NDJSON/session parsing in `cmdc-implementer.py` with the concrete Module. Keep higher Run policy in the Adapter until Delivery 2. Map structured failures to the existing text fields without a broad `except FileNotFoundError` around execution.

  Add a regression where cleanup raises after a valid spawn; assert `BLOCKER_CODE` is a cleanup code, never `CMD_NOT_FOUND`/`LAUNCHER_NOT_FOUND`.

- [ ] **Step 3: Route clean-host review through `run_process`**

  Replace `review-session.py` process creation, timeout, CIM/tasklist inventory, tree termination, and drain logic with `ProcessRequest`/`ProcessOutcome`. Keep Codex launcher resolution, review environment scrubbing, evidence files, legacy positional arguments, and report classification unchanged.

  Map wall timeout plus verified cleanup to exit `124`/`REVIEW INCOMPLETE`; map unverifiable or failed cleanup to the existing fail-closed review exit and include the precise process failure code.

- [ ] **Step 4: Delete duplicate private process code and prove no forbidden inventory remains**

  Delete the duplicated stream readers, `_terminate_process_tree`/`_terminate_tree`, Windows parent/tree capture, POSIX group capture, tasklist/CIM checks, and related globals from both Adapters. Do not leave unused compatibility copies.

  Run:

  ```powershell
  rg -n -i "wmic|Get-CimInstance|tasklist" scripts/sdd_cmdc_opencode scripts/cmdc-implementer.py scripts/review-session.py
  ```

  Expected result: exit `1` with no matches.

- [ ] **Step 5: Run Adapter and process regression suites**

  Run:

  ```powershell
  python -m pytest tests/test_process_supervisor.py tests/test_cmdc_local.py tests/test_cmdc_implementer.py tests/test_review_session.py -q
  ```

  Expected GREEN. Confirm `git diff --check` and inspect `git diff --stat` before committing.

- [ ] **Step 6: Commit the compatibility migration**

  Stage only the four Adapter/test files and commit:

  ```powershell
  git add skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py skills/sdd-cmdc-opencode/scripts/review-session.py skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py skills/sdd-cmdc-opencode/tests/test_review_session.py
  git commit -m "refactor: share process lifecycle across cmdc and review"
  ```

---

### Task 5: Document and verify Delivery 1 as an independently shippable cut

**Files:**
- Modify: `skills/sdd-cmdc-opencode/SKILL.md`
- Modify: `skills/sdd-cmdc-opencode/tests/test_skill_contract.py`
- Modify: `skills/sdd-cmdc-opencode/tests/test_package_contract.py`

**Interfaces:** Documentation names the two new Modules, the real smoke gate, precise failure phases, and verified cleanup. It does not advertise Delivery 2 `start/resume` contracts before they exist.

- [ ] **Step 1: Add RED contract and package assertions**

  Assert that `SKILL.md` documents `process_supervisor`, `cmdc-local`, Job Object cleanup proof, and separate launcher/spawn/runtime/cleanup failures. Assert all new package files are tracked, LF-only, and no generated `__pycache__`, `.pytest_cache`, smoke repository, or event artifact is tracked.

  Run `python -m pytest tests/test_skill_contract.py tests/test_package_contract.py -q`. Expected RED until documentation/package expectations are updated.

- [ ] **Step 2: Update the operational documentation**

  Document that both implementation and clean-host review use one process supervisor, Windows cleanup uses Job Objects, and a real local smoke is distinct from deterministic tests. Keep all existing protected-branch, deployed-path, plan-file, OCR-only, and explicit-yolo gates.

- [ ] **Step 3: Run Delivery 1 focused and complete source gates**

  From `skills/sdd-cmdc-opencode`:

  ```powershell
  python -m pytest tests/test_process_supervisor.py tests/test_cmdc_local.py tests/test_cmdc_implementer.py tests/test_review_session.py -q
  python -m pytest -q
  python -m py_compile scripts/cmdc-implementer.py scripts/review-session.py scripts/sdd_cmdc_opencode/process_supervisor.py scripts/sdd_cmdc_opencode/cmdc_local.py scripts/sdd_cmdc_opencode/_windows_job.py scripts/sdd_cmdc_opencode/_job_bootstrap.py
  ```

  From `skills/sdd-cmdc` in a separate command:

  ```powershell
  python -m pytest -q
  ```

  Record exact pass/skip counts independently. Do not combine them into one pytest collection.

- [ ] **Step 4: Run repository and parity audits**

  From the worktree root:

  ```powershell
  git diff --check
  git status --short
  git diff --name-only origin/master...HEAD
  python skills/sdd-cmdc-opencode/scripts/verify-install-parity.py skills/sdd-cmdc-opencode C:\Users\victor.bernardi\.agents\skills\sdd-cmdc-opencode C:\Users\victor.bernardi\.codex\skills\sdd-cmdc-opencode
  ```

  Parity drift is a separate publication blocker and must not trigger an overwrite.

- [ ] **Step 5: Commit Delivery 1 documentation**

  Stage only Task 5 paths and commit:

  ```powershell
  git add skills/sdd-cmdc-opencode/SKILL.md skills/sdd-cmdc-opencode/tests/test_skill_contract.py skills/sdd-cmdc-opencode/tests/test_package_contract.py
  git commit -m "docs: define cmdc process reliability gates"
  ```

## Delivery 1 Acceptance Gate

Delivery 1 is complete only when all statements are evidenced:

- implementation and clean-host review call the same `run_process` Interface;
- native Windows timeout kills a child and grandchild and Job accounting reports zero active processes;
- final stdout/stderr bytes are retained and drain is verified;
- no production source invokes WMIC, CIM ancestry, or tasklist inventory;
- launcher, spawn, runtime, termination, drain, and cleanup failures remain distinct;
- a cleanup exception cannot become a launcher-not-found diagnostic;
- `cmdc-local` records Session ID and terminal subtype from NDJSON;
- fake deterministic smoke passes, and real smoke is reported independently as pass, fail, or skipped;
- legacy CLI/output tests, the complete skill suite, sibling suite, package gate, and `git diff --check` pass;
- installed-copy parity is reported read-only and no installation is overwritten.
