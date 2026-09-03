---
name: open-code-review-delegate
description: >
  Delegated code review powered by open-code-review (OCR) deterministic engineering
  (file filtering, rule resolution, diff discovery) and executed by Google Antigravity (AGY)
  using Gemini 3.8 Flash (High). Cross-harness compatible across Codex, Command-code, and AGY:
  when invoked from another harness CLI, it launches an AGY subagent session with Gemini 3.8 High
  to perform the review; when invoked inside AGY, it runs directly.
license: Apache-2.0
compatibility: >
  Requires the `ocr` CLI installed (via `npm install -g @alibaba-group/open-code-review`
  or GitHub release binary) and `agy` CLI installed for external harness delegation.
metadata:
  author: alibaba / victorbernardi
  model: gemini-3.8-flash-high
  version: "2.0.0"
---

# Open Code Review — Delegation to AGY (Gemini 3.8 High)

A skill for performing AI code review where OCR provides deterministic engineering (file filtering, rule resolution) and Google Antigravity (AGY) performs the actual review using **Gemini 3.8 Flash (High)** (`gemini-3.8-flash-high`).

## Cross-Harness Execution Model

This skill is shared across **Codex**, **Command-code**, and **AGY**. The review reasoning is always executed by AGY using Gemini 3.8 High:

### 1. When Invoked from Another Harness (Codex, Command-code CLI)
Do **not** perform the code review using the host harness's own model. Instead, initiate an external AGY session (subagent) using `gemini-3.8-flash-high`:

```bash
agy -p "<review prompt>" --model gemini-3.8-flash-high --mode accept-edits --sandbox
```

The host acts as the orchestrator: it prepares the review target and rules (or lets AGY run OCR), triggers the AGY session, and collects the review findings to display to the user.

### 2. When Invoked Inside AGY (Current Harness is AGY)
You are already in AGY with `gemini-3.8-flash-high`.
- Execute the review directly in the current session (or spawn an AGY subagent via `invoke_subagent` if a separate conversation context is preferred).
- Follow the standard OCR Workflow below.

---

## Prerequisites

```bash
which ocr || echo "NOT INSTALLED"
```

If `ocr` is not installed:
```bash
npm install -g @alibaba-group/open-code-review
```

For external harnesses (Codex / Command-code), verify `agy` CLI is available:
```bash
agy --version
```

---

## Workflow

### Step 1: Preview — Determine What to Review

```bash
ocr delegate preview --format json [--from <ref> --to <ref>] [--commit <hash>] [--exclude <patterns>]
```

This outputs:
- **mode** (workspace / range / commit)
- **from / to / commit / merge_base** — ref metadata for constructing git commands
- **Reviewable file list** — paths, status, insertions/deletions
- **Excluded files** — with exclusion reason

**Common invocations:**

| Scenario | Command |
|----------|---------|
| Workspace changes | `ocr delegate preview` |
| Branch comparison | `ocr delegate preview --from main --to feature` |
| Single commit | `ocr delegate preview -c <hash>` |

#### Markdown Files Are Always In Scope
Every changed file whose extension is `.md` (case-insensitive) is reviewable. If OCR classifies `.md` as `unsupported_ext`, reconcile `reviewable_files` with Git's changed Markdown paths (`git diff --name-status HEAD -- '*.md'`).

### Step 2: Get Rules for Files

```bash
ocr delegate rule --format json <path1> <path2> ...
```

Pass the reviewable file paths from Step 1. Output is grouped by rule content — files sharing the same rule appear under one group.

### Step 3: Get Diffs

Use git directly based on the mode/ref info from Step 1:

**Range mode** (merge_base provided in preview output):
```bash
git diff <merge_base>..<to> -- <path>
```

**Commit mode**:
```bash
git show <commit> -- <path>
```

**Workspace mode**:
```bash
# Tracked files
git diff HEAD -- <path>
# New untracked files — read directly
cat <path>
```

### Step 4: Execute the Review

#### A. External Harness (Codex / Command-code) -> AGY Session
Construct a concise review brief and start the AGY subagent session:

```bash
agy -p "Perform an Open Code Review using Gemini 3.8 High:
Target: <workspace changes | range <from>..<to> | commit <hash>>
Reviewable Files: <list of files from Step 1>
Rules: <rules from Step 2>
Mode: Review only. Do not edit files unless explicitly requested.
Evaluate code quality, correctness, edge cases, security, and rule compliance.
Report findings structured by severity (Critical, High, Medium, Low)." --model gemini-3.8-flash-high --mode accept-edits --sandbox
```

Capture the output from AGY and present the review findings to the user.

#### B. Inside AGY
Review each file against its Rule Group using Gemini 3.8 High reasoning directly or via `invoke_subagent`.

### Step 5: Format Output

Each finding must follow this structure:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| path | string | yes | Relative file path |
| content | string | yes | Review comment describing the issue and suggested fix |
| start_line | integer | no | Start line in the new file |
| end_line | integer | no | End line in the new file |
| category | enum | no | bug, security, performance, maintainability, test, style, documentation, other |
| severity | enum | no | critical, high, medium, low |

### Step 6: Classify and Report

Group findings by severity:
- **Critical / High**: Bugs, security issues, data loss risks — always report
- **Medium**: Performance concerns, error handling gaps, maintainability issues — report with context
- **Low**: Style nits, minor suggestions — report only if clearly valuable

Include `total_files`, `reviewed_files`, `skipped_files`, and `coverage_rate` in the summary.

### Step 7: Fix (Optional)

If the user explicitly requested "review and fix":
- Apply High/Critical fixes directly
- Describe Medium fixes that require manual intervention
- Skip Low-priority items unless trivial

---

## Sub-commands & Flags Reference

| Command | Purpose |
|---------|---------|
| `ocr delegate preview` | Which files to review + mode/ref metadata |
| `ocr delegate rule <path...>` | Review rules grouped by content |

| Flag | Description |
|------|-------------|
| `--from <ref>` | Source ref for range mode |
| `--to <ref>` | Target ref for range mode |
| `-c, --commit <hash>` | Single commit mode |
| `--repo <path>` | Repository root (default: cwd) |
| `--rule <path>` | Custom rule.json path |
| `--exclude <patterns>` | Comma-separated exclude patterns |
| `-b, --background <text>` | Business context |
| `-f, --format <text\|json>` | Output format; use `json` for agent integrations |

## Gotchas & Troubleshooting

- **Model is Gemini 3.8 High**: When delegating to AGY, always pass `--model gemini-3.8-flash-high`.
- **KISS & YAGNI**: No complex receipt protocols are required for reviews; a simple headless AGY invocation returning structured text or JSON is sufficient.
- **Rules are grouped**: Files sharing the same rule are grouped together.
- **Working directory**: `ocr delegate` operates on the Git repo at current directory; use `--repo <path>` if needed.
- **Format fallback**: If `ocr ... --format json` fails with `unknown flag: --format`, rerun without `--format` and use standard text output.
