# Detailed ORCA Project Control protocol

## Purpose

This protocol separates project identity, delivery state, and model sessions:

- A **Project** is a stable repository identity.
- A **Run** is one coherent feature, bug, migration, release objective, or other
  independently closable unit of work.
- A **Control session** is the single active coordinator for one Run.
- A **Task** is a bounded unit that one worker session can finish.
- A **Dispatch** is one attempt to execute one Task.
- A **worker session** is ephemeral and owns only its assigned Dispatch.
- A **Run Charter** is the bounded, durable handoff from PROJECT_LEAD or the
  user to one CONTROL session. It carries approved intent and constraints but
  never overrides live Orca or Git state.

The feature belongs to the Run, not to a chat session. Sessions may be replaced;
the Run, Git state, tests, and CI carry continuity.

## Policy defaults

Unless a repository rule explicitly overrides them:

```text
DELEGATION_POLICY = SUPERVISED_FOR_CODE
CONTROL_HARNESS = codex
MAX_PARALLEL_WRITERS = 2
MAX_REMEDIATION_PASSES = 1
MAX_DEPENDENCY_DEPTH = 4
REVIEW_REQUIRES_FRESH_SESSION = true
WORKERS_MAY_DELEGATE = false
CONTROL_MAY_EDIT_CANDIDATE = false
FAIL_CLOSED_ON_AMBIGUITY = true
```

`SUPERVISED_FOR_CODE` is an explicit standing request to supervise delegated
repository mutation and review work. A full ownership handoff is allowed only
when the user explicitly says not to supervise, monitor, wait, or integrate the
result.

## Binding composition constraints

- The user selects the implementation executor for each Run. Persist `agy` or
  `command-code`; treat `cmdc` only as a conversational alias.
- CONTROL validates and applies that choice. It must not choose automatically or
  fall back from one implementation executor to the other.
- Keep `$delegate-to-agy` and `$commandcode-delegate` unchanged and invoke only
  the skill selected by the user.
- Compose the native `$orca-cli` and `$orchestration` skills without modifying
  or copying their command surface.
- Use `$orca-workflow-router` only to connect explicit lifecycle transitions to
  existing skills. It does not own lifecycle state or execute the capabilities.
- Use a fresh REVIEWER session for review. The default route is
  `$open-code-review-delegate`; `$open-code-review` requires explicit user
  selection. Do not modify either skill.
- `sdd-cmdc-opencode` is legacy. Never load, route, adapt, or use it as fallback.

## Source-of-truth hierarchy

Use these sources in this order:

1. Live Orca Run, Task, Dispatch, message, gate, and worker state for live
   coordination.
2. Live Git repository, branch, worktree, dirty state, diff, and exact HEAD
   for candidate identity.
3. Tests, linters, build, and CI for behavior evidence.
4. Approved designs, plans, ADRs, and briefs for intent and scope.
5. Project Registry and Work Ledger for explicit relations and
   classification, and discovery hints.
6. Mem0 for semantic preferences, historical decisions, and relations.
7. Reports and checkpoints for handoff and legibility only; never the sole
   authority.

Live Orca and Git are authoritative. Lower-authority records — approved
designs, plans, ADRs, briefs, the Project Registry, the Work Ledger, Mem0,
reports, checkpoints, or any other record below live Orca and Git — cannot
override them. Never use a model transcript, terminal title, memory summary,
SessionEnd hook, or ad hoc status file as the sole authority for ownership,
completion, or recovery.

Do not create a second lifecycle database beside Orca. A rebuildable local cache
may store only project-to-Run discovery hints and must never override Orca or
Git.

## Load the live Orca contract

Before any Orca mutation:

1. Load the native `$orca-cli` and `$orchestration` skills.
2. Resolve the Orca executable exactly as those installed skills require.
3. Run Orca status in JSON mode.
4. Load the version-matched CLI and orchestration guides from the selected
   executable.
5. Use commands and flags from those live guides; do not rely on remembered
   syntax or copy their command reference into this skill.
6. Stop on an unavailable runtime, missing capability, or ambiguous executable.
   Do not silently fall back to generic subagents, a headless launcher, an
   untracked terminal prompt, or another Orca binary.

Use `$orca-cli` for native workspace, worktree, terminal, session, and handoff
operations. Use `$orchestration` for Run, Task, Dispatch, message, gate, and
coordinator lifecycle. Git remains authoritative for candidate state.

## Role classification

Every session begins as `UNCLASSIFIED`. The global `AGENTS.md` role router
classifies PROJECT_LEAD, CONTROL, worker, and ORDINARY sessions before editing
files, creating Tasks, launching agents, or sending lifecycle messages.

PROJECT_LEAD uses `$orca-project-main`; it does not use this skill as authority
to coordinate every Run in the project.

### Dispatch preamble wins

A current, valid Orca Dispatch preamble containing the Task and Dispatch
identity establishes a worker role. It overrides assumptions based on being the
main thread, terminal title, model, or prior session history.

Classify the worker from the assigned Task:

- implementation or remediation -> `IMPLEMENTER`
- independent review or audit -> `REVIEWER`
- bounded read-only diagnosis -> `INVESTIGATOR`

A worker cannot promote itself to `CONTROL`.

### CONTROL

A session becomes `CONTROL` only after all of the following are true:

1. It has no live worker Dispatch preamble.
2. It has a valid `CONTROL_BOOTSTRAP` and approved Run Charter, or an explicit,
   evidence-based recovery target for one existing Run.
3. The project identity is known.
4. The target Run is selected unambiguously, or the Charter clearly authorizes
   creation of one new Run.
5. Before Task, Dispatch, message, or gate mutation, the current Orca terminal
   is bound to that exact Run.
6. No different live coordinator is being displaced without an explicit,
   evidence-based recovery decision.

Being the root Codex session, opening other terminals, receiving a broad
request, or having access to memory does not by itself make a session `CONTROL`.

### ORDINARY

Use `ORDINARY` for explanations, local discussion, read-only inspection, and
work that genuinely remains in one session without delegated implementation or
review. An ordinary session does not create orchestration state merely because
Orca is available.

## Run Charter input

CONTROL receives one durable Run Charter from PROJECT_LEAD or directly from the
user. It does not receive the full PROJECT_LEAD transcript, broad memory
retrieval, or unrelated project history.

The Charter must identify the Project, work slug, objective, baseline, scope,
constraints, acceptance criteria, named source artifacts, and implementation
executor. Record the executor with the frozen top-level schema:

```yaml
executor_policy:
  selected_by: victor
  value: agy | command-code
  automatic_fallback: false
  task_override: user_only
```

A Task-level executor override is valid only when the user explicitly provides
it and the durable coordination record preserves it. Normalize `cmdc` to
`command-code` when persisting the choice.

If the executor is missing or ambiguous, CONTROL may continue read-only
reconciliation, planning, Task design, and non-writing investigation, but it
must not dispatch implementation or remediation.

## Project identity

Prefer a stable `ORCA_PROJECT_KEY` declared by the repository's nearest
`AGENTS.md`.

When it is absent, derive a deterministic key from:

- canonical Git remote, when available;
- canonical Git common directory;
- repository root basename.

Use a short readable slug plus a collision-resistant suffix. Never identify the
project only by the current working directory, terminal title, or repository
basename.

Every newly created Run objective must start with:

```text
[project:<project_key>] [work:<work_slug>] <objective>
```

The `work_slug` names the coherent feature or delivery objective. It is not a
Task name.

If project identity is ambiguous, remain read-only and report the ambiguity.

## Run-scoped startup and recovery sweep

At CONTROL startup or recovery:

1. Validate the `CONTROL_BOOTSTRAP`, Run Charter, or exact recovery target.
2. Identify one exact Project and one exact Run. When creating a Run, use the
   approved Charter objective and project marker, then bind this CONTROL before
   further lifecycle mutation.
3. Read that Run in detail:
   - Run metadata and bound coordinator;
   - Tasks, dependencies, statuses, and results;
   - Dispatches and worker terminal accounting;
   - pending gates and actionable messages;
   - exact worktree, branch, dirty state, and candidate HEAD when available.
4. Read other active Runs only as a compact collision index containing Run ID,
   coordinator, explicitly recorded branch/worktree ownership, and explicitly
   recorded path or integration conflicts.
5. Read neighboring Run details only when a concrete collision requires a
   targeted read-only check. Do not ingest their complete Tasks, messages,
   Dispatch histories, memory, or transcripts.
6. Read bounded worker output only for a relevant Dispatch in the selected Run.
   Prefer Orca worker-read with a limit and cursor.
7. Build a compact selected-Run snapshot with Task/Dispatch state, candidate
   identity, selected executor, evidence, blockers, collisions, and next safe
   action.

CONTROL does not load broad project memory, cross-project context, unrelated
decisions, or complete neighboring-Run state. Those belong to
`$orca-project-main`. This session may mutate only its selected bound Run.

## Run selection

### Create a new Run when

- the approved Run Charter defines a new feature, bug, migration, initiative,
  or release objective with distinct acceptance and closure;
- an independent objective must proceed concurrently with another active Run;
- the user explicitly requests a separate lifecycle;
- the prior objective is terminally closed or deliberately abandoned and the
  new request is not continuation work.

### Reuse the same Run when

- moving from planning to implementation, review, remediation, integration, or
  release for the same objective;
- launching additional Tasks or parallel workers for the same feature;
- restarting, resuming, compacting, or replacing the coordinator session;
- retrying or recovering a Dispatch;
- continuing after a question, gate, or temporary blocker.

A context reset never creates a new Run by itself.

### New Control session

Start a separate Control session when:

- a new Run must be coordinated concurrently;
- the current session has a live worker role;
- the prior coordinator is unavailable and a deliberate recovery or takeover is
  required;
- a completed Run is followed by an unrelated objective and fresh context
  materially reduces contamination.

Do not make one permanent chat the owner of every project objective.

## Control boundaries

CONTROL owns:

- Run Charter reconciliation and design gate;
- Run selection and binding;
- Task decomposition and dependency ordering;
- validation of the user-selected implementation executor, plus model,
  effort, permissions, and placement within that selected contract unless
  already fixed by the user;
- Dispatch supervision;
- worker questions and escalations;
- evidence collection;
- review routing and verdict synthesis;
- integration sequencing and release readiness.

CONTROL does not:

- choose between AgY and Command Code without an explicit user decision;
- silently fall back, retry with, or substitute the other implementation
  executor;
- load project-wide memory or treat memory as live state;
- implement or directly repair candidate source, test, or configuration files;
- perform the independent review;
- use its own hidden reasoning as acceptance evidence;
- create untracked deliverable workers through native Codex subagents;
- let one worker widen scope or spawn another worker;
- resolve merge conflicts by editing candidate files;
- infer completion from silence, terminal idle state, or transport acceptance;
- run unlimited review-fix loops.

CONTROL may edit approved planning and coordination artifacts and may perform
non-content Git integration operations only when repository policy grants that
authority. A merge conflict that requires content changes becomes a Task.

## Workflow routing

At explicit lifecycle transitions, CONTROL invokes `$orca-workflow-router`.
The router receives the exact event and Run/Task context and returns the next
applicable skill, required brief, and expected next event. CONTROL validates and
executes the decision.

The router does not create Runs, Tasks, or Dispatches; mutate Orca or Git; choose
between `agy` and `command-code`; execute implementation, verification, review,
remediation, or finishing; or own a second state machine.

The detailed routing table belongs to `$orca-workflow-router`. At minimum it
connects:

- ready implementation work to the user-selected `$delegate-to-agy` or
  `$commandcode-delegate` skill;
- implementation and remediation reports to
  `$verification-before-completion`;
- valid verification to a fresh REVIEWER session, normally using
  `$open-code-review-delegate`;
- valid findings to `$receiving-code-review` and bounded remediation with the
  already selected executor;
- final accepted exact-HEAD evidence to
  `$finishing-a-development-branch`.

Never route to `sdd-cmdc-opencode`, and never copy leaf-skill logic into this
skill.

## Task design

Create a separate Task only when the unit:

- has explicit scope and owned paths;
- has its own discriminating verification;
- can be completed in one worker session;
- can be accepted or rejected independently from neighboring work;
- has a clear dependency relation.

Batch same-shaped mechanical work. Keep tightly coupled behavior in one Task.
Avoid dependency chains deeper than the configured limit.

Every Task brief must include:

```text
Role:
Objective:
Run Charter reference, Run and Task identity:
Selected implementation executor and selection authority, when applicable:
Required context and source-of-truth documents:
Owned worktree and branch:
Owned paths:
Protected paths and pre-existing dirty state:
Required behavior and acceptance criteria:
Plausible wrong implementation or failure mode:
Focused verification commands:
Project closure gates:
Forbidden actions:
Expected completion report:
```

The worker receives the brief and durable artifacts, not the Control session's
entire transcript.

## Worker placement

A fresh worker means a fresh native harness session. It does not always require
a new Git worktree.

Use the current or existing worktree only when write ownership cannot conflict.
Use a new child or top-level worktree when there will be concurrent writers, a
different branch, isolation requirements, or a concrete filesystem conflict.

Never run two writable sessions concurrently in the same worktree.

For implementation and remediation, use exactly the executor selected by the
user for the Run or explicit Task override. Pin the effective harness, model,
and reasoning effort when the live Orca surface supports it, and verify the
launch receipt. Failure or unavailability does not authorize the other
implementation executor.

## IMPLEMENTER contract

An IMPLEMENTER:

- owns exactly one active Dispatch;
- edits only assigned paths in the assigned worktree;
- reads repository instructions and named design artifacts;
- does not create or bind Runs, create Tasks, start workers, or use native
  subagents;
- does not merge, publish, force-push, reset, clean, stash, or alter another
  worktree;
- asks the coordinator when the contract is ambiguous or scope must widen;
- reports `NEEDS_REPLAN` rather than silently expanding architecture;
- runs the focused verification and required closure gates;
- creates task-scoped commits only when the brief grants commit authority;
- sends exactly one valid worker completion report for the current Dispatch,
  with explicit succeeded or failed outcome;
- ends the dispatched turn after reporting completion.

A task that cannot fit one session is a decomposition failure. Do not continue
indefinitely with partial handoffs.

## REVIEWER contract

A REVIEWER:

- is a fresh session that did not implement the candidate;
- is read-only unless a later, separate remediation Dispatch changes its role;
- receives the approved contract, baseline, exact diff or HEAD, and Dispatch
  evidence, not the implementer's chain of thought;
- reproduces the relevant tests and gates;
- checks correctness, scope, failure behavior, test discrimination, regressions,
  security and data risk, and release readiness;
- returns exactly one disposition:
  `ACCEPT`, `CHANGES_REQUESTED`, or `BLOCKED`;
- reports numbered findings with severity, evidence, file location, and concrete
  correction;
- sends one worker completion report. That report communicates findings; it
  does not authorize CONTROL to edit the candidate.

Use a different harness or model from the implementer when practical, but fresh
role-independent context is the minimum invariant. The Review Brief names the
review skill selected by the routing contract. Use `$open-code-review-delegate`
by default and `$open-code-review` only after explicit user selection; do not
fall back silently between them.

## Supervised loop

For one selected Run:

1. Reconcile the approved objective, scope, candidate baseline, and dirty state.
2. Create all known independent Tasks before launching the first parallel wave.
3. Route each ready implementation Task through `$orca-workflow-router` and
   dispatch only the executor selected by the user, respecting dependency and
   writer limits.
4. Wait through Orca message delivery for worker completion, escalation, or
   questions. A wait timeout is a checkpoint, not a failure.
5. Process every message in the delivered batch before acknowledging it.
6. Answer worker questions through the Orca reply path.
7. On escalation, classify the cause before acting:
   missing context, ambiguous contract, environment, model capacity, scope
   change, authority, or runtime failure.
8. On worker completion:
   - verify Task and Dispatch identity;
   - inspect bounded output and declared changed paths;
   - verify Git state and exact candidate identity;
   - reproduce focused evidence as required;
   - release, retain by explicit user request, or immediately reuse the exact
     settled terminal for a new Dispatch.
9. Route valid implementation evidence through `$orca-workflow-router` and
   dispatch a fresh independent review when required.
10. Route the verdict through `$orca-workflow-router` according to the
    bounded remediation policy.
11. Integrate accepted Tasks in dependency order.
12. Run exact-HEAD project gates and final review when required.
13. Use the project's finishing-development-branch workflow only after the
    applicable review accepts and evidence is green.
14. Report the Run outcome and leave no ambiguous live Dispatch.

## Remediation policy

For an in-contract `CHANGES_REQUESTED` verdict:

1. Send findings to the original implementer on a fresh remediation Dispatch in
   the same Task scope and worktree when that session is still trustworthy.
2. Permit one remediation pass.
3. The same reviewer rechecks the reproduced finding and fix-only diff.
4. A second rejection, scope change, or architectural contradiction becomes
   `REPLAN_OR_SPLIT`; do not start another automatic repair loop.

Preserve the user-selected implementation executor throughout remediation.
Change it only after an explicit user override recorded in durable coordination
state.

`BLOCKED` preserves the candidate and escalates the missing dependency,
authority, or decision. It is not silently converted into implementation
failure.

## Native Codex subagents

Do not use Codex internal subagents for implementation, independent review, or
any result that participates in Run acceptance. They lack the required Orca
Task/Dispatch lifecycle and independent session contract.

A repository may explicitly permit advisory read-only subagents outside an
active Run. Their output is non-authoritative and cannot replace a supervised
Task, Dispatch, reviewer, test, or gate.

## Recovery

When resuming an existing Run:

1. Perform the selected-Run recovery sweep and compact neighboring-Run collision
   check defined above.
2. Match the request to an exact Run using project key, work slug, objective,
   branch, Task, Dispatch, worktree, and candidate evidence.
3. Do not bind or take over a Run whose coordinator may still be active.
4. For an uncertain worker, inspect Run, Task, Dispatch, worker state, bounded
   output, and exact terminal/worktree identity before retrying.
5. Never create a duplicate Dispatch merely because no completion message is
   visible.
6. If the old attempt cannot be proven stopped or settled, fence or abandon it
   using the live Orca guide before replacement.
7. Bind the replacement Control session only after ownership is unambiguous.
8. Reconstruct context from Orca, Git, tests, CI, the Run Charter, and named
   approved artifacts. Do not require the previous CONTROL transcript or load
   broad project memory. Preserve the recorded executor; conflicting or missing
   executor evidence blocks writable recovery until the user resolves it.

## Fail-closed conditions

Remain read-only and surface the evidence when any of these are ambiguous:

- project identity;
- Run match;
- user-selected implementation executor;
- coordinator ownership;
- Task or Dispatch identity;
- worktree or branch ownership;
- dirty path ownership;
- candidate HEAD;
- worker liveness or settlement;
- required permissions;
- review route or independence;
- workflow-routing transition;
- destructive or publishing authority.

Do not compensate by guessing, broad global terminal operations, silent
fallbacks, or creating another state store.

## Required Control report

At each meaningful checkpoint, report:

```text
Project:
Run:
Control session:
Objective:
Implementation executor and selection authority:
Active Tasks and Dispatches:
Completed and accepted Tasks:
Blocked or uncertain Tasks:
Worktrees and branches:
Candidate HEAD:
Verification:
Review route and status:
Next workflow event or routed skill:
Open questions or gates:
Next safe action:
```

Only call work complete when the applicable review accepts, required evidence is
green on the exact candidate, and every Dispatch is settled or deliberately
accounted for.
