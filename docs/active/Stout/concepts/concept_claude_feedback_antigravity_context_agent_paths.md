---
name: Context-agent Antigravity — paths reais e ajustes nos plans
description: Estrutura real dos paths Antigravity context-agent vs o que estava nos plans; fase1+fase2 corrigidas, fase5 ainda com path issue
type: feedback
originSessionId: d9514933-84d2-47e9-8a28-1c957cdf5527
---
Estrutura real do context-agent Antigravity (validada em 2026-04-23 18:10):

**Skill (scripts + SKILL.md + references):**
`C:/Projetos/Stout/antigravity/skills/context-agent/`

- `scripts/` — todos os 11 .py + governance.py extra
- `SKILL.md` — entry point da skill
- `references/`
- `data/` — pasta legada (Apr 23 10:16, possivelmente órfã)

**Data atual (onde `config.py` aponta hoje):**
`C:/Projetos/Stout/antigravity/skills/context-management/context-agent/data/`

- ACTIVE_CONTEXT.md, context.db, PROJECT_REGISTRY.md, sessions/

⚠️ **DOIS data dirs coexistem.** A migração da Fase 1 deve unificar ambos no `memory/context-agent/`.

**Why:** A estrutura de `antigravity/skills/` foi refatorada durante a sessão de 2026-04-23 — arquivos `.md` viraram pastas. Os paths originalmente referenciados no spec/plans foram capturados antes/durante o refactor.

**How to apply:**

✅ **Já corrigido (commits após 9cfc742):**

- Fase 1 plan: scripts paths e SKILL.md paths apontam para `antigravity/skills/context-agent/`
- Fase 1 plan: Task 4 reescrita para migrar AMBOS data dirs
- Fase 2 plan: scripts paths corrigidos

⚠️ **Ainda precisa atenção antes de executar Fase 5:**

- Fase 5 referencia `antigravity/skills/using-superpowers/` que **não existe** localmente. A skill Antigravity análoga é `antigravity/skills/using-superantigravity/`. Decidir: criar `using-superpowers/` no Antigravity, ou usar `using-superantigravity/` como destino do `wiki-feedback.md`.

**Comando que funciona hoje** para save/load:

```bash
python C:/Projetos/Stout/antigravity/skills/context-agent/scripts/context_manager.py save
python C:/Projetos/Stout/antigravity/skills/context-agent/scripts/context_manager.py load
```

**Outras referências antigas no repo** (não corrigidas, fora do escopo da reforma):

- `memory/MEMORY.md` (Stout)
- `antigravity/skills/context-optimization/SKILL.md`
- `antigravity/skills/context-manager/SKILL.md`
- `antigravity/skills/context-management-context-save/SKILL.md`
- `antigravity/skills/context-management-context-restore/SKILL.md`
- `scripts/skill_health_dashboard.py`
