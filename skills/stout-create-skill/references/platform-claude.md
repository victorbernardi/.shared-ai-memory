# Platform Reference: Claude Code

## Platform ID
`claude-code`

## Output Directory
`~/.claude/skills/<skill-name>/`

## Platform-Specific Extensions

### `claude.allowed-tools`
- **Kind:** Frontmatter
- **Output:** `allowed-tools`
- **Value type:** string_list
- **Documentation:** https://code.claude.com/docs/en/skills

This extension specifies which tools the skill is allowed to use.

## Frontmatter — Claude Code Specific Fields

Claude Code reads the standard YAML frontmatter. No exclusive fields, but these have direct effect:

| Field | Behavior |
|-------|----------|
| `description` | Used by routing system to decide when to load the skill. Max 1024 chars. Prefix with "Use when" or "Use quando". |
| `name` | Unique identifier. Must match the directory name. |

## Capabilities

### Tool Use
Skills can reference and invoke tools directly:

```markdown
Use the `Read` tool to read the file, then `Edit` to modify it.
```

### MCP (Model Context Protocol)
Skills can instruct the use of MCP servers:

```markdown
Use the `context7` MCP server to fetch updated documentation before implementing.
```

### Skill Tool
Skills can invoke other skills:

```markdown
Invoke the `stout-commit` skill when finalizing the implementation.
```

### Subagents (Agent Tool)

```markdown
Dispatch a subagent with `subagent_type=Explore` to map the codebase.
```

## Rendering Rules

- Common files are copied to all platforms.
- The `claude.allowed-tools` extension is only included for `claude-code`.
- The renderer creates artifacts under `<output-dir>/rendered/claude-code/<skill-name>/`.
