# Fase 3 — Ar9av Compilador em Ambiente Isolado

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Instalar Ar9av/obsidian-wiki como motor novo de compilação em `wiki-compiler/compiler/`, apontando para um vault de teste isolado (não tocar no vault de produção). Construir adapters que alimentam o Ar9av a partir do storage unificado (`memory/context-agent/sessions/` e `cleaned/`) e post-processor que transforma a saída do Ar9av no formato preservado do vault atual (flat kebab-case, sem frontmatter). Remover check de NLM do audit engine. Validar o pipeline end-to-end antes de Fase 4 tocar em produção.

**Architecture:** Ar9av é instalado como subprojeto em `wiki-compiler/compiler/` (git clone). Opera em vault de teste `wiki-compiler/test-vault/` (ignorado pelo git exceto pela estrutura). Contratos externos do sistema (`raw/_pending/`, flat kebab-case, audit engine existente) são preservados via duas camadas de tradução: **entrada** (adapters copiam do storage unificado para `_raw/` do Ar9av) e **saída** (post-processor remove frontmatter, flatten, renomeia para kebab-case).

**Tech Stack:** Python 3.13, pytest, Ar9av/obsidian-wiki (git clone como dependência externa). Ar9av é implementado como skill-based — agent (Claude/Gemini) invoca slash commands `/wiki-ingest`, `/wiki-lint`, etc. Este plano assume Claude Code como agent invocador (Python scripts orquestram).

---

## Contexto para o engenheiro

Pré-requisitos:
- Fase 1 concluída (storage unificado com `sessions/` populado)
- Fase 2 concluída (cleaned/ populado após rodar `clean-superpowers`)
- Leia o spec em `docs/superpowers/specs/2026-04-23-llm-wiki-reforma-design.md`, seção Fase 3
- Leia o spec antigo do audit engine: `wiki-compiler/docs/superpowers/specs/2026-04-18-audit-engine-design.md`

**Estado atual do wiki-compiler:**
```
C:\Projetos\Stout\wiki-compiler\
├── run_wiki_work.sh              # entry point (vai ser modificado em Task 9)
├── SCHEMA.md                     # prompt do Gemini CLI (será aposentado em Fase 4)
├── harvest_brain.sh              # deprecado (Fase 3 não mexe, Fase 4 deleta)
├── docs/                         # specs do wiki-compiler
└── audit/                        # audit engine — wiki_text_utils.py, audit_knowledge.py
```

**Diferenças importantes entre Ar9av e o contrato atual:**

| Ar9av | Contrato atual (preservar) |
|---|---|
| Staging `_raw/` dentro do vault | Staging `raw/_pending/` dentro do vault |
| Páginas com YAML frontmatter (title, summary, tags, category, provenance, sources, created, updated) | Páginas sem frontmatter (apenas markdown puro, flat) |
| Kebab-case com espaço→hífen | Kebab-case igual |
| Estrutura com `_meta/`, `_insights.md`, `.manifest.json` | Nenhum desses; flat raiz |
| Invocação via slash commands (`/wiki-ingest`) | Invocação via shell script (`run_wiki_work.sh`) |

**Estratégia de adapters:**
1. **Entrada** — `sessions_to_pending.py` e `cleaned_to_pending.py` copiam do storage unificado para `raw/_pending/` (mantém contrato externo)
2. **Bridge** — `pending_to_ar9av_raw.py` move/symlinka de `raw/_pending/` para o `_raw/` do vault de teste Ar9av
3. **Compilação** — orquestrador chama Claude Code com prompt que dispara `/wiki-ingest` no vault de teste
4. **Saída** — `ar9av_post_processor.py` lê páginas do vault de teste, strip frontmatter, normaliza nomes, grava em um "staging de saída" que **posteriormente** (Fase 4) passa a escrever no vault de produção

**Ambiente de teste:**
- Vault de teste: `C:\Projetos\Stout\wiki-compiler\test-vault\`
- Não é commitado no git (apenas `.gitkeep` em estrutura mínima)
- Populado por testes com sessões sintéticas

---

## File Structure

**Será criado:**
- `wiki-compiler/compiler/` (git clone do Ar9av)
- `wiki-compiler/adapters/__init__.py`
- `wiki-compiler/adapters/sessions_to_pending.py`
- `wiki-compiler/adapters/cleaned_to_pending.py`
- `wiki-compiler/adapters/pending_to_ar9av_raw.py`
- `wiki-compiler/adapters/ar9av_post_processor.py`
- `wiki-compiler/adapters/orchestrator.py`
- `wiki-compiler/test-vault/.gitkeep`
- `wiki-compiler/test-vault/raw/_pending/.gitkeep`
- `wiki-compiler/test-vault/_raw/.gitkeep`
- `wiki-compiler/tests/__init__.py`
- `wiki-compiler/tests/test_sessions_to_pending.py`
- `wiki-compiler/tests/test_cleaned_to_pending.py`
- `wiki-compiler/tests/test_pending_to_ar9av_raw.py`
- `wiki-compiler/tests/test_ar9av_post_processor.py`
- `wiki-compiler/tests/test_integration.py`
- `wiki-compiler/tests/fixtures/sample_session.md`
- `wiki-compiler/tests/fixtures/sample_cleaned_spec.md`
- `wiki-compiler/tests/fixtures/sample_ar9av_output.md`
- `wiki-compiler/.gitignore` (exclui test-vault exceto .gitkeep)

**Será modificado:**
- `wiki-compiler/audit/audit_knowledge.py` (remover `check_conflicts` / NLM specific logic)
- `wiki-compiler/audit/tests/test_audit.py` (ajustar testes para refletir remoção)
- `wiki-compiler/run_wiki_work.sh` (novo entry point que invoca orchestrator)

---

## Task 1: Clonar Ar9av como subprojeto

**Files:**
- Create: `wiki-compiler/compiler/` (via git clone)
- Create: `wiki-compiler/.gitignore`
- Test: `wiki-compiler/tests/test_ar9av_installed.py`

- [ ] **Step 1: Escrever teste que valida presença de Ar9av**

Criar `C:\Projetos\Stout\wiki-compiler\tests\__init__.py` vazio.

Criar `C:\Projetos\Stout\wiki-compiler\tests\test_ar9av_installed.py`:

```python
"""Valida instalacao do Ar9av como subprojeto."""
from pathlib import Path

STOUT_ROOT = Path(r"C:\Projetos\Stout")
AR9AV_ROOT = STOUT_ROOT / "wiki-compiler" / "compiler"


def test_ar9av_compiler_dir_exists() -> None:
    assert AR9AV_ROOT.is_dir()


def test_ar9av_has_skills_dir() -> None:
    assert (AR9AV_ROOT / ".skills").is_dir() or (AR9AV_ROOT / ".claude" / "skills").is_dir()


def test_ar9av_readme_exists() -> None:
    assert (AR9AV_ROOT / "README.md").exists()
```

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest wiki-compiler/tests/test_ar9av_installed.py -v`
Expected: todos falham.

- [ ] **Step 3: Clonar Ar9av em `wiki-compiler/compiler/`**

```bash
git clone https://github.com/Ar9av/obsidian-wiki.git wiki-compiler/compiler
```

Em seguida, registrar como subprojeto (não submódulo — evita dependência externa pesada):

```bash
rm -rf wiki-compiler/compiler/.git
```

- [ ] **Step 4: Adicionar `.gitignore` para ignorar test-vault**

Criar `C:\Projetos\Stout\wiki-compiler\.gitignore`:

```
# Test vault: estrutura minima committada, conteudo ignorado
test-vault/_raw/*
test-vault/raw/_pending/*
test-vault/*.md
!test-vault/**/.gitkeep

# Ar9av runtime artifacts
compiler/node_modules/
compiler/.env
compiler/*.log
```

- [ ] **Step 5: Rodar teste para confirmar que passa**

Run: `pytest wiki-compiler/tests/test_ar9av_installed.py -v`
Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add wiki-compiler/.gitignore wiki-compiler/compiler wiki-compiler/tests/__init__.py wiki-compiler/tests/test_ar9av_installed.py
git commit -m "chore: instala Ar9av/obsidian-wiki como subprojeto em wiki-compiler/compiler"
```

---

## Task 2: Criar test-vault com estrutura mínima

**Files:**
- Create: `wiki-compiler/test-vault/.gitkeep`
- Create: `wiki-compiler/test-vault/raw/_pending/.gitkeep`
- Create: `wiki-compiler/test-vault/_raw/.gitkeep`
- Create: `wiki-compiler/test-vault/suggestion_ignore.md`

- [ ] **Step 1: Escrever teste que valida a estrutura do test-vault**

Criar `C:\Projetos\Stout\wiki-compiler\tests\test_test_vault.py`:

```python
"""Valida estrutura minima do test-vault."""
from pathlib import Path

TEST_VAULT = Path(r"C:\Projetos\Stout") / "wiki-compiler" / "test-vault"


def test_test_vault_exists() -> None:
    assert TEST_VAULT.is_dir()


def test_raw_pending_exists() -> None:
    assert (TEST_VAULT / "raw" / "_pending").is_dir()


def test_ar9av_raw_staging_exists() -> None:
    assert (TEST_VAULT / "_raw").is_dir()


def test_suggestion_ignore_exists() -> None:
    assert (TEST_VAULT / "suggestion_ignore.md").exists()
```

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest wiki-compiler/tests/test_test_vault.py -v`
Expected: todos falham.

- [ ] **Step 3: Criar diretorios e arquivos**

Criar os `.gitkeep`:
- `wiki-compiler/test-vault/.gitkeep`
- `wiki-compiler/test-vault/raw/_pending/.gitkeep`
- `wiki-compiler/test-vault/_raw/.gitkeep`

Criar `C:\Projetos\Stout\wiki-compiler\test-vault\suggestion_ignore.md`:

```markdown
# Suggestion Ignore List

Tópicos que não devem mais ser sugeridos.
```

- [ ] **Step 4: Rodar teste para confirmar que passa**

Run: `pytest wiki-compiler/tests/test_test_vault.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add wiki-compiler/test-vault/ wiki-compiler/tests/test_test_vault.py
git commit -m "chore: estrutura minima do test-vault para Ar9av"
```

---

## Task 3: Adapter `sessions_to_pending.py`

**Files:**
- Create: `wiki-compiler/adapters/__init__.py`
- Create: `wiki-compiler/adapters/sessions_to_pending.py`
- Create: `wiki-compiler/tests/fixtures/sample_session.md`
- Test: `wiki-compiler/tests/test_sessions_to_pending.py`

- [ ] **Step 1: Criar fixture de sessão**

Criar `C:\Projetos\Stout\wiki-compiler\tests\fixtures\sample_session.md`:

```markdown
# Sessao 042 — 2026-04-23
**Slug:** feature-x | **Duração:** ~25min | **Modelo:** claude-sonnet-4-6

## Tópicos
- implementacao do feature X
- decisao sobre retry logic

## Decisões
- Decidimos usar exponential backoff para retries
- Optamos por cache em memoria (nao Redis)

## Tarefas Concluídas
- [x] Implementar cliente HTTP
- [x] Adicionar testes de retry

## Arquivos Modificados
- `src/client.py` — edit
- `tests/test_client.py` — write
```

- [ ] **Step 2: Escrever teste**

Criar `C:\Projetos\Stout\wiki-compiler\tests\test_sessions_to_pending.py`:

```python
"""Testes do adapter sessions_to_pending."""
import sys
from pathlib import Path

import pytest

STOUT_ROOT = Path(r"C:\Projetos\Stout")
ADAPTERS = STOUT_ROOT / "wiki-compiler" / "adapters"
FIXTURES = STOUT_ROOT / "wiki-compiler" / "tests" / "fixtures"


@pytest.fixture(autouse=True)
def _add_to_path():
    sys.path.insert(0, str(ADAPTERS))
    for m in ("sessions_to_pending",):
        if m in sys.modules:
            del sys.modules[m]
    yield
    sys.path.remove(str(ADAPTERS))


def test_copy_sessions_to_pending_copies_md(tmp_path: Path) -> None:
    from sessions_to_pending import copy_sessions_to_pending
    sessions_dir = tmp_path / "sessions"
    pending_dir = tmp_path / "pending"
    sessions_dir.mkdir(); pending_dir.mkdir()

    (sessions_dir / "session-042-claude.md").write_text(
        (FIXTURES / "sample_session.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    count = copy_sessions_to_pending(sessions_dir, pending_dir)
    assert count == 1
    assert (pending_dir / "session-042-claude.md").exists()


def test_copy_sessions_to_pending_idempotent(tmp_path: Path) -> None:
    from sessions_to_pending import copy_sessions_to_pending
    sessions_dir = tmp_path / "sessions"
    pending_dir = tmp_path / "pending"
    sessions_dir.mkdir(); pending_dir.mkdir()

    (sessions_dir / "session-042-claude.md").write_text("content", encoding="utf-8")
    copy_sessions_to_pending(sessions_dir, pending_dir)

    # Rodar de novo — deve pular (mesmo conteúdo)
    count = copy_sessions_to_pending(sessions_dir, pending_dir)
    assert count == 0


def test_copy_sessions_skips_non_md_files(tmp_path: Path) -> None:
    from sessions_to_pending import copy_sessions_to_pending
    sessions_dir = tmp_path / "sessions"
    pending_dir = tmp_path / "pending"
    sessions_dir.mkdir(); pending_dir.mkdir()

    (sessions_dir / "session-042-claude.md").write_text("x", encoding="utf-8")
    (sessions_dir / "session-042-claude.json").write_text("{}", encoding="utf-8")
    (sessions_dir / "context.db").write_bytes(b"sqlite")

    count = copy_sessions_to_pending(sessions_dir, pending_dir)
    assert count == 1
```

- [ ] **Step 3: Rodar teste para confirmar que falha**

Run: `pytest wiki-compiler/tests/test_sessions_to_pending.py -v`
Expected: todos falham — módulo não existe.

- [ ] **Step 4: Implementar adapter**

Criar `C:\Projetos\Stout\wiki-compiler\adapters\__init__.py` vazio.

Criar `C:\Projetos\Stout\wiki-compiler\adapters\sessions_to_pending.py`:

```python
"""
Adapter: copia sessoes do storage unificado (memory/context-agent/sessions/)
para o staging raw/_pending/ do vault.
Idempotente: reprocessar nao duplica.
"""

from __future__ import annotations

import shutil
from pathlib import Path


def copy_sessions_to_pending(sessions_dir: Path, pending_dir: Path) -> int:
    """Copia todos os .md de sessions_dir para pending_dir. Retorna quantidade copiada."""
    pending_dir.mkdir(parents=True, exist_ok=True)
    if not sessions_dir.exists():
        return 0

    copied = 0
    for src in sessions_dir.glob("*.md"):
        dst = pending_dir / src.name
        if dst.exists() and dst.read_bytes() == src.read_bytes():
            continue
        shutil.copy2(src, dst)
        copied += 1
    return copied
```

- [ ] **Step 5: Rodar teste para confirmar que passa**

Run: `pytest wiki-compiler/tests/test_sessions_to_pending.py -v`
Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add wiki-compiler/adapters/ wiki-compiler/tests/fixtures/ wiki-compiler/tests/test_sessions_to_pending.py
git commit -m "feat: adapter sessions_to_pending com idempotencia"
```

---

## Task 4: Adapter `cleaned_to_pending.py`

**Files:**
- Create: `wiki-compiler/adapters/cleaned_to_pending.py`
- Create: `wiki-compiler/tests/fixtures/sample_cleaned_spec.md`
- Test: `wiki-compiler/tests/test_cleaned_to_pending.py`

- [ ] **Step 1: Criar fixture**

Criar `C:\Projetos\Stout\wiki-compiler\tests\fixtures\sample_cleaned_spec.md`:

```markdown
> Origem: C:/Projetos/Stout/docs/superpowers/specs/2026-04-15-exemplo-design.md

# Exemplo — Feature X

## Problema

O sistema nao suporta Y. Decidimos adotar Z.

## Solucao

Adapter de Z com camada de tradução.

## Decisoes

Optamos por manter o adapter stateless.
```

- [ ] **Step 2: Escrever teste**

Criar `C:\Projetos\Stout\wiki-compiler\tests\test_cleaned_to_pending.py`:

```python
"""Testes do adapter cleaned_to_pending."""
import sys
from pathlib import Path

import pytest

STOUT_ROOT = Path(r"C:\Projetos\Stout")
ADAPTERS = STOUT_ROOT / "wiki-compiler" / "adapters"
FIXTURES = STOUT_ROOT / "wiki-compiler" / "tests" / "fixtures"


@pytest.fixture(autouse=True)
def _add_to_path():
    sys.path.insert(0, str(ADAPTERS))
    for m in ("cleaned_to_pending",):
        if m in sys.modules:
            del sys.modules[m]
    yield
    sys.path.remove(str(ADAPTERS))


def test_copy_cleaned_to_pending_copies_specs(tmp_path: Path) -> None:
    from cleaned_to_pending import copy_cleaned_to_pending
    cleaned_dir = tmp_path / "cleaned"
    pending_dir = tmp_path / "pending"
    cleaned_dir.mkdir(); pending_dir.mkdir()

    sample = (FIXTURES / "sample_cleaned_spec.md").read_text(encoding="utf-8")
    (cleaned_dir / "spec-feature-x.md").write_text(sample, encoding="utf-8")
    (cleaned_dir / "plan-feature-x.md").write_text(sample, encoding="utf-8")

    count = copy_cleaned_to_pending(cleaned_dir, pending_dir)
    assert count == 2
    assert (pending_dir / "spec-feature-x.md").exists()
    assert (pending_dir / "plan-feature-x.md").exists()


def test_copy_cleaned_to_pending_idempotent(tmp_path: Path) -> None:
    from cleaned_to_pending import copy_cleaned_to_pending
    cleaned_dir = tmp_path / "cleaned"
    pending_dir = tmp_path / "pending"
    cleaned_dir.mkdir(); pending_dir.mkdir()

    (cleaned_dir / "spec-x.md").write_text("x", encoding="utf-8")
    copy_cleaned_to_pending(cleaned_dir, pending_dir)

    count = copy_cleaned_to_pending(cleaned_dir, pending_dir)
    assert count == 0
```

- [ ] **Step 3: Rodar teste para confirmar que falha**

Run: `pytest wiki-compiler/tests/test_cleaned_to_pending.py -v`
Expected: FAIL.

- [ ] **Step 4: Implementar adapter**

Criar `C:\Projetos\Stout\wiki-compiler\adapters\cleaned_to_pending.py`:

```python
"""
Adapter: copia specs/plans limpos (memory/context-agent/cleaned/)
para o staging raw/_pending/ do vault.
Idempotente.
"""

from __future__ import annotations

import shutil
from pathlib import Path


def copy_cleaned_to_pending(cleaned_dir: Path, pending_dir: Path) -> int:
    """Copia todos os .md de cleaned_dir para pending_dir. Retorna quantidade copiada."""
    pending_dir.mkdir(parents=True, exist_ok=True)
    if not cleaned_dir.exists():
        return 0

    copied = 0
    for src in cleaned_dir.glob("*.md"):
        dst = pending_dir / src.name
        if dst.exists() and dst.read_bytes() == src.read_bytes():
            continue
        shutil.copy2(src, dst)
        copied += 1
    return copied
```

- [ ] **Step 5: Rodar teste para confirmar que passa**

Run: `pytest wiki-compiler/tests/test_cleaned_to_pending.py -v`
Expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add wiki-compiler/adapters/cleaned_to_pending.py \
        wiki-compiler/tests/fixtures/sample_cleaned_spec.md \
        wiki-compiler/tests/test_cleaned_to_pending.py
git commit -m "feat: adapter cleaned_to_pending"
```

---

## Task 5: Bridge `pending_to_ar9av_raw.py`

**Files:**
- Create: `wiki-compiler/adapters/pending_to_ar9av_raw.py`
- Test: `wiki-compiler/tests/test_pending_to_ar9av_raw.py`

- [ ] **Step 1: Escrever teste**

Criar `C:\Projetos\Stout\wiki-compiler\tests\test_pending_to_ar9av_raw.py`:

```python
"""Testes do bridge pending_to_ar9av_raw."""
import sys
from pathlib import Path

import pytest

STOUT_ROOT = Path(r"C:\Projetos\Stout")
ADAPTERS = STOUT_ROOT / "wiki-compiler" / "adapters"


@pytest.fixture(autouse=True)
def _add_to_path():
    sys.path.insert(0, str(ADAPTERS))
    for m in ("pending_to_ar9av_raw",):
        if m in sys.modules:
            del sys.modules[m]
    yield
    sys.path.remove(str(ADAPTERS))


def test_move_pending_to_ar9av_raw_moves_files(tmp_path: Path) -> None:
    from pending_to_ar9av_raw import move_pending_to_ar9av_raw
    pending = tmp_path / "pending"
    ar9av_raw = tmp_path / "_raw"
    pending.mkdir(); ar9av_raw.mkdir()

    (pending / "foo.md").write_text("foo", encoding="utf-8")
    (pending / "bar.md").write_text("bar", encoding="utf-8")

    moved = move_pending_to_ar9av_raw(pending, ar9av_raw)
    assert moved == 2
    assert (ar9av_raw / "foo.md").exists()
    assert (ar9av_raw / "bar.md").exists()
    # Pending fica vazio após mover (comportamento do contrato atual)
    assert list(pending.glob("*.md")) == []


def test_move_pending_to_ar9av_raw_skips_non_md(tmp_path: Path) -> None:
    from pending_to_ar9av_raw import move_pending_to_ar9av_raw
    pending = tmp_path / "pending"
    ar9av_raw = tmp_path / "_raw"
    pending.mkdir(); ar9av_raw.mkdir()

    (pending / "foo.md").write_text("foo", encoding="utf-8")
    (pending / ".gitkeep").write_text("", encoding="utf-8")
    (pending / "bar.txt").write_text("bar", encoding="utf-8")

    moved = move_pending_to_ar9av_raw(pending, ar9av_raw)
    assert moved == 1
    assert (pending / ".gitkeep").exists()
    assert (pending / "bar.txt").exists()
```

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest wiki-compiler/tests/test_pending_to_ar9av_raw.py -v`
Expected: FAIL.

- [ ] **Step 3: Implementar bridge**

Criar `C:\Projetos\Stout\wiki-compiler\adapters\pending_to_ar9av_raw.py`:

```python
"""
Bridge: move arquivos de raw/_pending/ (contrato externo preservado)
para _raw/ do Ar9av (convenção interna do compiler).
Mover (não copiar) mantém o contrato de que _pending/ esvazia apos processamento.
"""

from __future__ import annotations

import shutil
from pathlib import Path


def move_pending_to_ar9av_raw(pending_dir: Path, ar9av_raw_dir: Path) -> int:
    """Move todos os .md de pending_dir para ar9av_raw_dir. Retorna quantidade movida."""
    ar9av_raw_dir.mkdir(parents=True, exist_ok=True)
    if not pending_dir.exists():
        return 0

    moved = 0
    for src in list(pending_dir.glob("*.md")):
        dst = ar9av_raw_dir / src.name
        if dst.exists():
            # Sobrescrever: pending é fonte da verdade para este run
            dst.unlink()
        shutil.move(str(src), str(dst))
        moved += 1
    return moved
```

- [ ] **Step 4: Rodar teste para confirmar que passa**

Run: `pytest wiki-compiler/tests/test_pending_to_ar9av_raw.py -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add wiki-compiler/adapters/pending_to_ar9av_raw.py \
        wiki-compiler/tests/test_pending_to_ar9av_raw.py
git commit -m "feat: bridge pending_to_ar9av_raw preservando contrato pending"
```

---

## Task 6: Post-processor `ar9av_post_processor.py`

**Files:**
- Create: `wiki-compiler/adapters/ar9av_post_processor.py`
- Create: `wiki-compiler/tests/fixtures/sample_ar9av_output.md`
- Test: `wiki-compiler/tests/test_ar9av_post_processor.py`

- [ ] **Step 1: Criar fixture com output do Ar9av**

Criar `C:\Projetos\Stout\wiki-compiler\tests\fixtures\sample_ar9av_output.md`:

```markdown
---
title: Stale Closure
summary: "Closure capturando variavel stale no React"
tags: [react, hooks, bug]
category: tecnologia/frontend
provenance: "extracted (70%), inferred (20%), ambiguous (10%)"
sources: [session-042-claude.md]
created: 2026-04-23T10:30:00Z
updated: 2026-04-23T14:45:00Z
---

## Problema

Hook useEffect captura valor antigo da variavel quando dependencia nao eh declarada.

## Solucao

Adicionar variavel ao array de dependencias. Ver [[react-hooks]] para detalhes.

Sources: [1](session-042-claude.md)
```

- [ ] **Step 2: Escrever teste**

Criar `C:\Projetos\Stout\wiki-compiler\tests\test_ar9av_post_processor.py`:

```python
"""Testes do post-processor Ar9av -> formato do vault atual."""
import sys
from pathlib import Path

import pytest

STOUT_ROOT = Path(r"C:\Projetos\Stout")
ADAPTERS = STOUT_ROOT / "wiki-compiler" / "adapters"
FIXTURES = STOUT_ROOT / "wiki-compiler" / "tests" / "fixtures"


@pytest.fixture(autouse=True)
def _add_to_path():
    sys.path.insert(0, str(ADAPTERS))
    for m in ("ar9av_post_processor",):
        if m in sys.modules:
            del sys.modules[m]
    yield
    sys.path.remove(str(ADAPTERS))


def test_strip_frontmatter_removes_yaml() -> None:
    from ar9av_post_processor import strip_frontmatter
    content = (FIXTURES / "sample_ar9av_output.md").read_text(encoding="utf-8")
    result = strip_frontmatter(content)
    assert "title:" not in result
    assert "## Problema" in result


def test_strip_frontmatter_preserves_body() -> None:
    from ar9av_post_processor import strip_frontmatter
    content = "---\ntitle: X\n---\n\n## S\nbody\n"
    result = strip_frontmatter(content)
    assert result.strip() == "## S\nbody"


def test_strip_sources_footer_removes_source_link_lines() -> None:
    from ar9av_post_processor import strip_sources_footer
    text = "Body here.\n\nSources: [1](session-042.md), [2](session-043.md)\n"
    result = strip_sources_footer(text)
    assert "Sources:" not in result
    assert "Body here." in result


def test_normalize_filename_returns_kebab_case() -> None:
    from ar9av_post_processor import normalize_filename
    assert normalize_filename("Stale Closure.md") == "stale-closure.md"
    assert normalize_filename("React Hooks Guide.md") == "react-hooks-guide.md"
    # Já kebab-case: preserva
    assert normalize_filename("stale-closure.md") == "stale-closure.md"


def test_post_process_page_full_pipeline(tmp_path: Path) -> None:
    from ar9av_post_processor import post_process_page
    src = tmp_path / "Stale Closure.md"
    src.write_text((FIXTURES / "sample_ar9av_output.md").read_text(encoding="utf-8"), encoding="utf-8")

    out_dir = tmp_path / "out"
    out_dir.mkdir()

    result_path = post_process_page(src, out_dir)
    assert result_path.name == "stale-closure.md"
    assert result_path.exists()

    content = result_path.read_text(encoding="utf-8")
    assert "title:" not in content  # frontmatter removido
    assert "Sources:" not in content  # footer removido
    assert "## Problema" in content
    assert "[[react-hooks]]" in content  # wikilinks preservados
```

- [ ] **Step 3: Rodar teste para confirmar que falha**

Run: `pytest wiki-compiler/tests/test_ar9av_post_processor.py -v`
Expected: 5 FAIL.

- [ ] **Step 4: Implementar post-processor**

Criar `C:\Projetos\Stout\wiki-compiler\adapters\ar9av_post_processor.py`:

```python
"""
Post-processor: converte output Ar9av (com frontmatter + sources footer + Title Case)
para formato do vault atual (sem frontmatter, flat, kebab-case).
"""

from __future__ import annotations

import re
from pathlib import Path


_FRONTMATTER_RE = re.compile(r"^---\r?\n.*?\r?\n---\r?\n\r?\n?", re.DOTALL)
_SOURCES_FOOTER_RE = re.compile(r"\n*Sources:\s*(?:\[\d+\]\([^)]+\),?\s*)+\s*$", re.MULTILINE)


def strip_frontmatter(content: str) -> str:
    """Remove bloco YAML frontmatter."""
    return _FRONTMATTER_RE.sub("", content, count=1)


def strip_sources_footer(content: str) -> str:
    """Remove linha 'Sources: [1](...), [2](...)' no final."""
    return _SOURCES_FOOTER_RE.sub("", content).rstrip() + "\n"


def normalize_filename(filename: str) -> str:
    """Converte para kebab-case lowercase."""
    path = Path(filename)
    stem = path.stem.lower().replace(" ", "-")
    # Colapsar múltiplos hífens
    stem = re.sub(r"-+", "-", stem).strip("-")
    return f"{stem}{path.suffix.lower()}"


def post_process_page(src: Path, out_dir: Path) -> Path:
    """Aplica transformações e escreve no out_dir com nome normalizado."""
    out_dir.mkdir(parents=True, exist_ok=True)
    content = src.read_text(encoding="utf-8")
    content = strip_frontmatter(content)
    content = strip_sources_footer(content)
    content = content.strip() + "\n"

    new_name = normalize_filename(src.name)
    out_path = out_dir / new_name
    out_path.write_text(content, encoding="utf-8")
    return out_path


def post_process_all(vault_pages_dir: Path, out_dir: Path) -> list[Path]:
    """Processa todas as páginas .md de vault_pages_dir. Retorna lista de caminhos escritos."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for src in sorted(vault_pages_dir.glob("*.md")):
        # Pular páginas internas do Ar9av
        if src.name.startswith("_"):
            continue
        written.append(post_process_page(src, out_dir))
    return written
```

- [ ] **Step 5: Rodar teste para confirmar que passa**

Run: `pytest wiki-compiler/tests/test_ar9av_post_processor.py -v`
Expected: 5 passed.

- [ ] **Step 6: Commit**

```bash
git add wiki-compiler/adapters/ar9av_post_processor.py \
        wiki-compiler/tests/fixtures/sample_ar9av_output.md \
        wiki-compiler/tests/test_ar9av_post_processor.py
git commit -m "feat: post-processor Ar9av (strip frontmatter/sources + kebab-case)"
```

---

## Task 7: Remover check NLM do audit engine

**Files:**
- Modify: `wiki-compiler/audit/audit_knowledge.py`
- Modify: `wiki-compiler/audit/tests/test_audit.py` (se existir)

- [ ] **Step 1: Escrever teste que valida ausência de `check_conflicts`**

Criar (ou modificar) `C:\Projetos\Stout\wiki-compiler\audit\tests\test_audit_no_nlm.py`:

```python
"""Valida que a verificação específica de NLM foi removida do audit."""
import sys
from pathlib import Path

import pytest

STOUT_ROOT = Path(r"C:\Projetos\Stout")
AUDIT_DIR = STOUT_ROOT / "wiki-compiler" / "audit"


@pytest.fixture(autouse=True)
def _add_to_path():
    sys.path.insert(0, str(AUDIT_DIR))
    for m in ("audit_knowledge",):
        if m in sys.modules:
            del sys.modules[m]
    yield
    sys.path.remove(str(AUDIT_DIR))


def test_check_conflicts_no_longer_exported() -> None:
    """check_conflicts (específico de NLM) foi removido."""
    import audit_knowledge
    assert not hasattr(audit_knowledge, "check_conflicts")


def test_run_audit_still_exists() -> None:
    import audit_knowledge
    assert hasattr(audit_knowledge, "run_audit")


def test_run_audit_accepts_two_dirs() -> None:
    """run_audit ainda aceita pending_dir e wiki_dir."""
    import audit_knowledge
    import inspect
    sig = inspect.signature(audit_knowledge.run_audit)
    params = list(sig.parameters)
    assert "pending_dir" in params
    assert "wiki_dir" in params
```

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest wiki-compiler/audit/tests/test_audit_no_nlm.py -v`
Expected: `test_check_conflicts_no_longer_exported` FALHA.

- [ ] **Step 3: Ler `audit_knowledge.py` atual**

Run:
```bash
cat wiki-compiler/audit/audit_knowledge.py
```

Identificar a função `check_conflicts` e o bloco que a chama em `run_audit`. O spec do audit engine (04-18) descreve essas funções.

- [ ] **Step 4: Remover `check_conflicts` e sua invocação**

Em `C:\Projetos\Stout\wiki-compiler\audit\audit_knowledge.py`:

- Deletar a função `check_conflicts(pending_dir, wiki_dir)` inteira
- Em `run_audit`, remover a linha que chama `check_conflicts(...)` e a agregação do resultado
- Remover a seção "## Conflitos com Decisões" do template de AUDIT_REPORT.md
- Preservar `check_orphans` e `check_duplicates`

- [ ] **Step 5: Rodar teste para confirmar que passa**

Run: `pytest wiki-compiler/audit/tests/test_audit_no_nlm.py -v`
Expected: 3 passed.

Run também suite existente de audit (se houver) para pegar regressão:
```bash
pytest wiki-compiler/audit/tests/ -v
```
Expected: testes existentes que dependiam de `check_conflicts` falham — esperado. Removê-los ou ajustá-los como parte desta task.

- [ ] **Step 6: Commit**

```bash
git add wiki-compiler/audit/audit_knowledge.py wiki-compiler/audit/tests/
git commit -m "refactor: remove check_conflicts (NLM nao eh mais input)"
```

---

## Task 8: Orchestrator Python coordena pipeline completo

**Files:**
- Create: `wiki-compiler/adapters/orchestrator.py`
- Test: `wiki-compiler/tests/test_integration.py`

- [ ] **Step 1: Escrever teste de integração**

Criar `C:\Projetos\Stout\wiki-compiler\tests\test_integration.py`:

```python
"""Teste de integracao: orchestrator executa pipeline completo no test-vault."""
import sys
from pathlib import Path

import pytest

STOUT_ROOT = Path(r"C:\Projetos\Stout")
ADAPTERS = STOUT_ROOT / "wiki-compiler" / "adapters"
FIXTURES = STOUT_ROOT / "wiki-compiler" / "tests" / "fixtures"


@pytest.fixture(autouse=True)
def _add_to_path():
    sys.path.insert(0, str(ADAPTERS))
    for m in (
        "orchestrator", "sessions_to_pending", "cleaned_to_pending",
        "pending_to_ar9av_raw", "ar9av_post_processor",
    ):
        if m in sys.modules:
            del sys.modules[m]
    yield
    sys.path.remove(str(ADAPTERS))


def test_orchestrator_runs_input_pipeline(tmp_path: Path) -> None:
    """sessions + cleaned → pending → ar9av _raw."""
    from orchestrator import run_input_pipeline

    sessions = tmp_path / "sessions"
    cleaned = tmp_path / "cleaned"
    pending = tmp_path / "pending"
    ar9av_raw = tmp_path / "_raw"
    for d in (sessions, cleaned, pending, ar9av_raw):
        d.mkdir()

    (sessions / "session-042-claude.md").write_text(
        (FIXTURES / "sample_session.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (cleaned / "spec-x.md").write_text(
        (FIXTURES / "sample_cleaned_spec.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    report = run_input_pipeline(
        sessions_dir=sessions,
        cleaned_dir=cleaned,
        pending_dir=pending,
        ar9av_raw_dir=ar9av_raw,
    )

    assert report["sessions_copied"] == 1
    assert report["cleaned_copied"] == 1
    assert report["moved_to_raw"] == 2
    # pending deve estar vazio apos move
    assert list(pending.glob("*.md")) == []
    # ar9av _raw tem os 2 arquivos
    assert len(list(ar9av_raw.glob("*.md"))) == 2


def test_orchestrator_runs_output_pipeline(tmp_path: Path) -> None:
    """ar9av vault pages → post-processed vault pages."""
    from orchestrator import run_output_pipeline

    vault_pages = tmp_path / "vault_pages"
    out = tmp_path / "out"
    vault_pages.mkdir(); out.mkdir()

    (vault_pages / "Stale Closure.md").write_text(
        (FIXTURES / "sample_ar9av_output.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    # Pagina interna Ar9av (nao deve ser processada)
    (vault_pages / "_meta.md").write_text("---\ninternal\n---\n", encoding="utf-8")

    written = run_output_pipeline(vault_pages_dir=vault_pages, out_dir=out)
    assert len(written) == 1
    assert (out / "stale-closure.md").exists()
    assert not (out / "_meta.md").exists()
```

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest wiki-compiler/tests/test_integration.py -v`
Expected: FAIL.

- [ ] **Step 3: Implementar orchestrator**

Criar `C:\Projetos\Stout\wiki-compiler\adapters\orchestrator.py`:

```python
"""
Orchestrador do pipeline wiki-compiler.
Coordena: sessions + cleaned → pending → Ar9av _raw → Ar9av ingest → vault pages → post-process.
Ar9av ingest e linting sao invocados externamente (via agent/slash commands);
este modulo trata a parte Python (adapters + post-processor + audit).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sessions_to_pending import copy_sessions_to_pending
from cleaned_to_pending import copy_cleaned_to_pending
from pending_to_ar9av_raw import move_pending_to_ar9av_raw
from ar9av_post_processor import post_process_all


@dataclass(frozen=True)
class InputReport:
    sessions_copied: int
    cleaned_copied: int
    moved_to_raw: int

    def __getitem__(self, key: str) -> int:
        return getattr(self, key)


def run_input_pipeline(
    sessions_dir: Path,
    cleaned_dir: Path,
    pending_dir: Path,
    ar9av_raw_dir: Path,
) -> InputReport:
    """Roda: sessions/cleaned -> pending -> ar9av _raw."""
    sessions_copied = copy_sessions_to_pending(sessions_dir, pending_dir)
    cleaned_copied = copy_cleaned_to_pending(cleaned_dir, pending_dir)
    moved = move_pending_to_ar9av_raw(pending_dir, ar9av_raw_dir)
    return InputReport(
        sessions_copied=sessions_copied,
        cleaned_copied=cleaned_copied,
        moved_to_raw=moved,
    )


def run_output_pipeline(vault_pages_dir: Path, out_dir: Path) -> list[Path]:
    """Roda: ar9av vault pages -> post-processed pages."""
    return post_process_all(vault_pages_dir, out_dir)
```

- [ ] **Step 4: Rodar teste para confirmar que passa**

Run: `pytest wiki-compiler/tests/test_integration.py -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add wiki-compiler/adapters/orchestrator.py \
        wiki-compiler/tests/test_integration.py
git commit -m "feat: orchestrator coordena input/output pipelines do wiki-compiler"
```

---

## Task 9: Novo `run_wiki_work.sh` invoca orchestrator

**Files:**
- Modify: `wiki-compiler/run_wiki_work.sh`

- [ ] **Step 1: Inspecionar `run_wiki_work.sh` atual**

```bash
cat wiki-compiler/run_wiki_work.sh
```

- [ ] **Step 2: Reescrever para invocar orchestrator Python**

Substituir integralmente o conteúdo de `C:\Projetos\Stout\wiki-compiler\run_wiki_work.sh` por:

```bash
#!/bin/bash
# Entry point do wiki-compiler (Fase 3 — ambiente isolado).
# Executa pipeline de entrada (sessions/cleaned -> pending -> ar9av _raw)
# e pipeline de saída (ar9av vault pages -> post-processed pages).
# Em Fase 3, opera sobre test-vault. Em Fase 4, apontara para vault de producao.

set -euo pipefail

STOUT_ROOT="${STOUT_ROOT:-/c/Projetos/Stout}"
VAULT="${VAULT:-$STOUT_ROOT/wiki-compiler/test-vault}"
LOCK_FILE="/tmp/wiki-compiler.lock"

# Lock file para prevenir execucoes concorrentes
if [ -f "$LOCK_FILE" ]; then
    echo "wiki-compiler ja esta rodando (lock: $LOCK_FILE). Abortando."
    exit 1
fi
trap "rm -f '$LOCK_FILE'" EXIT
echo $$ > "$LOCK_FILE"

# Paths
SESSIONS_DIR="$STOUT_ROOT/memory/context-agent/sessions"
CLEANED_DIR="$STOUT_ROOT/memory/context-agent/cleaned"
PENDING_DIR="$VAULT/raw/_pending"
AR9AV_RAW_DIR="$VAULT/_raw"
POST_PROCESSED_DIR="$VAULT/_post_processed"  # pre-vault staging (Fase 3)

# Pipeline de entrada (Python)
python -c "
import sys
sys.path.insert(0, r'$STOUT_ROOT/wiki-compiler/adapters')
from orchestrator import run_input_pipeline
from pathlib import Path
report = run_input_pipeline(
    sessions_dir=Path(r'$SESSIONS_DIR'),
    cleaned_dir=Path(r'$CLEANED_DIR'),
    pending_dir=Path(r'$PENDING_DIR'),
    ar9av_raw_dir=Path(r'$AR9AV_RAW_DIR'),
)
print(f'Input pipeline: sessions={report.sessions_copied}, cleaned={report.cleaned_copied}, moved_to_raw={report.moved_to_raw}')
"

echo ""
echo "Arquivos em $AR9AV_RAW_DIR prontos para Ar9av /wiki-ingest."
echo "Proximo passo manual: abrir Claude Code nesse vault e rodar /wiki-ingest."
echo ""
echo "Apos ingest, rodar:"
echo "  bash $STOUT_ROOT/wiki-compiler/run_post_process.sh"
```

- [ ] **Step 3: Criar `run_post_process.sh` complementar**

Criar `C:\Projetos\Stout\wiki-compiler\run_post_process.sh`:

```bash
#!/bin/bash
# Pipeline de saida do wiki-compiler: post-process + audit.

set -euo pipefail

STOUT_ROOT="${STOUT_ROOT:-/c/Projetos/Stout}"
VAULT="${VAULT:-$STOUT_ROOT/wiki-compiler/test-vault}"

# Pipeline de saida: Ar9av vault pages -> post-processed
python -c "
import sys
sys.path.insert(0, r'$STOUT_ROOT/wiki-compiler/adapters')
from orchestrator import run_output_pipeline
from pathlib import Path
written = run_output_pipeline(
    vault_pages_dir=Path(r'$VAULT'),
    out_dir=Path(r'$VAULT/_post_processed'),
)
print(f'Output pipeline: {len(written)} paginas pos-processadas')
"

# Audit
python -c "
import sys
sys.path.insert(0, r'$STOUT_ROOT/wiki-compiler/audit')
from audit_knowledge import run_audit
from pathlib import Path
report_path = run_audit(
    pending_dir=Path(r'$VAULT/raw/_pending'),
    wiki_dir=Path(r'$VAULT/_post_processed'),
)
print(f'Audit report: {report_path}')
"
```

Marcar ambos como executáveis:
```bash
chmod +x wiki-compiler/run_wiki_work.sh
chmod +x wiki-compiler/run_post_process.sh
```

- [ ] **Step 4: Smoke test manual**

Popular o test-vault com um arquivo e rodar:
```bash
echo "# Sessao test" > memory/context-agent/sessions/session-999-test.md
bash wiki-compiler/run_wiki_work.sh
```

Expected: arquivo aparece em `wiki-compiler/test-vault/_raw/`. Nenhum erro de Python. Lock file removido ao fim.

Limpar:
```bash
rm memory/context-agent/sessions/session-999-test.md
rm wiki-compiler/test-vault/_raw/session-999-test.md
```

- [ ] **Step 5: Commit**

```bash
git add wiki-compiler/run_wiki_work.sh wiki-compiler/run_post_process.sh
git commit -m "feat: run_wiki_work.sh invoca orchestrator Python no test-vault"
```

---

## Task 10: Documentar fluxo de invocação manual de `/wiki-ingest`

**Files:**
- Create: `wiki-compiler/README.md`

- [ ] **Step 1: Criar README do wiki-compiler**

Criar `C:\Projetos\Stout\wiki-compiler\README.md`:

```markdown
# Wiki Compiler (Fase 3 — ambiente isolado)

Reforma arquitetural do wiki-compiler: Ar9av/obsidian-wiki como motor de compilacao,
com adapters Python preservando contratos externos.

## Fluxo

1. **Input pipeline (automático):**
   ```bash
   bash run_wiki_work.sh
   ```
   Copia sessoes limpas e specs/plans processados para `test-vault/_raw/`.

2. **Compile (manual — Ar9av via agent):**
   Abrir Claude Code em `test-vault/` e rodar:
   ```
   /wiki-ingest
   /wiki-lint
   ```
   Gera paginas com frontmatter em `test-vault/`.

3. **Output pipeline (automático):**
   ```bash
   bash run_post_process.sh
   ```
   Strip frontmatter, normaliza nomes para kebab-case, gera audit report.

## Paths

- Input: `memory/context-agent/sessions/`, `memory/context-agent/cleaned/`
- Staging externo: `test-vault/raw/_pending/` (contrato preservado)
- Staging interno Ar9av: `test-vault/_raw/`
- Paginas Ar9av: `test-vault/*.md` (com frontmatter)
- Paginas pos-processadas: `test-vault/_post_processed/*.md` (sem frontmatter, kebab-case)

## Ambiente de teste

O `test-vault/` e usado apenas em Fase 3. Fase 4 aponta para vault de producao em
`C:\Users\victor.bernardi\Documents\Obsidian-Victor-Global\wiki\`.

## Regressoes conhecidas

- `check_conflicts` (NLM) removido do audit engine
- `harvest_brain.sh` e escrita direta do Bibliotecário em `_pending/` continuam deprecados; Fase 4 deleta
```

- [ ] **Step 2: Commit**

```bash
git add wiki-compiler/README.md
git commit -m "docs: README do wiki-compiler (Fase 3 — ambiente isolado)"
```

---

## Task 11: Validação end-to-end no test-vault

**Files:** nenhum (validação manual + smoke test)

- [ ] **Step 1: Garantir que ha sessoes e cleaned para processar**

Confirmar manualmente que `memory/context-agent/sessions/` e `memory/context-agent/cleaned/` têm pelo menos 1 arquivo cada.

Se vazios, gerar dados sintéticos:
```bash
echo "# Sessao test" > memory/context-agent/sessions/session-998-e2e-test.md
cp .opencode/skills/context-agent/references/context-format.md memory/context-agent/cleaned/spec-test.md
```

- [ ] **Step 2: Rodar pipeline de entrada**

```bash
bash wiki-compiler/run_wiki_work.sh
```

Expected: mensagem de sucesso. Arquivos em `wiki-compiler/test-vault/_raw/`.

- [ ] **Step 3: Rodar Ar9av ingest manualmente**

Abrir Claude Code no Stout root e solicitar:
> Rode `/wiki-ingest` no diretório `wiki-compiler/test-vault/`

Expected: Claude Code reconhece as skills do Ar9av em `wiki-compiler/compiler/.claude/skills/` (ou equivalente) e gera páginas em `wiki-compiler/test-vault/*.md`.

Se Claude não reconhecer as skills: verificar se os skills markdown do Ar9av estão visíveis. Pode precisar copiar skills para `.claude/skills/` do projeto ou ajustar `compiler/setup.sh`.

- [ ] **Step 4: Rodar pipeline de saída**

```bash
bash wiki-compiler/run_post_process.sh
```

Expected: páginas em `wiki-compiler/test-vault/_post_processed/` sem frontmatter, nomes kebab-case. Audit report gerado.

- [ ] **Step 5: Inspecionar outputs**

- Verificar manualmente 2-3 páginas pós-processadas — são legíveis? Preservam decisões/arquitetura?
- Abrir `AUDIT_REPORT.md` — há órfãos ou duplicatas? Sanity check.

- [ ] **Step 6: Limpar test-vault para proximo ciclo**

```bash
rm -rf wiki-compiler/test-vault/_raw/*
rm -rf wiki-compiler/test-vault/_post_processed/*
rm wiki-compiler/test-vault/*.md 2>/dev/null || true
rm memory/context-agent/sessions/session-998-e2e-test.md 2>/dev/null || true
rm memory/context-agent/cleaned/spec-test.md 2>/dev/null || true
```

- [ ] **Step 7: Rodar suite de testes Python completa**

```bash
pytest wiki-compiler/tests/ wiki-compiler/audit/tests/ -v
```

Expected: todos os testes passam.

- [ ] **Step 8: Commit final da fase**

Se houver quaisquer fixes emergentes no passo 3 (integração com Claude skills), commitar:
```bash
git add -A
git commit -m "chore: Fase 3 validada end-to-end no test-vault"
```

---

## Self-Review

**1. Spec coverage:**
- ✅ Fork/adaptação do Ar9av → Task 1
- ✅ Adapter `sessions_to_pending.py` → Task 3
- ✅ Adapter `cleaned_to_pending.py` → Task 4
- ✅ Integração com audit engine, remoção do check NLM → Task 7
- ✅ Preservar contrato externo `raw/_pending/` → bridge na Task 5 mantém semântica de move
- ✅ Ambiente isolado (não toca produção) → test-vault na Task 2
- ✅ Entry point `run_wiki_work.sh` preservado → Task 9

**2. Placeholder scan:** sem TBD/TODO.

**3. Type consistency:** `Path` em toda a interface; retornos tipados (`int`, `list[Path]`, `InputReport`); frozen dataclass para relatório.

**4. Gaps conscientes:**
- **Invocação automática do Ar9av `/wiki-ingest`**: este plano mantém essa etapa manual (Task 11 Step 3). Automação completa (fazer Python chamar Claude Code headless) é complexa e fica para Fase 5 ou pós-reforma.
- **Configuração do Ar9av (`.env`, `~/.obsidian-wiki/config`)**: não explicitado nos testes; fica como responsabilidade do engenheiro rodar `compiler/setup.sh` se necessário durante Task 11.

---

## Dependencies

- **Bloqueado por:** Fase 1 (storage unificado), Fase 2 (cleaned dir populado)
- **Bloqueia:** Fase 4 (reset + rebuild), Fase 5 (INDEX consome vault estável)

---

## Execution Notes

- Se Ar9av falhar ao ler `_raw/` (pode esperar files sem prefixo session/spec), ajustar naming nos adapters. O formato atual `session-NNN-<origin>.md` e `spec-<slug>.md` segue convenção markdown padrão e deve funcionar.
- O post-processor assume páginas com estrutura simples. Se Ar9av produzir estruturas mais complexas (ex: múltiplos arquivos por conceito, ou subfolders), estender o processor.
- `check_conflicts` foi removido; se algum teste existente em `wiki-compiler/audit/tests/` quebrar, ajustar (remoção é intencional).
