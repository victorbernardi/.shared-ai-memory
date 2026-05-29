# Skill Sandboxing Implementation Plan (V4.9)

## Background & Motivation

In the current V4.8 state, the CDD orchestrator evaluates rules and triggers skills or hooks, but the actual execution (`execute_script`, `execute_tool`) lacks a formal boundary. To prevent poorly designed or malicious scripts from compromising the host environment or hanging the orchestrator, we need a "Sandbox" layer. This aligns with the Stout Elite governance model, ensuring safe execution of dynamic actions.

## Scope & Impact

- **Scope:** Introduce a `SkillSandbox` execution layer in `src/core/sandbox.py`. Update the `dispatcher_fn` in `src/main.py` (and the core engine) to route all `execute_script` and `execute_tool` actions through this sandbox.
- **Impact:** Action execution will become safer and more predictable. Unlisted commands or scripts that run too long will be terminated automatically.

## Proposed Solution: Subprocess Whitelisting

1.  **Environment Filtering:** Strip sensitive environment variables (e.g., API keys, system paths) before passing them to the subprocess. Only explicitly required variables will be passed.
2.  **Timeout Enforcement:** Wrap `subprocess.run` with a configurable timeout (default 30s) to prevent infinite loops.
3.  **Command Whitelisting:** Define allowed executables (e.g., `python`, `pytest`) and allowed directories (e.g., `src/tools/`, `Research/`) in the configuration to prevent arbitrary code execution.
4.  **GCC Integration:** Capture the standard output and error of the executed scripts and log them using the `GCCController` to maintain the SRAO Context Graph.

## Alternatives Considered

-   **Venv Isolation:** Creating an ephemeral Python virtual environment for each execution. *Rejected* due to high overhead and slow startup times, which contradicts the fast, dynamic nature of the CDD engine.

## Implementation Steps

### Phase 1: Sandbox Core Component

-   Create `src/core/sandbox.py`.
-   Implement `SkillSandbox` class with a generic `execute()` method.
-   Add logic for timeout enforcement and environment variable sanitization.

### Phase 2: Configuration Updates

-   Update `data/config/rules.schema.json` to allow sandbox configuration overrides (e.g., custom timeout per action).
-   Define a global whitelist of allowed tools/scripts in `src/config.py`.

### Phase 3: Engine Integration

-   Refactor `src/main.py` to replace the `mock_dispatcher` with a real dispatcher that invokes `SkillSandbox.execute()`.
-   Integrate the sandbox execution results with `gcc_controller.commit_milestone` to track successes and failures.

### Phase 4: Testing & Validation

-   Write unit tests in `tests/test_sandbox.py` to simulate timeouts and blocked execution paths.
-   Integrate into the existing `test_e2e_integration.py` suite.

## Verification

-   Run `pytest` to ensure all 32 existing integration scenarios still pass.
-   Verify that attempting to execute an unwhitelisted script raises a `PermissionError` and is logged.
-   Verify that a script containing `time.sleep(60)` is killed after the timeout threshold and logged as a failure.

## Migration & Rollback

-   **Migration:** The new sandbox dispatcher will seamlessly replace the mock dispatcher. Existing rules calling `execute_script` will automatically be routed through the sandbox.
-   **Rollback:** Revert the dispatcher in `src/main.py` back to the mock or a direct `subprocess` call, and remove the `sandbox.py` file.