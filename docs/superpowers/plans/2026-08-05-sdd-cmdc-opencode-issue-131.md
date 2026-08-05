# Implementation Plan — sdd-cmdc-opencode Issue 131

## Source and scope

This plan implements the first source-backed correction from
[Inova issue #131](https://github.com/victorbernardi/Inova/issues/131), whose
real incident showed an outer execution window ending before the Command Code
worker could finish its commit and report. The later `preview.md` is a
separate pre-specification and is not implemented by this plan.

## Global constraints

- Preserve the fixed `deepseek/deepseek-v4-flash` implementer model.
- Preserve fail-closed behavior: timeout, missing commit, missing report, or
  real backend failure never becomes approval and never triggers a fallback
  reviewer or implementation backend.
- Preserve the existing `--wall-timeout-seconds` interface and add the
  explicit `--timeout-seconds` spelling as a compatibility alias for the same
  finite process watchdog.
- Do not change the default turn budget or start broad suite, Ruff, or review
  work before the implementer has committed and produced the report when the
  task brief assigns those checks to the host.
- Keep the change limited to the adapter contract, implementer prompt
  contract, and deterministic tests/documentation required by this incident.
- Do not alter the local canonical `master`, the prior feature worktree, or
  any global `.agents`/`.codex` installation during this task.

## Task 1 — Make issue-131 timeout and prompt behavior source-backed

### Requirements

1. The Command Code adapter accepts `--timeout-seconds` and routes it through
   the same finite process watchdog as `--wall-timeout-seconds`.
2. Existing callers using `--wall-timeout-seconds` keep working, and invalid
   non-positive timeout values remain rejected.
3. The skill command example documents an explicit bounded timeout suitable for
   the issue-131 retry, while making clear that the caller's outer process
   window must not be shorter than the adapter window.
4. The implementer prompt directs the worker to run focused tests, commit, and
   write the report before broad suite/Ruff/review work assigned to the host.
5. Deterministic tests prove the alias, validation, and prompt contract through
   behavior/contract boundaries rather than a standalone source-text check.

### Acceptance evidence

- Focused RED/GREEN tests cover the new CLI spelling and prompt behavior.
- `skills/sdd-cmdc-opencode/tests` and `skills/sdd-cmdc/tests` pass when run
  separately.
- `git diff --check` passes.
- The implementation report records the exact commands and outputs.
- The resulting commit contains no global installation or unrelated worktree
  changes.
