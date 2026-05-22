# Importação e Adaptação de Skills Core Implementation Plan

> **For Antigravity:** REQUIRED SUB-SKILL: Load @[/implement] to implement this plan task-by-task.

**Goal:** Importar, traduzir e ajustar as skills essenciais do Superpowers original (`using-git-worktrees` e `using-superpowers`) para o ecossistema local Antigravity (Windows/PowerShell).

**Architecture:** Adaptação de scripts Bash para PowerShell, tradução de regras instrucionais para PT-BR e alinhamento de caminhos do sistema para `%USERPROFILE%\.gemini\antigravity\`.

**Tech Stack:** Git, PowerShell, Markdown, Antigravity Skill Ecosystem.

---

### Task 1: Scaffolding e Skill `using-superantigravity`

**Files:**
- Create: `C:\Users\victor.bernardi\.gemini\antigravity\skills\using-superantigravity\SKILL.md`
- Test: Verificação de sintaxe e gatilhos via `skill-check` (análise manual baseada nas regras)

**Step 1: Criar estrutura da nova skill**

```bash
mkdir -p "C:\Users\victor.bernardi\.gemini\antigravity\skills\using-superantigravity"
```

**Step 2: Implementar conteúdo adaptado da skill de uso geral**

Conteúdo traduzido e ajustado para o contexto Antigravity, referenciando `view_file` em vez de `activate_skill`.

**Step 3: Verificar ativação simulada**

Mencionar "como usar as skills" e verificar se a nova skill é carregada.

**Step 4: Commit**

```bash
git add skills/using-superantigravity/SKILL.md
git commit -m "feat: add using-superantigravity skill adapted for local environment"
```

---

### Task 2: Adaptação da Skill `using-git-worktrees`

**Files:**
- Create: `C:\Users\victor.bernardi\.gemini\antigravity\skills\using-git-worktrees\SKILL.md`

**Step 1: Criar diretório da skill**

```bash
mkdir -p "C:\Users\victor.bernardi\.gemini\antigravity\skills\using-git-worktrees"
```

**Step 2: Implementar SKILL.md com comandos PowerShell**

Substituir snippets Bash por equivalentes PowerShell funcionais. Exemplo: 
Original: `project=$(basename "$(git rev-parse --show-toplevel)")`
PowerShell: `$project = Split-Path (git rev-parse --show-toplevel) -Leaf`

**Step 3: Validar lógica de .gitignore para Windows**

Garantir que o comando `git check-ignore` funcione corretamente com caminhos Windows no script da skill.

**Step 4: Commit**

```bash
git add skills/using-git-worktrees/SKILL.md
git commit -m "feat: add using-git-worktrees skill adapted for Windows/PowerShell"
```

---

## Perguntas para Discussão (Writing Plans Mode)

> [!IMPORTANT]
> **Decisões Críticas Necessárias:**
> 1. **Local Padrão de Worktrees:** Se você não especificar, a skill tentará criar em `.worktrees/` dentro do projeto. Prefere que eu configure uma pasta global como fallback (ex: `C:\Worktrees\<projeto>`)?
> 2. **Fluxo de Inicialização:** A skill original tenta rodar `npm install` ou `pip install`. Deseja que eu adicione suporte específico para as ferramentas que você usa na **Inova** (ex: venv ou conda)?
