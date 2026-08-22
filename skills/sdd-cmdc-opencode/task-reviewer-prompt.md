# Task Reviewer Prompt Template (initial review)

Use this template to render the prompt file for the clean host session that
reviews an already-finished committed range `BASE..HEAD`. The controller
renders it into a `PROMPT_FILE` in the plan's ignored workspace and hands it
to `scripts/review-session.py`; it is an instruction template for the new
ephemeral host session, not a Codex reviewer prompt and not a model selector.
The host session never re-runs OCR and never re-derives the range: the
controller supplies the preview output, the resolved rule groups, and the
exact diffs as evidence.

The controller must route OCR through the exact skill
`$open-code-review-codex:open-code-review-delegate`. Do not select the
similarly named LLM-backed `$open-code-review-codex:open-code-review` skill;
this review uses delegated `ocr delegate preview` and `ocr delegate rule`
only.

```
You are reviewing an already-finished implementation range in a fresh,
ephemeral host session with read-only access to the repository. You have no
history from any implementing session, and you must not call Command Code,
start a fix round, or modify the worktree. You only report findings and
state.

## The range under review

- Base: [BASE_SHA]
- Head: [HEAD_SHA]
- Plan file: [PLAN_FILE]

## Evidence provided by the controller (do not re-derive or re-run)

- Review package (generated with scripts/review-package PLAN_FILE BASE HEAD):
  [PACKAGE_FILE]
- `ocr delegate preview` output for this exact range: [PREVIEW_OUTPUT]
- Resolved rule groups (`ocr delegate rule`) for the reviewable paths:
  [RULE_GROUPS]
- Exact diffs for the reviewable paths: [DIFF_FILES]

## Your job

Review every file in the exact diffs against the resolved rule groups and
the plan's global constraints. Report findings and state only.

- Every file changed by the range must appear; every excluded file must carry
  its recorded justification.
- Read each exact diff; do not re-run git, OCR, or any review command.
- You are read-only: do not mutate the worktree, index, HEAD, or branch
  state.

## Report format

Write the report to [REPORT_FILE] with all of the following, with evidence:

- Files reviewed
- Excluded files
- Commands and Exit codes
- Findings by severity: Critical/High and Medium
- Review status (REVIEW CLEAN, REVIEW INCOMPLETE, or BLOCKED)
- BASE/HEAD evidence for the reviewed range
- Recommendations with path, start_line, and end_line when applicable

A missing field, a timeout, a partial scope, or missing evidence is REVIEW
INCOMPLETE or BLOCKED — never REVIEW CLEAN. Never claim approval from a zero
exit code alone.
```

**Placeholders:**
- `[BASE_SHA]` — REQUIRED: the exact base commit of the range under review
- `[HEAD_SHA]` — REQUIRED: the exact head commit of the range under review
- `[PLAN_FILE]` — REQUIRED: the plan file the implementation was executed
  from
- `[PACKAGE_FILE]` — REQUIRED: the review package path
  (`scripts/review-package PLAN_FILE BASE HEAD` prints the unique path)
- `[PREVIEW_OUTPUT]` — REQUIRED: the `ocr delegate preview` output for the
  exact range
- `[RULE_GROUPS]` — REQUIRED: the resolved rule groups from
  `ocr delegate rule` for every reviewable path
- `[DIFF_FILES]` — REQUIRED: the exact diffs for every reviewable path
- `[REPORT_FILE]` — REQUIRED: the report file path the host session must
  write

**Host session returns:** a review report containing `Files reviewed`,
`Excluded files`, `Commands`, `Exit codes`, `Critical/High`, `Medium`,
`Review status`, `BASE`/`HEAD` evidence, and recommendations with `path`,
`start_line`, and `end_line` when applicable.
