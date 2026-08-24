# Canonical Inova Refresh Skills Design

**Status:** approved for implementation by the instruction to follow the canonical-port recommendation.

## Goal

Publish the BUP and CEVAP refresh skills on top of the current repository `master`, preserving the governed BUP workflow and making the CEVAP workflow point exclusively to its standalone checkout.

## Boundaries

- `inova-bup-refresh` remains an orchestrator for `C:\Projetos\Inova`.
- BUP refresh uses the canonical Inova virtual environment, the recency report, `dependency_governance.py`, the BUP consolidator, and focused BUP QA.
- `inova-cevap-refresh` executes only through `C:\Projetos\Inova.maquinas\motor-cevap`.
- CEVAP receives its upstream BUP through `CEVAP_BUP_PATH`, preserves commercial controls through `CEVAP_ONEDRIVE_PATH`, and uses the standalone `.venv` or `uv run --no-project`.
- The shared registry remains the source of truth for names, roles, dependencies, and active status.
- The skills target Claude Code, Antigravity, CommandCode, and Codex because this repository is consumed by all four runtimes.

## Contract changes

The CEVAP skill must not instruct agents to execute `C:\Projetos\Inova\projects\motor-cevap`, use the monorepo Python environment, or assume that the legacy checkout is writable. Its run, test, output, and preflight instructions must be reproducible from the standalone checkout.

The blueprints describe the files actually delivered by each skill: `SKILL.md` plus contract tests. No placeholder `scripts/` directory is declared because the production scripts live in the governed Inova projects.

## Validation

Contract tests run before the skill documents are changed and fail on the old branch content. The green suite checks JSON/config consistency, required platform targets, governed BUP paths, standalone CEVAP paths, environment variables, forbidden legacy paths, and registry dependency edges. The repository quality gate and JSON parsing run after the tests.

This change does not execute either data refresh or publish any operational output. Pipeline execution remains an explicit downstream operation with its own source, recency, schema, preservation, and artifact gates.
