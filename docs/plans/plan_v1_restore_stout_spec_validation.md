# Restauração da Skill stout-spec-validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restaurar fisicamente e logicamente a skill stout-spec-validation do diretório de arquivados para torná-la uma skill oficial ativa.

**Architecture:** Mover a pasta da skill Stout Spec Validation do subdiretório de arquivamento para o diretório ativo e atualizar a propriedade status no registro central de skills (registry.json) para "active".

**Tech Stack:** PowerShell, JSON.

## Global Constraints

* O repositório global de memória reside em `C:\Users\victor.bernardi\.shared-ai-memory`.
* As alterações em `skills/` e no `registry.json` devem ser rastreadas e versionadas via Git.
* A edição do arquivo JSON deve respeitar estritamente a sintaxe válida para evitar quebrar o ledger.

---

### Task 1: Restauração Física dos Arquivos da Skill

**Files:**
* Modify: Mover de `C:\Users\victor.bernardi\.shared-ai-memory\skills\_archived\stout-spec-validation` para `C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-spec-validation`

- [ ] **Step 1: Mover pasta da skill via PowerShell**

Executar comando no PowerShell:
```powershell
Move-Item -Path "C:\Users\victor.bernardi\.shared-ai-memory\skills\_archived\stout-spec-validation" -Destination "C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-spec-validation"
```

- [ ] **Step 2: Verificar se a pasta foi movida com sucesso**

Executar comando no PowerShell:
```powershell
Test-Path "C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-spec-validation"
```
Expected: `True`

- [ ] **Step 3: Verificar se o local de origem foi limpo**

Executar comando no PowerShell:
```powershell
Test-Path "C:\Users\victor.bernardi\.shared-ai-memory\skills\_archived\stout-spec-validation"
```
Expected: `False`

- [ ] **Step 4: Confirmar integridade dos arquivos restaurados**

Executar comando no PowerShell:
```powershell
Get-ChildItem -Path "C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-spec-validation" -Recurse | Select-Object FullName
```
Expected:
```
SKILL.md
references\check-list.md
references\id-system.md
```

---

### Task 2: Reativação da Skill no Ledger Global (registry.json)

**Files:**
* Modify: `C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-skill-registry\registry.json:198-214`

- [ ] **Step 1: Atualizar o status e notas da skill no registry.json**

Localizar o trecho correspondente à skill `stout-spec-validation` no arquivo `C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-skill-registry\registry.json` e aplicar as seguintes alterações:

```diff
     {
       "name": "stout-spec-validation",
       "path": "skills/stout-spec-validation",
       "tier": 2,
       "category": "governance",
       "role": "Validação de consistência SOW -> Spec -> Teste",
       "triggers": [
         "validar especificação",
         "rastreabilidade"
       ],
       "version": "1.3.0",
-      "status": "deprecated",
+      "status": "active",
       "created_at": "2026-05-16",
       "updated_at": "2026-06-18",
       "author": "Victor",
-      "notes": "Arquivado em lote em 2026-06-18 a pedido do usuário.",
+      "notes": "Restaurada a pedido do usuário em 2026-06-18.",
       "promoted_at": "2026-05-29"
     },
```

- [ ] **Step 2: Validar sintaxe do arquivo registry.json**

Executar validação do arquivo JSON para garantir integridade estrutural via PowerShell:
```powershell
Get-Content "C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-skill-registry\registry.json" -Raw | ConvertFrom-Json
```
Expected: O comando deve rodar sem erros de parsing, exibindo o objeto JSON convertido na tela.

---

### Task 3: Verificação de Status Git e Versionamento

**Files:**
* Modify: Git repository state

- [ ] **Step 1: Executar git status**

Executar comando para verificar os arquivos modificados e não rastreados:
```bash
git -C "C:\Users\victor.bernardi\.shared-ai-memory" status
```
Expected: Mostrar a exclusão da pasta antiga, a inclusão da nova pasta `skills/stout-spec-validation` e a modificação no `registry.json`.

- [ ] **Step 2: Adicionar alterações ao índice do Git**

Executar comandos:
```bash
git -C "C:\Users\victor.bernardi\.shared-ai-memory" add skills/stout-spec-validation skills/stout-skill-registry/registry.json
```

- [ ] **Step 3: Confirmar alteração limpa no git diff**

Executar comando:
```bash
git -C "C:\Users\victor.bernardi\.shared-ai-memory" diff --cached registry.json
```
Expected: Mostrar apenas a alteração do status para "active" e a alteração da nota descritiva.

- [ ] **Step 4: Efetuar o commit**

Executar comando:
```bash
git -C "C:\Users\victor.bernardi\.shared-ai-memory" commit -m "chore(skills): restore stout-spec-validation as active official skill"
```
Expected: Commit efetuado com sucesso.
