# Auditoria e Reparo de Encoding Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Reparar arquivos Markdown corrompidos por encoding ANSI ou "Double UTF-8" e garantir a integridade de caracteres especiais em todo o repositório.

**Architecture:** 
1. **Restauração via Git (Plugins):** Como os plugins são repositórios Git sem modificações locais, utilizaremos `git checkout` para restaurar os arquivos originais corrompidos.
2. **Reparo Automatizado (Local):** Script Python `encoding_fixer.py` para conversão de ANSI e reversão de padrões de corrupção em arquivos autorais (specs, plans, etc.).

**Tech Stack:** Git, Python 3, `chardet`, `pathlib`.

---

### Task 1: Restauração de Plugins (Git Restore)

**Files:**
- `Plugins/antigravity-awesome-skills/`
- `Plugins/everything-claude-code/`
- `Plugins/knowledge-work-plugins/`
- `Plugins/notebooklm-mcp-cli/`

**Step 1: Executar restauração em cada plugin**

**Step 2: Verificar com auditoria**
Run: `python scripts/audit_encoding.py`
Expected: A pasta `Plugins/` deve estar limpa no relatório.

---

### Task 2: Ambiente de Teste (Local)

**Files:**
- Create: `scripts/test_encoding_samples.py`
- Create: `data/test_corrupted_ansi.md`
- Create: `data/test_corrupted_double.md`

**Step 1: Gerar amostras locais de falha**
**Step 2: Validar detecção da auditoria**

---

### Task 3: Implementação e Execução do `encoding_fixer.py` (Local)

**Files:**
- Create: `scripts/encoding_fixer.py`

**Step 1: Implementar e rodar o fixer para a raiz e subpastas locais**
**Step 2: Validar auditoria final**

---

### Task 4: Limpeza e Finalização
**Step 1: Remover backups e arquivos de teste**
**Step 2: Commit final**
