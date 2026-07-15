# Platform Reference: Hybrid (Common Contract)

## Overview

The hybrid platform defines the common contract for all supported platforms. Every skill source follows this contract, and platform-specific extensions are applied only during rendering.

## Supported Platforms

- `codex` → `~/.agents/skills/`
- `claude-code` → `~/.claude/skills/`
- `commandcode` → `~/.commandcode/skills/`

## Canonical Source Structure

```
skills/<skill-name>/
├── SKILL.md                  # Portable skill definition
├── skill.platforms.yaml      # Platform manifest (targets + extensions)
├── scripts/                  # Skill scripts
├── tests/                    # Skill tests
└── ...
```

## `skill.platforms.yaml`

This file declares which platforms the skill targets and which extensions are enabled.

```yaml
targets:
  - codex
  - claude-code
  - commandcode
extensions:
  - id: claude.allowed-tools
    required: false
    value:
      - Read
      - Grep
```

## Rules

- `SKILL.md` is the portable source of truth.
- Extensions are absent by default.
- Unknown or unsupported required extensions fail before installation.
- No junctions participate in discovery or installation.
- Installed copies are never edited as a source of truth.
