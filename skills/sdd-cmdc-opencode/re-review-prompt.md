# Re-Review Prompt Template (scoped re-review)

Use this template to render the prompt file for the clean host session that
re-verifies a fix round over the scoped range `FIX_BASE..HEAD`. It is the
re-review counterpart of `task-reviewer-prompt.md`: it receives the previous
findings list and verdicts every item `ADDRESSED` or `NOT ADDRESSED`. Like
the initial review, it is an instruction template for the ephemeral host
session run by `scripts/review-session.py` — not a Codex reviewer prompt,
never a model selector. It covers only `FIX_BASE..HEAD`; out-of-scope
observations go to the ledger, not to a fresh review.

The controller must route OCR through the exact skill
`$open-code-review-codex:open-code-review-delegate`. Do not select the
similarly named LLM-backed `$open-code-review-codex:open-code-review` skill;
this re-review uses delegated `ocr delegate preview` and `ocr delegate rule`
only.

```
You are re-reviewing a fix round over the scoped range FIX_BASE..HEAD in a
fresh, ephemeral host session with read-only access to the repository. A
previous review produced findings; an implementer attempted to fix them.
Your job is to verdict each finding and inspect the fix diff — nothing else.
You have no history from any implementing session, and you must not call
Command Code, start another fix round, or modify the worktree.

## The range under review

- Fix base: [FIX_BASE_SHA] (the head the previous review saw)
- Head: [HEAD_SHA]
- Plan file: [PLAN_FILE]

## Findings from the previous review

[FINDINGS]

## Evidence provided by the controller (do not re-derive or re-run)

- Review package (generated with scripts/review-package PLAN_FILE FIX_BASE
  HEAD): [PACKAGE_FILE]
- `ocr delegate preview` output for this exact fix range:
  [PREVIEW_OUTPUT]
- Resolved rule groups (`ocr delegate rule`) for the fix-range paths:
  [RULE_GROUPS]
- Exact diffs for the fix-range paths: [DIFF_FILES]

## Your job

Verdict every finding in the findings list, in order. Inspect the fix diff
for new problems the fix itself introduced. Do NOT re-review code the fix
did not touch: an issue entirely outside the fix diff goes under
Out-of-Scope Observations and does not extend the loop.

- Read each exact fix-range diff; do not re-run git, OCR, or any review
  command.
- You are read-only: do not mutate the worktree, index, HEAD, or branch
  state.
- "Attempted" is not addressed: the specific defect must no longer exist.

## Report format

Write the report to [REPORT_FILE]:

### Finding Verdicts

For each finding in the findings list, in order:
- **[finding one-liner]** — ADDRESSED | NOT ADDRESSED, with file:line
  evidence

### New Breakage in the Fix Diff

Anything the fix itself broke or introduced, with severity and file:line.
"None" if clean.

### Out-of-Scope Observations

Issues entirely outside the fix diff. Non-blocking; the controller ledgers
these. "None" if none.

### Review status

REVIEW CLEAN only when every finding is ADDRESSED and there is no new
Critical/High breakage; otherwise REVIEW INCOMPLETE or BLOCKED — never
approval from a zero exit code alone.
```

**Placeholders:**
- `[FIX_BASE_SHA]` — REQUIRED: the head the previous review saw
- `[HEAD_SHA]` — REQUIRED: the current head commit
- `[PLAN_FILE]` — REQUIRED: the plan file the implementation was executed
  from
- `[FINDINGS]` — REQUIRED: the previous review's findings, copied verbatim,
  one per bullet
- `[PACKAGE_FILE]` — REQUIRED: the fix-range review package path
  (`scripts/review-package PLAN_FILE FIX_BASE HEAD` prints the unique path)
- `[PREVIEW_OUTPUT]` — REQUIRED: the `ocr delegate preview` output for the
  exact fix range
- `[RULE_GROUPS]` — REQUIRED: the resolved rule groups from
  `ocr delegate rule` for the fix-range paths
- `[DIFF_FILES]` — REQUIRED: the exact diffs for the fix-range paths
- `[REPORT_FILE]` — REQUIRED: the report file path the host session must
  write

**Host session returns:** a verdict per finding (ADDRESSED / NOT ADDRESSED),
new breakage in the fix diff, out-of-scope observations, and a review status.
