# Bootstrap contracts

These contracts bind role and context; they do not own Orca lifecycle state.

## Classification and precedence

Every session starts as `UNCLASSIFIED`. A current valid **Dispatch preamble**
is checked first and overrides bootstrap history. Next, a valid
`CONTROL_BOOTSTRAP` bound to a Run establishes `CONTROL`. Next, a valid
`PROJECT_BOOTSTRAP` bound to a Project Key establishes `PROJECT_LEAD`.
Without those proofs the session is `ORDINARY`. A root location alone is not
enough; root location, title, first-opened session, Codex usage, or another
terminal cannot establish an authority role. Ambiguity is read-only.

The six roles are:

| Role | Required evidence | Context boundary |
|---|---|---|
| `PROJECT_LEAD` | Project-Key-bound Project Bootstrap | broad project discovery, directed memory, and all relevant Runs read-only |
| `CONTROL` | Run-bound Control Bootstrap | selected Run, Charter, and minimal collision index |
| `IMPLEMENTER` | current implementer Dispatch preamble | Task Brief, owned paths, and required sources only |
| `REVIEWER` | current review Dispatch preamble | fresh Review Brief and exact candidate range |
| `INVESTIGATOR` | current read-only investigation Dispatch preamble | named investigation scope, read-only |
| `ORDINARY` | no valid authority evidence | no broad project memory by default |

## Dispatch proof boundary

A worker role requires a current valid Dispatch preamble that is **current/live**
with all identity fields below; role names, a root path, a title, or a prior
transcript are not proof:

```yaml
dispatch_preamble:
  role: IMPLEMENTER | REVIEWER | INVESTIGATOR
  project_key: "sample-project"
  run_id: "run-example"
  task_id: "task-example"
  dispatch_id: "dispatch-example"
  worktree: "C:\\Projects\\sample"
  branch: "feature/sample"
```

The preamble must be current/live, match the selected Run and owned worktree,
and map the role to the assigned Task. Missing, stale, malformed, or
conflicting identity proof is invalid and fails closed to the lower applicable
role or `ORDINARY` read-only behavior. An implementation or remediation Task
maps to `IMPLEMENTER`, an independent review maps to `REVIEWER`, and a bounded
read-only diagnosis maps to `INVESTIGATOR`.

## PROJECT_BOOTSTRAP

Required fields include `role: PROJECT_LEAD`, a non-empty `project_key`,
allowed repositories/worktrees, the broad-read-only context tier, directed
memory query policy, and the source-of-truth hierarchy. A root location
without a Project Key is invalid.

## CONTROL_BOOTSTRAP

Required fields include `role: CONTROL`, a non-empty `run_id`, the Run Charter,
the selected Run detail, and a minimal collision index for branch, worktree,
path, writer, coordinator, and concurrent integration conflicts. It includes
the read-only-over-candidates rule and one-Control-per-Run rule. Control may
inspect other Runs only for those collision classes, not their full history.

## Worker and reviewer boundaries

An `IMPLEMENTER` receives only a Task Brief: identity, objective, required
sources, owned worktree/branch/paths, pre-existing dirty state, behavior,
acceptance, plausible wrong implementation, focused verification, forbidden
actions, and expected completion report. It receives no Mem0, project graph,
or superior transcript.

A `REVIEWER` receives only a Review Brief with `base_sha` and `head_sha`
frozen to the candidate, contract references, fresh verification evidence,
and the `ACCEPT`, `CHANGES_REQUESTED`, or `BLOCKED` disposition. It must be a
fresh session that did not implement the candidate.

## Source and safety rules

Orca and Git observations override approved documents, Registry/Ledger,
semantic memory, and reports. Mem0 is directed semantic context only. The
global patch is versioned separately and is not applied here. Credentials,
tokens, authenticated URLs, raw PII, and private data are forbidden in
bootstrap contracts. Protected native skills are not copied and remain
unchanged.
