---
name: orca-project-control
description: >-
  Coordinate exactly one supervised Orca Run. Use when a validated CONTROL
  session must reconcile a Run Charter, create or recover that Run, decompose
  it into Tasks, dispatch fresh implementation or review sessions, process
  worker_done, escalation, question, and decision-gate events, reproduce
  evidence, route bounded remediation, and coordinate integration readiness.
  Do not use for project-wide discovery or memory loading, ordinary
  single-session discussion, candidate implementation, independent review, or
  an explicit full ownership handoff that the user does not want supervised.
metadata:
  version: "1.0.0"
---

# ORCA Project Control

## Entry condition

This skill governs a supervised `CONTROL` session for exactly one Run. Before
creating a Run, Task, Dispatch, worker, gate, or recovery action, read the complete
[`references/control-protocol.md`](references/control-protocol.md).

## Purpose

Keep Project identity, Run lifecycle, Git candidate identity, and model
sessions distinct. This skill coordinates exactly one selected Run. Orca owns
live Run/Task/Dispatch state; Git owns branch, worktree, dirty state, diff,
commit, and `HEAD`; tests, CI, and review provide evidence. A local cache or
memory may never replace those authorities.

## Role classification

Every session starts `UNCLASSIFIED` and is classified before editing or
orchestration:

- a valid Dispatch preamble establishes `IMPLEMENTER`, `REVIEWER`, or
  `INVESTIGATOR` and takes precedence over prior conversation;
- a valid `CONTROL_BOOTSTRAP` plus Run Charter bound to one exact Run
  establishes `CONTROL`;
- a valid `PROJECT_BOOTSTRAP` bound to a Project Key establishes `PROJECT_LEAD`;
- otherwise use `ORDINARY`.

Ambiguous project, Run, Dispatch, coordinator, worktree, dirty-path, candidate,
or authority ownership remains read-only and fails closed. A worker cannot
promote itself to `CONTROL`.

## Hard boundaries

- Only validated `CONTROL` may create or bind Runs, create Tasks, dispatch
  workers, or resolve gates.
- `CONTROL` coordinates and accepts; it does not edit candidate source, tests,
  or configuration and it does not perform the independent review.
- `PROJECT_LEAD` performs project-wide read-only discovery and does not create
  implementation Tasks or Dispatches.
- The user selects `agy` or `command-code` for each Run. CONTROL records and
  preserves that choice; it never infers or silently substitutes an executor.
- Workers own only their assigned Dispatch; they do not create workers or
  widen scope. Reviewers are fresh, read-only, and return `ACCEPT`,
  `CHANGES_REQUESTED`, or `BLOCKED`.
- Explicit lifecycle transitions use `$orca-workflow-router`; it delegates to
  existing capabilities and does not own Orca lifecycle state.
- Do not create a second lifecycle store, use a silent executor fallback, or
  infer completion from silence, terminal state, transport acceptance, or a
  worker exit code.

## Governance

Governance is protocol-level and Orca-owned: Run/Task/Dispatch state, gates,
worker liveness, messages, and audit evidence come from the live Orca surface.
Do not add `governance.py`, a local action-log database, a daemon, or a second
rate-limit/lifecycle store to this skill. If the live runtime lacks a required
governance capability, preserve the state and report the gap.

## Live contract

Before any Orca mutation, load `$orca-cli` and `$orchestration`, resolve the
installed executable, run JSON status, and load the version-matched CLI and
orchestration guides. Use only their documented commands. Stop on unavailable
runtime, missing capability, stale identity, or ambiguous ownership; do not
fall back to generic subagents, guessed flags, or another Orca binary.

## Supervised loop

1. Reconcile the approved Run Charter, project key, selected Run, dirty
   baseline, and candidate `HEAD`.
2. Create bounded Tasks with owned paths, protected paths, verification, and
   closure gates before launching ready workers.
3. Respect one writer per worktree/path and the configured writer limit.
4. Verify Task/Dispatch identity, changed paths, exact Git state, and fresh
   evidence after every worker report.
5. Route implementation evidence through `$orca-workflow-router`, run
   verification, dispatch a fresh independent reviewer, and route its
   disposition through bounded remediation.
6. Integrate only accepted Tasks in dependency order, then run exact-`HEAD`
   final verification and review before finishing.

## Installation and reload

This reference skill is installed at `$CODEX_HOME/skills/orca-project-control`
and mirrored for cross-runtime discovery under `~/.agents/skills`. Its detailed
protocol is in `references/control-protocol.md`; the composed
`$orca-project-main` and `$orca-workflow-router` skills must also be available
before their routes are used. It has no Python or service dependency. Start a
new Codex session after changing global `AGENTS.md` so the new routing block is
loaded.

## Required report

At each meaningful checkpoint record Project, Run, Control session, selected
executor and authority, active and completed Tasks/Dispatches, worktrees/
branches, candidate `HEAD`, verification, review route/status, blockers, open
gates, routed next event, and the next safe action. Leave no live Dispatch
ambiguous.

## Detailed protocol

See [`references/control-protocol.md`](references/control-protocol.md) for
project sweep, Run selection, Task briefs, worker/reviewer contracts,
remediation, recovery, and fail-closed rules.
