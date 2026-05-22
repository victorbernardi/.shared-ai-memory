---
name: Transição Claude Code → OpenCode — Concluída
description: OpenCode configurado como motor do Stout com MCPs, plugins e memória. Validado em 2026-04-22.
type: project
originSessionId: 34dfc694-8d87-4662-81b7-67d2a1caac6d
---
Motor OpenCode operacional em `C:\Projetos\Stout` desde 2026-04-22.

**Why:** Claude Code continua para gestão/planejamento estratégico. OpenCode (100% OpenAI) é o motor de coding do ecossistema — toda modificação de agents, skills e workflows passa por ele.

**How to apply:** Quando o usuário mencionar modificações no ecossistema Stout/Antigravity/Inova, o trabalho de coding acontece no OpenCode, não aqui.

**Estado atual:**
- 5 MCPs conectados: context7, github, google-developer-knowledge, google-drive, notebooklm
- Plugins: Superpowers + ECC
- Memória carregada: GEMINI.md, MISSION_STOUT.md, memory/ecosystem.md, memory/preferences.md
- Repositório GitHub: https://github.com/victorbernardi/Stout (privado)
- Auth OpenAI: via OAuth (/connect) — sem API key

**Arquitetura de compartilhamento Antigravity ↔ Stout:**
- Skills: totalmente separadas. Antigravity mantém 1400+ community skills. OpenCode usa .opencode/skills/ + Superpowers + ECC. Sem conflito.
- Agents: seletivo via symlink. Script `scripts/link-agent-to-antigravity.ps1` cria symlinks por agente conforme necessário. Atualização no Stout sincroniza automaticamente.
- setup-antigravity-redirect.ps1 (junction de pasta inteira) foi descartado em favor de symlinks seletivos.

**Modelos por agente (atualizado 2026-04-22):**
- `build`: `openai/gpt-5.4` (flagship, agente primário)
- `planner`, `architect`, `deep-research`: `openai/gpt-5.2` (reasoning)
- `code-reviewer`, `plan-reviewer`: `openai/gpt-5.4-mini` + `mode: subagent`
- `doc-updater`: `openai/gpt-5.4-nano` (tarefas leves)
- global `model`: `openai/gpt-5.4-mini` / `small_model`: `openai/gpt-5.4-nano`
- Referência de modelos: https://developers.openai.com/codex/models

**Agentes no Stout (disponíveis para linkar ao Antigravity):**
- deep-research.md
- plan-reviewer.md

**Skills customizadas portadas:**
- .opencode/skills/canary-deployment/ (portada do Antigravity, log em logs/canary-log.md)

**Validação concluída (2026-04-23):**
- Canary-deployment testado e validado em produção
- context-agent skill portada para `.opencode/skills/`
- tavily-search MCP adicionado
- memory/MEMORY.md e rules/opencode_tool_routing.md nas instructions
- Motor OpenCode operacional e validado ✅

**Pendente:**
- Linkar agentes ao Antigravity conforme necessidade (`.\scripts\link-agent-to-antigravity.ps1 -List`)
