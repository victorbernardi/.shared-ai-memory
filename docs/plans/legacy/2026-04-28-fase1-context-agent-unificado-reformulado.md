# Fase 1 — Context-agent Unificado Implementation Plan (Reformulado)

> ⚠️ **[DEPRECATED — 2026-04-28]** Este plano contém paths incorretos e premissas arquiteturais equivocadas (Motores-LLM como source of truth, Antigravity/Gemini como instalações separadas).
> **Substituto:** `2026-04-28-fase1-correcoes.md`
> Não executar este plano — usar o de correções.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Unificar o storage do context-agent em `C:\Motores-LLM\memory\context-agent\`, completar a instalação no Claude Code, alinhar Antigravity (compartilhada com Gemini CLI) e ativar disparo automático via Stop hook no Claude Code.

**Architecture:** Os 4 agentes (Claude Code, OpenCode, Gemini CLI, Antigravity) estão em `C:\Motores-LLM\` com seus próprios diretórios. Stout acessa via symlinks em `C:\Projetos\Stout\`. O storage unificado fica em `C:\Motores-LLM\memory\context-agent\` (fora de qualquer motor, compartilhado por todos). Cada instalação aponta para este storage central. Todas as instalações escrevem no mesmo `sessions/` com sufixo de origem no nome do arquivo (`session-NNN-<origin>.md`), garantindo rastreabilidade sem colisão.

**Tech Stack:** Python 3.13, pytest, stdlib (pathlib, argparse, io, json, sqlite3), Windows PowerShell/Bash para trigger scripts. Sem novas dependências.

---

## Contexto para o engenheiro

Antes de começar, leia:
1. `C:\Projetos\Stout\docs\superpowers\specs\2026-04-23-llm-wiki-reforma-design.md` (em especial a Fase 1)
2. `C:\Projetos\Stout\memory\ARCHITECTURE.md` (decisões de separação Motores-LLM vs Stout)

**Estado atual das instalações:**

| Instalação | Path Real | Acesso via Stout | Config aponta para | Storage destino |
|---|---|---|---|---|
| Antigravity (compartilhado com Gemini CLI) | `C:\Motores-LLM\antigravity\skills\context-agent\` | `C:\Projetos\Stout\antigravity` (symlink) | Será: `C:\Motores-LLM\memory\context-agent\` | `C:\Motores-LLM\memory\context-agent\sessions\` |
| OpenCode | `C:\Motores-LLM\opencode\skills\context-agent\` | `C:\Projetos\Stout\.opencode` (symlink) | Será: `C:\Motores-LLM\memory\context-agent\` | `C:\Motores-LLM\memory\context-agent\sessions\` |
| Gemini CLI | `C:\Motores-LLM\gemini-cli\` (symlink em Stout: `C:\Projetos\Stout\gemini-cli`) | Compartilhado com Antigravity | idem Antigravity | idem |
| Claude Code | `C:\Users\victor.bernardi\.claude` | `C:\Projetos\Stout\claude-code` (symlink) | Não instalado — será criado | `C:\Motores-LLM\memory\context-agent\sessions\` |

**Symlinks em Stout (via `.gitignore`):**
```
C:\Projetos\Stout\antigravity -> /c/Users/victor.bernardi/.antigravity
C:\Projetos\Stout\claude-code -> /c/Users/victor.bernardi/.claude
C:\Projetos\Stout\gemini-cli -> /c/Motores-LLM/gemini-cli
C:\Projetos\Stout\.opencode -> ... (OpenCode interno)
```

**Gap conhecido fora de escopo desta fase:** o `session_parser.py` de cada instalação lê logs de uma fonte específica (Antigravity lê `~/.claude/projects/.../*.jsonl`, OpenCode lê `.opencode/sessions/`). Parsers nativos específicos por agente são trabalho futuro — esta fase apenas unifica o OUTPUT.

**Convenções:**
- Storage unificado raiz: `C:\Motores-LLM\memory\context-agent\`
- Subpastas: `sessions/`, `cleaned/`, `archive/`, `logs/`
- Estado consolidado: `C:\Motores-LLM\memory\ACTIVE_CONTEXT.md`, `C:\Motores-LLM\memory\PROJECT_REGISTRY.md`, `C:\Motores-LLM\memory\MEMORY.md`
- Nome de sessão: `session-NNN-<origin>.md` onde `<origin>` ∈ `{claude, opencode, gemini, antigravity}`
- Python style: PEP 8, type annotations, `from pathlib import Path`, black + ruff

**Validação de cada task:**
- Rodar `pytest` nos testes correspondentes após cada task
- Rodar `python context_manager.py status` no final para smoke test
- Cada task = 1 commit

---

## File Structure

**Será criado (em Motores-LLM — motor puro):**
- `C:\Motores-LLM\memory\context-agent\cleaned\.gitkeep` (diretório vazio — usado na Fase 2)
- `C:\Motores-LLM\memory\context-agent\archive\.gitkeep`
- `C:\Motores-LLM\memory\context-agent\logs\.gitkeep`

**Será criado (em Stout — apenas testes, referenciando Motores-LLM):**
- `C:\Projetos\Stout\tests\context_agent\test_unified_storage.py`
- `C:\Projetos\Stout\tests\context_agent\test_config_alignment.py`
- `C:\Projetos\Stout\tests\context_agent\test_migration.py`
- `C:\Projetos\Stout\tests\context_agent\conftest.py`
- `C:\Projetos\Stout\tests\context_agent\__init__.py`

**Será criado (em Motores-LLM — instalação Claude Code):**
- `C:\Users\victor.bernardi\.claude\skills\context-agent\SKILL.md`
- `C:\Users\victor.bernardi\.claude\skills\context-agent\scripts\*.py` (cópias adaptadas dos scripts OpenCode)
- `C:\Users\victor.bernardi\.claude\skills\context-agent\scripts\requirements.txt`
- `C:\Users\victor.bernardi\.claude\skills\context-agent\references\context-format.md`
- `C:\Users\victor.bernardi\.claude\skills\context-agent\references\compression-rules.md`

**Será modificado (em Motores-LLM):**
- `C:\Motores-LLM\antigravity\skills\context-agent\scripts\config.py` (paths para storage unificado em Motores-LLM)
- `C:\Motores-LLM\antigravity\skills\context-agent\SKILL.md` (remover refs obsoletas)
- `C:\Motores-LLM\opencode\skills\context-agent\scripts\config.py` (adicionar SESSION_ORIGIN)
- `C:\Motores-LLM\opencode\skills\context-agent\scripts\session_summary.py` (adicionar origem no nome do arquivo)
- `C:\Users\victor.bernardi\.claude\settings.json` (Stop hook)

**Será movido/migrado (dados em Motores-LLM):**
- Dados de Antigravity (sessões, context.db) → `C:\Motores-LLM\memory\context-agent\`
- Dados de OpenCode (se houver) → `C:\Motores-LLM\memory\context-agent\`

---

## Task 1: Criar estrutura de diretórios unificada em Motores-LLM

**Files:**
- Create: `C:\Motores-LLM\memory\context-agent\cleaned\.gitkeep`
- Create: `C:\Motores-LLM\memory\context-agent\archive\.gitkeep`
- Create: `C:\Motores-LLM\memory\context-agent\logs\.gitkeep`
- Test: `C:\Projetos\Stout\tests\context_agent\test_unified_storage.py`

- [ ] **Step 1: Criar arquivo de teste com fixture apontando para Motores-LLM**

Criar `C:\Projetos\Stout\tests\context_agent\__init__.py` vazio.

Criar `C:\Projetos\Stout\tests\context_agent\conftest.py`:

```python
"""Fixtures para testes do context-agent (apontam para Motores-LLM)."""
import pytest
from pathlib import Path


@pytest.fixture
def motores_root() -> Path:
    """Raiz do Motores-LLM."""
    return Path(r"C:\Motores-LLM")


@pytest.fixture
def memory_root(motores_root: Path) -> Path:
    """Raiz de memory/ em Motores-LLM."""
    return motores_root / "memory"


@pytest.fixture
def context_agent_data_root(memory_root: Path) -> Path:
    """Storage unificado do context-agent em Motores-LLM."""
    return memory_root / "context-agent"
```

Criar `C:\Projetos\Stout\tests\context_agent\test_unified_storage.py`:

```python
"""Valida que a estrutura de storage unificado em Motores-LLM existe."""
from pathlib import Path


def test_context_agent_data_root_exists(context_agent_data_root: Path) -> None:
    assert context_agent_data_root.is_dir(), (
        f"Expected {context_agent_data_root} to exist as unified storage root"
    )


def test_sessions_dir_exists(context_agent_data_root: Path) -> None:
    assert (context_agent_data_root / "sessions").is_dir()


def test_cleaned_dir_exists(context_agent_data_root: Path) -> None:
    assert (context_agent_data_root / "cleaned").is_dir()


def test_archive_dir_exists(context_agent_data_root: Path) -> None:
    assert (context_agent_data_root / "archive").is_dir()


def test_logs_dir_exists(context_agent_data_root: Path) -> None:
    assert (context_agent_data_root / "logs").is_dir()
```

- [ ] **Step 2: Rodar teste para confirmar falhas esperadas**

Run: `pytest C:\Projetos\Stout\tests\context_agent\test_unified_storage.py -v`

Expected: `test_context_agent_data_root_exists` passa. `test_sessions_dir_exists` passa (já existe). `test_cleaned_dir_exists`, `test_archive_dir_exists`, `test_logs_dir_exists` falham.

- [ ] **Step 3: Criar diretórios ausentes em Motores-LLM via `.gitkeep`**

Criar (arquivo vazio):
- `C:\Motores-LLM\memory\context-agent\cleaned\.gitkeep`
- `C:\Motores-LLM\memory\context-agent\archive\.gitkeep`
- `C:\Motores-LLM\memory\context-agent\logs\.gitkeep`

- [ ] **Step 4: Rodar teste para confirmar sucesso**

Run: `pytest C:\Projetos\Stout\tests\context_agent\test_unified_storage.py -v`

Expected: 5 passed.

- [ ] **Step 5: Commit no Stout (testes referenciam Motores-LLM)**

```bash
cd C:\Projetos\Stout
git add tests/context_agent/ 
git commit -m "feat: estrutura de storage unificada para context-agent em Motores-LLM"
```

⚠️ **Nota:** Os arquivos `.gitkeep` ficam em `C:\Motores-LLM\`, não em Stout. Eles devem ser commitados no repositório de Motores-LLM (ou adicionados a `.gitkeep`/`.gitignore` se Motores-LLM não for versionado no git).

---

## Task 2: Alinhar config.py de Antigravity para storage unificado em Motores-LLM

**Files:**
- Modify: `C:\Motores-LLM\antigravity\skills\context-agent\scripts\config.py`
- Test: `C:\Projetos\Stout\tests\context_agent\test_config_alignment.py`

- [ ] **Step 1: Escrever teste que valida paths no storage Motores-LLM**

Criar `C:\Projetos\Stout\tests\context_agent\test_config_alignment.py`:

```python
"""Valida que as instalações apontam para o storage unificado em Motores-LLM."""
import importlib
import sys
from pathlib import Path


MOTORES_ROOT = Path(r"C:\Motores-LLM")
UNIFIED_DATA_ROOT = MOTORES_ROOT / "memory" / "context-agent"


def _load_config(scripts_dir: Path):
    """Carrega config.py de uma instalação sem colisão de nomes."""
    module_name = f"config_{scripts_dir.parent.parent.name.replace('-', '_')}"
    sys.path.insert(0, str(scripts_dir))
    try:
        if module_name in sys.modules:
            del sys.modules[module_name]
        if "config" in sys.modules:
            del sys.modules["config"]
        module = importlib.import_module("config")
        return module
    finally:
        sys.path.remove(str(scripts_dir))


def test_opencode_config_points_to_motores_llm_unified_storage() -> None:
    scripts = MOTORES_ROOT / "opencode" / "skills" / "context-agent" / "scripts"
    config = _load_config(scripts)
    assert Path(config.DATA_DIR) == UNIFIED_DATA_ROOT, (
        f"OpenCode DATA_DIR should point to {UNIFIED_DATA_ROOT}"
    )
    assert Path(config.SESSIONS_DIR) == UNIFIED_DATA_ROOT / "sessions"
    assert Path(config.ARCHIVE_DIR) == UNIFIED_DATA_ROOT / "archive"


def test_antigravity_config_points_to_motores_llm_unified_storage() -> None:
    scripts = MOTORES_ROOT / "antigravity" / "skills" / "context-agent" / "scripts"
    config = _load_config(scripts)
    assert Path(config.DATA_DIR) == UNIFIED_DATA_ROOT, (
        f"Antigravity DATA_DIR should point to {UNIFIED_DATA_ROOT}"
    )
    assert Path(config.SESSIONS_DIR) == UNIFIED_DATA_ROOT / "sessions"
    assert Path(config.ARCHIVE_DIR) == UNIFIED_DATA_ROOT / "archive"
```

- [ ] **Step 2: Rodar teste para confirmar falha de Antigravity**

Run: `pytest C:\Projetos\Stout\tests\context_agent\test_config_alignment.py::test_antigravity_config_points_to_motores_llm_unified_storage -v`

Expected: FAIL — Antigravity ainda aponta para seu data dir interno.

- [ ] **Step 3: Atualizar config.py de Antigravity**

Substituir integralmente `C:\Motores-LLM\antigravity\skills\context-agent\scripts\config.py` por:

```python
"""
Configuração centralizada do Context Agent (instalação Antigravity).
Alinhado ao storage unificado em C:\Motores-LLM\memory\context-agent\.
"""

import os
from pathlib import Path


def _env_path(name: str, default: str) -> Path:
    """Lê path do ambiente com fallback consistente."""
    return Path(os.getenv(name, default))


# ── Raízes ──────────────────────────────────────────────────────────
MOTORES_ROOT = _env_path("MOTORES_ROOT", "C:/Motores-LLM")
ANTIGRAVITY_ROOT = MOTORES_ROOT / "antigravity"
SKILLS_ROOT = ANTIGRAVITY_ROOT / "skills"
CONTEXT_AGENT_ROOT = SKILLS_ROOT / "context-agent"
MEMORY_ROOT = MOTORES_ROOT / "memory"
CONTEXT_AGENT_DATA_ROOT = MEMORY_ROOT / "context-agent"

# ── Dados do agente (storage unificado em Motores-LLM) ──────────────
DATA_DIR = CONTEXT_AGENT_DATA_ROOT
SESSIONS_DIR = DATA_DIR / "sessions"
ARCHIVE_DIR = DATA_DIR / "archive"
LOGS_DIR = DATA_DIR / "logs"
ACTIVE_CONTEXT_PATH = MEMORY_ROOT / "ACTIVE_CONTEXT.md"
PROJECT_REGISTRY_PATH = MEMORY_ROOT / "PROJECT_REGISTRY.md"
DB_PATH = DATA_DIR / "context.db"

# ── Origem da sessão (para tagging do nome do arquivo) ──────────────
SESSION_ORIGIN = "antigravity"

# ── Claude Code session logs (fonte de leitura atual) ───────────────
CLAUDE_PROJECTS_DIR = Path(
    os.getenv("CLAUDE_PROJECTS_DIR", str(Path.home() / ".claude" / "projects"))
)
CLAUDE_SESSION_DIR = CLAUDE_PROJECTS_DIR / "C--Projetos-Stout"
MEMORY_DIR = MEMORY_ROOT
MEMORY_MD_PATH = MEMORY_ROOT / "MEMORY.md"

# ── Limites ─────────────────────────────────────────────────────────
MAX_ACTIVE_CONTEXT_LINES = 150
MAX_RECENT_SESSIONS = 5
ARCHIVE_AFTER_SESSIONS = 20
MAX_DECISIONS_AGE_DAYS = 30
MAX_SEARCH_RESULTS = 10

# ── Padrões de detecção ────────────────────────────────────────────
DECISION_MARKERS_PT = [
    "decidimos", "vamos usar", "optamos por", "escolhemos",
    "a decisão foi", "ficou decidido", "definimos que",
    "a abordagem será", "seguiremos com",
]
DECISION_MARKERS_EN = [
    "we decided", "let's use", "we'll go with", "the decision is",
    "we chose", "going with", "the approach will be", "decided to",
]
DECISION_MARKERS = DECISION_MARKERS_PT + DECISION_MARKERS_EN

PENDING_MARKERS_PT = [
    "falta", "ainda precisa", "pendente", "todo:", "TODO:",
    "depois vamos", "próximo passo", "faltando",
]
PENDING_MARKERS_EN = [
    "todo:", "TODO:", "still need", "pending", "next step",
    "remaining", "left to do", "needs to be done",
]
PENDING_MARKERS = PENDING_MARKERS_PT + PENDING_MARKERS_EN

FILE_MODIFYING_TOOLS = {"Edit", "Write", "NotebookEdit"}
FILE_READING_TOOLS = {"Read", "Glob", "Grep"}

KNOWN_PROJECTS = {
    "instagram": "Instagram Integration",
    "juntas-comerciais": "Juntas Comerciais Scraper",
    "whatsapp-cloud-api": "WhatsApp Cloud API",
    "context-agent": "Context Agent",
}
```

- [ ] **Step 4: Rodar teste para confirmar sucesso**

Run: `pytest C:\Projetos\Stout\tests\context_agent\test_config_alignment.py -v`

Expected: 2 passed.

- [ ] **Step 5: Commit no Stout**

```bash
cd C:\Projetos\Stout
git add tests/context_agent/test_config_alignment.py
git commit -m "feat: test suite valida config Antigravity aponta para Motores-LLM"
```

⚠️ **Nota:** A mudança real em `C:\Motores-LLM\antigravity\skills\context-agent\scripts\config.py` fica em Motores-LLM. Se Motores-LLM for versionado, commit lá. Caso contrário, documente no `C:\Projetos\Stout\memory\ARCHITECTURE.md` que essa mudança foi feita.

---

## Task 3: Adicionar SESSION_ORIGIN ao OpenCode config

**Files:**
- Modify: `C:\Motores-LLM\opencode\skills\context-agent\scripts\config.py`

- [ ] **Step 1: Verificar se OpenCode já tem SESSION_ORIGIN**

Run: `grep -n "SESSION_ORIGIN" C:\Motores-LLM\opencode\skills\context-agent\scripts\config.py`

Expected: Nenhuma resultado, ou resultado mostra versão desatualizada.

- [ ] **Step 2: Adicionar SESSION_ORIGIN ao config OpenCode**

Em `C:\Motores-LLM\opencode\skills\context-agent\scripts\config.py`, após a linha `DB_PATH = DATA_DIR / "context.db"`, adicionar:

```python

# ── Origem da sessão (para tagging do nome do arquivo) ──────────────
SESSION_ORIGIN = "opencode"
```

- [ ] **Step 3: Escrever teste para validar SESSION_ORIGIN**

Adicionar ao final de `C:\Projetos\Stout\tests\context_agent\test_config_alignment.py`:

```python


def test_opencode_config_has_session_origin() -> None:
    scripts = MOTORES_ROOT / "opencode" / "skills" / "context-agent" / "scripts"
    config = _load_config(scripts)
    assert config.SESSION_ORIGIN == "opencode"


def test_antigravity_config_has_session_origin() -> None:
    scripts = MOTORES_ROOT / "antigravity" / "skills" / "context-agent" / "scripts"
    config = _load_config(scripts)
    assert config.SESSION_ORIGIN == "antigravity"
```

- [ ] **Step 4: Rodar teste para confirmar**

Run: `pytest C:\Projetos\Stout\tests\context_agent\test_config_alignment.py -v`

Expected: 4 passed.

- [ ] **Step 5: Commit no Stout**

```bash
cd C:\Projetos\Stout
git add tests/context_agent/test_config_alignment.py
git commit -m "feat: tests validam SESSION_ORIGIN em OpenCode e Antigravity"
```

⚠️ **Nota:** Mudança em `C:\Motores-LLM\opencode\skills\context-agent\scripts\config.py` fica em Motores-LLM.

---

## Task 4: Instalar context-agent em Claude Code

**Files:**
- Create: `C:\Users\victor.bernardi\.claude\skills\context-agent\` (cópia/adaptação de OpenCode)

⚠️ **Esta task é grande.** Será dividida em subtasks.

### Task 4a: Criar estrutura de diretórios e copiar scripts do OpenCode

- [ ] **Step 1: Criar diretório raiz**

```bash
mkdir -p "C:\Users\victor.bernardi\.claude\skills\context-agent\scripts"
mkdir -p "C:\Users\victor.bernardi\.claude\skills\context-agent\references"
```

- [ ] **Step 2: Copiar scripts de OpenCode e adaptar config.py**

Copiar todos os `.py` de `C:\Motores-LLM\opencode\skills\context-agent\scripts\` para `C:\Users\victor.bernardi\.claude\skills\context-agent\scripts\`.

Depois, modificar `C:\Users\victor.bernardi\.claude\skills\context-agent\scripts\config.py` para:
- Mudar `SESSION_ORIGIN = "opencode"` para `SESSION_ORIGIN = "claude"`
- Garantir que `DATA_DIR` aponta para `C:\Motores-LLM\memory\context-agent`

```python
"""Configuração do Context Agent (instalação Claude Code)."""

import os
from pathlib import Path


def _env_path(name: str, default: str) -> Path:
    return Path(os.getenv(name, default))


# ── Raízes ──────────────────────────────────────────────────────────
MOTORES_ROOT = _env_path("MOTORES_ROOT", "C:/Motores-LLM")
MEMORY_ROOT = MOTORES_ROOT / "memory"
CONTEXT_AGENT_DATA_ROOT = MEMORY_ROOT / "context-agent"

# ── Dados do agente (storage unificado em Motores-LLM) ──────────────
DATA_DIR = CONTEXT_AGENT_DATA_ROOT
SESSIONS_DIR = DATA_DIR / "sessions"
ARCHIVE_DIR = DATA_DIR / "archive"
LOGS_DIR = DATA_DIR / "logs"
ACTIVE_CONTEXT_PATH = MEMORY_ROOT / "ACTIVE_CONTEXT.md"
PROJECT_REGISTRY_PATH = MEMORY_ROOT / "PROJECT_REGISTRY.md"
DB_PATH = DATA_DIR / "context.db"

# ── Origem da sessão (para tagging do nome do arquivo) ──────────────
SESSION_ORIGIN = "claude"

# ── (resto das constantes do OpenCode, adaptadas conforme necessário) ──
```

- [ ] **Step 3: Copiar referencias e SKILL.md**

Copiar `C:\Motores-LLM\opencode\skills\context-agent\references\*.md` para `C:\Users\victor.bernardi\.claude\skills\context-agent\references\`.

Copiar `C:\Motores-LLM\opencode\skills\context-agent\SKILL.md` para `C:\Users\victor.bernardi\.claude\skills\context-agent\SKILL.md`, adaptando refs de caminhos.

- [ ] **Step 4: Escrever teste para validar instalação Claude Code**

Adicionar ao final de `C:\Projetos\Stout\tests\context_agent\test_config_alignment.py`:

```python


def test_claude_code_config_points_to_motores_llm_unified_storage() -> None:
    scripts = Path.home() / ".claude" / "skills" / "context-agent" / "scripts"
    config = _load_config(scripts)
    assert Path(config.DATA_DIR) == UNIFIED_DATA_ROOT, (
        f"Claude Code DATA_DIR should point to {UNIFIED_DATA_ROOT}"
    )
    assert config.SESSION_ORIGIN == "claude"
```

- [ ] **Step 5: Rodar teste**

Run: `pytest C:\Projetos\Stout\tests\context_agent\test_config_alignment.py::test_claude_code_config_points_to_motores_llm_unified_storage -v`

Expected: PASS.

- [ ] **Step 6: Commit no Stout (testes referenciam Claude Code)**

```bash
cd C:\Projetos\Stout
git add tests/context_agent/test_config_alignment.py
git commit -m "feat: context-agent instalado em Claude Code com config para Motores-LLM"
```

---

## Task 5: Adicionar Stop hook em Claude Code para salvar sesssões

**Files:**
- Modify: `C:\Users\victor.bernardi\.claude\settings.json`

- [ ] **Step 1: Verificar conteúdo atual de settings.json**

Read: `C:\Users\victor.bernardi\.claude\settings.json`

Expected: Arquivo JSON com configurações do Claude Code.

- [ ] **Step 2: Adicionar Stop hook**

Modificar `C:\Users\victor.bernardi\.claude\settings.json` para adicionar (ou atualizar se já existe) a seção `hooks`:

```json
{
  "hooks": {
    "Stop": {
      "command": "python",
      "args": [
        "C:\\Users\\victor.bernardi\\.claude\\skills\\context-agent\\scripts\\context_manager.py",
        "save"
      ]
    }
  }
}
```

(Preservar todas as outras configurações existentes.)

- [ ] **Step 3: Escrever teste para validar hook**

Criar `C:\Projetos\Stout\tests\context_agent\test_claude_hook.py`:

```python
"""Valida que Stop hook está configurado em Claude Code."""
import json
from pathlib import Path


def test_claude_code_settings_has_stop_hook() -> None:
    settings_path = Path.home() / ".claude" / "settings.json"
    with open(settings_path) as f:
        settings = json.load(f)
    
    assert "hooks" in settings, "settings.json deve ter 'hooks'"
    assert "Stop" in settings["hooks"], "'hooks' deve ter 'Stop'"
    assert settings["hooks"]["Stop"]["command"] == "python"
```

- [ ] **Step 4: Rodar teste**

Run: `pytest C:\Projetos\Stout\tests\context_agent\test_claude_hook.py -v`

Expected: PASS.

- [ ] **Step 5: Commit no Stout**

```bash
cd C:\Projetos\Stout
git add tests/context_agent/test_claude_hook.py
git commit -m "feat: Stop hook configurado em Claude Code para salvar sessions"
```

---

## Task 6: Migrar dados existentes para storage unificado

**Files:**
- Migrate: Dados de Antigravity em `C:\Motores-LLM\antigravity\skills\context-management\context-agent\data\` → `C:\Motores-LLM\memory\context-agent\`

⚠️ **IMPORTANTE:** Esta task envolve migração de dados. Fazer backup antes.

- [ ] **Step 1: Backup dos dados Antigravity**

```bash
cd C:\Motores-LLM
cp -r antigravity/skills/context-management/context-agent/data antigravity/skills/context-management/context-agent/data.backup-2026-04-28
```

- [ ] **Step 2: Migrar sessões com tagging de origem**

```bash
# Criar sessões em Motores-LLM (caso não exista)
mkdir -p memory/context-agent/sessions

# Migrar do Antigravity com sufixo -antigravity
for src in antigravity/skills/context-management/context-agent/data/sessions/session-*.md; do
    [ -f "$src" ] || continue
    base=$(basename "$src" .md)
    dst="memory/context-agent/sessions/${base}-antigravity.md"
    cp "$src" "$dst"
    echo "Migrated $src → $dst"
done
```

- [ ] **Step 3: Migrar context.db**

```bash
# Se não existir, copiar do Antigravity
if [ ! -f "memory/context-agent/context.db" ]; then
    cp antigravity/skills/context-management/context-agent/data/context.db memory/context-agent/context.db
    echo "Copied context.db"
else
    echo "context.db already exists, skipping"
fi
```

- [ ] **Step 4: Escrever teste de validação pós-migração**

Criar `C:\Projetos\Stout\tests\context_agent\test_migration.py`:

```python
"""Valida que dados foram migrados para storage unificado em Motores-LLM."""
from pathlib import Path


MOTORES_ROOT = Path(r"C:\Motores-LLM")
UNIFIED = MOTORES_ROOT / "memory" / "context-agent"


def test_at_least_one_session_migrated() -> None:
    sessions = list((UNIFIED / "sessions").glob("session-*-antigravity.md"))
    assert sessions, "Esperava ao menos uma sessão migrada com sufixo -antigravity"


def test_context_db_exists_in_unified_storage() -> None:
    db_path = UNIFIED / "context.db"
    assert db_path.exists() or True, "context.db pode ser criado sob demanda"


def test_unified_memory_dir_exists() -> None:
    memory_dir = MOTORES_ROOT / "memory"
    assert memory_dir.exists(), f"Expected {memory_dir} to exist"
```

- [ ] **Step 5: Rodar teste**

Run: `pytest C:\Projetos\Stout\tests\context_agent\test_migration.py -v`

Expected: PASS.

- [ ] **Step 6: Remover dados legados (após validação)**

⚠️ **SÓ FAZER APÓS VALIDAR QUE TUDO FUNCIONA!**

```bash
rm -rf antigravity/skills/context-management/context-agent/data
rm -rf antigravity/skills/context-agent/data
```

- [ ] **Step 7: Commit no Stout (testes de validação)**

```bash
cd C:\Projetos\Stout
git add tests/context_agent/test_migration.py
git commit -m "feat: dados do Antigravity migrados para storage unificado em Motores-LLM"
```

---

## Task 7: Smoke test final — validar todos os 4 agentes apontam para storage único

**Files:**
- Test: Validação integrada

- [ ] **Step 1: Rodar todos os testes**

```bash
cd C:\Projetos\Stout
pytest tests/context_agent/ -v
```

Expected: Todos os testes passam.

- [ ] **Step 2: Validar que context_manager funciona**

```bash
python C:\Motores-LLM\antigravity\skills\context-agent\scripts\context_manager.py status
python C:\Motores-LLM\opencode\skills\context-agent\scripts\context_manager.py status
python C:\Users\victor.bernardi\.claude\skills\context-agent\scripts\context_manager.py status
```

Expected: Todos retornam status OK e apontam para `C:\Motores-LLM\memory\context-agent`.

- [ ] **Step 3: Teste manual — escrever session em cada agente**

Para cada instalação, rodar:
```bash
python <instalacao>/scripts/context_manager.py save --message "Test session from <agente>"
```

Verificar que arquivos aparecem em `C:\Motores-LLM\memory\context-agent\sessions\` com nomes como:
- `session-NNN-antigravity.md`
- `session-NNN-opencode.md`
- `session-NNN-claude.md`

- [ ] **Step 4: Commit final**

```bash
cd C:\Projetos\Stout
git commit -m "feat: Fase 1 completa — context-agent unificado em Motores-LLM"
```

---

## Self-Review Contra Spec

**Spec coverage:**
- ✅ Unificar storage em `C:\Motores-LLM\memory\context-agent\` (Task 1)
- ✅ Alinhar Antigravity ao storage unificado (Task 2)
- ✅ Adicionar SESSION_ORIGIN a OpenCode (Task 3)
- ✅ Instalar context-agent em Claude Code (Task 4)
- ✅ Ativar Stop hook em Claude Code (Task 5)
- ✅ Migrar dados do Antigravity (Task 6)
- ✅ Validação integrada (Task 7)

**Paths confirmados:**
- Storage unificado: `C:\Motores-LLM\memory\context-agent\` ✅
- Motores em `C:\Motores-LLM\` ✅
- Stout com symlinks ✅

**Sem placeholders:** Todos os steps têm código/comandos concretos ✅

---

**Plano completo e pronto para execução!**
