# `orca-project-memory-routing` — Design (Run 0 contract freeze)

**Status:** frozen for implementation, **gate pending** — the Run 0 gate is
`BLOCKED/OPEN_FOR_HUMAN_DECISION` (see §13). Writer Runs 1–4 must not start
until the gate is satisfied. This document is the shared, implementation-ready
design produced by the read-only Run 0.

**Document type:** design spec. Progressive disclosure: high-level intent
first, exact contracts after.

---

## 1. Purpose and non-goals

### Purpose

Connect existing Orca/Codex skills into a single workflow/memory router with
**only two new skills** (`skills/orca-project-main/**` and
`skills/orca-workflow-router/**`) plus a **minimal later patch** to the
existing `skills/orca-project-control/SKILL.md` (owned by Run 3, delimited by
exact markers), backed by one `AGENTS.md` role-router document and two
bootstrap-contract documents under `docs/orca-project-memory/`.

Roles route by **current, valid evidence**: a live Orca Dispatch preamble
(`IMPLEMENTER`/`REVIEWER`/`INVESTIGATOR`), a Run-bound `CONTROL_BOOTSTRAP`
(`CONTROL`), a Project-Key-bound `PROJECT_BOOTSTRAP` (`PROJECT_LEAD`), else
`ORDINARY`. Ambiguity fails closed into read-only behavior.

### Non-goals

This is **not** a framework, service, daemon, broker, database, MCP server,
or new lifecycle store. It does not:

- create a second lifecycle database, or let Mem0/registry/ledger own Run/Task
  status, branch/worktree, dirty state, HEAD, worker liveness, review
  acceptance, or CI;
- copy or modify native Orca skills (`$orca-cli`, `$orchestration`) or any
  protected skill;
- absorb `orca-project-control` into either new skill (Run 3 owns only a
  minimal, marker-delimited patch to the existing Control skill);
- route `$sdd-cmdc-opencode` (legacy) or Pi (not adopted in v1);
- run real AgY, Command Code, or OCR as part of unit tests;
- claim acceptance from task creation, process exit, terminal handle,
  accepted PTY input, or self-report.

---

## 2. Invariants

1. **Observed state always overrides memory.** Live Orca (Runs/Tasks/
   Dispatches/messages/gates/worker state), then live Git (branch, worktree,
   dirty state, diff, exact HEAD), then behavior evidence (tests, linters,
   build, CI) override any design, plan, registry, ledger, Mem0 note, report,
   or checkpoint.
2. **Source-of-truth hierarchy** (used in both documents and by all writers):
   1. Orca (live Runs, Tasks, Dispatches, messages, gates, worker state);
   2. Git (repository, branch, worktree, dirty state, diff, exact HEAD);
   3. tests, linters, build, CI (behavior evidence);
   4. approved designs, plans, ADRs, briefs (intent and scope);
   5. Project Registry and Work Ledger (explicit relations/classification,
      discovery hints);
   6. Mem0 (semantic preferences, historical decisions, relations);
   7. reports and checkpoints (handoff/legibility only — never sole
      authority).
3. **Native Orca owns Run/Task/Dispatch lifecycle.** Windows-native
   operation, exact preambles/IDs, worker completion evidence, and no silent
   fallback are required. A worker's exit code, a terminal handle, an accepted
   PTY input, a self-reported SUCCESS, or a missing/empty result is **not**
   acceptance. Acceptance requires identity, fresh Git state, artifact/diff,
   validation, and independent evidence.
4. **No executor substitution.** Missing/invalid executor blocks only
   dispatch and requests Victor's choice (`executor_policy.automatic_fallback:
   false`). AgY failure never selects Command Code; Command Code failure never
   selects AgY. `EXECUTOR_UNAVAILABLE` preserves state and asks Victor for a
   new decision.
5. **Ambiguity fails closed** into read-only behavior. Root location,
   first-opened session, Codex usage, broad context, title, or another
   terminal never proves PROJECT_LEAD or CONTROL.
6. **Fresh sessions for authority roles.** REVIEWER is a fresh session that
   did not implement the candidate. A review pinned to an old HEAD is
   stale/blocked for final acceptance.
7. **Bounded remediation.** Remediation is bounded by the project contract;
   findings are adjudicated via `$receiving-code-review` and routed as a
   remediation Dispatch to an implementer.
8. **Idempotent, reversible global patch.** The marked global router block
   is delimited exactly by `<!-- ORCA-PROJECT-ROUTER:BEGIN -->` /
   `<!-- ORCA-PROJECT-ROUTER:END -->`; removing the block restores previous
   content.
9. **No credentials, authenticated URLs, tokens, or raw PII** in artifacts,
   fixtures, or memory.

---

## 3. Role precedence and context tiers

### Classification (exact)

Roles: `PROJECT_LEAD`, `CONTROL`, `IMPLEMENTER`, `REVIEWER`, `INVESTIGATOR`,
`ORDINARY`.

Every session begins `UNCLASSIFIED`. Precedence is exactly:

1. a **current valid Orca Dispatch preamble** establishes `IMPLEMENTER`,
   `REVIEWER`, or `INVESTIGATOR`;
2. a valid `CONTROL_BOOTSTRAP` bound to a Run establishes `CONTROL`;
3. a valid `PROJECT_BOOTSTRAP` bound to a Project Key establishes
   `PROJECT_LEAD`;
4. otherwise `ORDINARY`.

Dispatch preamble always wins over prior transcript/history. Root location,
first-opened session, Codex usage, broad context, title, or another terminal
never proves PROJECT_LEAD or CONTROL. Ambiguity fails closed into read-only
behavior.

### Context tiers

Use broad project-wide context only at PROJECT_LEAD. Below it use minimum
sufficient context. Never transfer a superior session transcript downward.

- **PROJECT_LEAD:** broad read-only project sweep, all relevant Runs,
  branches/worktrees, directed Mem0 queries, Victor preferences, and project
  relations.
- **CONTROL:** selected Run in detail plus Run Charter and a minimal collision
  index. May query other Runs only for branch/worktree/path/writer/
  coordinator/integration collisions. One Control per Run; it does not edit
  candidates.
- **IMPLEMENTER:** only its Task/Dispatch brief, owned worktree/branch/paths,
  required sources, acceptance and verification.
- **REVIEWER:** only its review Task/Dispatch and Review Brief pinned to exact
  `base_sha`/`head_sha`; a fresh session that did not implement the candidate.
- **INVESTIGATOR:** only the named investigation scope and evidence sources.
- **ORDINARY:** no broad project memory or Run context by default.

---

## 4. Mem0 interface and policy

- Mem0 is **semantic only**: Victor preferences, style, accepted decisions,
  rejected alternatives and reasons, project relations, legacy/superseded
  components when explicitly marked, and recurring workflow conventions.
- Queries are **directed** (by PROJECT_LEAD); no unrestricted ingest; no
  secrets/PII.
- Mem0 **never owns** Run/Task status, current branch/worktree, dirty state,
  HEAD, worker liveness, current review acceptance, or CI — no second
  lifecycle database.
- **Unavailable:** PROJECT_LEAD degrades to Orca/Git factual discovery
  **without inventing memory** (test case 26).
- Age alone never marks a branch legacy (test case 27).

---

## 5. Project Registry and Work Ledger

- Reuse a compliant existing file-backed Registry/Work Ledger if found.
- If none exists, the minimum non-service fallback is
  `%USERPROFILE%\.codex\project-memory\registry.yaml` plus
  `projects/<project_key>.yaml`. The repository may contain **schemas,
  examples, and validation only** — never real user data.
- The registry/ledger records relations and explicit classification; it never
  replaces live Orca/Git and is never authoritative for lifecycle state
  (rollback preserves it as non-authoritative data).

### Registry schema (fallback baseline)

```yaml
schema_version: 1
projects:
  - project_key: ""          # e.g. "orca-project-memory-routing"
    related_projects: []     # relation list: other project keys + relation type
    classification: active | paused | blocked | completed | abandoned | superseded | legacy | experimental | unmanaged
    memory_provider: mem0 | unavailable
    notes: []                # semantic-only notes; explicit "legacy/superseded" markers required
```

### Work Ledger schema (fallback baseline)

```yaml
schema_version: 1
work_entries:
  - id: ""                   # Run/Task/Dispatch id mirror (never authoritative; Orca owns)
    kind: run | task | dispatch
    project_key: ""
    status: ""               # mirror of live Orca status; observed Orca state overrides
    relation_refs: []        # explicit relations (blocked_by, depends_on, collision_group)
    evidence_refs: []        # paths/ids of completion artifacts, if any
```

---

## 6. Project Snapshot (compact, frozen)

```yaml
project_snapshot:
  project_key: ""
  repositories: []
  related_projects: []
  memory:
    provider: mem0 | unavailable
    relevant_preferences: []
    relevant_decisions: []
    confidence_notes: []
  runs:
    - id: ""
      objective: ""
      status: ""
      coordinator: ""
      candidate_head: null
      next_safe_action: ""
  worktrees:
    - path: ""
      branch: ""
      head: ""
      dirty: false
      classification: active | paused | blocked | completed | abandoned | superseded | legacy | experimental | unmanaged
      evidence: []
  open_questions: []
  recommended_next_objectives: []
```

Rules: `dirty` and `head` come from live Git only; `status` mirrors live Orca
only; classification uses the exact enum above (`legacy` requires an explicit
marker, never age alone); `evidence` lists artifact/diff/validation
references.

---

## 7. Run Charter

- `schema_version: 1`; project and work identity; objective and why-now.
- Exact repository / branch / HEAD / worktree / dirty-state baseline
  (observed Git).
- Explicit Victor executor choice (policy below).
- Relevant memory/decisions (directed Mem0 query results, with
  confidence notes).
- In-scope and out-of-scope; protected paths; acceptance and verification.
- Required fresh review using `open-code-review-delegate`.
- Rollback (see §11).

```yaml
run_charter:
  schema_version: 1
  run_id: ""
  project_key: ""
  work_slug: ""
  objective: ""
  why_now: ""
  repository: ""            # canonical repo path/URL
  branch: ""
  base_sha: ""
  head_sha: ""
  worktree: ""              # path
  dirty_baseline: {}        # pre-existing dirty state at charter time
  executor_policy:
    selected_by: victor
    value: agy | command-code
    automatic_fallback: false
    task_override: user_only
  relevant_memory: []       # directed Mem0 results with confidence notes
  relevant_decisions: []
  in_scope: []
  out_of_scope: []
  protected_paths: []       # skills listed in §10; native Orca skills
  acceptance: []            # evidence rules; fresh review via open-code-review-delegate
  verification: []
  rollback: []              # see §11
```

---

## 8. Bootstrap and brief contracts

### PROJECT_BOOTSTRAP (binds to a Project Key → PROJECT_LEAD)

Must contain: `role: PROJECT_LEAD`, `project_key`, allowed repositories/
worktrees (read-only sweep), context tier grant (broad), directed Mem0 query
policy, and the source-of-truth hierarchy. Bound to a Project Key — a bare
title/root location is invalid.

### CONTROL_BOOTSTRAP (bound to a Run → CONTROL)

PROJECT_LEAD uses `$orca-cli` to start a dedicated CONTROL session and passes
only curated `CONTROL_BOOTSTRAP` plus the Run Charter. It does **not** create
implementation Tasks or Dispatches. Must contain: `role: CONTROL`, `run_id`,
Run Charter, minimal collision index (branch/worktree/path/writer/
coordinator/integration), read-only rule over candidates, one-Control-per-Run
rule.

### Task Brief (every implementer Task)

Contains only: role; Project/Run/Task/Dispatch identity; objective; required
sources; owned worktree/branch/paths; protected paths and pre-existing dirty
state; behavior; acceptance; plausible wrong implementation; focused
verification; forbidden actions; expected completion report.

### Review Brief

Must contain:

```yaml
role: REVIEWER
review_skill: open-code-review-delegate
project_id: ""
run_id: ""
implementation_id: ""       # Task/Dispatch reviewed
review_id: ""
repository: ""
worktree: ""
base_sha: ""                # exact
head_sha: ""                # exact
business_context: []
contract_refs: []           # this design + Run Charter + Task Brief
verification_evidence: []   # fresh, reproduced
forbidden_actions:
  - edit the candidate
  - widen scope
  - create workers
  - approve without accounting for every reviewable file
disposition: ACCEPT | CHANGES_REQUESTED | BLOCKED
```

A review pinned to an old HEAD is stale/blocked for final acceptance.

---

## 9. Workflow events and routing transitions (exact)

### Event set (frozen, exact)

`RUN_CHARTER_ACCEPTED`, `TASK_READY`, `IMPLEMENTATION_REPORTED`,
`VERIFICATION_PASSED`, `VERIFICATION_FAILED`, `REVIEW_ACCEPTED`,
`REVIEW_CHANGES_REQUESTED`, `REVIEW_BLOCKED`, `REMEDIATION_REPORTED`,
`ALL_TASKS_ACCEPTED`, `FINAL_VERIFICATION_PASSED`,
`FINAL_REVIEW_ACCEPTED`, `FINAL_REVIEW_CHANGES_REQUESTED`,
`EXECUTOR_UNAVAILABLE`.

### Transitions (frozen, exact)

| # | Event / condition | Routing behavior |
|---|---|---|
| T1 | `RUN_CHARTER_ACCEPTED` | Validate explicit executor (see §9.1) and decompose into Tasks. |
| T2 | `TASK_READY` + executor `agy` | Call `$delegate-to-agy`. |
| T3 | `TASK_READY` + executor `command-code` | Call `$commandcode-delegate`. |
| T4 | `TASK_READY` + missing/invalid executor | Block **only dispatch**; request Victor's choice; never choose or silently substitute an executor. |
| T5 | `IMPLEMENTATION_REPORTED` | Apply `$verification-before-completion`; reproduce fresh evidence (identity, Git state, artifact/diff, validation). |
| T6 | `VERIFICATION_PASSED` | Create a fresh independent REVIEWER Task/Dispatch. |
| T7 | `VERIFICATION_FAILED` | Preserve the failure and return only the bounded remediation transition. |
| T8 | reviewer start | Load `$open-code-review-delegate`; do not copy OCR logic. |
| T9 | `REVIEW_ACCEPTED` | Accept the Task; release dependents. |
| T10 | `REVIEW_CHANGES_REQUESTED` | Invoke `$receiving-code-review` for findings; adjudicate; create a remediation Dispatch to an implementer. |
| T11 | `REVIEW_BLOCKED` | Preserve the blocked review and request the next human decision; do not self-accept. |
| T12 | `REMEDIATION_REPORTED` | Reverify and perform **scoped** re-review. |
| T13 | `ALL_TASKS_ACCEPTED` | Final verification plus **whole-branch** review. |
| T14 | `FINAL_VERIFICATION_PASSED` | Permit the final review transition for the current candidate. |
| T15 | `FINAL_REVIEW_ACCEPTED` | Call `$finishing-a-development-branch` **only when** the review is valid for the current HEAD. |
| T16 | `FINAL_REVIEW_CHANGES_REQUESTED` | Route findings through the bounded remediation path and reverify. |
| T17 | `EXECUTOR_UNAVAILABLE` | Preserve state; ask Victor for a new decision; **no automatic fallback**. |

### Concurrency and staleness rules

- Independent Tasks may continue while a local review is pending; **only
  dependent transitions are blocked** (test case 25).
- A final review for an old HEAD is stale/blocked (test case 23).
- Verification failure returns to remediation scope, never to silent
  self-approval.

---

## 10. Ownership, waves, and protected boundaries

### Run ownership (exact)

| Run | Owns | Must not touch |
|---|---|---|
| Run 1 | `skills/orca-project-main/**` only | everything else |
| Run 2 | `skills/orca-workflow-router/**` only | everything else |
| Run 3 | minimal Control change + `docs/orca-project-memory/AGENTS-role-router.md` + `docs/orca-project-memory/bootstrap-contracts.md` | no other existing skill; prepares the global patch below |
| Run 4 | `tests/orca-project-memory-routing/**` only, under the repository's real test convention | everything else |

### Global patch (prepared by Run 3, applied in migration §11)

Delimited exactly by:

```text
<!-- ORCA-PROJECT-ROUTER:BEGIN -->
...
<!-- ORCA-PROJECT-ROUTER:END -->
```

Idempotent (test case 32); removing the block restores previous content
(test case 33).

### Waves and concurrency

- Run 1 and Run 2 are **parallel** after the Run 0 gate.
- Run 3 and Run 4 are **parallel** after the first wave.
- Maximum concurrent writers: **2**; no two writers share a worktree or dirty
  path; serialize path conflicts.
- Control's canonical source/path must be resolved before Run 3 starts.

### Protected paths (must remain unchanged except the scoped Control patch)

`$delegate-to-agy`, `$commandcode-delegate`, `$orca-cli`, `$orchestration`,
`$open-code-review-delegate`, `$open-code-review`,
`$receiving-code-review`, `$verification-before-completion`,
`$finishing-a-development-branch`. Do not copy or modify native Orca skills.

---

## 11. Migration, rollback, and gates

### Migration (gradual)

1. add the two new skills (Run 1, Run 2);
2. make the minimal Control patch (Run 3);
3. add tests (Run 4);
4. prepare the marked global block (Run 3) and apply it;
5. start a new session;
6. run **one** controlled real pilot (only after integration and a new
   session);
7. only then consider broader use.

No DB or service migration is allowed.

### Rollback

- Remove the marked global block (`<!-- ORCA-PROJECT-ROUTER:BEGIN -->` …
  `<!-- ORCA-PROJECT-ROUTER:END -->`).
- Revert the minimal Control patch.
- Disable/remove the two new skills.
- Preserve registry/ledger as **non-authoritative** data.

### Run 0 gate

See §13. Writers must not start until the gate is satisfied.

---

## 12. Contract-test strategy (35 cases, frozen)

Prefer deterministic **text/schema/contract tests**; temp directories for
registry/ledger; **mocks for Orca/Git/Mem0**; no real paid services, no real
executor/OCR in unit tests; no writes outside test temp directories. One
controlled real pilot occurs only after integration and a new session.

| # | Case | Mapping / expectation |
|---|---|---|
| 1 | no bootstrap/Dispatch | → `ORDINARY`; no broad project memory |
| 2 | valid `PROJECT_BOOTSTRAP` | → `PROJECT_LEAD` (Project-Key-bound) |
| 3 | valid `CONTROL_BOOTSTRAP` | → `CONTROL` (Run-bound) |
| 4 | valid Dispatch overrides Project/Control bootstrap | preamble precedence wins |
| 5 | implementer Dispatch | → `IMPLEMENTER` |
| 6 | review Dispatch | → `REVIEWER` |
| 7 | read-only diagnosis Dispatch | → `INVESTIGATOR` |
| 8 | PROJECT_LEAD receives broad context | broad sweep, all relevant Runs, directed Mem0 |
| 9 | CONTROL receives Charter/current Run/collision index only | no broad context; read-only over candidates |
| 10 | worker receives no Mem0/project graph/superior transcript | minimum sufficient context |
| 11 | Charter without executor blocks implementation | `TASK_READY` blocked; Victor asked |
| 12 | `agy` routes to `$delegate-to-agy` | T2 |
| 13 | `command-code` routes to `$commandcode-delegate` | T3 |
| 14 | AgY failure never selects Command Code | no fallback; `EXECUTOR_UNAVAILABLE` path |
| 15 | Command Code failure never selects AgY | no fallback; `EXECUTOR_UNAVAILABLE` path |
| 16 | `IMPLEMENTATION_REPORTED` → verification | `$verification-before-completion`, fresh evidence |
| 17 | green verification → fresh reviewer | new independent REVIEWER Task/Dispatch |
| 18 | reviewer loads `$open-code-review-delegate` | load, not copy, OCR logic |
| 19 | findings → receiving-review plus remediation Dispatch | `REVIEW_CHANGES_REQUESTED` path |
| 20 | fix → reverify plus scoped re-review | `REMEDIATION_REPORTED` path |
| 21 | all Tasks accepted → final verification + final review | `ALL_TASKS_ACCEPTED` → whole-branch review |
| 22 | finishing without valid final review → blocked | `$finishing-a-development-branch` gated |
| 23 | final review for old HEAD → stale/blocked | pinned `base_sha`/`head_sha` mismatch |
| 24 | valid final review for current HEAD → finishing allowed | T12 precondition met |
| 25 | pending local review blocks only dependent work | independent Tasks continue |
| 26 | Mem0 unavailable degrades without invented memory | Orca/Git factual discovery only |
| 27 | age alone never marks a branch legacy | explicit marker required |
| 28 | `sdd-cmdc-opencode` never appears in active routing | excluded; legacy |
| 29 | Pi never appears in active routing | not adopted in v1 |
| 30 | native Orca skills are not copied/modified | `$orca-cli`, `$orchestration` protected |
| 31 | no more than two writer Runs concurrently | wave rule; path conflicts serialized |
| 32 | global router patch is idempotent | re-applying BEGIN/END block is a no-op |
| 33 | removing the global block restores previous content | exact reverse of the patch |
| 34 | Windows paths, CRLF, and PowerShell quoting | contract text tests cover path/quoting forms |
| 35 | fixtures contain no credentials or real private data | static scan / schema check |

---

## 13. Run 0 gate and unresolved dependencies

### Gate verdict: `BLOCKED / OPEN_FOR_HUMAN_DECISION`

Honest status — the required Run 0 investigators (Tasks 0A–0D: Orca native,
current skills/routing, Mem0/registry/project state, current review) have
**no valid completion evidence** (failed Dispatch attempts, no result, no
`worker_done`; the 0A repair/retry also stalled). Therefore Run 0 must not be
marked complete or accepted, and no Victor approval of this design is claimed
or implied. The binding source brief supplies the requirements; a human gate
remains before writer Runs 1–4.

### Required checks before writer Runs may start

- Root/Git clear (branch, HEAD, dirty state, `.agy/**` preserved).
- Existing skill contracts read (complete protected-skill reads; the 0B
  investigation must finish).
- Live Orca surface loaded (executable, version, `$orca-cli`/
  `$orchestration` guides).
- Owned paths non-colliding.
- No new framework/service/lifecycle store introduced.
- `sdd-cmdc-opencode` and Pi excluded.
- Victor approval of this design, with no conflict against binding decisions.

### Unresolved dependency

The canonical source/path of `skills/orca-project-control/SKILL.md` is
**unresolved** in this worktree (path absent; canonical location outside the
checkout unknown). Run 3 cannot start until it is resolved. Control is not
absorbed into either new skill; Run 3's patch is minimal and marker-delimited.

---

## Appendix — exact identifiers used above

- Roles: `PROJECT_LEAD`, `CONTROL`, `IMPLEMENTER`, `REVIEWER`,
  `INVESTIGATOR`, `ORDINARY`.
- Router markers: `<!-- ORCA-PROJECT-ROUTER:BEGIN -->`,
  `<!-- ORCA-PROJECT-ROUTER:END -->`.
- Events: `RUN_CHARTER_ACCEPTED`, `TASK_READY`, `IMPLEMENTATION_REPORTED`,
  `VERIFICATION_PASSED`, `VERIFICATION_FAILED`, `REVIEW_ACCEPTED`,
  `REVIEW_CHANGES_REQUESTED`, `REVIEW_BLOCKED`, `REMEDIATION_REPORTED`,
  `ALL_TASKS_ACCEPTED`, `FINAL_VERIFICATION_PASSED`,
  `FINAL_REVIEW_ACCEPTED`, `FINAL_REVIEW_CHANGES_REQUESTED`,
  `EXECUTOR_UNAVAILABLE`.
- Executor policy: `selected_by: victor`; `value: agy | command-code`;
  `automatic_fallback: false`; `task_override: user_only`.
