# Transição de Identidade BUP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Consolidar a mudança de nome do projeto para BUP-base-unica-pós-venda em todo o ecossistema (local e global).

**Architecture:** Abordagem de renomeio em cascata: Memória Global -> Junctions locais -> Documentação de Governança -> Scripts auxiliares.

**Tech Stack:** Python (Pandas), Windows Shell (Junctions), Markdown.

---

### Task 1: Renomear Memória Global (.shared-ai-memory)

**Files:**
- Rename: `C:\Users\victor.bernardi\.shared-ai-memory\.gemini\history\lista-clientes` -> `.../BUP-base-unica-pós-venda`
- Rename: `C:\Users\victor.bernardi\.shared-ai-memory\.gemini\tmp\lista-clientes` -> `.../BUP-base-unica-pós-venda`
- Create: `C:\Users\victor.bernardi\.shared-ai-memory\docs\active\BUP-base-unica-pós-venda`

**Step 1: Renomear pastas de histórico e tmp**
Run: `Rename-Item -Path "C:\Users\victor.bernardi\.shared-ai-memory\.gemini\history\lista-clientes" -NewName "BUP-base-unica-pós-venda"`
Run: `Rename-Item -Path "C:\Users\victor.bernardi\.shared-ai-memory\.gemini\tmp\lista-clientes" -NewName "BUP-base-unica-pós-venda"`

**Step 2: Criar diretório de documentação ativa**
Run: `New-Item -ItemType Directory -Force -Path "C:\Users\victor.bernardi\.shared-ai-memory\docs\active\BUP-base-unica-pós-venda"`

---

### Task 2: Reconstruir Junction Local

**Files:**
- Create Junction: `c:\Projetos\Inova\projects\BUP-base-unica-pós-venda\docs` -> `C:\Users\victor.bernardi\.shared-ai-memory\docs\active\BUP-base-unica-pós-venda`

**Step 1: Remover pasta docs local (se vazia/existente)**
Run: `Remove-Item -Path "docs" -Recurse -Force`

**Step 2: Criar Junction**
Run: `cmd /c mklink /j "docs" "C:\Users\victor.bernardi\.shared-ai-memory\docs\active\BUP-base-unica-pós-venda"`

**Step 3: Validar link**
Run: `ls docs`

---

### Task 3: Atualizar Documentação de Governança

**Files:**
- Modify: `c:\Projetos\Inova\projects\BUP-base-unica-pós-venda\ANTIGRAVITY.md`
- Modify: `c:\Projetos\Inova\projects\BUP-base-unica-pós-venda\GEMINI.md`

**Step 1: Atualizar ANTIGRAVITY.md**
- Mudar `Projeto: lista-clientes` para `Projeto: BUP-base-unica-pós-venda`.
- Atualizar caminhos da Hierarquia e Junction Configurado.

**Step 2: Atualizar GEMINI.md**
- Mudar referência de `scripts/consolidate_cevap.py` para `scripts/consolidate_bup.py`.

---

### Task 4: Ajustar Scripts Auxiliares

**Files:**
- Modify: `c:\Projetos\Inova\projects\BUP-base-unica-pós-venda\scripts\qa_latest_output.py`
- Modify: `c:\Projetos\Inova\projects\BUP-base-unica-pós-venda\scripts\resgate_dados_v4.py`
- Modify: `c:\Projetos\Inova\projects\BUP-base-unica-pós-venda\scripts\polimento_final_v5.py`

**Step 1: Atualizar qa_latest_output.py**
- Remover caminho hardcoded e usar o padrão `BUP_POS_VENDA_*.xlsx`.

**Step 2: Saneamento de caminhos em Scripts de Resgate/Polimento**
- Substituir `C:/Projetos/Inova/Motor CEVAP/data/` por caminhos relativos ao projeto atual ou referências dinâmicas via `PROJECTS`.

---

### Task 5: Commit Final

**Step 1: Commit das alterações**
Run: `git add .`
Run: `git commit -m "chore: rebranding projeto para BUP e correção de caminhos de ingestão/output"`
