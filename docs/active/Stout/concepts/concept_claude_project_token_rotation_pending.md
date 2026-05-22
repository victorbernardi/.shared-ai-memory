---
name: Rotação de tokens pendente
description: GitHub PAT e Tavily key ainda precisam ser rotacionados — foram salvos em ~/.credentials/ mas as chaves originais vazaram em conversa
type: project
originSessionId: 580d3dad-2697-47f0-a703-c4e60548e17a
---
**Estado atual (2026-04-24):** Credenciais migradas para `~/.credentials/` (github.key, tavily.key) mas as chaves são as mesmas que vazaram — rotação ainda pendente.

Três secrets foram expostos em plaintext em arquivos de configuração MCP e vazaram em log de conversa no dia 2026-04-24:

1. **GitHub PAT #1** (prefixo `ghp_r034ix...`) — em `~/.gemini/mcp.json` e `~/.gemini/antigravity/mcp.json` (hardlinked com `mcp_master.json`). Usado pelo MCP `github` (`@modelcontextprotocol/server-github`). Revogar em <https://github.com/settings/tokens> e gerar novo com scopes mínimos (`repo` ou `public_repo`, `read:user`, `read:org` se usa orgs).

2. **Google API Key** (prefixo `AIzaSy...FQjY`) — em `~/.gemini/mcp.json` e `~/.gemini/antigravity/mcp.json`. Usada pelo MCP `google-developer-knowledge` para a API `developerknowledge.googleapis.com`. Revogar em <https://console.cloud.google.com/apis/credentials> e gerar nova restrita só à Developer Knowledge / Generative Language API.

3. **GitHub PAT #2** (prefixo `ghp_mD2zKv0...`) — em `~/.vscode/mcp.json`. Diferente do PAT #1 — é outro token. Mesmo procedimento de revogação.

Arquivos relacionados com os secrets (para auditar antes de commitar qualquer coisa):

- `C:\Users\victor.bernardi\.gemini\mcp.json`
- `C:\Users\victor.bernardi\.gemini\antigravity\mcp.json` (hardlink com `mcp_master.json` — mesmo inode)
- `C:\Users\victor.bernardi\.gemini\antigravity\mcp_master.json`
- `C:\Users\victor.bernardi\.gemini\antigravity\mcp_config.json` (versão antiga, 1600 bytes — ainda contém os secrets, verificar se está realmente obsoleto antes de apagar)
- `C:\Users\victor.bernardi\.gemini\antigravity\mcp.json.backup-20260423-2247`
- `C:\Users\victor.bernardi\.vscode\mcp.json` (tem bug adicional: backslashes não escapados na linha 5, JSON inválido)

**Why:** Secrets em plaintext num arquivo de config é risco permanente — qualquer log, screenshot, ou compartilhamento do arquivo vaza. Neste caso específico, os valores já apareceram no histórico desta conversa (e possivelmente em outros logs), então rotação é obrigatória, não opcional.

**How to apply:** Quando o usuário disser que gerou os tokens novos, atualizar `~/.gemini/mcp.json` para ler de variáveis de ambiente (`"${GITHUB_PAT}"` e `"${GOOGLE_DEV_KNOWLEDGE_KEY}"`) em vez de ter os valores inline. Valores reais ficam em `setx` no Windows. Nunca pedir para ele colar os tokens no chat — só instruir os comandos `setx` para ele rodar localmente.
