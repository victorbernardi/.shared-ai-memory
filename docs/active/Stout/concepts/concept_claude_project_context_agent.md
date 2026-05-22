---
name: Context Agent — Continuidade entre Sessões
description: Skill que salva e restaura contexto entre sessões do OpenCode. Trigger "encerrar sessão" deve acionar o save antes de fechar.
type: project
originSessionId: 34dfc694-8d87-4662-81b7-67d2a1caac6d
---
Skill `context-agent` portada para `.opencode/skills/context-agent/` em 2026-04-23.

**Por que existe:** Continuidade perfeita entre sessões OpenCode — captura tópicos, decisões, tarefas pendentes, arquivos modificados, erros resolvidos.

**Trigger obrigatório:** Quando Victor diz `encerrar sessão`, o context-agent DEVE ser acionado antes de fechar a conversa.

**Comandos principais:**

```bash
# Salvar contexto da sessão (rodar ao encerrar)
python C:/Projetos/Stout/.opencode/skills/context-agent/scripts/context_manager.py save

# Carregar briefing (rodar ao iniciar nova sessão)
python C:/Projetos/Stout/.opencode/skills/context-agent/scripts/context_manager.py load

# Status rápido
python C:/Projetos/Stout/.opencode/skills/context-agent/scripts/context_manager.py status

# Buscar no histórico
python C:/Projetos/Stout/.opencode/skills/context-agent/scripts/context_manager.py search "<termo>"
```

**Integração com OpenCode:** `memory/MEMORY.md` está nas `instructions` do `opencode.json` — o contexto salvo é carregado automaticamente na próxima sessão sem ação manual.

**How to apply:** Ao encerrar qualquer sessão no OpenCode/Stout, sempre rodar o `save` antes de fechar. No Claude Code (aqui), lembrar de salvar memórias manualmente já que o context-agent não roda aqui.
