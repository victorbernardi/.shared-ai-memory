# Orchestration Hooks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ativar 7 ganchos de orquestração e auto-reflexão no Antigravity (Gemini CLI) para que as skills certas disparem automaticamente — sem intervenção manual do Victor.

**Architecture:** Edições cirúrgicas mínimas nos 3 workflows existentes + criação de 4 arquivos de protocolo. Nenhuma skill é modificada — os workflows apenas declaram quando chamá-las.

**Tech Stack:** Markdown (arquivos de instrução do Antigravity/Gemini CLI), estrutura de diretórios `~/.gemini/antigravity/`

---

## Mapa de Arquivos

| Arquivo | Ação | Responsabilidade |
|---------|------|-----------------|
| `global_workflows/implement.md` | Editar (inserir Fase 0) | Briefing pré-execução obrigatório |
| `global_workflows/troubleshoot.md` | Editar (inserir decisão de paralelismo) | Detectar múltiplos domínios quebrados |
| `global_workflows/brainstorm.md` | Editar (inserir revisão adversarial) | Autocrítica antes de entregar propostas |
| `SESSION_START.md` | Criar | Protocolo de início de sessão com briefing |
| `END_OF_TASK.md` | Criar | Protocolo de encerramento com save de contexto |
| `GEMINI.md` | Editar (adicionar seção ao final) | Regra global de confidence-check em dados |
| `diary/erros.md` | Criar (+ criar pasta `diary/`) | Log estruturado de erros da sessão |

**Raiz de todos os caminhos:** `C:\Users\victor.bernardi\.gemini\antigravity\`

---

## Task 1: Gancho no `/implement` — Fase 0 obrigatória

**Files:**
- Modify: `C:\Users\victor.bernardi\.gemini\antigravity\global_workflows\implement.md` (antes da linha `## Step 0: Load the Plan`)

- [ ] **Step 1: Verificar o ponto de inserção**

  Abrir o arquivo e confirmar que a linha `## Step 0: Load the Plan` existe exatamente assim. A Fase 0 deve ser inserida **imediatamente antes** dela.

  ```bash
  grep -n "Step 0" "C:/Users/victor.bernardi/.gemini/antigravity/global_workflows/implement.md"
  ```

  Resultado esperado: `28:## Step 0: Load the Plan`

- [ ] **Step 2: Inserir a Fase 0**

  Substituir o bloco atual:
  ```markdown
  ## Step 0: Load the Plan
  ```

  Pelo bloco abaixo (Fase 0 + Step 0 original intacto):
  ```markdown
  ## Fase 0 — Briefing Pré-Execução (OBRIGATÓRIA)

  Execute antes de qualquer outra ação neste workflow:

  1. Carregar `task-intelligence` → classificar tarefa (Simples / Moderada / Complexa / Crítica)
  2. Se Complexa ou Crítica → carregar `blueprint` para gerar plano de construção
  3. Se ≥ 2 skills relevantes detectadas → carregar `dispatching-parallel-agents`

  Só avançar para o Step 0 após concluir a Fase 0.

  ## Step 0: Load the Plan
  ```

- [ ] **Step 3: Verificar o resultado**

  Confirmar que o arquivo tem as duas seções em sequência sem quebrar o conteúdo existente:

  ```bash
  grep -n "Fase 0\|Step 0\|Step 1\|Orchestration Flow" "C:/Users/victor.bernardi/.gemini/antigravity/global_workflows/implement.md"
  ```

  Resultado esperado (linhas aproximadas):
  ```
  28: ## Fase 0 — Briefing Pré-Execução (OBRIGATÓRIA)
  36: ## Step 0: Load the Plan
  40: ## Orchestration Flow
  ```

- [ ] **Step 4: Commit**

  ```bash
  cd "C:/Users/victor.bernardi/.gemini/antigravity" && git add global_workflows/implement.md && git commit -m "feat: add Fase 0 pre-execution briefing to /implement workflow"
  ```

  Se `antigravity/` não for um repositório git, pular o commit e continuar.

---

## Task 2: Gancho no `/troubleshoot` — Decisão de paralelismo

**Files:**
- Modify: `C:\Users\victor.bernardi\.gemini\antigravity\global_workflows\troubleshoot.md` (antes do item "2. Gather:")

- [ ] **Step 1: Verificar o ponto de inserção**

  ```bash
  grep -n "Gather\|Before loading" "C:/Users/victor.bernardi/.gemini/antigravity/global_workflows/troubleshoot.md"
  ```

  Resultado esperado:
  ```
  13: **Before loading the skill:**
  14: 1. Confirm the issue is reproducible...
  17: 2. Gather: exact error message, stack trace...
  ```

- [ ] **Step 2: Inserir a decisão de paralelismo**

  Substituir o bloco:
  ```markdown
  2. Gather: exact error message, stack trace, and "when did this last work?"
  ```

  Por:
  ```markdown
  2. Decisão de Paralelismo: "Este problema envolve mais de um sistema independente? (S/N)"
     - N → continuar para o item 3 (fluxo sequencial normal)
     - S → carregar `dispatching-parallel-agents`, designar 1 agente por domínio, e coordenar os resultados antes de avançar

  3. Gather: exact error message, stack trace, and "when did this last work?"
  ```

  Atenção: o item que antes era "2. Gather" passa a ser "3. Gather". Verificar se há referências numéricas subsequentes no arquivo que precisem ser ajustadas (não há — o restante do arquivo usa seções, não listas numeradas).

- [ ] **Step 3: Verificar o resultado**

  ```bash
  grep -n "Paralelismo\|Gather\|Before loading" "C:/Users/victor.bernardi/.gemini/antigravity/global_workflows/troubleshoot.md"
  ```

  Resultado esperado:
  ```
  13: **Before loading the skill:**
  14: 1. Confirm the issue is reproducible...
  17: 2. Decisão de Paralelismo...
  21: 3. Gather: exact error message...
  ```

- [ ] **Step 4: Commit**

  ```bash
  cd "C:/Users/victor.bernardi/.gemini/antigravity" && git add global_workflows/troubleshoot.md && git commit -m "feat: add parallelism decision gate to /troubleshoot workflow"
  ```

---

## Task 3: Gancho no `/brainstorm` — Revisão adversarial visível

**Files:**
- Modify: `C:\Users\victor.bernardi\.gemini\antigravity\global_workflows\brainstorm.md` (após o item "2. Load brainstorming skill")

- [ ] **Step 1: Verificar o ponto de inserção**

  ```bash
  grep -n "Load brainstorming\|Gate check\|Transition" "C:/Users/victor.bernardi/.gemini/antigravity/global_workflows/brainstorm.md"
  ```

  Resultado esperado:
  ```
  18: 2. **Load brainstorming skill** — follow it completely
  19: 3. **Gate check** before any code...
  20: 4. **Transition** to /plan when user approves
  ```

- [ ] **Step 2: Inserir a revisão adversarial**

  Substituir o bloco:
  ```markdown
  2. **Load brainstorming skill** — follow it completely
  3. **Gate check** before any code: confirm the design doc exists at docs/plans/YYYY-MM-DD-topic-design.md
  4. **Transition** to /plan when user approves
  ```

  Por:
  ```markdown
  2. **Load brainstorming skill** — follow it completely
  3. **Revisão Adversarial** — obrigatória antes de apresentar qualquer proposta ao usuário:
     - Para cada proposta gerada, listar explicitamente ao usuário:
       1. Fragilidade 1
       2. Fragilidade 2
       3. Fragilidade 3
     - Se alguma fragilidade for crítica → reformular a proposta antes de entregar
     - Formato de entrega: proposta + as 3 fragilidades identificadas (sempre visível — nunca silencioso)
  4. **Gate check** before any code: confirm the design doc exists at docs/plans/YYYY-MM-DD-topic-design.md
  5. **Transition** to /plan when user approves
  ```

- [ ] **Step 3: Verificar o resultado**

  ```bash
  grep -n "Revisão Adversarial\|Gate check\|Transition\|Load brainstorming" "C:/Users/victor.bernardi/.gemini/antigravity/global_workflows/brainstorm.md"
  ```

  Resultado esperado:
  ```
  18: 2. **Load brainstorming skill**...
  19: 3. **Revisão Adversarial**...
  26: 4. **Gate check**...
  27: 5. **Transition**...
  ```

- [ ] **Step 4: Commit**

  ```bash
  cd "C:/Users/victor.bernardi/.gemini/antigravity" && git add global_workflows/brainstorm.md && git commit -m "feat: add visible adversarial review to /brainstorm workflow"
  ```

---

## Task 4: Criar `SESSION_START.md` — Protocolo de início de sessão

**Files:**
- Create: `C:\Users\victor.bernardi\.gemini\antigravity\SESSION_START.md`

- [ ] **Step 1: Criar o arquivo**

  Criar `C:\Users\victor.bernardi\.gemini\antigravity\SESSION_START.md` com o conteúdo:

  ```markdown
  # Protocolo de Início de Sessão

  Execute automaticamente ao iniciar qualquer nova sessão no Antigravity.

  ## Passos

  1. Carregar skill `context-agent`
     - Executar: `python %USERPROFILE%\.gemini\antigravity\skills\context-agent\scripts\context_manager.py load`
     - Recuperar snapshot da sessão anterior (ACTIVE_CONTEXT.md + sessão mais recente)

  2. Emitir Briefing de Retomada (máx. 4 linhas):
     ```
     Projeto ativo: [Inova | Stout | Obsidian | outro]
     Em progresso: [tarefa em andamento]
     Pendentes: [próximos passos]
     Erros recentes: [se houver — omitir esta linha se não houver]
     ```

  3. Se nenhum snapshot existir → iniciar sessão limpa sem aviso ao usuário

  ## Restrições

  - O `diary` NÃO é lido no início de sessão — apenas escrito ao final (ver END_OF_TASK.md)
  - O context-agent salva em `skills/context-agent/data/sessions/` — isolado de `brain/`
  - Encaminhamento para wiki-compiler permanece decisão manual do usuário
  ```

- [ ] **Step 2: Verificar o arquivo criado**

  ```bash
  cat "C:/Users/victor.bernardi/.gemini/antigravity/SESSION_START.md"
  ```

  Confirmar que as 3 seções (Passos, Restrições, formato do briefing) estão presentes e legíveis.

- [ ] **Step 3: Commit**

  ```bash
  cd "C:/Users/victor.bernardi/.gemini/antigravity" && git add SESSION_START.md && git commit -m "feat: add SESSION_START protocol for automatic session briefing"
  ```

---

## Task 5: Criar `END_OF_TASK.md` — Protocolo de encerramento

**Files:**
- Create: `C:\Users\victor.bernardi\.gemini\antigravity\END_OF_TASK.md`

- [ ] **Step 1: Criar o arquivo**

  Criar `C:\Users\victor.bernardi\.gemini\antigravity\END_OF_TASK.md` com o conteúdo:

  ```markdown
  # Protocolo de Encerramento de Tarefa

  Execute ao final de cada bloco de trabalho significativo (feature concluída, sessão longa,
  ou quando o usuário sinalizar fim de bloco).

  ## Passos

  1. Marcar tasks concluídas em task.md (se existir no projeto ativo)

  2. Salvar snapshot de contexto via context-agent:
     ```bash
     python %USERPROFILE%\.gemini\antigravity\skills\context-agent\scripts\context_manager.py save
     ```
     → Grava em `skills/context-agent/data/sessions/session-NNN.md`
     → NÃO grava em `brain/` — não alimenta o wiki-compiler automaticamente

  3. Escrever entrada no diary (via skill `diary`):
     - O que foi feito nesta sessão
     - O que foi aprendido
     - Erros cometidos (se houver — registrar também em `diary/erros.md`)

  ## Restrições

  - O encaminhamento de conteúdo para o wiki-compiler é **sempre decisão manual do Victor**
  - Não executar este protocolo para tarefas triviais (perguntas, buscas rápidas)
  - Executar sempre que houver mudança de arquivo, commit, ou tarefa concluída
  ```

- [ ] **Step 2: Verificar o arquivo criado**

  ```bash
  cat "C:/Users/victor.bernardi/.gemini/antigravity/END_OF_TASK.md"
  ```

  Confirmar que o caminho do `context_manager.py` está correto e que a restrição de `brain/` está explícita.

- [ ] **Step 3: Commit**

  ```bash
  cd "C:/Users/victor.bernardi/.gemini/antigravity" && git add END_OF_TASK.md && git commit -m "feat: add END_OF_TASK protocol for session snapshot and diary"
  ```

---

## Task 6: Editar `GEMINI.md` — Regra global de confidence-check

**Files:**
- Modify: `C:\Users\victor.bernardi\.gemini\GEMINI.md` (adicionar seção ao final do arquivo)

- [ ] **Step 1: Verificar o final do arquivo**

  ```bash
  tail -10 "C:/Users/victor.bernardi/.gemini/GEMINI.md"
  ```

  Confirmar qual é a última linha do arquivo para saber onde anexar.

- [ ] **Step 2: Adicionar a seção ao final**

  Anexar ao final de `GEMINI.md`:

  ```markdown

  ---

  ## Regra Global: confidence-check em Código de Dados

  **Aplica-se em qualquer workflow ativo, sem exceção.**

  Antes de entregar qualquer bloco de código que toque dados
  (Python, SQL, Excel, engines Inova — M0 a M4), executar internamente:

  1. Tenho certeza sobre os dados de entrada e seus tipos?
  2. Há edge cases não tratados? (nulos, duplicatas, datas faltando, divisão por zero)
  3. O output pode ser verificado sem executar o código?

  Se a resposta for "Não" em qualquer um dos 3 pontos:
  → Sinalizar explicitamente **antes** de entregar o código
  → Formato: "⚠️ Ponto de atenção: [descrição do que não foi verificado]"

  Esta regra não depende de `/implement` estar ativo. Vale para qualquer resposta
  que contenha código tocando dados do Victor.
  ```

- [ ] **Step 3: Verificar o resultado**

  ```bash
  tail -25 "C:/Users/victor.bernardi/.gemini/GEMINI.md"
  ```

  Confirmar que a seção foi adicionada corretamente e que o separador `---` está presente.

- [ ] **Step 4: Commit**

  ```bash
  cd "C:/Users/victor.bernardi/.gemini" && git add GEMINI.md && git commit -m "feat: add global confidence-check rule for data code to GEMINI.md"
  ```

  Se `.gemini/` não for um repositório git, pular o commit.

---

## Task 7: Criar `diary/erros.md` — Log estruturado de erros

**Files:**
- Create: `C:\Users\victor.bernardi\.gemini\antigravity\diary\` (pasta nova)
- Create: `C:\Users\victor.bernardi\.gemini\antigravity\diary\erros.md`

- [ ] **Step 1: Criar a pasta `diary/`**

  ```bash
  mkdir -p "C:/Users/victor.bernardi/.gemini/antigravity/diary"
  ```

- [ ] **Step 2: Criar o arquivo `erros.md`**

  Criar `C:\Users\victor.bernardi\.gemini\antigravity\diary\erros.md` com o conteúdo:

  ```markdown
  # Log de Erros — Antigravity

  Formato por entrada:
  ```
  DATA | TIPO: [Densidade|Lógica|Contexto|Planejamento] | ERRO → CAUSA RAIZ → CORREÇÃO
  ```

  **Tipos:**
  - **Densidade:** skill simplificada ou degradada sem autorização
  - **Lógica:** raciocínio incorreto sobre o problema
  - **Contexto:** avaliação baseada em informação incompleta ou incorreta
  - **Planejamento:** ordem de execução errada, etapa pulada

  **Regra:** registrar imediatamente ao identificar o erro. Não acumular para depois.

  ---

  ## Entradas

  2026-04-17 | TIPO: Contexto | Avaliei wiki-compiler como pipeline manual → era automatizado via harvest_brain.sh coletando brain/ → corrigi após ler o script
  ```

- [ ] **Step 3: Verificar o arquivo**

  ```bash
  cat "C:/Users/victor.bernardi/.gemini/antigravity/diary/erros.md"
  ```

  Confirmar que o formato, os tipos e a primeira entrada de exemplo estão presentes.

- [ ] **Step 4: Commit**

  ```bash
  cd "C:/Users/victor.bernardi/.gemini/antigravity" && git add diary/ && git commit -m "feat: create diary/erros.md with structured error log format"
  ```

---

## Verificação Final

Após completar todas as 7 tasks:

- [ ] Abrir uma nova sessão no Antigravity e verificar se o Briefing de Retomada aparece
- [ ] Acionar `/implement` com qualquer tarefa e confirmar que a Fase 0 é executada antes do Step 0
- [ ] Descrever dois problemas simultâneos no `/troubleshoot` e confirmar que a pergunta de paralelismo aparece
- [ ] Verificar que `diary/erros.md` existe e é legível
- [ ] Verificar que `GEMINI.md` termina com a seção de confidence-check
