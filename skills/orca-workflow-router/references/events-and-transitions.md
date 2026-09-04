# Events and transitions

The following 14 events are frozen. Orca is the lifecycle owner; this
document only describes the next capability and gate.

| Event / condition | Next action |
|---|---|
| `RUN_CHARTER_ACCEPTED` | Validate Victor's executor choice and decompose the Run into Tasks. |
| `TASK_READY` + `agy` | Call `$delegate-to-agy` with the Task Brief. |
| `TASK_READY` + `command-code` | Call `$commandcode-delegate` with the Task Brief. |
| `TASK_READY` + missing/invalid executor | Block only the dispatch; request Victor's choice; never choose or substitute. |
| `IMPLEMENTATION_REPORTED` | Apply `$verification-before-completion` and reproduce fresh evidence. |
| `VERIFICATION_PASSED` | Create a fresh `REVIEWER` Task/Dispatch. |
| `VERIFICATION_FAILED` | Preserve the failure and return only the bounded remediation transition. |
| `REVIEW_ACCEPTED` | Accept the Task and release its dependents. |
| `REVIEW_CHANGES_REQUESTED` | Route findings to `$receiving-code-review`, adjudicate them, and create bounded remediation. |
| `REVIEW_BLOCKED` | Preserve the blocked review and request the next human decision; do not self-accept. |
| `REMEDIATION_REPORTED` | Reverify the fix and run a scoped re-review. |
| `ALL_TASKS_ACCEPTED` | Run final verification and a whole-branch review. |
| `FINAL_VERIFICATION_PASSED` | Permit the final review transition for the current candidate. |
| `FINAL_REVIEW_ACCEPTED` | Call `$finishing-a-development-branch` only when the review is valid for current `HEAD`. |
| `FINAL_REVIEW_CHANGES_REQUESTED` | Route findings through the bounded remediation path and reverify. |
| `EXECUTOR_UNAVAILABLE` | Preserve the current Run state and ask Victor for a new executor decision; no automatic fallback. |

## Evidence boundary

`worker_done` is necessary but not sufficient. The Control session must match
Project/Run/Task/Dispatch identity, current branch/worktree and exact `HEAD`,
changed artifact or diff, focused validation, and an independent evidence
record before emitting `IMPLEMENTATION_REPORTED`.

## Concurrency

```text
MAX_PARALLEL_WRITERS = 2
NO_TWO_WRITERS_IN_SAME_WORKTREE = true
```

Independent Tasks may continue while a local review is pending. A pending
review blocks only the dependent transition, not independent Tasks or the
entire project. A worktree or path conflict is serialized before a writer
starts. No two writers share a worktree or dirty path.

## Explicit exclusions

- Do not route `$sdd-cmdc-opencode`; it is legacy and inactive.
- Pi is not adopted in the active v1 route.
- Do not modify protected native Orca skills; they remain unchanged.
- Do not add a second lifecycle store.
