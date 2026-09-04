# Verification and review routing

```text
MAX_REMEDIATION_PASSES = 1
```

## Implementation report

After `IMPLEMENTATION_REPORTED`, invoke `$verification-before-completion`
and reproduce fresh evidence: Task/Dispatch identity, worktree and branch,
exact `HEAD`, changed files or artifact, focused commands, and results. A
worker exit code, accepted PTY input, self-report, or missing report is not
acceptance.

## Fresh reviewer

After `VERIFICATION_PASSED`, create a fresh `REVIEWER` Task/Dispatch. The
reviewer must be a new session that did not implement the candidate. Give it
only a Review Brief with the exact repository, worktree, branch, `base_sha`,
`head_sha`, contract references, and fresh verification evidence. The reviewer
loads `$open-code-review-delegate`; the router does not copy its review logic.

The reviewer returns one disposition: `ACCEPT`, `CHANGES_REQUESTED`, or
`BLOCKED`. Findings are evidence, not authorization for Control to edit the
candidate.

## Findings and remediation

For `REVIEW_CHANGES_REQUESTED`, call `$receiving-code-review` only for the
actual findings, adjudicate their scope, and create a remediation Dispatch for
an implementer. The Control session does not edit candidate files. After
`REMEDIATION_REPORTED`, reverify the fix and perform a scoped re-review. Allow
one remediation pass only. A second rejection, scope change, or architectural
contradiction becomes `REPLAN_OR_SPLIT`; do not start another automatic repair
loop. Remediation is bounded by the Run Charter; it does not widen the
project.

## Final gates

After `ALL_TASKS_ACCEPTED`, perform final verification and a whole-branch review.
A final review pinned to an old `HEAD` is stale and blocked. Compare
the exact `base_sha` and `head_sha` in the Review Brief with the current
candidate. Only `FINAL_REVIEW_ACCEPTED` for the current HEAD permits
`$finishing-a-development-branch`; without a valid final review the finishing
transition is blocked.

`FINAL_REVIEW_CHANGES_REQUESTED` returns to the same bounded remediation,
reverification, and scoped re-review path. A pending local review blocks only
its dependent transition; independent Tasks may continue.
