---
name: Reestruturação Antigravity — Pendente
description: Reset completo do antigravity e .gemini planejado; backup do .gemini criado, falta executar limpeza e reinstalar skills
type: project
originSessionId: 580d3dad-2697-47f0-a703-c4e60548e17a
---
Reestruturação completa planejada em 2026-04-24. Skills já restauradas em 2026-04-28.

**Status (atualizado 2026-04-28):**
- ✅ Backup de `.gemini` criado em `C:\Projetos\gemini-backup-2026-04-24\`
- ✅ Skills restauradas em `~/.gemini/antigravity/skills/` (23 skills ativas)
- ✅ `mcp_config.json` restaurado com 8 MCPs (google-developer-knowledge, google-drive, notebooklm, github, context7, tavily-search, notion, google-search-fallback)
- ✅ `google-developer-knowledge` usa Service Account via wrapper script `scripts/google-dev-knowledge-mcp.py`
- ⚠ `google-search-fallback` com Brave API key placeholder — confirmar se tem chave ou remover
- ⚠ Usuário menciona que havia 10 MCPs — 2 ainda não identificados

**Credenciais:** Todas em `~/.credentials/` (github.key, tavily.key, notion.key, google-service-account.json)

**How to apply:** Na próxima sessão, verificar quais 2 MCPs faltam e resolver o google-search-fallback.
