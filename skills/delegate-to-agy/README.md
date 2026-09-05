# delegate-to-agy

Delegate coding tasks to the Google Antigravity CLI (`agy`) as a background implementer, then review the diff and land it yourself.

Designed for orchestrator agents such as **Codex**, **Command Code**, and **Claude Code**.

Based on the canonical architecture from [amElnagdy/delegate-skills](https://github.com/amElnagdy/delegate-skills).

## Prerequisites

- **Google Antigravity CLI (`agy`)**: installed and authenticated (`agy models` succeeds).
- **Node.js**: v18+ available on `PATH`.
- **Git**: installed and available on `PATH`.

## How it works

1. **Write the brief:** The orchestrator writes a self-contained brief (`brief.txt`) describing the task, files to change, and verification commands.
2. **Dispatch:** The orchestrator runs `relay.mjs`:
   ```bash
   node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo
   ```
3. **Wait / Poll:** `relay.mjs` executes `agy --print`, monitors execution with a watchdog timer, and writes `<out-dir>/result.json`.
4. **Review:** The orchestrator reads `result.json`, runs project tests/gates independently, and reviews `git diff`.
5. **Land:** The orchestrator commits the verified work, or sends a remediation brief via `--resume-last`.

## Usage Options

```text
node scripts/relay.mjs --brief <file> [options]

Options:
  --brief <file>          Path to brief file (or read from stdin)
  --cd <dir>              Working directory for Antigravity (default: current directory)
  --model <name>          Antigravity model label (default: agy configured default)
  --effort <level>        Reasoning effort: low, medium, or high
  --read-only             Run in plan mode (no edits)
  --sandbox               Enable Antigravity terminal sandbox
  --resume-last           Continue most recent conversation with delta brief
  --conversation <id>     Continue specific conversation with delta brief
  --print-timeout <dur>   Print mode timeout (default: 30m)
  --timeout <dur>         Relay watchdog timeout
  --out-dir <dir>         Directory for run artifacts and result.json
```

## Result Format (`result.json`)

```json
{
  "schema": "delegate-relay.result.v1",
  "tool": "agy",
  "workdir": "C:\\path\\to\\repo",
  "status": "completed",
  "exitCode": 0,
  "finalMessage": "...",
  "touchedFiles": ["src/index.js"],
  "projectId": "...",
  "conversationId": "..."
}
```
