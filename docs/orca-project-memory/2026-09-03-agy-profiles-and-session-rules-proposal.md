# Proposta: Integração dos Perfis e Regras de Sessão do AGY (Worker & Leader)

- **Data:** 2026-09-03
- **Origem:** Sessão de Implementação / Configuração AGY
- **Destino:** Sessão Principal `PROJECT_LEAD` / Plano de Implementação

---

## 1. Resumo Executivo
Padronização da execução do Antigravity CLI (`agy`) com a criação de dois perfis formais (`worker` e `leader`), compatíveis com o ambiente de permissões padrão (sem necessidade de privilégios de administrador) e alinhados às diretrizes do ecossistema Orca e do `feat/project_lead`.

---

## 2. Perfis Configurados

### A. Perfil `worker` (Executor de Tasks Delimitadas)
- **Papel:** `IMPLEMENTER` / `WORKER` (Bounded Implementation).
- **Invocação:** `agy --mode=accept-edits --sandbox` (Alias: `agyw` / `agy-worker`).
- **Comportamento & Limites:**
  - Estritamente restrito ao `task.json` / Task Brief despachado.
  - Opera 100% no sandbox do workspace ativo.
  - Não redefine arquitetura, não cria subagentes e não faz alterações fora do escopo da task.

### B. Perfil `leader` (Sessão Principal / Interativa)
- **Papel:** `PROJECT_LEAD` / `COORDINATOR` / `INTERACTIVE USER`.
- **Invocação:** `agy --dangerously-skip-permissions` (Alias: `agyl` / `agy-leader`).
- **Comportamento & Limites:**
  - Permissão total para editar arquivos, criar planos e rodar validações locais (modo YOLO).
  - Auto-aprova todas as solicitações de permissão de ferramentas sem confirmação.
  - Capacidade de acionar skills sob demanda (`$superpowers`, `$orca-cli`, etc.).
  - Capacidade de estruturar tarefas e despachar para coordenadoras / workers.

---

## 3. Artefatos Criados no Workspace

- [`templates/agy-profiles.ps1`](file:///C:/Projetos/Inova.maquinas.worktrees/.shared-ai-memory/feat-PROJECT_LEAD/templates/agy-profiles.ps1) — Script PowerShell com funções e aliases (`agyw`, `agyl`) com suporte a dot-sourcing.
- [`templates/agy-worker.cmd`](file:///C:/Projetos/Inova.maquinas.worktrees/.shared-ai-memory/feat-PROJECT_LEAD/templates/agy-worker.cmd) — Executável batch para modo worker (`--mode=accept-edits --sandbox`).
- [`templates/agy-leader.cmd`](file:///C:/Projetos/Inova.maquinas.worktrees/.shared-ai-memory/feat-PROJECT_LEAD/templates/agy-leader.cmd) — Executável batch para modo leader/yolo (`--dangerously-skip-permissions`).
- [`docs/AGY-PROFILES-GUIDE.md`](file:///C:/Projetos/Inova.maquinas.worktrees/.shared-ai-memory/feat-PROJECT_LEAD/docs/AGY-PROFILES-GUIDE.md) — Documentação e guia de uso.

---

## 4. Itens Propostos para Atualização do Plano de Implementação

1. **Adicionar Item de Perfis no Plano:**
   - Formalizar `templates/agy-profiles.ps1` como o padrão para workers e líderes no ecossistema do projeto.
2. **Harmonização com `AGENTS-role-router.md`:**
   - Confirmar a precedência de papéis: `worker` vincula-se ao Dispatch ativo; `leader` vincula-se à sessão interativa principal.
3. **Garantia de Não-Elevação:**
   - Manter todas as operações restritas ao espaço do usuário, sem dependência de privilégios de administrador.
