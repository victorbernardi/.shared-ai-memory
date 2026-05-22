# Plano de Execução: Otimização de Performance - Skill using-superantigravity

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Refatorar a skill `using-superantigravity` para reduzir a carga de contexto inicial e latência de carregamento, aplicando a Regra 1 (Progressive Disclosure) do ecossistema Stout.

**Architecture:** Fragmentação do monólito `SKILL.md` em 3 níveis. O arquivo principal atuará como um launcher minimalista, enquanto as instruções densas residirão em `references/stout-lifecycle.md`, `references/philosophy.md` e `references/infrastructure.md`.

**Tech Stack:** Markdown, Shell (PowerShell), Gemini Skill Pattern.

---

### Task 1: Estruturação de Referências (Nível 3)

**Files:**
- Create: `C:\Users\victor.bernardi\.shared-ai-memory\.gemini\skills\process-superantigravity\references\philosophy.md`
- Create: `C:\Users\victor.bernardi\.shared-ai-memory\.gemini\skills\process-superantigravity\references\infrastructure.md`

**Step 1: Criar philosophy.md**
Mover as seções "Core Philosophy", "Red Flags" e o gráfico DOT para este arquivo.

**Step 2: Criar infrastructure.md**
Mover as seções "How to Access Skills", "Clonagem e Isolamento" e "Comando promote-to-global" para este arquivo.

**Step 3: Validar arquivos**
Run: `ls C:\Users\victor.bernardi\.shared-ai-memory\.gemini\skills\process-superantigravity\references\`
Expected: Ver os novos arquivos .md listados.

---

### Task 2: Definição do Ciclo de Vida (Nível 2)

**Files:**
- Create: `C:\Users\victor.bernardi\.shared-ai-memory\.gemini\skills\process-superantigravity\references\stout-lifecycle.md`

**Step 1: Criar stout-lifecycle.md**
Mover o detalhamento das fases Research (Brainstorm), Strategy (Plan) e Build (Execution) para este arquivo.

**Step 2: Adicionar cabeçalho de ativação**
Incluir no topo do arquivo uma instrução clara de que este é o Nível 2 de ativação obrigatório para as fases de projeto.

---

### Task 3: Refatoração do Launcher Minimalista (Nível 1)

**Files:**
- Modify: `C:\Users\victor.bernardi\.shared-ai-memory\.gemini\skills\process-superantigravity\SKILL.md`

**Step 1: Limpeza do SKILL.md**
Remover todo o conteúdo denso, mantendo apenas:
- Frontmatter YAML.
- Seção "Inicialização de Sessão" (brain-watcher.py).
- Seção "When to Use" simplificada.
- Seção "Launcher" apontando para os arquivos em `references/`.

**Step 2: Inserir instrução de carregamento de nível**
```markdown
## Como Usar esta Skill
Esta skill agora opera em 3 níveis (Regra 1 GEMINI.md).
1. **Nível 1 (Atual):** Monitoramento de infraestrutura.
2. **Nível 2 (Processo):** Leia `references/stout-lifecycle.md` para iniciar uma fase de projeto.
3. **Nível 3 (Base):** Consulte `references/philosophy.md` ou `infrastructure.md` para dúvidas teóricas.
```

---

### Task 4: Validação Final e Teste de Carga

**Step 1: Simular ativação**
Run: `activate_skill using-superantigravity`
Expected: Resposta instantânea e presença apenas do launcher minimalista no contexto.

**Step 2: Simular acesso ao Ciclo de Vida**
Run: `read_file C:\Users\victor.bernardi\.shared-ai-memory\.gemini\skills\process-superantigravity\references\stout-lifecycle.md`
Expected: Acesso total às instruções das fases sem inflar a inicialização.

**Step 3: Verificar Background Watcher**
Run: `list_background_processes`
Expected: Confirmar que o `brain-watcher.py` continua sendo disparado.
