# Platform Reference: Codex

## Platform ID
`codex`

## Output Directory
`~/.agents/skills/<skill-name>/`

## Platform-Specific Extensions

### `codex.openai-ui-metadata`
- **Kind:** File
- **Output:** `agents/openai.yaml`
- **Value type:** mapping
- **Documentation:** https://learn.chatgpt.com/docs/build-skills.md

This extension adds OpenAI-specific metadata for the Codex runtime.

## Rendering Rules

- Common files are copied to all platforms.
- Platform-specific extensions are only included for their target platform.
- The renderer creates artifacts under `<output-dir>/rendered/<platform>/<skill-name>/`.
