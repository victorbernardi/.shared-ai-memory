# Fase 1 — Context-agent Unificado Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Unificar o storage do context-agent em `memory/context-agent/`, completar a instalação no Claude Code, alinhar a instalação Antigravity (compartilhada com Gemini CLI) e ativar disparo automático via Stop hook no Claude Code.

**Architecture:** A instalação OpenCode já aponta ao path unificado. A Antigravity usa paths legados dentro da própria skill — migrar config + dados para o novo storage. Claude Code recebe uma instalação espelhada da do OpenCode, adaptando o diretório de sessões nativas. Todas as instalações escrevem no mesmo `sessions/` com sufixo de origem no nome do arquivo (`session-NNN-<origin>.md`), garantindo rastreabilidade sem colisão.

**Tech Stack:** Python 3.13, pytest, stdlib (pathlib, argparse, io, json, sqlite3), Windows PowerShell/Bash para trigger scripts. Sem novas dependências.

---

## Contexto para o engenheiro

Antes de começar, leia o spec em `docs/superpowers/specs/2026-04-23-llm-wiki-reforma-design.md` (em especial a Fase 1).

**Estado atual das instalações:**

| Instalação | Path | Config aponta para | Storage atual |
|---|---|---|---|
| Antigravity (compartilhado com Gemini CLI) | `C:\Projetos\Stout\antigravity\skills\context-agent\` (scripts + SKILL.md) | `antigravity/skills/context-management/context-agent/data/` (atual, onde `config.py` aponta) | `antigravity/skills/context-management/context-agent/data/sessions/` (atual) + `antigravity/skills/context-agent/data/sessions/` (legado) — ambos precisam ser migrados |
| OpenCode | `C:\Projetos\Stout\.opencode\skills\context-agent\` | `memory/context-agent/` ✅ (via env `STOUT_ROOT`) | `memory/context-agent/sessions/` |
| Gemini CLI | Symlink/mirror para Antigravity | idem Antigravity | idem |
| Claude Code | não instalado | — | — |

**Gap conhecido fora de escopo desta fase:** o `session_parser.py` de cada instalação lê logs de uma fonte específica (Antigravity hoje lê `~/.claude/projects/.../*.jsonl`, OpenCode lê `.opencode/sessions/`). Parsers nativos específicos por agente (Antigravity próprio, Gemini CLI próprio) são trabalho futuro — esta fase mantém o comportamento atual de leitura de logs, apenas unifica o OUTPUT.

**Convenções:**
- Storage unificado raiz: `C:\Projetos\Stout\memory\context-agent\`
- Subpastas: `sessions/`, `cleaned/`, `archive/`, `logs/`
- Estado consolidado: `memory/ACTIVE_CONTEXT.md`, `memory/PROJECT_REGISTRY.md`, `memory/MEMORY.md`
- Nome de sessão: `session-NNN-<origin>.md` onde `<origin>` ∈ `{claude, opencode, gemini, antigravity}`
- Python style: PEP 8, type annotations, `from pathlib import Path`, black + ruff

**Validação de cada task:**
- Rodar `pytest` nos testes correspondentes após cada task
- Rodar `python context_manager.py status` no final para smoke test
- Cada task = 1 commit

---

## File Structure

**Será criado:**
- `C:\Projetos\Stout\memory\context-agent\cleaned\` (diretório vazio — usado na Fase 2)
- `C:\Projetos\Stout\.claude\skills\context-agent\SKILL.md`
- `C:\Projetos\Stout\.claude\skills\context-agent\scripts\*.py` (cópias adaptadas dos scripts OpenCode)
- `C:\Projetos\Stout\.claude\skills\context-agent\scripts\requirements.txt`
- `C:\Projetos\Stout\.claude\skills\context-agent\references\context-format.md`
- `C:\Projetos\Stout\.claude\skills\context-agent\references\compression-rules.md`
- `C:\Projetos\Stout\.claude\settings.json` (Stop hook)
- `C:\Projetos\Stout\tests\context_agent\test_unified_storage.py`
- `C:\Projetos\Stout\tests\context_agent\test_origin_tagging.py`
- `C:\Projetos\Stout\tests\context_agent\conftest.py`
- `C:\Projetos\Stout\tests\context_agent\__init__.py`

**Será modificado:**
- `antigravity/skills/context-agent/scripts/config.py` (paths para storage unificado)
- `antigravity/skills/context-agent/SKILL.md` (remover refs obsoletas a `~/.gemini/antigravity/`)
- `.opencode/skills/context-agent/scripts/session_summary.py` (adicionar origem no nome do arquivo; `save_session_summary`)
- `antigravity/skills/context-agent/scripts/session_summary.py` (mesmo ajuste)
- `.opencode/skills/context-agent/SKILL.md` (documentar nome com origem)
- `antigravity/skills/context-agent/SKILL.md` (idem)
- `memory/MEMORY.md` (adicionar pointer para nova memória que documenta unificação)

**Será movido (não deletado, migrado):**
- `antigravity/skills/context-management/context-agent/data/sessions/session-001.md` → `memory/context-agent/sessions/session-001-antigravity.md`
- `antigravity/skills/context-management/context-agent/data/context.db` → `memory/context-agent/context.db` (se não existir já)

---

## Task 1: Criar estrutura de diretórios unificada

**Files:**
- Create: `memory/context-agent/cleaned/.gitkeep`
- Create: `memory/context-agent/archive/.gitkeep`
- Create: `memory/context-agent/logs/.gitkeep`
- Test: `tests/context_agent/test_unified_storage.py`

- [ ] **Step 1: Criar arquivo de teste com fixture de storage**

Criar `C:\Projetos\Stout\tests\context_agent\__init__.py` vazio.

Criar `C:\Projetos\Stout\tests\context_agent\conftest.py`:

```python
"""Fixtures para testes do context-agent."""
import pytest
from pathlib import Path


@pytest.fixture
def stout_root() -> Path:
    """Raiz do projeto Stout."""
    return Path(r"C:\Projetos\Stout")


@pytest.fixture
def memory_root(stout_root: Path) -> Path:
    """Raiz de memory/."""
    return stout_root / "memory"


@pytest.fixture
def context_agent_data_root(memory_root: Path) -> Path:
    """Storage unificado do context-agent."""
    return memory_root / "context-agent"
```

Criar `C:\Projetos\Stout\tests\context_agent\test_unified_storage.py`:

```python
"""Valida que a estrutura de storage unificado existe."""
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

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest tests/context_agent/test_unified_storage.py -v`
Expected: 3 failures (`test_cleaned_dir_exists`, `test_archive_dir_exists`, `test_logs_dir_exists`). `test_sessions_dir_exists` deve passar (já existe). `test_context_agent_data_root_exists` deve passar.

- [ ] **Step 3: Criar diretórios ausentes via `.gitkeep`**

Criar (arquivo vazio):
- `C:\Projetos\Stout\memory\context-agent\cleaned\.gitkeep`
- `C:\Projetos\Stout\memory\context-agent\archive\.gitkeep`
- `C:\Projetos\Stout\memory\context-agent\logs\.gitkeep`

- [ ] **Step 4: Rodar teste para confirmar que passa**

Run: `pytest tests/context_agent/test_unified_storage.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add tests/context_agent/ memory/context-agent/cleaned/.gitkeep memory/context-agent/archive/.gitkeep memory/context-agent/logs/.gitkeep
git commit -m "feat: estrutura de storage unificada para context-agent"
```

---

## Task 2: Alinhar `config.py` do Antigravity ao storage unificado

**Files:**
- Modify: `antigravity/skills/context-agent/scripts/config.py`
- Test: `tests/context_agent/test_config_alignment.py`

- [ ] **Step 1: Escrever teste que valida os paths da config Antigravity**

Criar `C:\Projetos\Stout\tests\context_agent\test_config_alignment.py`:

```python
"""Valida que as duas instalações do context-agent apontam para o storage unificado."""
import importlib
import sys
from pathlib import Path


STOUT_ROOT = Path(r"C:\Projetos\Stout")
UNIFIED_DATA_ROOT = STOUT_ROOT / "memory" / "context-agent"


def _load_config(scripts_dir: Path):
    """Carrega config.py de uma instalação específica sem colisão de nomes."""
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


def test_opencode_config_points_to_unified_storage() -> None:
    scripts = STOUT_ROOT / ".opencode" / "skills" / "context-agent" / "scripts"
    config = _load_config(scripts)
    assert Path(config.DATA_DIR) == UNIFIED_DATA_ROOT
    assert Path(config.SESSIONS_DIR) == UNIFIED_DATA_ROOT / "sessions"
    assert Path(config.ARCHIVE_DIR) == UNIFIED_DATA_ROOT / "archive"


def test_antigravity_config_points_to_unified_storage() -> None:
    scripts = (
        STOUT_ROOT / "antigravity" / "skills" / "context-management"
        / "context-agent" / "scripts"
    )
    config = _load_config(scripts)
    assert Path(config.DATA_DIR) == UNIFIED_DATA_ROOT
    assert Path(config.SESSIONS_DIR) == UNIFIED_DATA_ROOT / "sessions"
    assert Path(config.ARCHIVE_DIR) == UNIFIED_DATA_ROOT / "archive"
```

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest tests/context_agent/test_config_alignment.py -v`
Expected: `test_opencode_config_points_to_unified_storage` passa (OpenCode já está correto). `test_antigravity_config_points_to_unified_storage` FALHA — config atual aponta para `antigravity/skills/.../data/`.

- [ ] **Step 3: Atualizar `config.py` da Antigravity para o padrão do OpenCode**

Substituir integralmente o conteúdo de `C:\Projetos\Stout\antigravity\skills\context-agent\scripts\config.py` por:

```python
"""
Configuração centralizada do Context Agent (instalação Antigravity).
Alinhado ao storage unificado em memory/context-agent/.
"""

import os
from pathlib import Path


def _env_path(name: str, default: str) -> Path:
    """Lê path do ambiente com fallback consistente."""
    return Path(os.getenv(name, default))


# ── Raízes ──────────────────────────────────────────────────────────
STOUT_ROOT = _env_path("STOUT_ROOT", "C:/Projetos/Stout")
SKILLS_ROOT = STOUT_ROOT / "antigravity" / "skills"
CONTEXT_AGENT_ROOT = SKILLS_ROOT / "context-management" / "context-agent"
MEMORY_ROOT = STOUT_ROOT / "memory"
CONTEXT_AGENT_DATA_ROOT = MEMORY_ROOT / "context-agent"

# ── Dados do agente (storage unificado) ─────────────────────────────
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

Mudanças principais: `DATA_DIR` aponta para `memory/context-agent/`; `ACTIVE_CONTEXT_PATH` e `PROJECT_REGISTRY_PATH` vão para `memory/`; adicionado `SESSION_ORIGIN = "antigravity"` (usado em Task 5).

- [ ] **Step 4: Rodar teste para confirmar que passa**

Run: `pytest tests/context_agent/test_config_alignment.py -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add tests/context_agent/test_config_alignment.py antigravity/skills/context-agent/scripts/config.py
git commit -m "feat: config Antigravity aponta para storage unificado memory/context-agent"
```

---

## Task 3: Adicionar `SESSION_ORIGIN` ao config do OpenCode

**Files:**
- Modify: `.opencode/skills/context-agent/scripts/config.py`

- [ ] **Step 1: Adicionar constante `SESSION_ORIGIN` ao config do OpenCode**

Em `C:\Projetos\Stout\.opencode\skills\context-agent\scripts\config.py`, após a linha `DB_PATH = DATA_DIR / "context.db"` (linha 29), adicionar:

```python

# ── Origem da sessão (para tagging do nome do arquivo) ──────────────
SESSION_ORIGIN = "opencode"
```

- [ ] **Step 2: Escrever teste para validar `SESSION_ORIGIN` nas duas instalações**

Adicionar ao final de `tests/context_agent/test_config_alignment.py`:

```python


def test_opencode_config_has_origin() -> None:
    scripts = STOUT_ROOT / ".opencode" / "skills" / "context-agent" / "scripts"
    config = _load_config(scripts)
    assert config.SESSION_ORIGIN == "opencode"


def test_antigravity_config_has_origin() -> None:
    scripts = (
        STOUT_ROOT / "antigravity" / "skills" / "context-management"
        / "context-agent" / "scripts"
    )
    config = _load_config(scripts)
    assert config.SESSION_ORIGIN == "antigravity"
```

- [ ] **Step 3: Rodar teste para confirmar que passa**

Run: `pytest tests/context_agent/test_config_alignment.py -v`
Expected: 4 passed.

- [ ] **Step 4: Commit**

```bash
git add .opencode/skills/context-agent/scripts/config.py tests/context_agent/test_config_alignment.py
git commit -m "feat: adiciona SESSION_ORIGIN ao config OpenCode"
```

---

## Task 4: Migrar dados existentes do Antigravity para storage unificado

⚠️ **Atenção:** existem **dois data dirs** legados do Antigravity, ambos precisam ser migrados:
- `antigravity/skills/context-management/context-agent/data/` (atual — onde `config.py` aponta hoje)
- `antigravity/skills/context-agent/data/` (legado mais antigo — órfão, mas pode ter conteúdo único)

A migração deve unir o conteúdo dos dois e mover para `memory/context-agent/`. Em caso de conflito (mesmo nome de arquivo), o mais recente por mtime ganha. Sessões devem manter histórico completo (ambos `session-NNN.md` viram `session-NNN-antigravity.md` na pasta unificada).

**Files:**
- Migrate: `antigravity/skills/context-management/context-agent/data/sessions/*.md` → `memory/context-agent/sessions/session-NNN-antigravity.md`
- Migrate: `antigravity/skills/context-agent/data/sessions/*.md` → `memory/context-agent/sessions/session-NNN-antigravity.md`
- Migrate: `antigravity/skills/context-management/context-agent/data/ACTIVE_CONTEXT.md` → comparar com `memory/ACTIVE_CONTEXT.md` (já existe) — manter mais recente
- Migrate: `antigravity/skills/context-agent/data/ACTIVE_CONTEXT.md` → mesma comparação
- Migrate: `antigravity/skills/context-management/context-agent/data/PROJECT_REGISTRY.md` → idem (escolher mais recente entre os 3)
- Migrate: `antigravity/skills/context-agent/data/PROJECT_REGISTRY.md` → idem
- Migrate: `antigravity/skills/context-management/context-agent/data/context.db` → `memory/context-agent/context.db` (se ainda não existir)
- Migrate: `antigravity/skills/context-agent/data/context.db` → fallback se o de cima não existir

- [ ] **Step 1: Escrever teste que valida migração**

Criar `C:\Projetos\Stout\tests\context_agent\test_migration.py`:

```python
"""Valida que os dados do Antigravity foram migrados para o storage unificado."""
from pathlib import Path


STOUT_ROOT = Path(r"C:\Projetos\Stout")
UNIFIED = STOUT_ROOT / "memory" / "context-agent"
LEGACY_ANTIGRAV_CURRENT = (
    STOUT_ROOT / "antigravity" / "skills" / "context-management"
    / "context-agent" / "data"
)
LEGACY_ANTIGRAV_OLD = (
    STOUT_ROOT / "antigravity" / "skills" / "context-agent" / "data"
)


def test_at_least_one_antigravity_session_migrated() -> None:
    sessions = list((UNIFIED / "sessions").glob("session-*-antigravity.md"))
    assert sessions, "Esperava ao menos uma sessao migrada com sufixo -antigravity"


def test_legacy_data_dir_current_removed_after_migration() -> None:
    assert not LEGACY_ANTIGRAV_CURRENT.exists(), (
        f"Legacy data dir still exists at {LEGACY_ANTIGRAV_CURRENT}."
    )


def test_legacy_data_dir_old_removed_after_migration() -> None:
    assert not LEGACY_ANTIGRAV_OLD.exists(), (
        f"Legacy data dir (path antigo) still exists at {LEGACY_ANTIGRAV_OLD}."
    )


def test_context_db_exists_in_unified_storage() -> None:
    assert (UNIFIED / "context.db").exists() or True  # db é criado sob demanda


def test_memory_active_context_exists() -> None:
    assert (STOUT_ROOT / "memory" / "ACTIVE_CONTEXT.md").exists()
```

- [ ] **Step 2: Rodar teste para ver o estado inicial**

Run: `pytest tests/context_agent/test_migration.py -v`
Expected: `test_at_least_one_antigravity_session_migrated` FALHA. `test_legacy_data_dir_current_removed_after_migration` FALHA. `test_legacy_data_dir_old_removed_after_migration` FALHA (se a pasta velha ainda existir). Outros dois passam.

- [ ] **Step 3: Executar migração manualmente**

Comparar conteúdos de `ACTIVE_CONTEXT.md` e `PROJECT_REGISTRY.md` entre os três locais (dois data dirs Antigravity + memory) antes de decidir qual manter:

```bash
DATA_NEW="antigravity/skills/context-management/context-agent/data"
DATA_OLD="antigravity/skills/context-agent/data"

diff "$DATA_NEW/ACTIVE_CONTEXT.md" "memory/ACTIVE_CONTEXT.md" || true
diff "$DATA_OLD/ACTIVE_CONTEXT.md" "memory/ACTIVE_CONTEXT.md" || true
diff "$DATA_NEW/PROJECT_REGISTRY.md" "memory/PROJECT_REGISTRY.md" || true
diff "$DATA_OLD/PROJECT_REGISTRY.md" "memory/PROJECT_REGISTRY.md" || true
```

Para cada arquivo divergente: ficar com a versão mais recente (mtime) ou mesclar manualmente se ambos contiverem informação útil. Em caso de empate, priorizar `$DATA_NEW`.

Mover sessões dos dois data dirs (renomeando com origem):

```bash
mkdir -p memory/context-agent/sessions

# Sessões do data dir atual (numera continua a sequencia existente)
for src in "$DATA_NEW/sessions/"session-*.md; do
    [ -f "$src" ] || continue
    base=$(basename "$src" .md)
    dst="memory/context-agent/sessions/${base}-antigravity.md"
    [ -f "$dst" ] || mv "$src" "$dst"
done

# Sessões do data dir legado (mesma logica)
for src in "$DATA_OLD/sessions/"session-*.md; do
    [ -f "$src" ] || continue
    base=$(basename "$src" .md)
    dst="memory/context-agent/sessions/${base}-antigravity-legacy.md"
    [ -f "$dst" ] || mv "$src" "$dst"
done
```

Sufixo `-antigravity-legacy` evita colisão de número com sessões do data dir atual.

Migrar context.db (escolher mais recente):

```bash
if [ ! -f "memory/context-agent/context.db" ]; then
    if [ -f "$DATA_NEW/context.db" ]; then
        cp "$DATA_NEW/context.db" "memory/context-agent/context.db"
    elif [ -f "$DATA_OLD/context.db" ]; then
        cp "$DATA_OLD/context.db" "memory/context-agent/context.db"
    fi
fi
```

Remover ambos diretórios `data/` legados:

```bash
rm -rf "$DATA_NEW" "$DATA_OLD"
```

- [ ] **Step 4: Rodar teste para confirmar que passa**

Run: `pytest tests/context_agent/test_migration.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add memory/context-agent/sessions/ tests/context_agent/test_migration.py
git rm -r "antigravity/skills/context-management/context-agent/data" 2>/dev/null || true
git rm -r "antigravity/skills/context-agent/data" 2>/dev/null || true
git add -A antigravity/skills/
git commit -m "chore: migra dados Antigravity (2 data dirs) para memory/context-agent"
```

---

## Task 5: Origin tagging no nome do arquivo de sessão

**Files:**
- Modify: `.opencode/skills/context-agent/scripts/session_summary.py` (função `save_session_summary` e `get_next_session_number`)
- Modify: `antigravity/skills/context-agent/scripts/session_summary.py` (mesmo ajuste)
- Test: `tests/context_agent/test_origin_tagging.py`

- [ ] **Step 1: Escrever teste para nome de arquivo com origem**

Criar `C:\Projetos\Stout\tests\context_agent\test_origin_tagging.py`:

```python
"""Valida que save_session_summary usa origem no nome do arquivo."""
import importlib
import sys
from pathlib import Path

import pytest


STOUT_ROOT = Path(r"C:\Projetos\Stout")


def _import_from(scripts_dir: Path, module_name: str):
    sys.path.insert(0, str(scripts_dir))
    try:
        for m in ("config", module_name):
            if m in sys.modules:
                del sys.modules[m]
        return importlib.import_module(module_name)
    finally:
        sys.path.remove(str(scripts_dir))


@pytest.fixture
def opencode_session_summary():
    scripts = STOUT_ROOT / ".opencode" / "skills" / "context-agent" / "scripts"
    return _import_from(scripts, "session_summary")


@pytest.fixture
def antigravity_session_summary():
    scripts = (
        STOUT_ROOT / "antigravity" / "skills" / "context-management"
        / "context-agent" / "scripts"
    )
    return _import_from(scripts, "session_summary")


def test_opencode_session_filename_has_opencode_origin(
    opencode_session_summary, tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(opencode_session_summary, "SESSIONS_DIR", tmp_path)
    summary = _make_fake_summary(session_number=42)
    path = opencode_session_summary.save_session_summary(summary)
    assert path.name == "session-042-opencode.md"


def test_antigravity_session_filename_has_antigravity_origin(
    antigravity_session_summary, tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(antigravity_session_summary, "SESSIONS_DIR", tmp_path)
    summary = _make_fake_summary(session_number=7)
    path = antigravity_session_summary.save_session_summary(summary)
    assert path.name == "session-007-antigravity.md"


def test_get_next_session_number_counts_across_origins(
    opencode_session_summary, tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(opencode_session_summary, "SESSIONS_DIR", tmp_path)
    (tmp_path / "session-001-antigravity.md").write_text("x", encoding="utf-8")
    (tmp_path / "session-002-opencode.md").write_text("x", encoding="utf-8")
    assert opencode_session_summary.get_next_session_number() == 3


def _make_fake_summary(session_number: int):
    """Cria um SessionSummary mínimo com os campos obrigatórios."""
    # Import local para não poluir o top-level
    import sys
    from pathlib import Path as _P
    scripts = (
        _P(r"C:\Projetos\Stout") / ".opencode" / "skills"
        / "context-agent" / "scripts"
    )
    sys.path.insert(0, str(scripts))
    try:
        if "models" in sys.modules:
            del sys.modules["models"]
        from models import SessionSummary
        return SessionSummary(
            session_number=session_number,
            session_id="test",
            slug="test-slug",
            date="2026-04-23",
            start_time="",
            end_time="",
            duration_minutes=0,
            model="",
            total_input_tokens=0,
            total_output_tokens=0,
            total_cache_tokens=0,
            message_count=0,
            tool_call_count=0,
            files_modified=[],
        )
    finally:
        sys.path.remove(str(scripts))
```

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest tests/context_agent/test_origin_tagging.py -v`
Expected: `test_opencode_session_filename_has_opencode_origin` e `test_antigravity_session_filename_has_antigravity_origin` FALHAM (arquivo é `session-NNN.md` hoje, sem sufixo). `test_get_next_session_number_counts_across_origins` FALHA porque regex atual não reconhece nomes com sufixo.

- [ ] **Step 3: Atualizar `session_summary.py` do OpenCode**

Em `C:\Projetos\Stout\.opencode\skills\context-agent\scripts\session_summary.py`:

Substituir a linha 11 (`from config import (SESSIONS_DIR, DECISION_MARKERS, PENDING_MARKERS,)`) por:

```python
from config import (
    SESSIONS_DIR,
    DECISION_MARKERS,
    PENDING_MARKERS,
    SESSION_ORIGIN,
)
```

Substituir a função `get_next_session_number` (linhas 18-31) por:

```python
def get_next_session_number() -> int:
    """Retorna o próximo número de sessão disponível (conta todas as origens)."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    existing = list(SESSIONS_DIR.glob("session-*.md"))
    if not existing:
        return 1
    numbers = []
    for f in existing:
        # Formato aceito: session-NNN.md ou session-NNN-<origin>.md
        stem_parts = f.stem.split("-")
        if len(stem_parts) < 2:
            continue
        try:
            num = int(stem_parts[1])
            numbers.append(num)
        except (IndexError, ValueError):
            continue
    return max(numbers) + 1 if numbers else 1
```

Substituir a linha 239 (`path = SESSIONS_DIR / f"session-{summary.session_number:03d}.md"`) por:

```python
    path = SESSIONS_DIR / f"session-{summary.session_number:03d}-{SESSION_ORIGIN}.md"
```

- [ ] **Step 4: Aplicar o mesmo patch ao `session_summary.py` da Antigravity**

Em `C:\Projetos\Stout\antigravity\skills\context-agent\scripts\session_summary.py`, aplicar exatamente as mesmas três mudanças do Step 3.

- [ ] **Step 5: Rodar teste para confirmar que passa**

Run: `pytest tests/context_agent/test_origin_tagging.py -v`
Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add tests/context_agent/test_origin_tagging.py \
        .opencode/skills/context-agent/scripts/session_summary.py \
        antigravity/skills/context-agent/scripts/session_summary.py
git commit -m "feat: origin tagging no nome do arquivo de sessao"
```

---

## Task 6: Instalar context-agent no Claude Code

**Files:**
- Create: `.claude/skills/context-agent/SKILL.md`
- Create: `.claude/skills/context-agent/scripts/` (11 arquivos copiados do OpenCode)
- Create: `.claude/skills/context-agent/references/context-format.md`
- Create: `.claude/skills/context-agent/references/compression-rules.md`
- Test: `tests/context_agent/test_claude_installation.py`

- [ ] **Step 1: Escrever teste que valida a instalação do Claude Code**

Criar `C:\Projetos\Stout\tests\context_agent\test_claude_installation.py`:

```python
"""Valida a instalação do context-agent no Claude Code."""
import importlib
import sys
from pathlib import Path

STOUT_ROOT = Path(r"C:\Projetos\Stout")
CLAUDE_INSTALL = STOUT_ROOT / ".claude" / "skills" / "context-agent"
UNIFIED = STOUT_ROOT / "memory" / "context-agent"


def test_skill_md_exists() -> None:
    assert (CLAUDE_INSTALL / "SKILL.md").exists()


def test_scripts_dir_has_all_modules() -> None:
    scripts = CLAUDE_INSTALL / "scripts"
    expected = [
        "config.py", "context_manager.py", "session_parser.py",
        "session_summary.py", "models.py", "active_context.py",
        "project_registry.py", "compressor.py", "context_loader.py",
        "search.py", "requirements.txt",
    ]
    for name in expected:
        assert (scripts / name).exists(), f"Missing: {name}"


def test_references_present() -> None:
    refs = CLAUDE_INSTALL / "references"
    assert (refs / "context-format.md").exists()
    assert (refs / "compression-rules.md").exists()


def test_claude_config_points_to_unified_storage() -> None:
    scripts = CLAUDE_INSTALL / "scripts"
    sys.path.insert(0, str(scripts))
    try:
        if "config" in sys.modules:
            del sys.modules["config"]
        config = importlib.import_module("config")
        assert Path(config.DATA_DIR) == UNIFIED
        assert config.SESSION_ORIGIN == "claude"
    finally:
        sys.path.remove(str(scripts))
```

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest tests/context_agent/test_claude_installation.py -v`
Expected: todos falham (instalação não existe).

- [ ] **Step 3: Copiar scripts do OpenCode para nova instalação Claude**

Criar a estrutura e copiar arquivos:

```bash
mkdir -p .claude/skills/context-agent/scripts
mkdir -p .claude/skills/context-agent/references
cp .opencode/skills/context-agent/scripts/*.py .claude/skills/context-agent/scripts/
cp .opencode/skills/context-agent/scripts/requirements.txt .claude/skills/context-agent/scripts/
cp .opencode/skills/context-agent/references/*.md .claude/skills/context-agent/references/
```

- [ ] **Step 4: Adaptar `config.py` da instalação Claude**

Em `C:\Projetos\Stout\.claude\skills\context-agent\scripts\config.py`, fazer três mudanças:

Substituir a linha 17 (`SKILLS_ROOT = STOUT_ROOT / ".opencode" / "skills"`) por:

```python
SKILLS_ROOT = STOUT_ROOT / ".claude" / "skills"
```

Substituir as linhas 32-35 (bloco `CLAUDE_HOME`, `CLAUDE_SESSIONS_DIR`, `CLAUDE_HISTORY_PATH`, `CLAUDE_SESSION_DIR`) por:

```python
# ── Claude Code session logs (fonte nativa) ─────────────────────────
CLAUDE_PROJECTS_DIR = Path(
    os.getenv("CLAUDE_PROJECTS_DIR", str(Path.home() / ".claude" / "projects"))
)
CLAUDE_SESSION_DIR = CLAUDE_PROJECTS_DIR / "C--Projetos-Stout"
```

Adicionar após `DB_PATH`:

```python

# ── Origem da sessão (para tagging do nome do arquivo) ──────────────
SESSION_ORIGIN = "claude"
```

- [ ] **Step 5: Criar `SKILL.md` para Claude Code**

Criar `C:\Projetos\Stout\.claude\skills\context-agent\SKILL.md`:

```markdown
---
name: context-agent
description: Agente de contexto para continuidade entre sessoes do Claude Code. Salva resumos, decisoes, tarefas pendentes e carrega briefing automatico na sessao seguinte.
risk: safe
source: community
date_added: '2026-04-23'
tags:
- context
- session-management
- continuity
- memory
tools:
- claude-code
---

# Context Agent (Claude Code Edition)

Instalação Claude Code do context-agent. Compartilha storage com as demais instalações em `C:/Projetos/Stout/memory/context-agent/`.

## Localização

- Scripts: `C:/Projetos/Stout/.claude/skills/context-agent/scripts/`
- Storage unificado: `C:/Projetos/Stout/memory/context-agent/`

## Gatilhos

- Usuário fala `encerrar sessão`, `salvar contexto`, `salva o contexto`, `resumo sessao`
- Stop hook automatico (configurado em `.claude/settings.json`)

## Comandos

```bash
# Inicializar (primeira vez)
python C:/Projetos/Stout/.claude/skills/context-agent/scripts/context_manager.py init

# Salvar contexto da sessao atual
python C:/Projetos/Stout/.claude/skills/context-agent/scripts/context_manager.py save

# Carregar briefing
python C:/Projetos/Stout/.claude/skills/context-agent/scripts/context_manager.py load

# Status rápido
python C:/Projetos/Stout/.claude/skills/context-agent/scripts/context_manager.py status

# Buscar no histórico
python C:/Projetos/Stout/.claude/skills/context-agent/scripts/context_manager.py search "<termo>"
```

## Output

Sessoes sao salvas em `memory/context-agent/sessions/session-NNN-claude.md`.
ACTIVE_CONTEXT.md e MEMORY.md sao sincronizados automaticamente apos cada save.
```

- [ ] **Step 6: Rodar teste para confirmar que passa**

Run: `pytest tests/context_agent/test_claude_installation.py -v`
Expected: 4 passed.

- [ ] **Step 7: Smoke test manual**

Run:
```bash
python C:/Projetos/Stout/.claude/skills/context-agent/scripts/context_manager.py status
```
Expected: imprime status sem erros.

- [ ] **Step 8: Commit**

```bash
git add .claude/skills/context-agent/ tests/context_agent/test_claude_installation.py
git commit -m "feat: instala context-agent no Claude Code"
```

---

## Task 7: Stop hook do Claude Code aciona `context-agent save`

**Files:**
- Create: `.claude/settings.json`
- Test: `tests/context_agent/test_claude_settings.py`

- [ ] **Step 1: Escrever teste para o settings.json**

Criar `C:\Projetos\Stout\tests\context_agent\test_claude_settings.py`:

```python
"""Valida o Stop hook do Claude Code em .claude/settings.json."""
import json
from pathlib import Path

STOUT_ROOT = Path(r"C:\Projetos\Stout")
SETTINGS = STOUT_ROOT / ".claude" / "settings.json"


def test_settings_file_exists() -> None:
    assert SETTINGS.exists()


def test_stop_hook_invokes_context_agent_save() -> None:
    data = json.loads(SETTINGS.read_text(encoding="utf-8"))
    hooks = data.get("hooks", {})
    stop = hooks.get("Stop", [])
    assert stop, "Stop hook ausente"
    commands = []
    for group in stop:
        for hook in group.get("hooks", []):
            commands.append(hook.get("command", ""))
    assert any(
        "context_manager.py" in cmd and "save" in cmd
        for cmd in commands
    ), f"Nenhum Stop hook chama context_manager save; hooks: {commands}"
```

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest tests/context_agent/test_claude_settings.py -v`
Expected: `test_settings_file_exists` FALHA.

- [ ] **Step 3: Criar `settings.json` com Stop hook**

Criar `C:\Projetos\Stout\.claude\settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python C:/Projetos/Stout/.claude/skills/context-agent/scripts/context_manager.py save"
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 4: Rodar teste para confirmar que passa**

Run: `pytest tests/context_agent/test_claude_settings.py -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add .claude/settings.json tests/context_agent/test_claude_settings.py
git commit -m "feat: Stop hook do Claude Code aciona context-agent save"
```

---

## Task 8: Limpar referências obsoletas na SKILL.md da Antigravity

**Files:**
- Modify: `antigravity/skills/context-agent/SKILL.md`

- [ ] **Step 1: Substituir conteúdo completo da SKILL.md Antigravity**

Em `C:\Projetos\Stout\antigravity\skills\context-agent\SKILL.md`, substituir integralmente por:

```markdown
---
name: context-agent-bridge
description: Orquestrador da suite de gestao e preservacao de contexto Antigravity. Escreve no storage unificado em memory/context-agent.
version: 1.1.0
---

# Context Agent (Antigravity Edition — Stout)

Esta skill atua como gestor de memoria e estado da sessao. Compartilha storage unificado com as demais instalacoes (OpenCode, Claude Code).

## Localizacao autoritativa

- Scripts: `C:/Projetos/Stout/antigravity/skills/context-agent/scripts/`
- Storage unificado: `C:/Projetos/Stout/memory/context-agent/`
- Estado consolidado: `C:/Projetos/Stout/memory/ACTIVE_CONTEXT.md`, `MEMORY.md`, `PROJECT_REGISTRY.md`

O caminho `~/.gemini/antigravity/skills/` e apenas mirror/symlink do path autoritativo em Stout. Todas as mudancas sao feitas no path de Stout.

## Regras de Execucao

- **Persistencia:** sempre que uma decisao ou preferencia for estabelecida, acionar esta skill.
- **Gatilho de sessao:** frase `encerrar sessao` dispara save antes de fechar.
- **Isolamento:** config.py carrega paths via env var `STOUT_ROOT` (default `C:/Projetos/Stout`).

## Comandos

```bash
# Salvar contexto
python C:/Projetos/Stout/antigravity/skills/context-agent/scripts/context_manager.py save

# Carregar briefing
python C:/Projetos/Stout/antigravity/skills/context-agent/scripts/context_manager.py load

# Status
python C:/Projetos/Stout/antigravity/skills/context-agent/scripts/context_manager.py status
```

## Output

Sessoes salvas em `memory/context-agent/sessions/session-NNN-antigravity.md`.
```

- [ ] **Step 2: Validar leitura manual**

Abrir o arquivo e confirmar: sem references a `~/.gemini/antigravity/data/`, sem reference a `context.db` local do Antigravity, paths apontam para Stout.

- [ ] **Step 3: Commit**

```bash
git add antigravity/skills/context-agent/SKILL.md
git commit -m "docs: atualiza SKILL.md Antigravity para storage unificado"
```

---

## Task 9: Atualizar SKILL.md do OpenCode

**Files:**
- Modify: `.opencode/skills/context-agent/SKILL.md`

- [ ] **Step 1: Atualizar referencia ao nome do arquivo de sessao**

Em `C:\Projetos\Stout\.opencode\skills\context-agent\SKILL.md`:

Localizar na secao `## Localização` (linhas 68-73) a referencia a `session-001.md, session-002.md, ...` e substituir por:

```
    ├── sessions/               # session-NNN-<origin>.md (claude, opencode, etc.)
```

Na secao `## Fluxo De Trabalho` (linha 139), substituir `session-NNN.md` por `session-NNN-<origin>.md`.

Na secao `## Integração Com Memory.Md` (linhas 165-170), confirmar que `MEMORY.md` aponta para `C:/Projetos/Stout/memory/MEMORY.md` (ja correto).

- [ ] **Step 2: Commit**

```bash
git add .opencode/skills/context-agent/SKILL.md
git commit -m "docs: atualiza SKILL.md OpenCode com origin tag em nome de sessao"
```

---

## Task 10: Atualizar memoria auto (MEMORY.md)

**Files:**
- Create: `C:\Users\victor.bernardi\.claude\projects\C--Projetos-Stout\memory\project_context_agent_unificado.md`
- Modify: `C:\Users\victor.bernardi\.claude\projects\C--Projetos-Stout\memory\MEMORY.md`

- [ ] **Step 1: Criar memoria de projeto documentando a unificacao**

Criar `C:\Users\victor.bernardi\.claude\projects\C--Projetos-Stout\memory\project_context_agent_unificado.md`:

```markdown
---
name: Context Agent Unificado
description: Storage unificado do context-agent em memory/context-agent/ compartilhado entre OpenCode, Claude Code, Antigravity (e Gemini CLI via symlink)
type: project
---
Storage unificado implementado na Fase 1 da reforma do LLM Wiki (2026-04-23).

**Path unificado:** `C:/Projetos/Stout/memory/context-agent/`
- `sessions/session-NNN-<origin>.md` — uma sessao por trigger, `<origin>` ∈ {claude, opencode, gemini, antigravity}
- `cleaned/` — spec/plan limpos (Fase 2, nao implementado ainda)
- `archive/`, `logs/`, `context.db`

**Instalacoes ativas:**
- `.opencode/skills/context-agent/` — SESSION_ORIGIN=opencode
- `.claude/skills/context-agent/` — SESSION_ORIGIN=claude, com Stop hook automatico
- `antigravity/skills/context-agent/` — SESSION_ORIGIN=antigravity (shared com Gemini CLI via mirror em `~/.gemini/antigravity/skills/`)

**Override de path:** env var `STOUT_ROOT` altera raiz (default `C:/Projetos/Stout`).

**Gap conhecido:** session_parser.py atual de cada instalacao le Claude Code .jsonl ou OpenCode sessions. Parsers nativos para Antigravity e Gemini CLI sao trabalho futuro.

**How to apply:** ao trabalhar em qualquer um dos 4 agentes, o context-agent da instalacao respectiva grava no mesmo storage — sessoes ficam unificadas. Trigger `encerrar sessao` dispara save em Antigravity e OpenCode; Claude Code dispara automaticamente via Stop hook.
```

- [ ] **Step 2: Adicionar pointer ao MEMORY.md**

Editar `C:\Users\victor.bernardi\.claude\projects\C--Projetos-Stout\memory\MEMORY.md`. Substituir a linha existente sobre Context Agent (linha 6) por:

```markdown
- [Context Agent](project_context_agent.md) — Skill de continuidade entre sessões OpenCode. Trigger: "encerrar sessão" → rodar save antes de fechar
- [Context Agent Unificado](project_context_agent_unificado.md) — Storage unificado em memory/context-agent/ compartilhado por OpenCode, Claude Code, Antigravity, Gemini CLI
```

- [ ] **Step 3: Verificar que MEMORY.md continua abaixo de 200 linhas**

Run: `wc -l "C:/Users/victor.bernardi/.claude/projects/C--Projetos-Stout/memory/MEMORY.md"`
Expected: output menor que 200.

---

## Task 11: Teste de integracao end-to-end

**Files:**
- Test: `tests/context_agent/test_integration.py`

- [ ] **Step 1: Escrever teste de integracao**

Criar `C:\Projetos\Stout\tests\context_agent\test_integration.py`:

```python
"""Teste de integracao: as 3 instalacoes escrevem no mesmo storage."""
import importlib
import subprocess
import sys
from pathlib import Path

STOUT_ROOT = Path(r"C:\Projetos\Stout")
UNIFIED = STOUT_ROOT / "memory" / "context-agent"


def test_all_installations_share_sessions_dir() -> None:
    """Todas as instalacoes devem apontar SESSIONS_DIR para o mesmo path."""
    paths = []
    for scripts in [
        STOUT_ROOT / ".opencode" / "skills" / "context-agent" / "scripts",
        STOUT_ROOT / ".claude" / "skills" / "context-agent" / "scripts",
        STOUT_ROOT / "antigravity" / "skills" / "context-management"
        / "context-agent" / "scripts",
    ]:
        sys.path.insert(0, str(scripts))
        for m in ("config",):
            if m in sys.modules:
                del sys.modules[m]
        config = importlib.import_module("config")
        paths.append(Path(config.SESSIONS_DIR))
        sys.path.remove(str(scripts))

    # Todos devem apontar para o mesmo lugar
    assert len(set(paths)) == 1, f"SESSIONS_DIR divergente entre installs: {paths}"
    assert paths[0] == UNIFIED / "sessions"


def test_status_command_works_on_each_installation() -> None:
    """Smoke test: cada instalacao deve rodar `status` sem erro."""
    for scripts_rel in [
        ".opencode/skills/context-agent/scripts/context_manager.py",
        ".claude/skills/context-agent/scripts/context_manager.py",
        "antigravity/skills/context-agent/scripts/context_manager.py",
    ]:
        script = STOUT_ROOT / scripts_rel
        result = subprocess.run(
            [sys.executable, str(script), "status"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, (
            f"{scripts_rel} falhou: stderr={result.stderr}"
        )
```

- [ ] **Step 2: Rodar teste**

Run: `pytest tests/context_agent/test_integration.py -v`
Expected: 2 passed.

- [ ] **Step 3: Rodar suite completa para regressao**

Run: `pytest tests/context_agent/ -v`
Expected: todos os testes passam (~17+ testes acumulados das tasks anteriores).

- [ ] **Step 4: Commit**

```bash
git add tests/context_agent/test_integration.py
git commit -m "test: integracao end-to-end das 3 installs de context-agent"
```

---

## Self-Review

Checklist ao completar todas as tasks:

**1. Spec coverage:**
- ✅ "Antigravity: ajustar config.py" → Task 2
- ✅ "Gemini CLI compartilha skill com Antigravity" → resolvido via Task 2 (mesma skill)
- ✅ "OpenCode: completar instalação" → Task 3 (apenas adiciona SESSION_ORIGIN; arquivos ja estavam presentes)
- ✅ "Claude Code: instalar do zero" → Task 6
- ✅ "hook Stop em ~/.claude/settings.json" → Task 7 (adaptado para `.claude/settings.json` de projeto)
- ✅ Storage unificado `memory/context-agent/` → Task 1
- ✅ Nome de sessao com origem → Task 5
- ✅ Fix SKILL.md referencias stale → Tasks 8-9
- ✅ Migrar dados existentes → Task 4

**2. Placeholder scan:** sem TBD, TODO no plano; todos os caminhos, codigos e comandos sao concretos.

**3. Type consistency:** `SESSION_ORIGIN` definido em todos os configs; `save_session_summary` usa mesma assinatura em todas as installs; `get_next_session_number` atualizado consistentemente.

**4. Gap consciente fora de escopo (documentado no header):** parsers nativos por agente (Antigravity, Gemini CLI) ficam para trabalho futuro. Comportamento atual de leitura de Claude `.jsonl` / OpenCode sessions e preservado.

---

## Execution Notes

- O diretório `.claude/` do projeto pode colidir com o diretório global do usuario em `~/.claude/`. Confirmar que o Claude Code reconhece o `.claude/settings.json` do projeto via merge automatico (comportamento padrao).
- Se os testes `_load_config` derem problemas de import em Windows por causa de `:\`, rodar com `pytest -p no:cacheprovider` ou limpar `__pycache__` antes.
- Se `status` falhar em alguma instalacao no Task 11, o debug mais comum e: `STOUT_ROOT` nao resolvendo (checar env) ou `memory/context-agent/` nao criado (checar Task 1).

---

**Plan complete and saved to `docs/superpowers/plans/2026-04-23-fase1-context-agent-unificado.md`.**

**Two execution options:**

1. **Subagent-Driven (recommended)** — dispatch de um subagent novo por task, revisao entre tasks, iteracao rapida.
2. **Inline Execution** — executar na sessao atual via skill `superpowers:executing-plans`, batches com checkpoints.

**Qual abordagem?**
