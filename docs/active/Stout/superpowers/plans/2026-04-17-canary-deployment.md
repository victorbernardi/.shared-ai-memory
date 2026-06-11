# Canary Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Criar a skill `canary-deployment` no Antigravity para proteger qualquer modificação significativa nos domínios monitorados com comparação explícita e aprovação manual antes de promover.

**Architecture:** Uma skill markdown (SKILL.md) que instrui o agente Gemini CLI a seguir o protocolo de canary sempre que modificar arquivos nos domínios monitorados. Backup via arquivos `.stable.*`, comparação via diff, log em `diary/canary-log.md`.

**Tech Stack:** Markdown (instrução para Gemini CLI), bash (`diff`, `copy`, `del`), Python (execução paralela de engines quando necessário).

---

## Mapa de Arquivos

| Arquivo | Ação |
|---------|------|
| `C:\Users\victor.bernardi\.gemini\antigravity\skills\canary-deployment\SKILL.md` | Criar |
| `C:\Users\victor.bernardi\.gemini\antigravity\diary\canary-log.md` | Criar |

---

## Task 1: Criar skill `canary-deployment`

**Files:**
- Create: `C:\Users\victor.bernardi\.gemini\antigravity\skills\canary-deployment\SKILL.md`

- [x] **Step 1: Criar o diretório da skill**

```bash
mkdir -p "C:/Users/victor.bernardi/.gemini/antigravity/skills/canary-deployment"
```

Verificar:
```bash
ls "C:/Users/victor.bernardi/.gemini/antigravity/skills/canary-deployment/"
```
Resultado esperado: diretório vazio criado.

- [x] **Step 2: Criar SKILL.md com o protocolo completo**

Criar `C:\Users\victor.bernardi\.gemini\antigravity\skills\canary-deployment\SKILL.md` com o conteúdo exato abaixo:

```markdown
---
name: canary-deployment
description: "Protocolo universal de canary deployment para o ecossistema Antigravity. Ativa automaticamente antes de salvar modificações significativas nos domínios monitorados — apresenta comparação lado a lado e exige aprovação antes de promover a nova versão."
risk: safe
source: custom
date_added: "2026-04-17"
tags:
- canary
- deployment
- safety
- file-protection
tools:
- antigravity
- gemini-cli
- claude-code
---

# Canary Deployment — Protocolo Universal

## Quando Usar Esta Skill

Ativar ANTES de salvar qualquer modificação significativa nos seguintes domínios:

### Domínios Monitorados (sempre canary)
- `C:\Users\victor.bernardi\.gemini\antigravity\**` — ecossistema Antigravity completo
- `C:\Users\victor.bernardi\.gemini\GEMINI.md` — config global
- `C:\Projetos\Stout\**\*.py`, `*.sh`, `*.md` — projetos Stout
- `C:\Projetos\Inova\**\*.py`, `*.sql` — engines e queries Inova
- `C:\Projetos\*\**\*.py`, `*.sh` — qualquer novo projeto em C:\Projetos\

### NÃO Ativar Para
- Arquivos dentro de `docs/`, `raw/`, `diary/` (exceto `diary/canary-log.md`)
- Edições triviais: typos, formatação, comentários sem impacto funcional
- Primeiro arquivo substantivo de um novo projeto (sem versão anterior para comparar)
- Arquivos de log, outputs temporários, `.gitignore`

---

## Protocolo Completo

### Passo 1 — Backup (antes de salvar)

Copiar o arquivo atual para `.stable.*` ANTES de aplicar qualquer modificação:

```bash
# Windows (Git Bash / PowerShell)
copy "<caminho\arquivo.ext>" "<caminho\arquivo.stable.ext>"
```

Exemplos:
```bash
copy "C:\Users\victor.bernardi\.gemini\antigravity\skills\task-intelligence\SKILL.md" \
     "C:\Users\victor.bernardi\.gemini\antigravity\skills\task-intelligence\SKILL.stable.md"

copy "C:\Projetos\Inova\engines\engine_M1.py" \
     "C:\Projetos\Inova\engines\engine_M1.stable.py"
```

### Passo 2 — Salvar nova versão

Salvar a modificação no arquivo original normalmente (Edit ou Write).

### Passo 3 — Apresentar comparação

**Modo Texto** — para: `.md`, `.yaml`, `.json`, `.txt`, `.sh`

```
═══════════════════════════════════════════════════
CANARY ATIVO: <caminho relativo do arquivo>
═══════════════════════════════════════════════════
```

Executar diff e apresentar ao usuário:
```bash
diff "<arquivo.stable.ext>" "<arquivo.ext>"
```

Apresentar o output do diff no formato:
```
STABLE (atual)          │ CANARY (nova versão)
────────────────────────┼────────────────────────
- linha removida        │
                        │ + linha adicionada
  linha igual           │   linha igual
```

**Modo Execução** — para: `.py`, `.sql`

```
═══════════════════════════════════════════════════
CANARY ATIVO: <caminho relativo do arquivo>
═══════════════════════════════════════════════════
```

1. Apresentar diff de código primeiro (mesmo formato acima)
2. Perguntar: `Executar ambas as versões no dataset de amostra para comparar outputs? (S/N)`
3. Se S → perguntar: `Qual dataset/input usar para o teste?`
4. Executar ambas as versões:
```bash
python "<arquivo.stable.py>" <args informados pelo usuário>
python "<arquivo.py>" <args informados pelo usuário>
```
5. Apresentar outputs lado a lado para comparação visual

### Passo 4 — Decisão de promoção

```
Promover canary para stable? (S/N)
```

**Se S (promover):**
```bash
del "<arquivo.stable.ext>"
```
Registrar em `C:\Users\victor.bernardi\.gemini\antigravity\diary\canary-log.md`:
```
<YYYY-MM-DD> | <caminho relativo do arquivo> | AÇÃO: promovido | <resumo de 1 linha da mudança>
```

**Se N (reverter):**
```bash
copy "<arquivo.stable.ext>" "<arquivo.ext>"
del "<arquivo.stable.ext>"
```
Registrar em `diary\canary-log.md`:
```
<YYYY-MM-DD> | <caminho relativo do arquivo> | AÇÃO: revertido | <resumo de 1 linha da mudança>
```

---

## Rollback Posterior

Quando Victor usar `/canary rollback <arquivo>`:

1. Consultar `diary\canary-log.md` — localizar entrada mais recente do arquivo informado
2. Verificar se `<arquivo.stable.ext>` ainda existe:
   - **Sim** → restaurar:
     ```bash
     copy "<arquivo.stable.ext>" "<arquivo.ext>"
     del "<arquivo.stable.ext>"
     ```
   - **Não** → informar: "Backup `.stable.*` não encontrado. Se o repositório usa git, tente: `git checkout HEAD~1 -- <arquivo>`"
3. Registrar em `diary\canary-log.md`:
   ```
   <YYYY-MM-DD> | <arquivo> | AÇÃO: rollback-manual | solicitado pelo usuário
   ```

---

## Regras de Ouro

1. **Nunca salvar sem backup primeiro** — o `.stable.*` é criado antes do Edit/Write
2. **Nunca promover automaticamente** — sempre aguardar S/N do Victor
3. **Sempre registrar em canary-log.md** — tanto promoções quanto reversões
4. **Modo execução só com input confirmado** — nunca presumir o dataset de teste
```

- [x] **Step 3: Verificar o arquivo criado**

```bash
cat "C:/Users/victor.bernardi/.gemini/antigravity/skills/canary-deployment/SKILL.md" | head -20
```

Resultado esperado: frontmatter com `name: canary-deployment` e início do conteúdo.

- [x] **Step 4: Verificar estrutura da skill**

```bash
grep -n "Domínios Monitorados\|Passo 1\|Passo 2\|Passo 3\|Passo 4\|Rollback\|Regras de Ouro" \
  "C:/Users/victor.bernardi/.gemini/antigravity/skills/canary-deployment/SKILL.md"
```

Resultado esperado: todas as 7 seções encontradas.

---

## Task 2: Criar `diary/canary-log.md`

**Files:**
- Modify: `C:\Users\victor.bernardi\.gemini\antigravity\diary\canary-log.md` (criar — `diary/` já existe)

- [x] **Step 1: Confirmar que `diary/` existe**

```bash
ls "C:/Users/victor.bernardi/.gemini/antigravity/diary/"
```

Resultado esperado: `erros.md` listado (criado anteriormente). Se `diary/` não existir: `mkdir -p "C:/Users/victor.bernardi/.gemini/antigravity/diary"`.

- [x] **Step 2: Criar canary-log.md**

Criar `C:\Users\victor.bernardi\.gemini\antigravity\diary\canary-log.md` com o conteúdo:

```markdown
# Canary Log — Antigravity

Registro de todas as promoções e reversões de canary deployment.

## Formato

```
YYYY-MM-DD | <caminho relativo do arquivo> | AÇÃO: [promovido|revertido|rollback-manual] | <resumo da mudança>
```

## Entradas

<!-- Entradas serão adicionadas automaticamente pelo protocolo canary-deployment -->
```

- [x] **Step 3: Verificar o arquivo**

```bash
cat "C:/Users/victor.bernardi/.gemini/antigravity/diary/canary-log.md"
```

Resultado esperado: heading, formato e placeholder de entradas presentes.

---

## Task 3: Verificação Final

- [x] **Step 1: Confirmar estrutura completa**

```bash
ls "C:/Users/victor.bernardi/.gemini/antigravity/skills/canary-deployment/"
ls "C:/Users/victor.bernardi/.gemini/antigravity/diary/"
```

Resultado esperado:
```
# skills/canary-deployment/
SKILL.md

# diary/
canary-log.md
erros.md
```

- [x] **Step 2: Confirmar que a skill é detectável pelo Antigravity**

```bash
grep -l "canary" "C:/Users/victor.bernardi/.gemini/antigravity/skills/canary-deployment/SKILL.md"
```

Resultado esperado: o arquivo é retornado (confirma que a keyword existe e a skill será carregada pelo agente).

- [x] **Step 3: Teste manual do protocolo**

Simular o cenário mais comum — modificação de uma skill existente:

1. Abrir uma nova sessão no Gemini CLI
2. Pedir ao agente para modificar qualquer linha da skill `task-intelligence`
3. Verificar que o agente:
   - Cria `SKILL.stable.md` antes de salvar
   - Apresenta o diff no formato canary
   - Aguarda S/N antes de promover
   - Registra em `canary-log.md`

Critério de sucesso: o agente não salva a modificação sem passar pelo protocolo.
