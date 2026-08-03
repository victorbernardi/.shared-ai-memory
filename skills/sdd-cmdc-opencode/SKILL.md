---
name: sdd-cmdc-opencode
description: Use when executing implementation plans with independent tasks in the current session and delegating implementation tasks to Command Code
---

# SDD via Command Code with delegated Open Code Review

Execute the plan by running one fresh Command Code implementer per task, a
delegated Open Code Review (task spec compliance + code quality) after each,
and a broad delegated whole-branch review at the end. Every review — task
review, fix re-review, and final review — uses the `open-code-review-delegate`
subskill with `ocr delegate preview` followed by `ocr delegate rule`; no
review is ever routed to a Codex reviewer.

**Backend boundary:** implementation runs only through
`scripts/cmdc-implementer.py` (Command Code, fixed model
`deepseek/deepseek-v4-flash`); reviewers, re-reviewers and the final reviewer
run in the host session through delegated OCR, never through Codex review
prompts. A Command Code failure is fail-closed: report its structured blocker
and do not silently implement the task in Codex. An OCR failure is
fail-closed: `BLOCKED` or `REVIEW INCOMPLETE`, never approval, and never a
silent fallback to an ordinary Codex review.

**Delegated review only:** `ocr review`, `ocr llm test`, `OCR_LLM_*` and
`OPENAI_API_KEY` are outside this workflow and must never be executed or set.
The host session performs the reasoning and writes the review report; OCR
performs deterministic file selection and rule resolution. The ChatGPT Pro
session is never transformed into an API credential. Automatic GitHub PR
comment publication is out of scope — never publish review comments to
GitHub.

**Why subagents:** You delegate tasks to specialized agents with isolated
context. By precisely crafting their instructions and context, you ensure
they stay focused and succeed at their task. They should never inherit your
session's context or history — you construct exactly what they need. This
also preserves your own context for coordination work.

**Core principle:** Fresh subagent per task + delegated task review (spec +
quality) + broad delegated final review = high quality, fast iteration

**Narration:** between tool calls, narrate at most one short line — the
ledger and the tool results carry the record.

**Continuous execution:** Do not pause to check in with your human partner
between tasks. Execute all tasks from the plan without stopping. The only
reasons to stop are: BLOCKED status you cannot resolve, ambiguity that
genuinely prevents progress, or all tasks complete. "Should I continue?"
prompts and progress summaries waste their time — they asked you to execute
the plan, so execute it.

## When to Use

```dot
digraph when_to_use {
    "Have implementation plan?" [shape=diamond];
    "Tasks mostly independent?" [shape=diamond];
    "Stay in this session?" [shape=diamond];
    "subagent-driven-development" [shape=box];
    "executing-plans" [shape=box];
    "Manual execution or brainstorm first" [shape=box];

    "Have implementation plan?" -> "Tasks mostly independent?" [label="yes"];
    "Have implementation plan?" -> "Manual execution or brainstorm first" [label="no"];
    "Tasks mostly independent?" -> "Stay in this session?" [label="yes"];
    "Tasks mostly independent?" -> "Manual execution or brainstorm first" [label="no - tightly coupled"];
    "Stay in this session?" -> "subagent-driven-development" [label="yes"];
    "Stay in this session?" -> "executing-plans" [label="no - parallel session"];
}
```

**vs. Executing Plans (parallel session):**
- Same session (no context switch)
- Fresh subagent per task (no context pollution)
- Delegated review after each task (spec compliance + code quality), broad
  delegated review at the end
- Faster iteration (no human-in-loop between tasks)

## The Process

```dot
digraph process {
    rankdir=TB;

    subgraph cluster_per_task {
        label="Per Task";
        "Run cmdc implementer (./implementer-prompt.md)" [shape=box];
        "Implementer asks questions?" [shape=diamond];
        "Answer questions, provide context" [shape=box];
        "Implementer implements, tests, commits, self-reviews" [shape=box];
        "Generate review package, run delegated OCR review" [shape=box];
        "Review status REVIEW CLEAN?" [shape=diamond];
        "Finding conflicts with plan text?" [shape=diamond];
        "Ask human partner which governs" [shape=box];
        "Fix round R of 5: fresh cmdc implementer with persistent findings" [shape=box];
        "Run scoped delegated re-review (FIX_BASE)" [shape=box];
        "All findings addressed?" [shape=diamond];
        "R = 5?" [shape=diamond];
        "Adjudicate each open finding" [shape=box];
        "Any load-bearing finding?" [shape=diamond];
        "STOP: report BLOCKED to human partner" [shape=box];
        "Park findings in ledger with rulings" [shape=box];
        "Append completion to ledger, mark todo complete" [shape=box];
    }

    "Setup: worktree, ledger check, read plan, pre-flight review" [shape=box];
    "More tasks remain?" [shape=diamond];
    "Run delegated whole-branch review" [shape=box];
    "Final findings? ONE fix dispatch, one scoped re-review, adjudicate residuals" [shape=box];
    "Final review clean: delete this plan's workspace" [shape=box];
    "Use superpowers:finishing-a-development-branch" [shape=box style=filled fillcolor=lightgreen];

    "Setup: worktree, ledger check, read plan, pre-flight review" -> "Run cmdc implementer (./implementer-prompt.md)";
    "Run cmdc implementer (./implementer-prompt.md)" -> "Implementer asks questions?";
    "Implementer asks questions?" -> "Answer questions, provide context" [label="yes"];
    "Answer questions, provide context" -> "Implementer implements, tests, commits, self-reviews";
    "Implementer asks questions?" -> "Implementer implements, tests, commits, self-reviews" [label="no"];
    "Implementer implements, tests, commits, self-reviews" -> "Generate review package, run delegated OCR review";
    "Generate review package, run delegated OCR review" -> "Review status REVIEW CLEAN?";
    "Review status REVIEW CLEAN?" -> "Append completion to ledger, mark todo complete" [label="yes"];
    "Review status REVIEW CLEAN?" -> "Finding conflicts with plan text?" [label="no"];
    "Finding conflicts with plan text?" -> "Ask human partner which governs" [label="yes"];
    "Ask human partner which governs" -> "Fix round R of 5: fresh cmdc implementer with persistent findings";
    "Finding conflicts with plan text?" -> "Fix round R of 5: fresh cmdc implementer with persistent findings" [label="no"];
    "Fix round R of 5: fresh cmdc implementer with persistent findings" -> "Run scoped delegated re-review (FIX_BASE)";
    "Run scoped delegated re-review (FIX_BASE)" -> "All findings addressed?";
    "All findings addressed?" -> "Append completion to ledger, mark todo complete" [label="yes"];
    "All findings addressed?" -> "R = 5?" [label="no"];
    "R = 5?" -> "Fix round R of 5: fresh cmdc implementer with persistent findings" [label="no - next round"];
    "R = 5?" -> "Adjudicate each open finding" [label="yes - breaker trips"];
    "Adjudicate each open finding" -> "Any load-bearing finding?";
    "Any load-bearing finding?" -> "STOP: report BLOCKED to human partner" [label="yes"];
    "Any load-bearing finding?" -> "Park findings in ledger with rulings" [label="no"];
    "Park findings in ledger with rulings" -> "Append completion to ledger, mark todo complete";
    "Append completion to ledger, mark todo complete" -> "More tasks remain?";
    "More tasks remain?" -> "Run cmdc implementer (./implementer-prompt.md)" [label="yes"];
    "More tasks remain?" -> "Run delegated whole-branch review" [label="no"];
    "Run delegated whole-branch review" -> "Final findings? ONE fix dispatch, one scoped re-review, adjudicate residuals";
    "Final findings? ONE fix dispatch, one scoped re-review, adjudicate residuals" -> "Final review clean: delete this plan's workspace";
    "Final review clean: delete this plan's workspace" -> "Use superpowers:finishing-a-development-branch";
}
```

## Setup

Ensure the work happens in an isolated workspace: use
superpowers:using-git-worktrees to create one or verify the existing one.
Never start implementation on a main/master branch without your human
partner's explicit consent.

Conversation memory does not survive compaction. In real sessions,
controllers that lost their place have re-dispatched entire completed task
sequences — the single most expensive failure observed. Track progress in
a ledger file, not only in todos.

- Each plan owns a workspace: at skill start, run this skill's
  `scripts/sdd-workspace PLAN_FILE` — it prints the plan's git-ignored
  directory (`<repo-root>/.superpowers/sdd/<plan-basename>/`), home to
  every artifact for THIS plan: ledger, briefs, reports, review packages.
  Another plan's directory is never yours to read or write.
- Check for this plan's ledger at `<workspace>/progress.md`. If its first
  line names your plan file, tasks with a `Task <N>: complete` line are DONE
  — do not re-dispatch them; resume at the first task without one. A task
  whose last line is a fix round is mid-loop: resume the loop at the next
  round. A ledger whose first line names a different plan file — or a stray
  ledger at the old flat path `.superpowers/sdd/progress.md` — is another
  plan's progress: leave it in place and start your own, fresh.
- Create the ledger with its identity as the first line:
  `# SDD ledger — plan: <plan file path>`.
- The ledger is your recovery map: the commits it names exist in git even
  when your context no longer remembers creating them. After compaction,
  trust the ledger and `git log` over your own recollection.
- `git clean -fdx` will destroy the workspace (it's git-ignored scratch); if
  that happens, recover from `git log`.

Read the plan once, note its context and Global Constraints, and create a
todo per task.

Before dispatching Task 1, scan the plan once for conflicts:

- tasks that contradict each other or the plan's Global Constraints
- anything the plan explicitly mandates that the review rubric treats as a
  defect (a test that asserts nothing, verbatim duplication of a logic block)

Present everything you find to your human partner as one batched question —
each finding beside the plan text that mandates it, asking which governs —
before execution begins, not one interrupt per discovery mid-plan. If the
scan is clean, proceed without comment. The review loop remains the net for
conflicts that only emerge from implementation.

## Model Selection

### Implementer backend

- Every implementation task and every implementation fix round invokes
  `scripts/cmdc-implementer.py`.
- The adapter always passes `--model deepseek/deepseek-v4-flash` and defaults to
  `--max-turns 20`.
- The adapter passes `--no-skills` so the implementation worker cannot load
  global orchestration/reviewer skills and recursively spend its turn budget
  planning the SDD workflow. Its only workflow context is the focused prompt,
  brief, report and repository files supplied by the controller.
- On Windows, resolve `cmdc`, `cmdc.ps1` or `cmdc.cmd`; reject the native
  `C:\Windows\System32\cmd.exe` as the backend.
- Never route implementation to a Codex worker and never silently fall back to
  Codex when Command Code is unavailable.

### Reviewer backend

- Every review — task review, scoped re-review, and the final whole-branch
  review — uses the `open-code-review-delegate` subskill in the host
  session: `ocr delegate preview` for the exact repository and range,
  then `ocr delegate rule` for every reviewable path.
- Never dispatch a Codex reviewer. This skill ships no reviewer prompts:
  there is no Codex review stage and no other mechanism replaces the
  delegated flow.
- Reviewer quality and review-loop rules remain the same as the source SDD,
  but the review mechanism is delegated OCR only.

## The Task Loop

Everything you paste into a dispatch prompt — and everything a subagent
prints back — stays resident in your context for the rest of the session
and is re-read on every later turn. Hand artifacts over as files.

### 1. Run the Command Code implementer

Record BASE (`git rev-parse HEAD`) before running Command Code — the review
package and fix-round diffs need it.

- **Task brief:** before running an implementer, run this skill's
  `scripts/task-brief PLAN_FILE N` — it extracts the task's full text to a
  uniquely named file and prints the path. Compose the dispatch so the
  brief stays the single source of
  requirements. Your dispatch should contain: (1) one line on where this
  task fits in the project; (2) the brief path, introduced as "read this
  first — it is your requirements, with the exact values to use verbatim";
  (3) interfaces and decisions from earlier tasks that the brief cannot
  know; (4) your resolution of any ambiguity you noticed in the brief;
  (5) the report-file path and report contract. Exact values (numbers,
  magic strings, signatures, test cases) appear only in the brief. Never
  make a subagent read the whole plan file.
- **Report file:** name the implementer's report file after the brief
  (brief `…/task-N-brief.md` → report `…/task-N-report.md`) and put it in
  the dispatch prompt. The implementer writes the full report there and
  returns only status, commits, a one-line test summary, and concerns.
- The Command Code prompt describes one task, not the session's history. Do not
  paste accumulated prior-task summaries ("state after Tasks 1-3") into
  later dispatches — a real session's dispatch hit 42k chars of which 99%
  was pasted history. A fresh subagent needs its task, the interfaces it
  touches, and the global constraints. Nothing else.
- If an earlier task parked a finding in the area this task touches, carry
  a pointer to that ledger entry in the dispatch.
- There is no live implementer identity to resume. Each task and fix round is
  a fresh Command Code process; the brief, report and ledger are its persistent
  context.
- Never run multiple implementation processes in parallel (conflicts).

Create a focused prompt file containing the brief path, report path, relevant
interfaces, resolved ambiguities, global constraints and the required report
contract. Then run:

```powershell
$skillDir = (Resolve-Path "<path-to-this-skill>").Path
$workspace = (Get-Location).Path
& python (Join-Path $skillDir "scripts\cmdc-implementer.py") `
  --cwd $workspace `
  --prompt-file "<cmdc-prompt-file>" `
  --max-turns 20 `
  --checkpoint-file "<checkpoint-file>" `
  --heartbeat-interval 30 `
  --recovery-max-turns 5
```

The adapter's JSON event stream on stdout, stderr and exit code are part of the dispatch result. A
non-zero result or missing report emits `STATUS: BLOCKED` with
`BLOCKER_CODE`, `MESSAGE`, `COMMAND`, `EXIT_CODE`, `STDERR` and `ACTION`; write
that reason into the ledger and do not generate a review package. A timeout
with workspace evidence emits `STATUS: IMPLEMENTATION INCOMPLETE`, appends a
`TIMED_OUT` JSONL checkpoint and blocks review/next-task progression until the
workspace, report and commit are recovered deterministically. When a partial
diff or commit is present, the adapter starts one fresh, bounded CMDc recovery
phase. Recovery is accepted only when a new commit, the requested report and
detectable test evidence all exist; otherwise it remains incomplete and blocks
review. A successful recovery emits `STATUS: RECOVERED`; this permits package
generation only after the normal delegated review gates are rechecked.
An exit code `4` is classified as `PERMISSION_DENIED`; the headless adapter
does not wait for an interactive permission answer.

Template: [implementer-prompt.md](implementer-prompt.md)

### 2. Handle the report

Command Code implementers report one of four statuses. Handle each appropriately:

**DONE:** Generate the review package (`scripts/review-package PLAN_FILE BASE HEAD`, from this skill's directory — it prints the unique file path it wrote; BASE is the commit you recorded before running the implementer — never `HEAD~1`, which silently drops all but the last commit of a multi-commit task), then run the delegated OCR task review with the printed path.

**DONE_WITH_CONCERNS:** The implementer completed the work but flagged doubts. Read the concerns before proceeding. If the concerns are about correctness or scope, address them before review. If they're observations (e.g., "this file is getting large"), note them and proceed to review.

**NEEDS_CONTEXT:** The implementer needs information that wasn't provided. Provide the missing context and run a fresh Command Code invocation with the same fixed model.

**BLOCKED:** The implementer cannot complete the task. If the adapter emitted a
structured `BLOCKED` diagnostic, append its code/message/action to the ledger,
do not dispatch a reviewer, and report the infrastructure blocker to the human.
If the Command Code worker itself returned `BLOCKED`, assess its report:
provide missing context and run a fresh Command Code invocation with the same
fixed model, or escalate a plan defect to the human.

**Never** ignore an escalation or force the same model to retry without changes. If the implementer said it's stuck, something needs to change.

If the implementer asks questions — before starting or mid-task — answer
clearly and completely, provide additional context if needed, and don't
rush it into implementation.

### 3. Review the task

Per-task reviews are task-scoped gates. The broad review happens once, at the
final whole-branch review. Never skip the task review, and never accept a
report missing either verdict — spec compliance AND task quality are both
required. Implementer self-review never replaces the task review; both are
needed.

Every review — task review, fix re-review, and final whole-branch review —
follows the same delegated OCR flow through the `open-code-review-delegate`
subskill:

1. Generate the review package for audit evidence with the exact range:
   `scripts/review-package PLAN_FILE BASE HEAD` for a task review,
   `scripts/review-package PLAN_FILE FIX_BASE HEAD` for a re-review, and
   `scripts/review-package PLAN_FILE MERGE_BASE HEAD` for the final review.
   Use the BASE you recorded before dispatching the implementer — never
   `HEAD~1`, which silently truncates multi-commit tasks.
2. Run `ocr delegate preview` for that exact repository and range. The
   preview resolves the reviewable scope: mode, merge_base, commit and `to`
   metadata, plus the excluded paths and their reasons.
3. Stop as BLOCKED if the preview fails or the scope is incomplete: a
   timeout, a partial preview, or an excluded file without justification
   recorded in the preview output is never approval. Re-run the preview
   with a higher limit, or escalate as BLOCKED.
4. Run `ocr delegate rule` for every reviewable path, in batches if the
   path list is large. Every path the preview resolved must be covered by
   a rule run; a rule that cannot be resolved is a blocker, not a skip.
5. Read each exact diff for every reviewable path, using the mode and ref
   metadata (`mode`, `merge_base`, `commit`, `to`) returned by the preview.
6. Review each file against its resolved rule group and repository context,
   and report findings in the delegated Open Code Review format.
7. Treat Critical/High findings as blocking and run a fresh Command Code fix
   round (section 4). Report Medium findings with context. Discard only
   clearly low-value false positives, recording that decision.
8. Re-run only the fix range through delegated preview/rule/diff review
   after a fix round (section 4).

**Windows shell for exact-range OCR:** PowerShell mangles OCR ref
arguments — `ocr delegate preview --commit <rev>` or `--from/--to` fails
with `Needed a single revision` — while Git Bash resolves the same exact
ref. Detect a working shell at the start of each review: prefer Git Bash on
Windows (or any shell where OCR ref resolution demonstrably succeeds) and
run every exact-range `ocr delegate preview` and `ocr delegate rule`
through it. Preserve the exact BASE/FIX_BASE/MERGE_BASE range the review
package was built from; never shift, truncate, or re-derive the range to
work around a shell quirk. Record the shell name, the full command, and its
exit code in the review evidence, along with any fallback shell attempt or
blocker. Never change the range silently, and never fall back to a Codex or
API review when the shell or OCR fails.

The review output must identify: the number of files reviewed, the excluded
files, the commands executed, their exit codes, findings by severity
(Critical/High and Medium), and the review status. Every recommendation
carries a `path`, `start_line` and `end_line`. A preview that excluded a
file must not be reported as a complete review of that file. The skill must
not claim approval from a zero exit code alone.

**Reviewer inputs:** the delegated review gets three paths — the same brief
file, the report file, and the review package — plus the global
constraints that bind the task. The delegate reads the diff files itself
from the exact range; it does not re-derive the range.

- The global-constraints block you hand the review is its attention
  lens. Copy the binding requirements verbatim from the plan's Global
  Constraints section or the spec: exact values, exact formats, and the
  stated relationships between components ("same layout as X", "matches
  Y").
- Do not add open-ended directives like "check all uses" or "run race tests
  if useful" without a concrete, task-specific reason
- Do not ask the review to re-run tests the implementer already ran on the
  same code — the implementer's report carries the test evidence
- Do not pre-judge findings for the review — never instruct it to
  ignore or not flag a specific issue. If you believe a finding would be a
  false positive, let the review raise it and adjudicate it in the review
  loop. If the prompt you are writing contains "do not flag," "don't treat X
  as a defect," "at most Minor," or "the plan chose" — stop: you are
  pre-judging, usually to spare yourself a review loop.
The delegated review may report "⚠️ Cannot verify from diff" items —
requirements that live in unchanged code or span tasks. These do not block
the rest of the review, but you must resolve each one yourself before
marking the task complete: you hold the plan and cross-task context the
review lacks. If you confirm an item is a real gap, treat it as a failed
spec review — it enters the fix loop with the other findings.

### 4. The fix loop

The loop triggers when the delegated review reports spec ❌, any Critical or
High finding, or a ⚠️ item you confirmed as a real gap.

Before the loop starts, two routes leave it immediately:

- Record Minor findings in the progress ledger as you go
  (`Task <N>: minor (deferred): <one-liner>`), and point the final
  whole-branch review at that list so it can triage which must be fixed
  before merge. A roll-up nobody reads is a silent discard. Minor findings
  never enter the loop.
- A finding labeled plan-mandated — or any finding that conflicts with
  what the plan's text requires — is the human's decision, like any plan
  contradiction: present the finding and the plan text, ask which governs.
  Do not dismiss the finding because the plan mandates it, and do not
  dispatch a fix that contradicts the plan without asking.
Everything else enters the loop. A fix round is one fix dispatch plus one
scoped delegated re-review. Five rounds maximum per task:

**Rounds 1-5 — run a fresh Command Code implementer.** Send the open findings
verbatim, together with the brief path and report-file path. The report file is
the persistent memory because Command Code invocations are not resumable. Keep
the fixed `deepseek/deepseek-v4-flash` model in every round; the five-round cap
and the scoped delegated re-review remain unchanged.

**Every round, either way:** the implementer fixes, re-runs the tests
covering the amended code, appends its fix report to the same report file,
and returns the short contract. Before re-dispatching the review, confirm
the fix report contains the covering tests, the command run, and the
output; dispatch the re-review once all three are present. Name the
covering test files in the fix message — a one-line fix does not need the
whole suite.

**The re-review is scoped.** Run `scripts/review-package PLAN_FILE FIX_BASE HEAD`
where FIX_BASE is the head the previous review saw, then run the delegated
OCR flow (section 3) over that exact fix range only: `ocr delegate preview`,
`ocr delegate rule` for the fix-range paths, reading each exact diff, and
reporting in the delegated format. The re-review verdicts each finding
ADDRESSED or NOT ADDRESSED and flags new breakage in the fix diff only.
New Critical/High breakage in the fix diff joins the open findings list.
Out-of-scope observations go to the ledger as deferred minors — they never
extend the loop.

**After each round,** append to the ledger:
`Task <N>: fix round <R>/5 (<X> addressed, <Y> open — <finding one-liners>; commits <a7>..<b7>)`

Never fix findings yourself in the controller session — your context stays
clean for coordination, and controller fixes skip review.

**The breaker.** When round 5's re-review still leaves findings open, stop
dispatching. Adjudicate each open finding yourself — you hold the plan and
the cross-task context the review lacks:

- **The review is wrong, or the point is contestable:** park it —
  `Task <N>: parked — <finding> — ruling: <why the code stands>`. The final
  review sees both sides.
- **Real, but nothing downstream builds on it:** park it the same way, with
  a ruling that says it's real and deferred.
- **Real and load-bearing** — a later task builds on it, or it reveals a
  plan defect: STOP. Append `Task <N>: BLOCKED — <reason>` and report to
  your human partner with the finding, the plan text it collides with, and
  the fix history. Parking a structural failure lets every dependent task
  build on it and hands the final review a problem it cannot fix either.

Adjudicate only at the cap. Adjudicating earlier to end a loop is
pre-judging with a different name. Every adjudication is a ledger entry —
a silent discard is forbidden.

### 5. Complete the task

When the delegated review comes back REVIEW CLEAN — or every open finding is
parked with a ruling at the cap — append the completion line to the ledger
in the same message as your other bookkeeping:

- `Task <N>: complete (commits <base7>..<head7>, review clean)`
- `Task <N>: complete (commits <base7>..<head7>, <K> parked)` after a
  tripped breaker

Then mark the todo complete and move on. Never move to the next task while
the review has open Critical/High issues that are neither fixed nor
parked-with-ruling at the cap.

## Governance States

The fail-closed states below govern every review, re-review, and the final
review. A zero exit code alone never claims approval.

- **REVIEW CLEAN** — every reviewable file and resolved rule group was
  processed through `ocr delegate preview`, `ocr delegate rule`, and exact
  diff reading; no blocking findings remain; and the command evidence
  (commands, exit codes, files reviewed, excluded files) is recorded in the
  review report. Only REVIEW CLEAN completes a task or the plan.
- **REVIEW INCOMPLETE** — the delegated process timed out or returned only
  a partial scope. It is never approval: re-run the preview with a higher
  limit or escalate as BLOCKED. Record the command that expired, its
  `EXIT_CODE`/timeout, and the scope that was not obtained in the ledger:
  `Task <N>: REVIEW INCOMPLETE — <REASON>: <scope not obtained>; sem aprovação`
- **BLOCKED** — OCR is unavailable, the preview or rule resolution failed,
  the exact range cannot be established, or the review evidence is missing.
  Stop dispatching and report the blocker with the plan text it collides
  with. Timeout, partial preview, excluded file without justification, or
  an unresolved rule can never produce approval; each is recorded in the
  ledger as BLOCKED or REVIEW INCOMPLETE, never as REVIEW CLEAN.

## Final Review

The final whole-branch review gets a package too: run
`scripts/review-package PLAN_FILE MERGE_BASE HEAD` (MERGE_BASE = the commit the
branch started from, e.g. `git merge-base main HEAD`) and include the
printed path in the final review, so the delegated review reads one file
instead of re-deriving the branch diff with git commands. Then run the
delegated OCR flow (section 3) over the exact branch range: `ocr delegate
preview`, `ocr delegate rule` for every reviewable path, reading each exact
diff, and reporting in the delegated format. Point it at the ledger's
deferred-minor and parked lines so it can triage which must be fixed before
merge.

If the final whole-branch review returns findings, dispatch ONE fix subagent
with the complete findings list — not one fixer per finding.
Per-finding fixers each rebuild context and re-run suites; a real
session's final-review fix wave cost more than all its tasks combined.
Then run exactly one scoped delegated re-review of the fix wave
(`scripts/review-package PLAN_FILE FIX_BASE HEAD` over the fix range,
delegated preview/rule/diff per section 3).
Adjudicate any residual findings as in the task loop's breaker: park with
rulings, or stop on load-bearing ones. There is no second fix wave —
residual load-bearing findings surface to your human partner when
finishing-a-development-branch presents the options.

## Finish

When the final whole-branch review is REVIEW CLEAN and its fixes are merged,
delete this plan's workspace (`rm -rf <workspace>`) — the git history is
the record now. Sibling directories belong to other plans; leave them
alone.

Use superpowers:finishing-a-development-branch.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Close enough on spec compliance" | Reviewer found spec gaps = not done. Fix or hit the cap and adjudicate — those are the only exits. |
| "I'll fix it myself, dispatching is overhead" | Controller fixes pollute your context and skip review. Resume the implementer. |
| "One more round will converge" | Past the cap, rounds don't converge — the failure is structural. Adjudicate and route. |
| "The reviewer will just find something new anyway" | Scoped re-reviews verify fixes; they cannot wander. New findings on untouched code go to the ledger, not the loop. |
| "This finding is obviously wrong, I'll drop it" | You adjudicate only at the cap, and every ruling is a ledger entry. Silent discards are forbidden. |
| "The fix was small, skip the re-review" | Unreviewed fixes are how regressions land. Every round ends with a scoped delegated re-review. |
| "Reviews slow the loop down" | The loop without reviews is just unverified churn. Reviews are the loop's brakes and steering. |
| "OCR failed, I'll just do a quick Codex review" | OCR failure is fail-closed: BLOCKED or REVIEW INCOMPLETE, never a substitute review mechanism. |
| "Ledger bookkeeping is overhead" | The ledger is what survives compaction. Controllers without one have re-dispatched entire completed task sequences. |

## Example Workflow

```
You: I'm using Subagent-Driven Development to execute this plan.

[Setup: worktree verified]
[Read plan file once: docs/superpowers/plans/feature-plan.md]
[Resolve workspace: scripts/sdd-workspace docs/superpowers/plans/feature-plan.md — no ledger inside, fresh start]
[Create todos for all tasks]

Task 1: Hook installation script

[Run task-brief for Task 1; dispatch implementer with brief + report paths + context]

Implementer: "Before I begin - should the hook be installed at user or system level?"

You: "User level (~/.config/superpowers/hooks/)"

Implementer: [Later]
  - Implemented install-hook command
  - Added tests, 5/5 passing
  - Self-review: Found I missed --force flag, added it
  - Committed

[Run review-package PLAN_FILE BASE HEAD; record BASE before the dispatch]
[Run ocr delegate preview for that exact repository and range; scope complete]
[Run ocr delegate rule for each reviewable path; read each exact diff]
Delegated review: Spec ✅ - all requirements met, nothing extra.
  Strengths: Good test coverage, clean. Issues: None.
  Review status: REVIEW CLEAN (N files reviewed, 0 excluded, exit codes 0)

[Ledger: Task 1: complete (commits a1b2c3d..d4e5f6a, review clean)]

Task 2: Recovery modes

[Run task-brief for Task 2; dispatch implementer with brief + report paths + context]

Implementer: [No questions]
  - Added verify/repair modes
  - 8/8 tests passing
  - Committed

[Run review-package PLAN_FILE BASE HEAD; delegated preview/rule/diff review]
Delegated review: Spec ❌:
  - Missing: Progress reporting (spec says "report every 100 items")
  Issues (High): Magic number (100) — path src/recovery.js, start_line 41, end_line 41

[Fix round 1: resume the implementer with both findings]
Implementer: Added progress reporting, extracted PROGRESS_INTERVAL constant.
  Re-ran test/recovery.test.js — 10/10 passing. Fix report appended.

[Run review-package PLAN_FILE FIX_BASE HEAD; scoped delegated preview/rule/diff re-review]
Delegated re-review: Missing progress reporting — ADDRESSED (src/recovery.js:41).
  Magic number — ADDRESSED (src/recovery.js:7). New breakage: none.
  Verdict: all findings addressed. Review status: REVIEW CLEAN.

[Ledger: Task 2: fix round 1/5 (2 addressed, 0 open; commits d4e5f6a..b7c8d9e)]
[Ledger: Task 2: complete (commits d4e5f6a..b7c8d9e, review clean)]

...

[After all tasks]
[Run review-package PLAN_FILE MERGE_BASE HEAD; delegated whole-branch review]
Final reviewer: All requirements met. Deferred minors triaged: none block merge.
  Review status: REVIEW CLEAN.

[Delete this plan's workspace — the record now lives in git]

Done! Using superpowers:finishing-a-development-branch.
```
