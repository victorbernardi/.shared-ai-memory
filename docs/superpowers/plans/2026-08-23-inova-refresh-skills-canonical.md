# Inova Refresh Skills Canonical Port Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port the governed BUP and CEVAP refresh skills from the stale feature branch onto the current `master`, with CEVAP bound to its standalone repository and both skills protected by executable contract tests.

**Architecture:** The skill repository contains documentation and metadata only. BUP continues to orchestrate the monorepo BUP pipeline, while CEVAP orchestrates the standalone motor using explicit upstream and OneDrive environment variables. Contract tests validate the documentation boundary without running a production data refresh.

**Tech Stack:** Markdown Agent Skills, JSON metadata, Python `pytest`, PowerShell paths, Git.

## Global Constraints

- Preserve the old branch `feat/inova-refresh-skills`; do not reset, clean, or delete it.
- Base the port on the current `master` through `feat/inova-refresh-skills-canonical`.
- Do not execute BUP or CEVAP production refreshes during this change.
- CEVAP must use `C:\Projetos\Inova.maquinas\motor-cevap`, `CEVAP_BUP_PATH`, and `CEVAP_ONEDRIVE_PATH`.
- CEVAP must not instruct execution from `C:\Projetos\Inova\projects\motor-cevap`.
- BUP must retain governed recency and dependency preflight before consolidation.
- JSON files must parse, and each skill must pass `skill_validator.py`.

---

### Task 1: Record the canonical boundary

**Files:**
- Create: `docs/superpowers/specs/2026-08-23-inova-refresh-skills-canonical-design.md`
- Create: `docs/superpowers/plans/2026-08-23-inova-refresh-skills-canonical.md`

**Interfaces:**
- Consumes: stale commits `0953eac` and `d0b34a9`, current `master`, BUP `AGENTS.md`, standalone CEVAP `AGENTS.md`.
- Produces: an auditable design and executable plan on `feat/inova-refresh-skills-canonical`.

- [x] Verify the branch is isolated and based on current `master`.
- [x] Record the BUP/CEVAP boundary, standalone CEVAP environment, platform targets, and no-production-refresh constraint.
- [ ] Commit the design and plan:

```powershell
git add docs/superpowers/specs/2026-08-23-inova-refresh-skills-canonical-design.md docs/superpowers/plans/2026-08-23-inova-refresh-skills-canonical.md
git commit -m "docs: define canonical refresh skill port"
```

### Task 2: Add RED contract tests

**Files:**
- Create: `skills/inova-bup-refresh/tests/test_bup_skill_contract.py`
- Create: `skills/inova-cevap-refresh/tests/test_cevap_skill_contract.py`

**Interfaces:**
- Consumes: local skill documents, configs, blueprints, and registry JSON.
- Produces: deterministic tests that fail when the old CEVAP monorepo path or incomplete metadata is present.

- [ ] Write BUP tests for required files, four target platforms, `C:\Projetos\Inova`, `refresh_governance.json`, `dependency_governance.py`, canonical Python, focused QA names, blueprint structure, and registry dependencies.
- [ ] Write CEVAP tests for the standalone path, `CEVAP_BUP_PATH`, `CEVAP_ONEDRIVE_PATH`, standalone UV/local-venv command, focused tests, forbidden legacy path, and blueprint structure.
- [ ] Run RED:

```powershell
python -m pytest skills/inova-bup-refresh/tests skills/inova-cevap-refresh/tests -q
```

Expected: failure because the new `master` branch does not yet contain the ported skill artifacts.

### Task 3: Port and correct skill artifacts

**Files:**
- Create: `skills/inova-bup-refresh/SKILL.md`, `audit_result.json`, `blueprint.json`, `skill.config.json`
- Create: `skills/inova-cevap-refresh/SKILL.md`, `audit_result.json`, `blueprint.json`, `skill.config.json`
- Modify: `skills/stout-skill-registry/registry.json`

**Interfaces:**
- Consumes: Task 2 tests and production contracts in the BUP and standalone CEVAP repositories.
- Produces: active registry entries with `inova-cevap-refresh -> inova-bup-refresh` dependency and correct runtime instructions.

- [ ] Port BUP docs while retaining governed preflight, source list, focused QA, feedback preservation, and no-destructive-operation constraints; add Codex metadata; declare `SKILL.md` and `tests/` in the blueprint.
- [ ] Rewrite CEVAP docs for `C:\Projetos\Inova.maquinas\motor-cevap`, explicit environment variables, standalone Python/UV, standalone commands/tests, timestamped output, and commercial-field preservation; remove legacy monorepo execution instructions.
- [ ] Port configs and registry entries with Claude Code, Antigravity, CommandCode, and Codex; map Codex to `.codex/skills`.

### Task 4: Run GREEN validation and audits

**Files:**
- Verify: both contract tests, all skill JSON, registry JSON, and both skill directories.

**Interfaces:**
- Consumes: Task 3 artifacts.
- Produces: fresh evidence for contract tests, JSON parsing, quality gates, semantic overlap, and whitespace.

- [ ] Run contract tests and confirm zero failures.
- [ ] Run both commands:

```powershell
python skills/stout-create-skill/scripts/skill_validator.py --path skills/inova-bup-refresh
python skills/stout-create-skill/scripts/skill_validator.py --path skills/inova-cevap-refresh
```

- [ ] Parse every target JSON and run `git diff --check master...HEAD`.
- [ ] Run semantic overlap checks for both proposed roles against the current registry. Record results without claiming operational refresh success.

### Task 5: Review and commit the port

**Files:**
- Verify: `git diff master...HEAD` and `git status --short --branch --untracked-files=all`.

**Interfaces:**
- Consumes: all Task 4 evidence.
- Produces: a reviewable canonical branch with the old branch reference preserved.

- [ ] Search the final diff for the forbidden legacy CEVAP path and required standalone variables.
- [ ] Commit the tested port:

```powershell
git add skills/inova-bup-refresh skills/inova-cevap-refresh skills/stout-skill-registry/registry.json
git commit -m "feat: port governed BUP and CEVAP refresh skills"
```

- [ ] Re-run the full verification after commit and report branch, commit SHA, clean status, test count, and limitations.
