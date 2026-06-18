# Plano de Triagem e Limpeza do Git (Stout)

**Objetivo:** Restaurar a saúde do repositório Git principal (`C:\Projetos\Stout`), com foco absoluto em código (Python, scripts) e arquivos `.md` fundamentais de configuração/skills. 

## 1. Atualização de Regras de Ignorar (.gitignore)
Vamos adicionar ao `.gitignore` as pastas que não devem ser rastreadas:
- `docs/`
- `memory/`
- `.karpathy-skills-temp/`
- `Projetos/Stout-Shared-Memory/scratch/`
- `Projetos/git-guard/.coverage`
- `Projetos/Configuration-Driven Development/` (já possui seu próprio repositório `.git` interno).

*(Nota: Com isso, todos os arquivos como planos de migração, specs e sessões `HANDOFF` que estão dentro de `docs/` e `memory/` serão automaticamente ignorados e não farão parte dos commits).*

## 2. Governança de Dados, Plugins e Sub-repositórios (Un-track)
Vamos remover do rastreamento do Git os itens que devem ficar apenas locais:
- **NotebookLM:** Vamos remover a pasta `Projetos/NotebookLM/.git` para que o conteúdo (código/scripts) passe a ser rastreado pelo repositório principal Stout.
- **Pastas Locais/Noisy:** Executaremos os seguintes comandos para desenraizar arquivos previamente commitados que agora são ignorados:
  - `git rm -r --cached docs/`
  - `git rm -r --cached memory/`
  - `git rm -r --cached Plugins/`

## 3. Consolidação (Commits)
Agruparemos as mudanças reais em commits coesos:

### Commit 1: Atualização de Skills e Core MDs
- **Arquivos Modificados:**
  - `MISSION_STOUT.md`
  - `antigravity/skills/process-superantigravity/SKILL.md`
  - `antigravity/skills/process-superantigravity/references/gemini-tools.md`
- **Mensagem Proposta:** `feat(skills): update mission and superantigravity skills`

### Commit 2: Arquivamento de Skills Legado
- **Ação:** Removeremos a skill obsoleta do escopo ativo (`git rm -r antigravity/skills/process-context-agent`).
- **Mensagem Proposta:** `refactor(skills): archive legacy process-context-agent skill`

### Commit 3: Scripts e Código
- **Arquivos:**
  - `scripts/consolidate_legacy_sessions.py`
- **Mensagem Proposta:** `feat(scripts): add consolidate legacy sessions script`

### Commit 4: Governança do Repositório e Novos Projetos
- **Arquivos:**
  - `.gitignore`
  - `Projetos/NotebookLM/`
- **Mensagem Proposta:** `chore(git): update gitignore, untrack local docs/memory folders and integrate NotebookLM`

## 4. Validação
Ao final, executaremos `git status` para confirmar que:
1. O repositório está limpo ("nothing to commit, working tree clean").
2. Não há mais "Untracked files" residuais (docs e memory não deverão mais aparecer).