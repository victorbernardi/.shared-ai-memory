# Guia de Perfis do Antigravity CLI (`agy`)

Este documento descreve a configuração e uso dos dois perfis criados para o `agy`: **`worker`** e **`leader`**.

---

## 1. Definição dos Perfis

### **`worker` (Executor de Tasks)**
- **Objetivo**: Executar tarefas delimitadas vindas do fluxo Orca / `feat/project_lead`.
- **Comportamento**: Focado estritamente no escopo da tarefa atribuída, sem redefinir arquitetura ou desviar do contrato.
- **Flags**: `agy --mode=accept-edits --sandbox` (opera com segurança no sandbox aceitando edições no workspace).

### **`leader` (Sessão Principal / YOLO)**
- **Objetivo**: Sessão interativa principal de comando, onde você tem controle total.
- **Comportamento**: Pode planejar, coordenar, despachar tarefas para outras IAs, invocar skills sob demanda e alterar arquivos diretamente.
- **Flags**: `agy --dangerously-skip-permissions` (aprovação automática de todas as ferramentas e edições de arquivos sem prompts).

---

## 2. Arquivos Disponíveis no Projeto

- [`agy-profiles.ps1`](file:///C:/Projetos/Inova.maquinas.worktrees/.shared-ai-memory/feat-PROJECT_LEAD/templates/agy-profiles.ps1): Funções e aliases para carregar no PowerShell.
- [`agy-worker.cmd`](file:///C:/Projetos/Inova.maquinas.worktrees/.shared-ai-memory/feat-PROJECT_LEAD/templates/agy-worker.cmd): Script executável direto para iniciar o perfil Worker.
- [`agy-leader.cmd`](file:///C:/Projetos/Inova.maquinas.worktrees/.shared-ai-memory/feat-PROJECT_LEAD/templates/agy-leader.cmd): Script executável direto para iniciar o perfil Leader.

---

## 3. Como Ativar no seu PowerShell (Sem privilégios de Administrador)

Para carregar as funções na sessão atual do PowerShell:
```powershell
. "C:\Projetos\Inova.maquinas.worktrees\.shared-ai-memory\feat-PROJECT_LEAD\templates\agy-profiles.ps1"
```

Para deixar permanente em todos os novos terminais:
1. Abra o arquivo de perfil do seu usuário:
   ```powershell
   notepad $PROFILE
   ```
2. Adicione a linha de carregamento:
   ```powershell
   . "C:\Projetos\Inova.maquinas.worktrees\.shared-ai-memory\feat-PROJECT_LEAD\templates\agy-profiles.ps1"
   ```

---

## 4. Comandos Disponíveis no Terminal

| Ação | Comando Completo | Alias Rápido | Flags Utilizadas |
| :--- | :--- | :--- | :--- |
| Iniciar Sessão Executor de Tasks | `agy-worker` | `agyw` | `--mode=accept-edits --sandbox` |
| Iniciar Sessão Principal / YOLO | `agy-leader` | `agyl` | `--dangerously-skip-permissions` |
