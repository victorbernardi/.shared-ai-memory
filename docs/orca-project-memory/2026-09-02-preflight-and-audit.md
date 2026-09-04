# Run 0 Preflight and Audit — `orca-project-memory-routing`

**Status:** `BLOCKED / OPEN_FOR_HUMAN_DECISION` (Run 0 gate pending — do not
start writer Runs 1–4)

**Document type:** factual preflight and audit for the Run 0 gate of the
`orca-project-memory-routing` program. Documentation-only artifact.

---

## 1. Timestamp and context

- Audit date: **2026-09-02** (audit written 2026-09-02 03:29 local,
  UTC-03:00).
- Worktree: `C:\Projetos\Inova.maquinas.worktrees\.shared-ai-memory\feat-PROJECT_LEAD`.
- Branch: `feat/PROJECT_LEAD`.
- HEAD at audit: `82c75f2e1f370a5b147f4d33b6597db6d5faa05d` — **verified** by
  `git rev-parse HEAD`.
- Program: Run 0 of `orca-project-memory-routing` — audit and contract freeze
  for a workflow/memory router connecting existing Orca/Codex skills through
  two new skills and a minimal later patch to
  `skills/orca-project-control/SKILL.md`.
- This run is **read-only discovery plus a shared design**. It creates
  planning, audit, and design artifacts only; it does not implement skills,
  tests, or runtime patches.

Item labels: **[fact]** verified in this worktree/session; **[inference]**
reasoned from verified facts; **[open]** unresolved question or gate.

---

## 2. Scope and non-goals

**Scope of Run 0 (this audit):**

- Verify repository/branch/HEAD/dirty state.
- Inventory discovered AGENTS files and skills relevant to routing.
- Record live Orca evidence (status reachable, executable, version, guides).
- Record Run 0 Run/Task/Dispatch statuses honestly, including missing
  `worker_done`.
- Audit Mem0 / Registry / Work Ledger findings.
- Audit review/verification findings.
- Audit path ownership and collisions against the Run 1–4 ownership plan.
- Freeze the shared design in
  `docs/superpowers/specs/2026-09-02-orca-project-memory-routing-design.md`.
- Report the Run 0 gate table, including open gates.

**Non-goals (Run 0 does not):** implement or edit production skills; write
tests; write runtime code; edit global instructions (`~/.codex/AGENTS.md` or
any ancestor AGENTS.md); touch Orca configuration; create implementation
Tasks/Dispatches; start writers; run real AgY/Command Code/OCR; commit,
stage, reset, clean, merge, push, publish, or delete.

---

## 3. Repository / branch / HEAD / dirty state

- **[fact]** Repository root: `C:\Projetos\Inova.maquinas.worktrees\.shared-ai-memory\feat-PROJECT_LEAD`.
- **[fact]** Current branch: `feat/PROJECT_LEAD` (`git branch --show-current`).
- **[fact]** HEAD: `82c75f2e1f370a5b147f4d33b6597db6d5faa05d`
  (`git rev-parse HEAD`).
- **[fact]** Working tree at audit time: clean except for one pre-existing
  untracked control directory, `.agy/`. `git status --short` output:
  `?? .agy/`.
- **[fact]** `.agy/` must be preserved byte-for-byte; it was not inspected and
  its receipts were not read or rewritten.
- **[fact]** HEAD commit subject: `fix(impeccable): ignore CSS comments in
  static scan` (recent history also shows two related `impeccable` fixes:
  `607b614` and `96c8e0d`). **Context is advisory** — the effective contract is
  the binding source brief, not git history.
- **[fact]** No target output file existed at audit time. The output directory
  `docs/orca-project-memory/` was empty, while `docs/superpowers/specs/`
  contained only the unrelated prior design document
  `docs/superpowers/specs/2026-08-23-inova-refresh-skills-canonical-design.md`.
  This run creates the two new documents.
- **[inference]** Because the tree is clean at HEAD and `.agy/` is a control
  directory (untracked, pre-existing), later writer runs may rely on a clean
  baseline for their owned paths; any dirty path must be preserved and
  reported by the writer owning it.
- **[open]** None for repo state; state is fully verified.

**Top-level layout (verified):** `.agy/` (untracked), `.codex/` (contains
`hooks.json` only), `.cursor/`, `.grok/`, `.superpowers/`, `docs/` (with
`orca-project-memory/` and `superpowers/specs|plans/`), `skills/`, plus
`.git`, `.gitignore`, `audit_result.json`, `pytest.ini` (pytest configured
with `--import-mode=importlib`).

---

## 4. Discovered AGENTS files and skills

### AGENTS.md discovery

- **[fact]** The repository/ancestor scan found **no competing local
  `AGENTS.md`** in this worktree (glob `**/AGENTS.md` returned nothing inside
  the worktree).
- **[fact]** The global `~/.codex/AGENTS.md` **is present** (existence check
  only — not read, not changed, outside this worktree). It contains general
  project/data instructions, not this new router. **[inference]** The audit
  was instructed that the global file contains general instructions, not the
  new router; no local AGENTS.md role router competes. It must not be changed
  in Run 0.
- **[open]** Whether the canonical source of
  `skills/orca-project-control/SKILL.md` lives outside this worktree — the
  Control path/canonical source must be resolved before writer Run 3 starts.

### Skill inventory in this worktree (relevant to routing)

- **[fact]** Present (verified paths under `skills/`):
  - `orca-cli/` and `orchestration/` — **discovery stubs**, not usage guides.
    Frontmatter confirms the live, version-matched guide is served by the
    `orca` binary itself. Native Orca remains the owner of Run/Task/Dispatch
    lifecycle; stubs must not be copied or modified.
  - `sdd-cmdc-opencode/` — **legacy**; must not be routed, copied, or
    modified. (Frontmatter: implements SDD via delegated Open Code Review.)
  - Additional existing orchestration/review skills present in the tree,
    e.g. `verification-before-completion/`, `receiving-code-review/`,
    `finishing-a-development-branch/`, `requesting-code-review/`,
    `dispatching-parallel-agents/`, `using-git-worktrees/`,
    `executing-plans/`, `handoff/`, `triage/`, etc.
- **[fact]** **Absent** (glob `**/orca-project-{main,workflow-router,project-control}/**`
  returned nothing): `skills/orca-project-main`,
  `skills/orca-workflow-router`, and `skills/orca-project-control`. This is an
  **audit finding**: the target skills do not yet exist in this checkout —
  there is nothing to collide with today, but their absence is also not
  permission to absorb Control into either new skill. Run 3 explicitly owns a
  **minimal patch** to `skills/orca-project-control/SKILL.md`; the canonical
  source/path must be resolved before that writer starts.
- **[fact]** Protected existing skills and their contracts were identified for
  audit (present at `~/.commandcode/skills/` unless noted): `delegate-to-agy`,
  `commandcode-delegate`, `open-code-review-delegate`,
  `verification-before-completion`, `receiving-code-review`,
  `finishing-a-development-branch`, plus `orca-cli` (stub) and
  `orchestration` (stub) in-worktree.
  - `open-code-review` (parent of `open-code-review-delegate`) is **not
    installed** at `~/.commandcode/skills/open-code-review/` (presence check
    only). This is recorded as an audit fact; it does not change the routing
    design, which routes reviewers through `open-code-review-delegate`.
- **[fact]** `$orca-cli` and `$orchestration` stubs exist in-worktree and are
  the correct entry points into native Orca surfaces; native Orca skills must
  not be copied or modified.

---

## 5. Live Orca evidence

- **[fact]** Selected Orca executable:
  `C:\Users\victor.bernardi\AppData\Local\Programs\orca\resources\bin\orca.cmd`.
- **[fact]** Live Orca status was reachable and ready; app version `1.4.190`.
- **[fact]** Live guides for `$orca-cli` and `$orchestration` were loaded
  (native Orca reference for the CLI and orchestration surfaces).
- **[fact]** The current feature worktree is registered in Orca and has a live
  original terminal (Windows-native operation).
- **[inference]** Native Orca remains the owner of Run/Task/Dispatch
  lifecycle: Windows-native operation, exact preambles/IDs, worker completion
  evidence, and no silent fallback are required.
- **[fact]** Opaque runtime IDs are not reproduced here because they are not
  necessary to explain the evidence; no credentials or secrets are recorded in
  this audit.

---

## 6. Run 0 / Task / Dispatch table (honest statuses)

**Program:** Run 0 — objective: *audit and contract freeze for
`orca-project-memory-routing`; read-only discovery; no writer implementation.*

**Verdict: the Run 0 investigations were NOT completed.** Task creation,
terminal creation, accepted PTY input, exit status, and stale summaries are
**not** completion evidence. No investigation produced a result or
`worker_done`.

| Item | Identity | Status | Evidence / notes |
|---|---|---|---|
| Run 0 | `orca-project-memory-routing` Run 0 | **OPEN** — must not be marked complete or accepted | Objective: audit and contract freeze. Read-only discovery; no writer implementation. |
| Task 0A | Orca native (live surface, Run/Task/Dispatch lifecycle, preamble/IDs, worker evidence, Windows-native, no fallback) | **FAILED dispatch, no result, no `worker_done`** | Investigation not completed. |
| Task 0B | Current skills / routing (stubs, protected skills, `sdd-cmdc-opencode` legacy) | **FAILED dispatch, no result, no `worker_done`** | Investigation not completed. |
| Task 0C | Mem0 / registry / project state | **FAILED dispatch, no result, no `worker_done`** | Investigation not completed. |
| Task 0D | Current review / verification | **FAILED dispatch, no result, no `worker_done`** | Investigation not completed. |
| Repair/retry 0A | Retry attempt for Task 0A | **FAILED — stalled prompt** | Repair/retry attempt failed; no result, no `worker_done`. |

**[fact]** All four investigation Tasks currently have failed Dispatch
attempts, no result, and no `worker_done`; a repair/retry attempt for 0A also
failed with a stalled prompt.
**[inference]** Because the required investigators have no valid completion
evidence, the Run 0 gate is **`BLOCKED/OPEN_FOR_HUMAN_DECISION`** (see §11
gate table). Run 0 must not be marked complete or accepted on the basis of
task creation, terminal creation, accepted PTY input, exit status, or stale
summaries.
**[open]** Whether the four investigations can be retried with a valid,
non-stalled dispatch and complete with real evidence (a human decision on
repair strategy is required; no retry is performed in this run).

### Executor-attempt evidence

- **[fact]** An earlier `$delegate-to-agy` attempt produced an **empty
  terminal error** and a **non-retryable `NEEDS_FOLLOWUP` receipt**.
- **[fact]** That attempt is **not delivery** and is **not an executor
  fallback**.
- **[fact]** Its control artifacts (`.agy/**`) are preserved byte-for-byte;
  not retried in Run 0.
- **[inference]** The failed AgY attempt does not evidence an executor choice
  for later Runs. Executor selection remains `selected_by: victor`,
  `automatic_fallback: false`, `task_override: user_only`; missing/invalid
  executor blocks only dispatch and requests Victor's choice.
- **[open]** Which executor Victor selects for each implementer Run remains an
  open decision pending at the gate.

---

## 7. Mem0 / Registry / Work Ledger findings

- **[fact]** No file-backed project-memory Registry or Work Ledger exists in
  this worktree (`docs/orca-project-memory/` is empty; no `registry.yaml` in
  `.codex/`; `.codex/` contains only `hooks.json`).
- **[fact]** The fallback path `%USERPROFILE%\.codex\project-memory\registry.yaml`
  is **not present** (existence check only).
- **[open]** Whether a compliant existing file-backed Registry/Work Ledger
  exists elsewhere (e.g. under a different profile path or an approved
  location outside this worktree) is unresolved. If none exists, the minimum
  non-service fallback is
  `%USERPROFILE%\.codex\project-memory\registry.yaml` plus
  `projects/<project_key>.yaml`, with the repository containing only
  schemas/examples/validation — never real user data.
- **[inference]** Mem0 status is unverified in this session; Run 0 had no
  completed investigator to query it. When Mem0 is unavailable, PROJECT_LEAD
  degrades to Orca/Git factual discovery without inventing memory. Mem0 is
  semantic only (preferences, accepted decisions, rejected alternatives,
  relations, explicitly marked legacy/superseded components, recurring
  conventions); it is never the owner of Run/Task status, branch/worktree,
  dirty state, HEAD, worker liveness, review acceptance, or CI.

---

## 8. Review and verification findings

- **[fact]** No review artifact exists for this Run 0 (the 0D investigation
  failed before producing findings). No reviewer Dispatch was created.
- **[fact]** Task creation, terminal creation, accepted PTY input, exit
  status, and self-reported SUCCESS are not acceptance; identity, fresh Git
  state, artifact/diff, validation, and independent evidence are required.
- **[inference]** The review/verification contract frozen in the design
  (fresh independent REVIEWER per green verification; final review pinned to
  the current HEAD; `REVIEW_ACCEPTED` / `REVIEW_CHANGES_REQUESTED` /
  `REVIEW_BLOCKED`; review routed through `$open-code-review-delegate`) is
  consistent with the evidence: no run has ever produced a reviewable
  artifact in this program yet.
- **[open]** Whether the existing `$open-code-review`-family parent skill is
  required on this machine for `$open-code-review-delegate` to run (its parent
  is not installed under `~/.commandcode/skills/open-code-review/`) — resolved
  by the reviewer writer (Run-3-wave) before first use; the design freezes the
  delegate as the only review route.

---

## 9. Path ownership and collision audit

| Run | Owned path(s) | Verified collision status |
|---|---|---|
| Run 1 | `skills/orca-project-main/**` | **[fact]** Absent today; no collision. Created only after the Run 0 gate. |
| Run 2 | `skills/orca-workflow-router/**` | **[fact]** Absent today; no collision. Created only after the Run 0 gate. |
| Run 3 | Minimal change to `skills/orca-project-control/SKILL.md`; `docs/orca-project-memory/AGENTS-role-router.md`; `docs/orca-project-memory/bootstrap-contracts.md` | **[fact]** Control path absent in-worktree; **[open]** canonical source/path unresolved — must be resolved before Run 3 starts. Docs paths are free (empty directory today). Run 3 must not modify any other existing skill. |
| Run 4 | `tests/orca-project-memory-routing/**` under the repository's real test convention | **[fact]** No such test directory today; pytest exists with `--import-mode=importlib`. **[open]** The real test convention must be confirmed by the Run 4 writer. |

- **[fact]** No two writers share a worktree or dirty path; maximum concurrent
  writers is 2 (Run 1 ∥ Run 2 after the Run 0 gate; Run 3 ∥ Run 4 after the
  first wave); path conflicts are serialized.
- **[inference]** The two output documents of Run 0
  (`docs/orca-project-memory/2026-09-02-preflight-and-audit.md` and
  `docs/superpowers/specs/2026-09-02-orca-project-memory-routing-design.md`)
  do not collide with any later Run's ownership.

---

## 10. Risks and open decisions

1. **[open]** Run 0 gate: required investigators have no valid completion
   evidence; four Tasks failed dispatch and the 0A repair retry stalled.
   Gate: **`BLOCKED/OPEN_FOR_HUMAN_DECISION`**. No claim of Victor approval of
   the design is made in this audit.
2. **[open]** Canonical source/path of `skills/orca-project-control/SKILL.md`
   unresolved; Run 3 cannot start without it. Control must not be absorbed
   into the two new skills.
3. **[open]** Executor choice per Run remains `selected_by: victor`, with
   `automatic_fallback: false`; a missing/invalid executor blocks only
   dispatch and requests Victor's choice.
4. **[open]** File-backed Registry/Work Ledger: none found in-worktree or at
   the fallback path; reuse a compliant existing one if found, else use the
   minimum non-service fallback (schemas/examples/validation only in the
   repository).
5. **[inference]** `open-code-review` parent absent under
   `~/.commandcode/skills/`; `open-code-review-delegate` present. Verify
   delegate operability before the first real review.
6. **[inference]** No new framework/service/daemon/broker/database/MCP
   server/lifecycle store is introduced by this design; Mem0 never owns
   lifecycle state. Observed state always overrides memory.
7. **[fact]** The binding source brief supplies the requirements (the
   user-provided program brief); a **human gate remains** before writer Runs
   1–4 start.

---

## 11. Run 0 gate table

| Gate check | Status | Evidence |
|---|---|---|
| Repository / Git clear (branch, HEAD, dirty state) | **MET** | `feat/PROJECT_LEAD` at `82c75f2e…`; only untracked `.agy/` (preserved byte-for-byte). |
| Root and output paths clear | **MET** | `docs/orca-project-memory/` and `docs/superpowers/specs/` free for the two output documents. |
| Existing skill contracts read | **MET (partial)** | `orca-cli`, `orchestration`, `sdd-cmdc-opencode` read (stubs confirmed). Protected-skill contracts identified; **[open]** full contract reads of every protected skill are the 0B investigation's job and did not complete. |
| Live Orca surface loaded | **MET** | Executable present; status reachable/ready; version `1.4.190`; live guides for `$orca-cli` and `$orchestration` loaded. |
| Paths non-colliding | **MET (today)** | Run 1–4 owned paths absent today; **[open]** canonical Control path unresolved. |
| No new framework/service/lifecycle store | **MET** | Design freezes two new skills + minimal Control patch; no DB/service/daemon. |
| `sdd-cmdc-opencode` and Pi excluded | **MET** | Legacy skill flagged; Pi not adopted; native Orca skills not copied or modified. |
| **Required investigators completed (0A–0D) with `worker_done`** | **NOT MET** | All four Tasks failed dispatch, no result, no `worker_done`; 0A repair retry stalled. |
| **Control path / canonical source resolved** | **NOT MET** | `skills/orca-project-control/SKILL.md` absent in-worktree; canonical location unresolved. |
| Victor approval / no conflict with binding decisions | **NOT MET (pending)** | Human gate remains; the binding source brief supplies the requirements; no approval claimed. |

**Run 0 gate verdict: `BLOCKED / OPEN_FOR_HUMAN_DECISION`.** Writer Runs 1–4
must not start until the gate is satisfied: the required investigators must
complete with valid evidence (`worker_done`), the missing Control
path/canonical source must be resolved, and Victor must approve the frozen
design with no conflict against binding decisions.

**Exit-gate requirements for a future accepted Run 0:** root/Git clear; all
existing skill contracts read; live Orca surface loaded; all owned paths
non-colliding; no new framework; `sdd-cmdc-opencode` and Pi excluded; Victor
approval of the design with no conflict against binding decisions.
