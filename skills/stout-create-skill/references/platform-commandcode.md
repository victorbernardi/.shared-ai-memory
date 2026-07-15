# Platform Reference: CommandCode

## Platform ID
`commandcode`

## Output Directory
`~/.commandcode/skills/<skill-name>/`

## Platform-Specific Extensions

### `commandcode.metadata`
- **Kind:** Frontmatter
- **Output:** `metadata`
- **Value type:** mapping
- **Documentation:** https://commandcode.ai/docs/skills

This extension adds CommandCode-specific metadata.

## Frontmatter — CommandCode Specific Fields

| Field | Behavior |
|-------|----------|
| `name` | Required. Lowercase with hyphens. Must match directory name. |
| `description` | Required. Determines when skill is activated. Prefix with "Use when" or "Use quando". Max 1024 chars. |
| `version` | Optional but recommended. SemVer. |
| `author` | Optional. |
| `tags` | Optional. List for categorization. |
| `agents` | Optional. List of compatible agents (e.g., `["commandcode", "claude"]`). |

## Capabilities

| Capability | Support |
|-----------|---------|
| Python/Bash/Node scripts | Via `scripts/` |
| YAML frontmatter | Full standard |
| Native tool use | Depends on agent implementation |
| MCP servers | Via separate configuration |
| Skill invocation | No native mechanism |

## Rendering Rules

- Common files are copied to all platforms.
- The `commandcode.metadata` extension is only included for `commandcode`.
- The renderer creates artifacts under `<output-dir>/rendered/commandcode/<skill-name>/`.
