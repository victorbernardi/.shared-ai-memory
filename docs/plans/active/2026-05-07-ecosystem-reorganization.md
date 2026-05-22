# Ecosystem Reorganization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Estabelecer `~/.gemini` como home real do Gemini CLI, consolidar toda memória e skills em `~/.shared-ai-memory`, eliminar junctions desnecessários, e migrar Gemini CLI para extensão do Antigravity.

**Architecture:** `C:\Projetos\Stout\.gemini` era a home real do Gemini CLI mas deveria ser `~/.gemini`. As 96 skills e o context-agent vivem dentro de `C:\Projetos\Stout` mas deveriam viver em `~/.shared-ai-memory`. O plano inverte essas relações: move tudo para os lugares canônicos e elimina as dependências de projeto.

**Tech Stack:** PowerShell (robocopy, cmd mklink/rmdir), Windows junction points, Antigravity IDE extension system.

---

## Estado Atual (o problema)

```
~/.gemini/                          ← quase vazia, só 2 junctions
  skills  →  Stout/antigravity/skills
  antigravity  →  ~/.shared-ai-memory

C:\Projetos\Stout\.gemini/          ← home REAL do Gemini CLI (errado)
  settings.json                     ← config global dos MCPs
  GEMINI.md, ANTIGRAVITY.md         ← docs globais
  perfil.md.md                      ← memória pessoal
  draft/                            ← rascunhos
  .git                              ← repositório git próprio
  antigravity  →  ~/.shared-ai-memory

~/.shared-ai-memory/                ← correto, mas com junctions para Stout
  skills  →  Stout/antigravity/skills
  context-agent  →  Stout/memory/context-agent

C:\Projetos\Stout/memory/           ← memória do ecossistema (errado)
  context-agent/                    ← sessions, db, pending
  ARCHITECTURE.md, ecosystem.md...  ← docs globais

C:\Projetos\Stout/antigravity/skills/  ← 96 skills (errado)
```

## Estado Final (o objetivo)

```
~/.gemini/                          ← home real do Gemini CLI
  settings.json                     ← config global dos MCPs (movida)
  GEMINI.md, ANTIGRAVITY.md         ← docs globais (movidos)
  .env                              ← variáveis de ambiente (movido)

~/.shared-ai-memory/                ← fonte única de verdade
  skills/                           ← pasta REAL com 96 skills
  context-agent/                    ← pasta REAL com sessions, db, pending
  memory/                           ← docs globais (ecosystem, mission...)
  brain/, conversations/, docs/...  ← já corretos

~/.antigravity/                     ← acesso do Antigravity via junctions
  skills  →  ~/.shared-ai-memory/skills      (já existe, passa a apontar para pasta real)
  brain, conversations, docs...     ← já corretos

C:\Projetos\Stout/                  ← apenas código do projeto
  (sem .gemini, sem antigravity, sem memory)
```

## Mapa de Junctions — Atual vs Final

| Junction | Atual | Final |
|----------|-------|-------|
| `~/.shared-ai-memory/skills` | Junction → `Stout/antigravity/skills` | **Pasta real** |
| `~/.shared-ai-memory/context-agent` | Junction → `Stout/memory/context-agent` | **Pasta real** |
| `~/.antigravity/skills` | Junction → `~/.shared-ai-memory/skills` | Mantém |
| `~/.gemini/skills` | Junction → `Stout/antigravity/skills` | **Remove** |
| `~/.gemini/antigravity` | Junction → `~/.shared-ai-memory` | **Remove** |
| `Stout/.gemini/antigravity` | Junction → `~/.shared-ai-memory` | **Remove** (junto com a pasta) |

---

## Fase 0 — Inverter ~/.gemini e Stout/.gemini

> Estabelecer `~/.gemini` como home real do Gemini CLI. Hoje `C:\Projetos\Stout\.gemini` tem a config real e `~/.gemini` está quase vazia.

### Task 0: Mover config global do Stout/.gemini para ~/.gemini

**Arquivos a mover de `C:\Projetos\Stout\.gemini\` para `~/.gemini\`:**
- `settings.json` — já existe idêntico em `~/.gemini` (via junction) → confirmar e manter
- `GEMINI.md` — doc global do Gemini CLI
- `ANTIGRAVITY.md` — doc global do Antigravity
- `.env` — variáveis de ambiente globais
- `perfil.md.md` → vai para `~/.shared-ai-memory/memory/perfil.md`
- `install_stout_init.py` → vai para `~/.shared-ai-memory/scripts/`
- `draft/` → vai para `~/.shared-ai-memory/scratch/draft/`
- `antigravity-browser-profile/` → vai para `~/.antigravity/`

**Não mover:**
- `.git` — repositório git do Stout/.gemini, avaliar separado
- `chrome_profile_notebooklm/` — perfil de browser, avaliar separado
- `.pytest_cache/` — cache temporário, pode deletar

- [ ] **Step 1: Verificar que settings.json é idêntico nos dois lugares**

```powershell
$a = Get-Content "C:\Users\victor.bernardi\.gemini\settings.json" -Raw
$b = Get-Content "C:\Projetos\Stout\.gemini\settings.json" -Raw
if ($a -eq $b) { Write-Output "IDÊNTICOS — ok" } else { Write-Output "DIFERENTES — revisar antes de continuar" }
```

Esperado: `IDÊNTICOS — ok`

- [ ] **Step 2: Copiar GEMINI.md e ANTIGRAVITY.md para ~/.gemini**

```powershell
Copy-Item "C:\Projetos\Stout\.gemini\GEMINI.md" "C:\Users\victor.bernardi\.gemini\GEMINI.md" -Force
Copy-Item "C:\Projetos\Stout\.gemini\ANTIGRAVITY.md" "C:\Users\victor.bernardi\.gemini\ANTIGRAVITY.md" -Force
```

- [ ] **Step 3: Copiar .env para ~/.gemini**

```powershell
Copy-Item "C:\Projetos\Stout\.gemini\.env" "C:\Users\victor.bernardi\.gemini\.env" -Force
```

- [ ] **Step 4: Mover perfil para ~/.shared-ai-memory/memory**

```powershell
Copy-Item "C:\Projetos\Stout\.gemini\perfil.md.md" "C:\Users\victor.bernardi\.shared-ai-memory\memory\perfil.md" -Force
```

- [ ] **Step 5: Mover install_stout_init.py para ~/.shared-ai-memory/scripts**

```powershell
Copy-Item "C:\Projetos\Stout\.gemini\install_stout_init.py" "C:\Users\victor.bernardi\.shared-ai-memory\scripts\install_stout_init.py" -Force
```

- [ ] **Step 6: Mover draft/ para ~/.shared-ai-memory/scratch/draft**

```powershell
robocopy "C:\Projetos\Stout\.gemini\draft" "C:\Users\victor.bernardi\.shared-ai-memory\scratch\draft" /E /COPYALL /R:3 /W:5
```

- [ ] **Step 7: Mover antigravity-browser-profile para ~/.antigravity**

```powershell
robocopy "C:\Projetos\Stout\.gemini\antigravity-browser-profile" "C:\Users\victor.bernardi\.antigravity\antigravity-browser-profile" /E /COPYALL /R:3 /W:5
```

- [ ] **Step 8: Remover junction Stout/.gemini/antigravity**

```powershell
cmd /c "rmdir C:\Projetos\Stout\.gemini\antigravity"
```

- [ ] **Step 9: Remover junction Stout/.gemini/skills**

```powershell
cmd /c "rmdir C:\Projetos\Stout\.gemini\skills"
```

- [ ] **Step 10: Verificar estado de ~/.gemini após migração**

```powershell
cmd /c "dir /a C:\Users\victor.bernardi\.gemini 2>&1"
```

Esperado: `settings.json`, `GEMINI.md`, `ANTIGRAVITY.md`, `.env` presentes. Nenhum junction.

---

## Fase 1 — Consolidar Memória em ~/.shared-ai-memory

### Task 1: Mover context-agent para pasta real

**Source:** `C:\Projetos\Stout\memory\context-agent\`
**Junction atual:** `~/.shared-ai-memory/context-agent → Stout/memory/context-agent`
**Destino:** `~/.shared-ai-memory/context-agent` (pasta real)

- [ ] **Step 1: Anotar contagem de arquivos antes da migração**

```powershell
(Get-ChildItem "C:\Projetos\Stout\memory\context-agent" -Recurse -File).Count
```

Anotar o número.

- [ ] **Step 2: Remover junction**

```powershell
cmd /c "rmdir C:\Users\victor.bernardi\.shared-ai-memory\context-agent"
```

- [ ] **Step 3: Criar pasta real e copiar conteúdo**

```powershell
New-Item -ItemType Directory -Path "C:\Users\victor.bernardi\.shared-ai-memory\context-agent" -Force
robocopy "C:\Projetos\Stout\memory\context-agent" "C:\Users\victor.bernardi\.shared-ai-memory\context-agent" /E /COPYALL /R:3 /W:5
```

- [ ] **Step 4: Verificar contagem**

```powershell
(Get-ChildItem "C:\Users\victor.bernardi\.shared-ai-memory\context-agent" -Recurse -File).Count
```

Esperado: mesmo número do Step 1.

### Task 2: Mover arquivos soltos de Stout/memory para ~/.shared-ai-memory/memory

- [ ] **Step 1: Copiar arquivos**

```powershell
$src = "C:\Projetos\Stout\memory"
$dst = "C:\Users\victor.bernardi\.shared-ai-memory\memory"
@("ACTIVE_CONTEXT.md","ARCHITECTURE.md","ecosystem.md","mission.md","preferences.md","PROJECT_REGISTRY.md") | ForEach-Object {
    Copy-Item "$src\$_" "$dst\$_" -Force
    Write-Output "Copiado: $_"
}
```

- [ ] **Step 2: Verificar**

```powershell
Get-ChildItem "C:\Users\victor.bernardi\.shared-ai-memory\memory" | Select-Object Name
```

### Task 3: Atualizar config.py do context-agent para novo caminho

- [ ] **Step 1: Ler config.py atual**

```powershell
Get-Content "C:\Users\victor.bernardi\.shared-ai-memory\skills\context-agent\scripts\config.py"
```

Identificar variável `DATA_DIR` ou equivalente.

- [ ] **Step 2: Atualizar caminho**

Substituir qualquer referência a `C:\Projetos\Stout\memory\context-agent` por:
```
C:\Users\victor.bernardi\.shared-ai-memory\context-agent
```

- [ ] **Step 3: Testar**

```powershell
python "C:\Users\victor.bernardi\.shared-ai-memory\skills\context-agent\scripts\context_manager.py" load
```

Esperado: output sem erros de caminho.

---

## Fase 2 — Backup Completo

> Feito após consolidação, antes de qualquer remoção.

### Task 4: Backup

- [ ] **Step 1: Criar pastas de backup**

```powershell
New-Item -ItemType Directory -Path "C:\Backup-AI-Ecosystem-2026-05-07\skills" -Force
New-Item -ItemType Directory -Path "C:\Backup-AI-Ecosystem-2026-05-07\shared-ai-memory" -Force
New-Item -ItemType Directory -Path "C:\Backup-AI-Ecosystem-2026-05-07\gemini-config" -Force
```

- [ ] **Step 2: Backup das 96 skills**

```powershell
robocopy "C:\Projetos\Stout\antigravity\skills" "C:\Backup-AI-Ecosystem-2026-05-07\skills" /E /COPYALL /R:3 /W:5
```

Verificar: `(Get-ChildItem "C:\Backup-AI-Ecosystem-2026-05-07\skills" -Directory).Count` → esperado `96`

- [ ] **Step 3: Backup de ~/.shared-ai-memory (excluindo junctions)**

```powershell
robocopy "C:\Users\victor.bernardi\.shared-ai-memory" "C:\Backup-AI-Ecosystem-2026-05-07\shared-ai-memory" /E /COPYALL /XJ /R:3 /W:5
```

- [ ] **Step 4: Backup de ~/.gemini**

```powershell
robocopy "C:\Users\victor.bernardi\.gemini" "C:\Backup-AI-Ecosystem-2026-05-07\gemini-config" /E /COPYALL /XJ /R:3 /W:5
```

- [ ] **Step 5: Verificar tamanho total**

```powershell
$size = (Get-ChildItem "C:\Backup-AI-Ecosystem-2026-05-07" -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Output "Backup total: $([math]::Round($size, 1)) MB"
```

---

## Fase 3 — Migrar Skills para Pasta Real

### Task 5: Mover skills para ~/.shared-ai-memory/skills

- [ ] **Step 1: Remover junction ~/.shared-ai-memory/skills**

```powershell
cmd /c "rmdir C:\Users\victor.bernardi\.shared-ai-memory\skills"
```

> ⚠️ `rmdir` em junction remove apenas o ponteiro. O conteúdo em `Stout/antigravity/skills` permanece intacto.

- [ ] **Step 2: Criar pasta real e copiar**

```powershell
New-Item -ItemType Directory -Path "C:\Users\victor.bernardi\.shared-ai-memory\skills"
robocopy "C:\Projetos\Stout\antigravity\skills" "C:\Users\victor.bernardi\.shared-ai-memory\skills" /E /COPYALL /R:3 /W:5
```

- [ ] **Step 3: Verificar**

```powershell
(Get-ChildItem "C:\Users\victor.bernardi\.shared-ai-memory\skills" -Directory).Count
(Get-ChildItem "C:\Users\victor.bernardi\.antigravity\skills" -Directory).Count
```

Esperado: `96` nos dois — confirma que `~/.antigravity/skills → ~/.shared-ai-memory/skills` resolve corretamente.

---

## Fase 4 — Remover Junctions do ~/.gemini

### Task 6: Limpar ~/.gemini

- [ ] **Step 1: Remover junction ~/.gemini/skills**

```powershell
cmd /c "rmdir C:\Users\victor.bernardi\.gemini\skills"
```

- [ ] **Step 2: Remover junction ~/.gemini/antigravity**

```powershell
cmd /c "rmdir C:\Users\victor.bernardi\.gemini\antigravity"
```

- [ ] **Step 3: Confirmar estado final de ~/.gemini**

```powershell
cmd /c "dir /a C:\Users\victor.bernardi\.gemini 2>&1"
```

Esperado: `settings.json`, `GEMINI.md`, `ANTIGRAVITY.md`, `.env`. Nenhum junction.

- [ ] **Step 4: Confirmar que ~/.shared-ai-memory não foi afetado**

```powershell
(Get-ChildItem "C:\Users\victor.bernardi\.shared-ai-memory\skills" -Directory).Count
Test-Path "C:\Users\victor.bernardi\.shared-ai-memory\context-agent"
```

Esperado: `96` e `True`.

---

## Fase 5 — Gemini CLI como Extensão do Antigravity

### Task 7: Instalar Gemini CLI Companion no Antigravity

- [ ] **Step 1: Abrir o Antigravity**

Abrir `C:\Users\victor.bernardi\AppData\Local\Programs\Antigravity\Antigravity.exe`.

- [ ] **Step 2: Executar o comando de vinculação**

No terminal integrado do Antigravity:
```
/ide
```

Este comando instala a extensão "Gemini CLI Companion" vinculando sessões CLI a sessões do IDE.

- [ ] **Step 3: Confirmar extensão instalada**

No Antigravity: painel de extensões → confirmar "Gemini CLI Companion" presente.

- [ ] **Step 4: Verificar onde a extensão salva sua config**

No Antigravity, verificar se foi criado um `settings.json` para a extensão Gemini CLI Companion. Localização provável:
```
C:\Users\victor.bernardi\AppData\Roaming\Antigravity\User\globalStorage\
```

Anotar o caminho encontrado.

- [ ] **Step 5: Verificar MCPs configurados na extensão**

Abrir o `settings.json` da extensão e confirmar se os MCPs estão presentes. MCPs que devem existir:
- `context7`
- `tavily-search`
- `github-mcp-server`
- `google-drive`
- `google-developer-knowledge`
- `google-cloud-logging`
- `cloudrun`
- `chrome-devtools-mcp`
- `notion-mcp-server`
- `notebooklm`

- [ ] **Step 6: Migrar MCPs se a extensão gerou config vazia**

Se o `settings.json` da extensão não tiver os MCPs, copiar o conteúdo de `~/.gemini/settings.json` para ele:

```powershell
# Substituir <caminho-da-extensao> pelo caminho encontrado no Step 4
Copy-Item "C:\Users\victor.bernardi\.gemini\settings.json" "<caminho-da-extensao>\settings.json" -Force
```

- [ ] **Step 7: Testar vinculação e MCPs**

```powershell
gemini
```

Dentro da sessão Gemini CLI Companion: executar `/mcp` ou equivalente para listar MCPs ativos. Confirmar que todos os 10 MCPs aparecem.

### Task 8: Desinstalar Gemini CLI standalone

> ⚠️ Só executar após Task 7 Step 4 confirmado.

- [ ] **Step 1: Verificar instalação atual**

```powershell
Get-Command gemini | Select-Object -ExpandProperty Source
```

- [ ] **Step 2: Desinstalar**

Se via npm:
```powershell
npm uninstall -g @google/gemini-cli
```

Se via winget:
```powershell
winget uninstall --name "Gemini CLI"
```

- [ ] **Step 3: Confirmar**

```powershell
Get-Command gemini -ErrorAction SilentlyContinue | Select-Object Source
```

---

## Fase 6 — Limpeza Final

### Task 9: Remover pastas do Stout que migraram

> ⚠️ Só após todas as fases anteriores verificadas. Mover para lixeira, não deletar permanentemente.

- [ ] **Step 1: Confirmar que nenhum junction aponta para Stout/antigravity ou Stout/memory**

```powershell
cmd /c "dir /aL C:\Users\victor.bernardi\.gemini\ 2>&1"
cmd /c "dir /aL C:\Users\victor.bernardi\.shared-ai-memory\ 2>&1"
cmd /c "dir /aL C:\Users\victor.bernardi\.antigravity\ 2>&1"
```

Esperado: zero junctions apontando para `C:\Projetos\Stout`.

- [ ] **Step 2: Mover Stout/antigravity para lixeira**

```powershell
$shell = New-Object -ComObject Shell.Application
$shell.Namespace(0).ParseName("C:\Projetos\Stout\antigravity").InvokeVerb("delete")
```

- [ ] **Step 3: Mover Stout/memory para lixeira**

```powershell
$shell = New-Object -ComObject Shell.Application
$shell.Namespace(0).ParseName("C:\Projetos\Stout\memory").InvokeVerb("delete")
```

- [ ] **Step 4: Verificar estado final**

```powershell
(Get-ChildItem "C:\Users\victor.bernardi\.antigravity\skills" -Directory).Count
cmd /c "dir /aL C:\Users\victor.bernardi\.gemini\ 2>&1"
cmd /c "dir /aL C:\Users\victor.bernardi\.shared-ai-memory\ 2>&1"
```

Esperado: `96`, zero junctions em `.gemini`, zero junctions em `.shared-ai-memory`.

---

## Rollback

```powershell
# Restaurar skills
cmd /c "rmdir C:\Users\victor.bernardi\.shared-ai-memory\skills"
cmd /c "mklink /J C:\Users\victor.bernardi\.shared-ai-memory\skills C:\Projetos\Stout\antigravity\skills"

# Restaurar context-agent
cmd /c "rmdir C:\Users\victor.bernardi\.shared-ai-memory\context-agent"
cmd /c "mklink /J C:\Users\victor.bernardi\.shared-ai-memory\context-agent C:\Projetos\Stout\memory\context-agent"

# Restaurar junctions ~/.gemini
cmd /c "mklink /J C:\Users\victor.bernardi\.gemini\antigravity C:\Users\victor.bernardi\.shared-ai-memory"
cmd /c "mklink /J C:\Users\victor.bernardi\.gemini\skills C:\Projetos\Stout\antigravity\skills"
```

`C:\Projetos\Stout\antigravity\skills` e `C:\Projetos\Stout\memory\context-agent` só são removidos na Fase 6 — até lá são fontes de rollback. O backup em `C:\Backup-AI-Ecosystem-2026-05-07\` permanece intocado.

---

## Próximos Planos (fora do escopo deste)

1. **Automatizar legacy/active** — criar fluxo que move planos de `docs/plans/active/` para `docs/plans/legacy/` quando concluídos
2. **Rever .git em Stout/.gemini** — avaliar o repositório git que existe em `C:\Projetos\Stout\.gemini`
3. **Avaliar `chrome_profile_notebooklm/`** — presente em múltiplos lugares, definir localização canônica
