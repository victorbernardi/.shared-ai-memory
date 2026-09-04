# Versioned global role-router patch

This file is a versioned payload for a later integration step. It is not the
user profile `AGENTS.md` and is not applied by the inline implementation.

<!-- ORCA-PROJECT-ROUTER:BEGIN -->
## Orca project-memory role routing

Classify every session as `UNCLASSIFIED` before applying this precedence:

1. A current valid Orca Dispatch preamble establishes `IMPLEMENTER`,
   `REVIEWER`, or `INVESTIGATOR`.
2. A valid Run-bound `CONTROL_BOOTSTRAP` establishes `CONTROL`.
3. A valid Project-Key-bound `PROJECT_BOOTSTRAP` establishes `PROJECT_LEAD`.
4. Otherwise the session is `ORDINARY`.

Sem bootstrap válido, a sessão permanece `ORDINARY` e read-only.

Dispatch precedence overrides bootstrap history. Root location, title, first
session, Codex usage, broad context, and another terminal never establish
`PROJECT_LEAD` or `CONTROL`. Ambiguity fails closed into read-only behavior.

A worker role is valid only with a current/live Dispatch preamble carrying
`role`, `project_key`, `run_id`, `task_id`, `dispatch_id`, `worktree`, and
`branch`, matched to the assigned Task. Missing, stale, malformed, or
conflicting Dispatch proof is invalid; do not infer a worker from the root,
title, transcript, or terminal.

- `PROJECT_LEAD` may load `$orca-project-main` for broad read-only discovery,
  but does not create Tasks or Dispatches.
- `CONTROL` may load `$orca-project-control` and
  `$orca-workflow-router` only with a valid Run-bound bootstrap.
- An implementer follows only its Task Brief and selected executor Dispatch;
  it receives no superior transcript or broad memory.
- A `REVIEWER` is a fresh session and loads the review skill named in its
  Review Brief, normally `$open-code-review-delegate`.
- Broad memory is prohibited below `PROJECT_LEAD`.
- `CONTROL` does not implement or edit the candidate.

The block is idempotent: applying a document that already contains this
BEGIN/END block is a no-op. Removing exactly this block restores the prior
content. Native skills remain protected, not copied, and unchanged.
<!-- ORCA-PROJECT-ROUTER:END -->
