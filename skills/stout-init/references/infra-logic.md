# Configuração e Lógica de Infraestrutura

## 🛠️ Configuração de MCPs (settings.json)

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@context7/mcp@latest"]
    },
    "google-drive": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-google-drive@latest"]
    },
    "notebooklm": {
      "command": "npx",
      "args": ["-y", "notebooklm-mcp@latest"]
    }
  }
}
```

## 🛠️ Wrappers de Skills (`.claude/skills/`)

Skills thin são instaladas em `.claude/skills/<nome>/` dentro do workspace do projeto. **NÃO usar** `.gemini/skills/` nem `.agents/skills/`.

Estrutura padrão de um wrapper thin:

```
.claude/skills/<nome>/
  SKILL.md       ← ponteiro para a Golden Copy em ~/.shared-ai-memory/skills/<nome>/
```

## 🛠️ Detecção de Ferramentas por Motor

| Operação | Claude Code (primário) | Codex/OpenAI (secundário) |
| :--- | :--- | :--- |
| Ler | `Read` | `read_file` |
| Escrever | `Write` | `write_file` |
| Editar | `Edit` | `replace` |
| Shell | `Bash` / `PowerShell` | `run_shell_command` |
| Buscar | `Grep` / `Glob` | `grep_search` / `find_files` |
