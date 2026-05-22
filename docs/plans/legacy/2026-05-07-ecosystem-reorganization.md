# Ecosystem Reorganization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidar skills e memória em fontes únicas e confiáveis em `~/.shared-ai-memory`, eliminar junctions desnecessários, e migrar Gemini CLI para extensão do Antigravity.

**Architecture:** Toda memória (docs, brain, context-agent, sessions) e as 96 skills vivem fisicamente em `~/.shared-ai-memory`. O Antigravity acessa via junctions existentes em `~/.antigravity/`. Gemini CLI é desinstalado como standalone e reinstalado como extensão do Antigravity via Gemini CLI Companion.

**Tech Stack:** PowerShell (robocopy, cmd mklink, Remove-Item), Windows junction points, Antigravity IDE extension system.

---

## Mapa de Junctions — Estado Atual vs Final

| Junction | Atual | Final |
|----------|-------|-------|
| `~/.shared-ai-memory/skills` | Junction → `C:\Projetos\Stout\antigravity\skills` | **Pasta real** com as 96 skills |
| `~/.shared-ai-memory/context-agent` | Junction → `C:\Projetos\Stout\memory\context-agent` | **Pasta real** com sessions, db, pending |
| `~/.antigravity/skills` | Junction → `~/.shared-ai-memory/skills` | Mantém (aponta para pasta real agora) |
| `~/.gemini/skills` | Junction → `C:\Projetos\Stout\antigravity\skills` | **Remove** |
| `~/.gemini/antigravity` | Junction → `~/.shared-ai-memory` | **Remove** |
| `~/.antigravity/brain,conversations,docs,implicit,knowledge` | Junctions → `~/.shared-ai-memory/...` | Mantém sem alteração |

---

## Fase 0 — Consolidar Memória em ~/.shared-ai-memory

> Esta fase garante que tudo que está em `C:\Projetos\Stout\memory\` seja migrado para `~/.shared-ai-memory` antes de qualquer outra mudança.

### Task 0: Mover context-agent para pasta real em ~/.shared-ai-memory

**Arquivos envolvidos:**
- Source: `C:\Projetos\Stout\memory\context-agent\` (sessions, db, pending, archive, projects...)
- Junction atual: `~/.shared-ai-memory/context-agent → C:\Projetos\Stout\memory\context-agent`
- Destino: `~/.shared-ai-memory/context-agent` (pasta real)

- [ ] **Step 1: Confirmar que o junction existe e está acessível**

```powershell
cmd /c "dir /aL C:\Users\victor.bernardi\.shared-ai-memory\ 2>&1"
(Get-ChildItem "C:\Users\victor.bernardi\.shared-ai-memory\context-agent" -Recurse -File).Count
```

Anotar o número de arquivos — será verificado após a migração.

- [ ] **Step 2: Remover o junction ~/.shared-ai-memory/context-agent**

```powershell
cmd /c "rmdir C:\Users\victor.bernardi\.shared-ai-memory\context-agent"
```

> ⚠️ `rmdir` em junction remove apenas o ponteiro. O conteúdo em `C:\Projetos\Stout\memory\context-agent` permanece intacto.

- [ ] **Step 3: Criar pasta real e copiar conteúdo**

```powershell
New-Item -ItemType Directory -Path "C:\Users\victor.bernardi\.shared-ai-memory\context-agent" -Force
robocopy "C:\Projetos\Stout\memory\context-agent" "C:\Users\victor.bernardi\.shared-ai-memory\context-agent" /E /COPYALL /R:3 /W:5
```

- [ ] **Step 4: Verificar contagem de arquivos**

```powershell
(Get-ChildItem "C:\Users\victor.bernardi\.shared-ai-memory\context-agent" -Recurse -File).Count
```

Esperado: mesmo número anotado no Step 1.

### Task 1b: Mover arquivos soltos de Stout/memory para ~/.shared-ai-memory/memory

**Arquivos envolvidos:**
- `C:\Projetos\Stout\memory\ACTIVE_CONTEXT.md`
- `C:\Projetos\Stout\memory\ARCHITECTURE.md`
- `C:\Projetos\Stout\memory\ecosystem.md`
- `C:\Projetos\Stout\memory\mission.md`
- `C:\Projetos\Stout\memory\preferences.md`
- `C:\Projetos\Stout\memory\PROJECT_REGISTRY.md`
- (MEMORY.md já existe idêntico em ~/.shared-ai-memory/memory/ — ignorar)

- [ ] **Step 1: Copiar arquivos soltos para ~/.shared-ai-memory/memory/**

```powershell
$src = "C:\Projetos\Stout\memory"
$dst = "C:\Users\victor.bernardi\.shared-ai-memory\memory"
@("ACTIVE_CONTEXT.md","ARCHITECTURE.md","ecosystem.md","mission.md","preferences.md","PROJECT_REGISTRY.md") | ForEach-Object {
    Copy-Item "$src\$_" "$dst\$_" -Force
    Write-Output "Copiado: $_"
}
```

- [ ] **Step 2: Verificar que os arquivos chegaram**

```powershell
Get-ChildItem "C:\Users\victor.bernardi\.shared-ai-memory\memory" | Select-Object Name
```

Esperado: `MEMORY.md`, `ACTIVE_CONTEXT.md`, `ARCHITECTURE.md`, `ecosystem.md`, `mission.md`, `preferences.md`, `PROJECT_REGISTRY.md`.

### Task 1c: Atualizar config do context-agent para novo caminho

O context-agent tem um `config.py` que define o caminho base dos dados. Precisa apontar para o novo local.

- [ ] **Step 1: Localizar e ler o config.py**

```powershell
Get-Content "C:\Users\victor.bernardi\.shared-ai-memory\skills\context-agent\scripts\config.py"
```

Identificar a variável que define o `DATA_DIR` ou caminho base.

- [ ] **Step 2: Atualizar o caminho no config.py**

Substituir qualquer referência a `C:\Projetos\Stout\memory\context-agent` ou `~/.gemini/antigravity/skills/context-agent/data` por:

```
C:\Users\victor.bernardi\.shared-ai-memory\context-agent
```

- [ ] **Step 3: Testar que o context-agent encontra os dados**

```powershell
python "C:\Users\victor.bernardi\.shared-ai-memory\skills\context-agent\scripts\context_manager.py" load
```

Esperado: output sem erros de caminho, mostrando o contexto ativo.

---

## Fase 1 — Backup

### Task 1: Backup de skills e memória

**Arquivos envolvidos:**
- Source: `C:\Projetos\Stout\antigravity\skills` (96 skills, pasta real)
- Source: `C:\Projetos\Stout\memory\context-agent` (sessions, db, pending)
- Source: `C:\Users\victor.bernardi\.shared-ai-memory` (memória completa, excluindo junctions)
- Destino: `C:\Backup-AI-Ecosystem-2026-05-07\`

- [ ] **Step 1: Criar pasta de backup**

```powershell
New-Item -ItemType Directory -Path "C:\Backup-AI-Ecosystem-2026-05-07\skills" -Force
New-Item -ItemType Directory -Path "C:\Backup-AI-Ecosystem-2026-05-07\shared-ai-memory" -Force
```

- [ ] **Step 2: Copiar as 96 skills (fonte real)**

```powershell
robocopy "C:\Projetos\Stout\antigravity\skills" "C:\Backup-AI-Ecosystem-2026-05-07\skills" /E /COPYALL /R:3 /W:5
```

Esperado: robocopy retorna exit code 1 (arquivos copiados com sucesso). Exit code > 7 indica erro.

- [ ] **Step 3: Verificar contagem de skills copiadas**

```powershell
(Get-ChildItem "C:\Backup-AI-Ecosystem-2026-05-07\skills" -Directory).Count
```

Esperado: `96`

- [ ] **Step 4: Copiar context-agent (fonte real em Stout)**

```powershell
New-Item -ItemType Directory -Path "C:\Backup-AI-Ecosystem-2026-05-07\context-agent" -Force
robocopy "C:\Projetos\Stout\memory\context-agent" "C:\Backup-AI-Ecosystem-2026-05-07\context-agent" /E /COPYALL /R:3 /W:5
```

- [ ] **Step 5: Copiar shared-ai-memory (excluindo junctions — robocopy não segue por padrão)**

```powershell
robocopy "C:\Users\victor.bernardi\.shared-ai-memory" "C:\Backup-AI-Ecosystem-2026-05-07\shared-ai-memory" /E /COPYALL /XJ /R:3 /W:5
```

O flag `/XJ` exclui junctions — copia apenas arquivos reais presentes em `.shared-ai-memory`.

- [ ] **Step 6: Verificar tamanho do backup**

```powershell
$size = (Get-ChildItem "C:\Backup-AI-Ecosystem-2026-05-07" -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Output "Backup total: $([math]::Round($size, 1)) MB"
```

Esperado: valor > 0 MB. Anotar o número para referência.

- [ ] **Step 7: Registrar estado atual dos junctions (para rollback se necessário)**

```powershell
cmd /c "dir /aL C:\Users\victor.bernardi\.gemini\ 2>&1"
cmd /c "dir /aL C:\Users\victor.bernardi\.shared-ai-memory\ 2>&1"
cmd /c "dir /aL C:\Users\victor.bernardi\.antigravity\ 2>&1"
```

Copiar e salvar o output — é o mapa de rollback.

---

## Fase 2 — Migração das Skills para Pasta Real

### Task 2: Mover skills para ~/.shared-ai-memory/skills (pasta real)

- [ ] **Step 1: Confirmar que o junction atual existe e está funcional**

```powershell
cmd /c "dir /aL C:\Users\victor.bernardi\.shared-ai-memory\ 2>&1"
```

Esperado: linha `<JUNCTION> skills [C:\Projetos\Stout\antigravity\skills]`

- [ ] **Step 2: Remover o junction ~/.shared-ai-memory/skills**

```powershell
cmd /c "rmdir C:\Users\victor.bernardi\.shared-ai-memory\skills"
```

> ⚠️ `rmdir` em junction remove apenas o ponteiro, não o conteúdo do destino. Não use `Remove-Item -Recurse`.

- [ ] **Step 3: Verificar que o junction foi removido e a pasta destino continua intacta**

```powershell
Test-Path "C:\Users\victor.bernardi\.shared-ai-memory\skills"  # deve ser False
(Get-ChildItem "C:\Projetos\Stout\antigravity\skills" -Directory).Count  # deve ser 96
```

- [ ] **Step 4: Criar pasta real ~/.shared-ai-memory/skills**

```powershell
New-Item -ItemType Directory -Path "C:\Users\victor.bernardi\.shared-ai-memory\skills"
```

- [ ] **Step 5: Copiar as 96 skills para o novo local canônico**

```powershell
robocopy "C:\Projetos\Stout\antigravity\skills" "C:\Users\victor.bernardi\.shared-ai-memory\skills" /E /COPYALL /R:3 /W:5
```

- [ ] **Step 6: Verificar que todas as skills chegaram**

```powershell
(Get-ChildItem "C:\Users\victor.bernardi\.shared-ai-memory\skills" -Directory).Count
```

Esperado: `96`

- [ ] **Step 7: Verificar que ~/.antigravity/skills ainda funciona (aponta para pasta real agora)**

```powershell
(Get-ChildItem "C:\Users\victor.bernardi\.antigravity\skills" -Directory).Count
```

Esperado: `96` — confirma que o junction `~/.antigravity/skills → ~/.shared-ai-memory/skills` resolve corretamente.

---

## Fase 3 — Remover Junctions do Gemini CLI

### Task 3: Limpar junctions desnecessários em ~/.gemini

- [ ] **Step 1: Verificar junctions existentes antes de remover**

```powershell
cmd /c "dir /aL C:\Users\victor.bernardi\.gemini\ 2>&1"
```

Esperado: 2 junctions — `antigravity` e `skills`.

- [ ] **Step 2: Remover junction ~/.gemini/skills**

```powershell
cmd /c "rmdir C:\Users\victor.bernardi\.gemini\skills"
```

- [ ] **Step 3: Remover junction ~/.gemini/antigravity**

```powershell
cmd /c "rmdir C:\Users\victor.bernardi\.gemini\antigravity"
```

- [ ] **Step 4: Confirmar que os junctions foram removidos**

```powershell
cmd /c "dir /aL C:\Users\victor.bernardi\.gemini\ 2>&1"
```

Esperado: `Arquivo não encontrado` (nenhum junction restante).

- [ ] **Step 5: Confirmar que ~/.shared-ai-memory não foi afetado**

```powershell
Test-Path "C:\Users\victor.bernardi\.shared-ai-memory\skills"
(Get-ChildItem "C:\Users\victor.bernardi\.shared-ai-memory\skills" -Directory).Count
```

Esperado: `True` e `96`.

---

## Fase 4 — Gemini CLI como Extensão do Antigravity

### Task 4: Instalar Gemini CLI Companion no Antigravity

- [ ] **Step 1: Abrir o Antigravity**

Abrir `C:\Users\victor.bernardi\AppData\Local\Programs\Antigravity\Antigravity.exe`.

- [ ] **Step 2: Abrir uma sessão de chat no Antigravity e executar o comando de vinculação**

No Antigravity, abrir o terminal integrado (ou nova sessão Gemini CLI) e executar:

```
/ide
```

Este comando instala a extensão "Gemini CLI Companion" no Antigravity, vinculando sessões CLI a sessões do IDE.

- [ ] **Step 3: Verificar que a extensão foi instalada**

No Antigravity: Abrir o painel de extensões e confirmar que "Gemini CLI Companion" aparece na lista.

- [ ] **Step 4: Testar que o Gemini CLI reconhece o Antigravity**

Abrir terminal e executar:

```powershell
gemini
```

Dentro da sessão Gemini CLI: verificar que sessões do Antigravity abertas aparecem vinculadas.

### Task 5: Desinstalar Gemini CLI standalone

> ⚠️ Só executar após confirmar que a extensão está funcionando no Step 4 acima.

- [ ] **Step 1: Verificar onde o Gemini CLI standalone está instalado**

```powershell
Get-Command gemini | Select-Object -ExpandProperty Source
```

Anotar o caminho.

- [ ] **Step 2: Desinstalar via winget ou instalador**

Se instalado via winget:
```powershell
winget uninstall --name "Gemini CLI"
```

Se instalado via npm:
```powershell
npm uninstall -g @google/gemini-cli
```

- [ ] **Step 3: Verificar que o comando `gemini` no terminal agora aponta para o bundled do Antigravity**

```powershell
Get-Command gemini -ErrorAction SilentlyContinue | Select-Object Source
```

Esperado: caminho dentro do diretório do Antigravity, ou comando não encontrado (se o acesso for apenas via Antigravity).

---

## Fase 5 — Limpeza Final

### Task 6: Remover pasta antigravity de dentro do Stout

> ⚠️ Só executar após todas as fases anteriores verificadas com sucesso.

- [ ] **Step 1: Confirmar que nenhum junction aponta mais para C:\Projetos\Stout\antigravity\skills**

```powershell
# Verifica todos os junctions nos locais conhecidos
cmd /c "dir /aL C:\Users\victor.bernardi\.gemini\ 2>&1"
cmd /c "dir /aL C:\Users\victor.bernardi\.shared-ai-memory\ 2>&1"
cmd /c "dir /aL C:\Users\victor.bernardi\.antigravity\ 2>&1"
```

Esperado: nenhum junction deve apontar para `C:\Projetos\Stout\antigravity`.

- [ ] **Step 2: Mover para lixeira (não deletar permanentemente)**

```powershell
# Usar shell para mover para lixeira em vez de deletar permanentemente
$shell = New-Object -ComObject Shell.Application
$item = $shell.Namespace(0).ParseName("C:\Projetos\Stout\antigravity")
$item.InvokeVerb("delete")
```

- [ ] **Step 3: Verificar estado final completo**

```powershell
# Skills acessíveis via Antigravity
(Get-ChildItem "C:\Users\victor.bernardi\.antigravity\skills" -Directory).Count

# Pasta real existe
Test-Path "C:\Users\victor.bernardi\.shared-ai-memory\skills"

# Nenhum junction quebrado
cmd /c "dir /aL C:\Users\victor.bernardi\.gemini\ 2>&1"
```

Esperado: `96`, `True`, `Arquivo não encontrado` (zero junctions em .gemini).

---

## Rollback

Se algo der errado em qualquer fase:

```powershell
# Restaurar skills
cmd /c "rmdir C:\Users\victor.bernardi\.shared-ai-memory\skills"
robocopy "C:\Backup-AI-Ecosystem-2026-05-07\skills" "C:\Users\victor.bernardi\.shared-ai-memory\skills" /E /COPYALL

# Restaurar context-agent
cmd /c "rmdir C:\Users\victor.bernardi\.shared-ai-memory\context-agent"
robocopy "C:\Backup-AI-Ecosystem-2026-05-07\context-agent" "C:\Users\victor.bernardi\.shared-ai-memory\context-agent" /E /COPYALL

# Recriar junctions originais se necessário
cmd /c "rmdir C:\Users\victor.bernardi\.shared-ai-memory\skills"
cmd /c "mklink /J C:\Users\victor.bernardi\.shared-ai-memory\skills C:\Projetos\Stout\antigravity\skills"

cmd /c "rmdir C:\Users\victor.bernardi\.shared-ai-memory\context-agent"
cmd /c "mklink /J C:\Users\victor.bernardi\.shared-ai-memory\context-agent C:\Projetos\Stout\memory\context-agent"
```

O backup em `C:\Backup-AI-Ecosystem-2026-05-07\` permanece intocado durante toda a execução. `C:\Projetos\Stout\antigravity\skills` e `C:\Projetos\Stout\memory\context-agent` só são removidos na Fase 5 — antes disso são fontes de rollback.
