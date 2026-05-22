---
name: Padrão de Credenciais — Sem Hardcode
description: Todas as API keys e tokens devem estar em ~/.credentials/*.key, nunca hardcoded em configs
type: feedback
originSessionId: 4b8582b6-0aaf-42f5-b1ec-0db8461e3c66
---
Nunca colocar tokens ou API keys diretamente em arquivos de configuração (mcp_config.json, settings.json, opencode.json, etc.).

**Why:** Risco de vazamento em conversas com IA, versionamento acidental ou compartilhamento de configs.

**How to apply:**
1. Salvar o token em `~/.credentials/<nome>.key` (ex: `notion.key`, `github.key`)
2. Carregar via `C:\Projetos\Stout\load-credentials.ps1` como env var
3. Referenciar no config como `${NOME_DA_VAR}` (Antigravity/Gemini CLI) ou `{env:NOME_DA_VAR}` (OpenCode)
4. Nunca mostrar o valor real de um token em resposta — apenas o nome da variável
