---
name: orca-project-main
description: Use when a valid Project-Key-bound PROJECT_BOOTSTRAP is present for an Orca project-wide discovery or project-lead coordination request.
metadata:
  version: "1.0.0"
  tier: "3"
  category: orchestration
---

# orca-project-main

## Role and entry condition

This skill is the `PROJECT_LEAD` capability. It is usable only after a valid
`PROJECT_BOOTSTRAP` binds the session to a `project_key`. A root location,
title, first-opened session, use of Codex, broad context, or another terminal
does not establish this role. Dispatch preambles and a valid
`CONTROL_BOOTSTRAP` have higher precedence; see the role-router references.

## Responsibility

Build a compact, factual Project Snapshot from the native Orca surface, Git,
directed semantic memory, and durable examples. The project-wide sweep is
read-only. `$orca-cli` and `$orchestration` are existing capabilities: use
`$orca-cli` for worktrees, terminals, and sessions, and use `$orchestration`
in read-only mode for Runs, Tasks, Dispatches, gates, and worker state.

The source-of-truth order is Orca, Git, tests/linters/build/CI, approved
designs/plans/briefs, Project Registry/Work Ledger, Mem0, then reports. Live
state always overrides memory. Mem0 is semantic context only; it never owns a
Run, Task, branch, worktree, dirty state, `HEAD`, worker liveness, review
acceptance, or CI result.

## Operating sequence

1. Validate the Project Key and the bootstrap contract.
2. Read the permitted broad project context without editing observed Runs or
   candidates.
3. Inspect live Orca state and Git branch, worktree, dirty paths, and exact
   `HEAD`.
4. Query Mem0 only for directed preferences, accepted decisions, project
   relations, explicit legacy/superseded markers, and related incidents.
5. Produce the Project Snapshot, distinguishing facts, inferences, and open
   questions. If Mem0 is unavailable, continue with Orca/Git factual discovery
   and mark semantic context as degraded; do not invent memory.
6. Discuss priorities with Victor. Only an explicit Victor choice may put
   `agy` or `command-code` in a Run Charter.
7. Produce the Run Charter and pass only a curated `CONTROL_BOOTSTRAP` plus
   that Charter to a new Control session through `$orca-cli`.

This skill does not create Tasks and does not dispatch implementation workers.
It does not transfer its transcript or broad memory to Control, implementers,
reviewers, investigators, or ordinary sessions.

## Outputs and boundaries

The required outputs are defined in:

- `references/context-scope.md`
- `references/memory-policy.md`
- `references/project-snapshot.md`
- `references/run-charter.md`
- `templates/PROJECT_BOOTSTRAP.md`
- `templates/CONTROL_BOOTSTRAP.md`

Use the example Registry and Work Ledger only as schemas/examples. They are
not a second lifecycle store, and real user data belongs outside the
repository under `%USERPROFILE%\\.codex\\project-memory\\` only when the
applicable contract permits it.

Protected Orca and review skills remain unchanged and are not copied into
this skill. Do not add a service, daemon, database, Pi route, or legacy
`$sdd-cmdc-opencode` route. Never place credentials, tokens, authenticated
URLs, raw PII, or private user data in a snapshot, template, fixture, or
report. Windows and PowerShell quoting, including CRLF files, must remain
safe and explicit.
