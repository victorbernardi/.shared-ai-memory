# Design: sdd-cmdc-opencode

Date: 2026-08-01  
Status: Proposed

## Goal

Create `sdd-cmdc-opencode` as an independent SDD workflow skill. It preserves
the implementation, ledger, worktree, and fix-loop controls of `sdd-cmdc`, but
replaces its Codex review stages with Open Code Review in Delegation Mode.

The existing `sdd-cmdc` skill and its installed copies are read-only inputs.
They must not be edited, renamed, or replaced.

## Authentication boundary

The workflow must use Open Code Review's delegation mode exclusively:

- OCR performs deterministic file selection and rule resolution.
- The host Codex session performs the reasoning and review report.
- `ocr review`, `ocr llm test`, `OCR_LLM_*`, and `OPENAI_API_KEY` are outside
  the workflow.
- A missing OCR CLI, failed preview, failed rule resolution, or timeout is a
  fail-closed blocker. The workflow must never silently fall back to an
  ordinary Codex review.

This reuses the ChatGPT-authenticated Codex session without treating the
ChatGPT Pro subscription as an OpenAI API credential.

## Host session boundary (review-only)

The clean host session is a context boundary, not a review fallback. It is
the mechanism for reviewing already-finished implementation in a fresh,
ephemeral host session that has no history from the implementing session,
with read-only access to the same worktree and the same exact range
(`BASE`/`MERGE_BASE`..`HEAD`). It is started through
`scripts/review-session.py` with `codex exec --ephemeral --sandbox
read-only`, a finite timeout, and a verified process-tree cleanup.

This must be distinguished from a Codex review fallback:

- The clean host session runs **only after** the delegated OCR flow
  (`ocr delegate preview`, `ocr delegate rule`, and exact diff reading) has
  completed; OCR is a prerequisite, never replaced.
- Review-only never invokes the Command Code implementer
  (`scripts/cmdc-implementer.py`), never starts a fix round, and never
  re-reviews without explicit authorization.
- Review-only never publishes GitHub comments and never uses an API/LLM
  fallback (`ocr review`, `ocr llm test`, `OCR_LLM_*`, `OPENAI_API_KEY`).
- A missing final message, a timeout, partial output, an orphaned process,
  or missing evidence is `REVIEW INCOMPLETE` or `BLOCKED` — never
  `REVIEW CLEAN`.
- The separate host-session prompt templates (`task-reviewer-prompt.md` and
  `re-review-prompt.md`) do not create a new review backend: they are
  instruction templates for the clean host session, not Codex reviewer
  prompts, and both require prior OCR and run only through the launcher.

## Scope

### Preserved from `sdd-cmdc`

- One fresh Command Code implementer per implementation task and fix round.
- `scripts/cmdc-implementer.py` as the only implementation backend.
- Isolated worktree setup and plan-specific ledger.
- Task completion only after review evidence is clean or findings are parked
  at the five-round breaker.
- One final whole-branch review and one final fix wave at most.
- No silent recovery from Command Code failures, timeouts, or missing reports.

### Replaced

- The per-task Codex spec/quality reviewer is replaced by delegated OCR review.
- The scoped Codex re-review is replaced by delegated OCR re-review.
- The final broad Codex reviewer is replaced by delegated OCR whole-branch
  review.

### Out of scope

- Editing `sdd-cmdc` or any existing skill.
- Calling a paid LLM endpoint from OCR.
- Automatic GitHub PR comment publication.
- Changes to `REFERENCES.md` or `.llm-git-rules.md`.
- Broad changes to the Inova `AGENTS.md`; an optional routing note is a
  separate follow-up.

## Review workflow

For every task review, fix re-review, and final review:

1. Generate the existing review package for audit evidence using the correct
   BASE or FIX_BASE. Never infer the range from `HEAD~1`.
2. Run `ocr delegate preview` against the exact repository and review range.
3. Collect the reviewable paths and excluded paths from the preview output.
4. Run `ocr delegate rule` for the reviewable paths, batching large path lists
   when necessary.
5. Read the exact diff for each reviewable path using the mode and ref
   metadata from the preview.
6. Review each file against its resolved rule group and repository context.
7. Report findings with path, new-file line range, category, severity, and
   concrete recommendation.
8. Treat Critical/High findings as blocking, report Medium findings with
   context, and discard only clearly low-value false positives.

The review output must identify the number of files reviewed, excluded files,
commands executed, exit codes, findings by severity, and whether the review is
complete. A preview that excludes a file must not be reported as a complete
review of that file.

## Fix loop

When a delegated review reports a blocking finding:

- Dispatch a fresh Command Code implementer with the finding verbatim,
  preserving the existing report and ledger paths.
- Require the implementer to rerun the covering tests and append evidence.
- Run one scoped delegated OCR re-review over only the fix range.
- Record addressed and open findings in the ledger.
- Repeat for at most five rounds per task.
- At the cap, park contestable or non-load-bearing findings with a ruling;
  stop and report `BLOCKED` for a load-bearing finding.

The controller must not implement fixes directly, because that would bypass
the implementation boundary and its review evidence.

## Fail-closed states

Use these states consistently:

- `BLOCKED`: OCR is unavailable, preview/rule resolution failed, the exact
  range cannot be established, or the review evidence is missing.
- `REVIEW INCOMPLETE`: the process timed out or returned only a partial scope;
  it is never approval.
- `REVIEW CLEAN`: every reviewable file and resolved rule group was processed,
  no blocking findings remain, and command evidence is recorded.

The skill must not claim approval from a zero exit code alone.

## Installation and synchronization

The source of truth is:

`C:\Users\victor.bernardi\.shared-ai-memory\skills\sdd-cmdc-opencode`

After validation, synchronize the complete skill directory to:

- `C:\Users\victor.bernardi\.agents\skills\sdd-cmdc-opencode`
- `C:\Users\victor.bernardi\.codex\skills\sdd-cmdc-opencode`

The destinations must contain no copied `.git` directories and must have
matching `SKILL.md` SHA-256 hashes with the canonical source.

## Verification

Before promotion:

- Test the skill's pressure scenarios without the new skill and record the
  baseline failure modes.
- Verify the same scenarios with the new skill, including API-key pressure,
  OCR timeout, partial preview, dirty workspace, and a reviewer finding that
  requires a fix round.
- Validate that the skill does not edit either `sdd-cmdc` copy.
- Run the skill/documentation validators available in the shared memory repo.
- Verify canonical/destination file sets, absence of copied `.git`, and hash
  parity.

## Branch and commit policy

All changes for this work use branch `feat/sdd-cmdc-opencode` in the isolated
shared-memory worktree. The Inova checkout remains untouched. The design
commit precedes implementation; the implementation commit follows a separate
approved plan and verification cycle.
