# Orca Project Memory Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the two new Orca project-memory skills, add the canonical repository Control package, their durable contract references and templates, the versioned role-router/bootstrap integration documents, and the deterministic contract suite without modifying protected Orca skills or the global `AGENTS.md`.

**Architecture:** `$orca-project-main` owns read-only project-wide discovery and produces a compact Project Snapshot plus a Victor-approved Run Charter. `$orca-workflow-router` consumes Run events and delegates lifecycle transitions to existing skills while Orca remains the lifecycle owner. The repository-relative `skills/orca-project-control/**` package is the canonical versioned Control source; promotion or global integration remains a separate gated action.

**Tech Stack:** Markdown skill contracts, YAML examples/templates, Python `pytest` contract tests, regular expressions and standard-library filesystem helpers only.

## Global Constraints

- This is a temporary inline implementation override only; it does not authorize global instruction changes, publication, merge, push, activation, or the real pilot.
- Create exactly two new routing skills: `skills/orca-project-main/**` and `skills/orca-workflow-router/**`; add the repository-relative canonical Control package separately.
- Preserve the existing Run 0 audit/design artifacts and all pre-existing dirty paths; do not overwrite them.
- Do not modify `$delegate-to-agy`, `$commandcode-delegate`, `$orca-cli`, `$orchestration`, `$open-code-review-delegate`, `$open-code-review`, `$receiving-code-review`, `$verification-before-completion`, or `$finishing-a-development-branch`.
- Do not create a second lifecycle store, service, daemon, database, paid-service fixture, Pi route, or `$sdd-cmdc-opencode` route.
- The role precedence is Dispatch preamble, then valid `CONTROL_BOOTSTRAP`, then valid `PROJECT_BOOTSTRAP`, then `ORDINARY`; ambiguity is read-only.
- Orca owns Run/Task/Dispatch lifecycle; Git owns branch/worktree/dirty state/HEAD; memory is semantic only.
- No global `AGENTS.md` edit is performed in this plan. The integration patch is only a versioned, idempotent marker-delimited document.
- The canonical Control source is the repository-relative `skills/orca-project-control/**`; use installed files as a read-only baseline and record the source decision without claiming global promotion.
- Tests must run without real Orca, AgY, Command Code, OCR, Mem0, network access, credentials, or writes outside pytest temporary directories.
- The final report must distinguish implementation evidence from runtime lifecycle evidence and must report the pre-existing full-suite `pandas` collection blocker.

---

## File Map

### New project-lead skill

- Create: `skills/orca-project-main/SKILL.md` — concise trigger, role boundary, workflow, output contract, and forbidden actions.
- Create: `skills/orca-project-main/references/context-scope.md` — role precedence and minimum-sufficient context matrix.
- Create: `skills/orca-project-main/references/memory-policy.md` — directed Mem0 policy, degraded mode, and registry/ledger authority boundary.
- Create: `skills/orca-project-main/references/project-snapshot.md` — compact snapshot schema and evidence/classification rules.
- Create: `skills/orca-project-main/references/run-charter.md` — Victor-selected executor and curated Control bootstrap contract.
- Create: `skills/orca-project-main/templates/PROJECT_BOOTSTRAP.md` — Project-Key-bound bootstrap template.
- Create: `skills/orca-project-main/templates/CONTROL_BOOTSTRAP.md` — Run-bound Control bootstrap template.
- Create: `skills/orca-project-main/templates/project-registry.example.yaml` — non-authoritative registry example.
- Create: `skills/orca-project-main/templates/project-ledger.example.yaml` — non-authoritative work-ledger example.

### New workflow router skill

- Create: `skills/orca-workflow-router/SKILL.md` — event-to-capability contract and routing boundaries.
- Create: `skills/orca-workflow-router/references/events-and-transitions.md` — complete frozen event set and transition table.
- Create: `skills/orca-workflow-router/references/executor-policy.md` — explicit AgY/Command Code choice and no-fallback behavior.
- Create: `skills/orca-workflow-router/references/review-routing.md` — verification, fresh reviewer, remediation, stale-HEAD, and finishing gates.
- Create: `skills/orca-workflow-router/templates/task-brief.md` — minimum implementer context.
- Create: `skills/orca-workflow-router/templates/review-brief.md` — exact-range fresh reviewer context.
- Create: `skills/orca-workflow-router/templates/completion-report.md` — evidence-bearing worker report.

### Versioned integration documents

- Create: `docs/orca-project-memory/AGENTS-role-router.md` — small idempotent global-router block, not applied to the user profile.
- Create: `docs/orca-project-memory/bootstrap-contracts.md` — six roles, bootstrap validation, precedence, and context boundaries.
- Create: `docs/orca-project-memory/control-canonical-source-decision.md` — repository source decision and promotion boundary.

### Canonical Control package

- Create: `skills/orca-project-control/SKILL.md` — repository version of the installed Control contract.
- Create: `skills/orca-project-control/references/control-protocol.md` — detailed Run-bound Control protocol.

### Contract tests

- Create: `tests/orca-project-memory-routing/test_contracts.py` — deterministic text/schema tests for the 35 frozen cases plus exact-schema, source, security-regex, and temporary-directory guards.

### Deliberately unchanged

- Do not modify `C:\Users\victor.bernardi\.codex\AGENTS.md`.
- Do not modify native or protected skills.

---

## Task 1: Establish the contract-test harness in RED

**Files:**
- Create: `tests/orca-project-memory-routing/test_contracts.py`
- Read: `docs/superpowers/specs/2026-09-02-orca-project-memory-routing-design.md`
- Read: `docs/orca-project-memory/2026-09-02-preflight-and-audit.md`

**Interfaces:**
- Consumes: the frozen role, event, ownership, migration, and rollback contracts from the Run 0 design.
- Produces: deterministic pytest assertions that fail because the new skill and integration files do not yet exist.

- [ ] **Step 1: Write the failing contract tests**

Create standard-library-only helpers that resolve `REPO_ROOT`, read UTF-8 files, assert required files, and parse only the contract text needed by each test. Add one focused test per behavior group, with explicit names for all 35 cases:

```python
def test_missing_bootstrap_routes_to_ordinary():
    router = _read("docs/orca-project-memory/AGENTS-role-router.md")
    assert "ORDINARY" in router
    assert "sem bootstrap" in router.lower()


def test_dispatch_precedence_and_six_roles_are_explicit():
    text = _all_contract_text()
    for role in ("PROJECT_LEAD", "CONTROL", "IMPLEMENTER", "REVIEWER", "INVESTIGATOR", "ORDINARY"):
        assert role in text
    assert text.index("Dispatch") < text.index("CONTROL_BOOTSTRAP")
    assert text.index("CONTROL_BOOTSTRAP") < text.index("PROJECT_BOOTSTRAP")


def test_project_main_contract_owns_read_only_snapshot_and_curated_control():
    text = _read("skills/orca-project-main/SKILL.md")
    for required in ("$orca-cli", "$orchestration", "Project Snapshot", "Run Charter", "read-only", "Mem0"):
        assert required in text
    assert "does not create Tasks" in text
    assert "does not dispatch" in text


def test_router_covers_every_frozen_event():
    text = _read("skills/orca-workflow-router/references/events-and-transitions.md")
    for event in FROZEN_EVENTS:
        assert event in text


def test_executor_policy_is_explicit_and_has_no_fallback():
    text = _read("skills/orca-workflow-router/references/executor-policy.md")
    assert "agy" in text and "command-code" in text
    assert "automatic_fallback: false" in text
    assert "never" in text.lower() and "fallback" in text.lower()
    assert "EXECUTOR_UNAVAILABLE" in text


def test_review_contract_keeps_verification_review_and_finishing_separate():
    text = _read("skills/orca-workflow-router/references/review-routing.md")
    for required in (
        "$verification-before-completion",
        "$open-code-review-delegate",
        "$receiving-code-review",
        "$finishing-a-development-branch",
        "base_sha",
        "head_sha",
        "stale",
    ):
        assert required in text


def test_protected_and_excluded_routes_are_not_active():
    text = _all_contract_text()
    assert "$sdd-cmdc-opencode" not in text
    assert "Pi" not in _active_route_lines(text)
    assert "second lifecycle" in text.lower()


def test_role_router_markers_are_exact_and_idempotent():
    text = _read("docs/orca-project-memory/AGENTS-role-router.md")
    assert text.count("<!-- ORCA-PROJECT-ROUTER:BEGIN -->") == 1
    assert text.count("<!-- ORCA-PROJECT-ROUTER:END -->") == 1
    assert text.index("<!-- ORCA-PROJECT-ROUTER:BEGIN -->") < text.index("<!-- ORCA-PROJECT-ROUTER:END -->")


def test_templates_for_windows_and_private_data_contracts():
    text = _all_contract_text()
    assert "PowerShell" in text or "Windows" in text
    assert "credential" in text.lower() or "token" in text.lower()
    assert "authenticated URL" in text or "PII" in text


def test_control_source_decision_is_repository_canonical_without_promotion_claim():
    decision = _read("docs/orca-project-memory/control-canonical-source-decision.md")
    assert "skills/orca-project-control/" in decision
    assert "canonical" in decision.lower()
    assert "promotion" in decision.lower()
    assert "not" in decision.lower()
```

The actual test file must enumerate the remaining cases explicitly rather than relying on a vague aggregate assertion: Mem0 degradation, age-not-legacy, worker context minimization, independent-review behavior, stale HEAD, one-pass remediation and `REPLAN_OR_SPLIT`, two-writer limit, native-skill protection, global-block removal, CRLF/PowerShell text, corrected security regexes, exact identity schemas, temporary-directory isolation, and fixture privacy.

- [ ] **Step 2: Run the focused tests and verify RED**

Run: `python -m pytest tests/orca-project-memory-routing/test_contracts.py -q`

Expected: collection succeeds and tests fail because the target skill and integration files are missing. If collection errors, fix only the test harness until it produces assertion failures; do not create production documents before a valid RED result.

- [ ] **Step 3: Check the baseline boundary**

Run: `python -m pytest -q`

Expected: the pre-existing collection failure for `skills/inova-parquet-to-excel/tests/test_convert.py` due to missing `pandas` remains separately recorded. Do not install dependencies or change unrelated tests as part of this task.

---

## Task 2: Implement `$orca-project-main` minimally

**Files:**
- Create: all nine files under `skills/orca-project-main/**` listed in the File Map.
- Test: `tests/orca-project-memory-routing/test_contracts.py`

**Interfaces:**
- Consumes: live Orca/Git evidence, directed Mem0 results when available, existing Registry/Work Ledger when compliant, and the Victor-approved objective.
- Produces: `Project Snapshot`, `Run Charter`, `PROJECT_BOOTSTRAP`, and curated `CONTROL_BOOTSTRAP`; no implementation Task or Dispatch.

- [ ] **Step 1: Write the failing project-main-specific assertions**

Extend the test file with exact required-file assertions and checks for: `role: PROJECT_LEAD`, `$orca-cli`, `$orchestration`, read-only sweep, Git branch/worktree/dirty/HEAD discovery, directed Mem0, degraded Mem0 mode, explicit legacy evidence, Victor executor choice, curated Control context, and no Task/Dispatch creation.

- [ ] **Step 2: Run the project-main tests to verify RED**

Run: `python -m pytest tests/orca-project-memory-routing/test_contracts.py -q -k project_main`

Expected: assertion failures identify missing files or missing contract terms.

- [ ] **Step 3: Write the minimal `SKILL.md`**

Use frontmatter with `name: orca-project-main` and a concise description. Keep the body procedural and progressive-disclosure-oriented. It must state, in this order:

1. valid `PROJECT_BOOTSTRAP` is required and bare root/title/first session never establishes the role;
2. `$orca-cli` and `$orchestration` are loaded as existing capabilities, with orchestration read-only for discovery;
3. Orca, Git, tests/CI, approved designs, Registry/Ledger, Mem0, and reports follow the frozen source-of-truth hierarchy;
4. the snapshot is factual, compact, and marks semantic context as degraded when Mem0 is unavailable;
5. Victor approves priorities and selects `agy` or `command-code` in the Run Charter;
6. the skill starts a dedicated Control session with curated bootstrap context and never creates implementation Tasks/Dispatches;
7. workers receive minimum sufficient context and no superior transcript;
8. protected paths, credentials, authenticated URLs, tokens, PII, Pi, and legacy `sdd-cmdc-opencode` are excluded.

- [ ] **Step 4: Add the references and templates**

Make the reference files carry the exact schema and policy details rather than duplicating a monolithic manual in `SKILL.md`. Use examples with synthetic project keys and empty collections; explicitly mark Registry/Ledger as non-authoritative. The Control template must include only the Run Charter, selected Run detail, minimal collision index, read-only rule, and one-Control-per-Run rule.

- [ ] **Step 5: Run focused project-main tests to verify GREEN**

Run: `python -m pytest tests/orca-project-memory-routing/test_contracts.py -q -k project_main`

Expected: all project-main assertions pass with no warnings or collection errors.

- [ ] **Step 6: Review the diff boundary**

Run: `git diff -- skills/orca-project-main tests/orca-project-memory-routing/test_contracts.py`

Expected: only project-main files and the contract test are present; no protected skill, global instruction, `.agy` receipt, or Run 0 document is modified.

---

## Task 3: Implement `$orca-workflow-router` minimally

**Files:**
- Create: all seven files under `skills/orca-workflow-router/**` listed in the File Map.
- Test: `tests/orca-project-memory-routing/test_contracts.py`

**Interfaces:**
- Consumes: a valid `CONTROL_BOOTSTRAP`, Run Charter, live Orca Run/Task/Dispatch state, and one frozen event.
- Produces: the next existing skill/capability to invoke; it does not implement, review, or persist lifecycle state.

- [ ] **Step 1: Write the failing router-specific assertions**

Add exact tests for all 14 frozen events and transitions, the `agy` and `command-code` routes, invalid/missing executor blocking, no automatic fallback, `worker_done` evidence requirements, fresh reviewer creation, findings/remediation, stale HEAD, independent-task continuation, and final finishing gate.

- [ ] **Step 2: Run the router tests to verify RED**

Run: `python -m pytest tests/orca-project-memory-routing/test_contracts.py -q -k router`

Expected: assertion failures identify missing router files or missing transitions.

- [ ] **Step 3: Write the minimal router skill and references**

The router skill must begin with its entry conditions (`CONTROL` only, valid Run-bound Control bootstrap) and then link to the event table, executor policy, and review routing reference. The transition reference must contain each exact event once in an unambiguous table. The executor reference must normalize conversational `cmdc` to `command-code`, state `automatic_fallback: false`, ask Victor on `EXECUTOR_UNAVAILABLE`, and route only `agy -> $delegate-to-agy` or `command-code -> $commandcode-delegate`. The review reference must load existing review/verification/finishing skills instead of copying their internals, allow one remediation pass, and route a second rejection or scope change to `REPLAN_OR_SPLIT`.

- [ ] **Step 4: Add the minimum Task/Review/Completion templates**

Task Brief fields: role, Project/Run/Task/Dispatch identity, Run Charter reference, selected implementation executor and user selection authority, objective, sources, owned worktree/branch/paths, protected paths and dirty baseline, behavior, acceptance, project closure gates, plausible wrong implementation, focused verification, forbidden actions, and expected report.

Review Brief fields: `role: REVIEWER`, `review_skill: open-code-review-delegate`, project/run/implementation/review IDs, implementation/review Dispatch IDs, repository/worktree/branch, exact `base_sha` and `head_sha`, business context, contract references, fresh verification evidence, forbidden actions, and `ACCEPT | CHANGES_REQUESTED | BLOCKED`.

Completion Report fields: identity, exact worktree/branch/HEAD, changed files, validation commands/results, worker completion evidence, blockers, and no-claim rule for absent evidence.

- [ ] **Step 5: Run focused router tests to verify GREEN**

Run: `python -m pytest tests/orca-project-memory-routing/test_contracts.py -q -k router`

Expected: all router assertions pass.

- [ ] **Step 6: Review the protected-route boundary**

Run: `git diff -- skills/orca-workflow-router`

Expected: the diff contains only the new router skill and references/templates; no OCR logic or protected-skill edits appear.

---

## Task 4: Implement the versioned role-router and bootstrap integration documents

**Files:**
- Create: `docs/orca-project-memory/AGENTS-role-router.md`
- Create: `docs/orca-project-memory/bootstrap-contracts.md`
- Test: `tests/orca-project-memory-routing/test_contracts.py`
- Read only: `docs/orca-project-memory/2026-09-02-preflight-and-audit.md`

**Interfaces:**
- Consumes: the role precedence, context-tier, bootstrap, and rollback contracts from the design.
- Produces: a versioned global-router patch payload and bootstrap reference documents; it does not edit the user profile `AGENTS.md`.

- [ ] **Step 1: Write the failing integration assertions**

Add tests for the exact BEGIN/END markers, all six roles, Dispatch precedence, broad-memory restriction, Control non-implementation, Project Lead non-dispatch rule, worker/reviewer boundaries, idempotent marker count, and reversible block extraction.

- [ ] **Step 2: Run integration tests to verify RED**

Run: `python -m pytest tests/orca-project-memory-routing/test_contracts.py -q -k integration`

Expected: failures identify missing versioned integration documents.

- [ ] **Step 3: Write the marker-delimited router document**

Place exactly one block between:

```text
<!-- ORCA-PROJECT-ROUTER:BEGIN -->
...
<!-- ORCA-PROJECT-ROUTER:END -->
```

The block must describe role classification and scope only. It must not reproduce the full skills, include runtime commands, or alter global instructions. Include the exact rule that removing the block restores prior content.

- [ ] **Step 4: Write bootstrap-contracts.md**

Document the required fields and validation for `PROJECT_BOOTSTRAP`, `CONTROL_BOOTSTRAP`, Dispatch preambles, Task Briefs, and Review Briefs. State that ambiguity fails closed and that superior transcripts never transfer downward.

- [ ] **Step 5: Run integration tests to verify GREEN**

Run: `python -m pytest tests/orca-project-memory-routing/test_contracts.py -q -k integration`

Expected: all integration-document assertions pass.

- [ ] **Step 6: Verify the canonical Control package boundary**

Run: `Test-Path -LiteralPath skills/orca-project-control/SKILL.md; Test-Path -LiteralPath docs/orca-project-memory/control-canonical-source-decision.md`

Expected: both paths are present in this worktree. The decision document must state that repository source resolution does not imply Run 0 approval, installation, integration, activation, publication, or pilot.

---

## Task 5: Complete the deterministic contract suite

**Files:**
- Modify: `tests/orca-project-memory-routing/test_contracts.py`
- Read: every new `SKILL.md`, reference, template, and versioned integration document.

**Interfaces:**
- Consumes: all implementation artifacts and the frozen 35-case table.
- Produces: reproducible local evidence for role routing, context isolation, executor policy, lifecycle/review gates, safety exclusions, concurrency, Windows text, and fixture privacy.

- [ ] **Step 1: Map each frozen case to one named test**

Use the exact frozen case order from the design: cases 1–7 role classification; 8–10 context tiers; 11–15 executor policy; 16–25 verification/review/remediation/final routing; 26–27 memory/legacy rules; 28–30 excluded/protected skills; 31 concurrency; 32–33 global patch idempotence/rollback; 34 Windows/CRLF/PowerShell; 35 privacy. Add deterministic guards for the canonical Control source, exact Charter/Task/Review identity schemas, Dispatch proof boundaries, `cmdc` normalization, one-pass remediation, corrected secret regexes, and temporary-directory isolation.

- [ ] **Step 2: Run the complete focused suite**

Run: `python -m pytest tests/orca-project-memory-routing/test_contracts.py -q`

Expected: all frozen contract behaviors and the added guards pass, with no real service startup and no writes outside pytest temporary directories.

- [ ] **Step 3: Run static safety checks**

Run: `rg -n --hidden --pcre2 "(sk-[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9._-]{20,}|client_secret\s*[:=]|password\s*[:=]\s*\S+|https://[^\s]+oauth[^\s]*|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})" skills/orca-project-main skills/orca-workflow-router skills/orca-project-control docs/orca-project-memory`

Expected: no production-document credential, authenticated URL, token, or raw private-data match. The test file's detector patterns are intentionally excluded from this scan; they are validated by the focused suite.

- [ ] **Step 4: Run the full repository suite for a fresh boundary check**

Run: `python -m pytest -q`

Expected: the new focused suite remains green; the known unrelated `pandas` collection error is reported separately if still present.

---

## Task 6: Independent verification and review checkpoint

**Files:**
- Read: all implementation and test files.
- Do not modify: candidate files during review.

**Interfaces:**
- Consumes: exact Git diff, focused test output, static safety output, and the Run 0 design/audit.
- Produces: an evidence-backed review disposition; no merge, push, global activation, or pilot.

- [ ] **Step 1: Freeze the local evidence range**

Run: `git status --short --branch; git rev-parse HEAD; git diff --stat; git diff --name-only`

Record the current branch, exact base `HEAD`, dirty baseline paths, all new files, and the fact that the Run 0 artifacts predate this inline override.

- [ ] **Step 2: Perform deterministic requirements review**

Check every File Map entry, each frozen case and added guard, all protected-path invariants, the canonical Control source decision, and the no-global-write rule. Any gap is `CHANGES_REQUESTED` or `IMPLEMENTATION_BLOCKED`, never silently accepted.

- [ ] **Step 3: Request a fresh independent review when the route is available**

Before dispatching a reviewer, freeze the exact base/head range and obtain the required reviewer model/tier choice under the review skill. A missing, timed-out, empty, or stale reviewer report remains `REVIEW INCOMPLETE`; it is not approval.

- [ ] **Step 4: Report the implementation-only status**

Use `IMPLEMENTATION_BLOCKED` while the canonical Control source or required evidence is unresolved. Use `INTEGRATION_REVIEW_PENDING` only after all intended artifacts and focused verification exist and the remaining work is explicitly the separate integration/review gate.

---

## Completion Checklist

- [ ] Exactly two new routing skills and the repository-relative canonical Control package exist.
- [ ] Project-main and workflow-router focused tests passed after their RED phase.
- [ ] All 35 frozen contract cases are named and covered, plus guards for the canonical Control source, exact identity schemas, Dispatch proof, security regexes, and temporary-directory isolation.
- [ ] No protected skill or global `AGENTS.md` was modified.
- [ ] No second lifecycle store, Pi route, legacy SDD route, or real paid executor/OCR was added.
- [ ] Control source decision is recorded without claiming global promotion, installation, integration, activation, publication, or pilot.
- [ ] Full-suite `pandas` collection failure is reported as a pre-existing environment boundary.
- [ ] Fresh independent review evidence exists before any acceptance claim.
- [ ] No merge, push, global activation, or real pilot was performed.
