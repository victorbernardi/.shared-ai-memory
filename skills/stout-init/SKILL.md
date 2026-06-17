---
# [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace.
name: stout-init
description: "Inicialização modular de projetos Stout com arquitetura de Addons. Triggers: inicializar projeto, novo projeto, scaffold, stout-init, projeto modular."
version: 2.2.0
author: Arquiteto Stout
tier: 3
source: custom
date_added: "2026-05-16"
category: meta-governance
---

# 🚀 SKILL: STOUT-INIT V2.2 — Scaffolding Modular de Alta Fidelidade (Leis Karpathy)

## Propósito

Garantir que todo novo projeto nasça com a base técnica nota 100 da Stout, unindo o scaffolding dinâmico da V2 com a inteligência de templates da V1, de forma auto-contida.

---

## 🛫 Bloco PRÉ-VÔO (Think Before Coding)

**ATENÇÃO AGENTE:** Antes de inicializar as pastas ou escrever os arquivos de configuração, você DEVE fazer as seguintes perguntas ao Victor:
1. Domínio do projeto (Stout ou Inova)?
2. Addons a serem instalados (ex: `cdd` - recomendado)?
3. Stack tecnológica do projeto (ex: Python/uv, Node.js)?

**Regra Absoluta:** NÃO inicie nenhuma execução física (criação de diretórios ou arquivos) antes de ter essas respostas.

---

## 🛠️ Padrão Universal de Encoding

Todo script Python gerado por esta skill ou seus addons DEVE conter o seguinte cabeçalho para garantir compatibilidade de codificação no Windows:

```python
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

---

## 🛠️ Pipeline de Execução (4 Fases)

### Phase 1: Discovery & Configuration
Coleta dos dados pré-vôo acima. Definir a raiz do projeto (ex: `C:\Projetos\Stout\<NomeProjeto>` ou local especificado).

### Phase 2: Core Scaffolding
1. Crie a estrutura base física: `src/`, `data/`, `tests/`, `notes/`.
   * **NÃO crie `docs/` manualmente** (será criada como Junction no passo de infraestrutura).
2. Escrever os arquivos base (`README.md`, `.env.example`, `.gitignore`) com dados básicos.
3. Gerar os arquivos de identidade `GEMINI.md` e `ANTIGRAVITY.md` conforme os templates abaixo.

#### Bootstrap Python/uv (obrigatório se stack for Python)
1. Criar `requirements.txt` na raiz.
2. Inicializar o `.venv` isolado:
   ```powershell
   cd <raiz-do-projeto>
   uv venv --python 3.12
   uv pip install -r requirements.txt
   ```
3. Validar execução:
   ```powershell
   uv run python -c "import sys; print(f'Python {sys.version[:5]} OK')"
   ```

#### Criação de Link Físico (Junction docs/)
Execute no PowerShell para conectar a pasta de documentação local à memória global:
```powershell
$projeto = "<NomeProjetoReal>"
$destino = "$HOME\.shared-ai-memory\docs\active\$projeto"
New-Item -ItemType Directory -Force -Path $destino | Out-Null
mklink /J "docs" $destino
```
*Após a criação, verifique:*
```powershell
(Get-Item "docs").LinkType  # deve retornar "Junction"
```
Crie dentro de `docs/governance/` (após criar a junction): `known_issues.md` e `evolution_backlog.md` usando os templates abaixo.

### Phase 3: Addon Injection
Para cada addon selecionado no pré-vôo:
1. Localize a pasta `C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-init\addons\<addon>\`.
2. Leia o `ADDON.md` correspondente e execute os passos de instalação e stitching.

### Phase 4: Finalization & Quality
1. **Sanitização:** Execute obrigatoriamente o script de auto-fix sobre todos os Markdowns gerados:
   ```powershell
   python $HOME\.shared-ai-memory\scripts\markdown_auto_fixer_v1.py <raiz-do-projeto>
   ```
2. **Manifesto:** Salve um arquivo `stout-manifest.json` na raiz contendo os metadados do projeto.

---

## 📄 Templates de Arquivos Core

### 1. Modelo GEMINI.md
```markdown
# 📂 GEMINI.md — PROJETO: [Nome do Projeto]

> [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace.

> **Herança:** Plano Executivo Global
> **Ambiente:** [Gemini CLI / Antigravity]
> **Inicializado em:** [DATA]

---

## 1. CONTEXTO DE NEGÓCIO
**Objetivo:** [Descreva aqui]
**KPI Principal:** [Como medir sucesso]

## 2. CONTEXTO TÉCNICO
### Stack
- Linguagem: [Preencher]
- MCPs: context7, google-drive, notebooklm

## 3. REGRAS LOCAIS
- Seguir padrão CDD.
- Rastreabilidade em .GCC/.

## 4. ESTADO ATUAL
- Phase: Research ⏳
```

### 2. Modelo ANTIGRAVITY.md
```markdown
# 🧠 ANTIGRAVITY.md — Kernel Agêntico

> [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace.

---
## 1. ARQUITETURA DE MEMÓRIA
- Junction: docs/ -> .shared-ai-memory/docs/[Projeto]

## 2. FRAMEWORK STOUT
1. Research -> 2. Strategy -> 3. Execution -> 4. Validation
```

### 3. Modelo docs/governance/known_issues.md
```markdown
# 🐛 Lista de Bugs Conhecidos & Workarounds

Este documento registra de forma viva, imutável e estruturada todos os bugs de ambiente, bibliotecas ou travas físicas reincidentes descobertos nas sessões do ecossistema Stout, juntamente com suas soluções temporárias (workarounds) e status de correção definitiva.

---

| Bug ID | Categoria | Descrição | Ocorrências | Workaround Conhecido | Correção Definitiva | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |

---

> [!NOTE]
> Este arquivo é atualizado de forma dinâmica e programática pela skill `stout-session-learning` ao final de cada sessão.
```

### 4. Modelo docs/governance/evolution_backlog.md
```markdown
# 🚀 Backlog de Evolução Técnica & Estética

Este documento centraliza e prioriza todas as sugestões de otimização agêntica, melhorias estéticas de interface, refatorações de código e avanços na infraestrutura do ecossistema Stout sugeridos pelas habilidades a partir do aprendizado consolidado de sessões passadas.

---

## 📅 Sugestões de Melhoria e Propostas

| ID | Data | Origem (Sessão) | Proposta / Oportunidade de Melhoria | Impacto Esperado | Prioridade | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |

---

> [!NOTE]
> Novas propostas identificadas são compiladas e integradas aqui pela skill `stout-session-learning` de forma autônoma.
```

---

## 🏁 Verificação Final (DoD)

O processo de inicialização só é considerado concluído quando todos os itens abaixo forem validados (marcar com `[x]`):
- [ ] Estrutura base física criada (`src/`, `data/`, `tests/`, `notes/`).
- [ ] Junction de `docs/` criada apontando com sucesso para `.shared-ai-memory\docs\active\<NomeProjeto>`.
- [ ] Arquivos `GEMINI.md`, `ANTIGRAVITY.md` e arquivos de governança criados com base nos templates corretos.
- [ ] Ambiente virtual Python `.venv` inicializado e validado via `uv run` (se stack Python).
- [ ] Script de auto-fix `markdown_auto_fixer_v1.py` executado sobre todos os markdowns gerados sem reportar falhas.
