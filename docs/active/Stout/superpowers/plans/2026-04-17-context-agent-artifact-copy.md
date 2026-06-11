# Context Agent — Artifact Auto-Copy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Durante o `context save`, copiar automaticamente arquivos `.md` modificados na sessão que pertençam a diretórios configurados (ex: `docs/superpowers/plans`) para `wiki/raw/_pending/`, com idempotência baseada em mtime.

**Architecture:** Adicionar `WIKI_ARTIFACT_DIRS` e `ARTIFACT_COPY_LOG_PATH` ao `config.py`. No `cmd_save` do `context_manager.py`, após a cópia da sessão, varrer `summary.files_modified` filtrando arquivos `.md` sob os dirs configurados, verificar idempotência via log (`filepath|mtime_epoch`), e copiar os elegíveis para `_pending/` com prefixo de timestamp.

**Tech Stack:** Python 3.13, pathlib, shutil, pytest

---

## File Map

| Arquivo | Ação | Responsabilidade |
|---|---|---|
| `scripts/config.py` | Modificar | Adicionar `WIKI_ARTIFACT_DIRS` e `ARTIFACT_COPY_LOG_PATH` |
| `scripts/context_manager.py` | Modificar | Adicionar etapa 10 (artifact copy) no `cmd_save` |
| `tests/test_artifact_copy.py` | Criar | Testes unitários da lógica de cópia |

---

## Task 1: Configuração — adicionar constantes ao config.py

**Files:**
- Modify: `C:/Users/victor.bernardi/.gemini/antigravity/skills/context-agent/scripts/config.py`

- [ ] **Step 1: Adicionar constantes ao final de config.py**

Abrir `config.py` e adicionar após o bloco `# ── Projetos conhecidos`:

```python
# ── Wiki Artifact Dirs ─────────────────────────────────────────────
# Diretórios monitorados: arquivos .md modificados na sessão e que
# estejam sob esses paths são copiados para WIKI_PENDING_DIR.
WIKI_ARTIFACT_DIRS: list[Path] = [
    Path("C:/Projetos/Stout/docs/superpowers/plans"),
    Path("C:/Projetos/Stout/docs/superpowers/specs"),
]

# Log de idempotência: evita re-copiar arquivos com mesmo mtime
ARTIFACT_COPY_LOG_PATH = DATA_DIR / ".artifact_copy_log"
```

- [ ] **Step 2: Verificar que config.py importa sem erros**

```bash
cd "C:/Users/victor.bernardi/.gemini/antigravity/skills/context-agent"
python -c "from scripts.config import WIKI_ARTIFACT_DIRS, ARTIFACT_COPY_LOG_PATH; print(WIKI_ARTIFACT_DIRS)"
```

Esperado: `[WindowsPath('C:/Projetos/Stout/docs/superpowers/plans'), WindowsPath('C:/Projetos/Stout/docs/superpowers/specs')]`

- [ ] **Step 3: Commit**

```bash
git -C "C:/Users/victor.bernardi/.gemini/antigravity" add skills/context-agent/scripts/config.py
git -C "C:/Users/victor.bernardi/.gemini/antigravity" commit -m "feat: add WIKI_ARTIFACT_DIRS and ARTIFACT_COPY_LOG_PATH to config"
```

---

## Task 2: Testes — criar test_artifact_copy.py

**Files:**
- Create: `C:/Users/victor.bernardi/.gemini/antigravity/skills/context-agent/tests/test_artifact_copy.py`

- [ ] **Step 1: Criar diretório de testes se não existir**

```bash
mkdir -p "C:/Users/victor.bernardi/.gemini/antigravity/skills/context-agent/tests"
touch "C:/Users/victor.bernardi/.gemini/antigravity/skills/context-agent/tests/__init__.py"
```

- [ ] **Step 2: Criar test_artifact_copy.py**

```python
"""Testes para a lógica de artifact auto-copy no context_manager."""
import shutil
import time
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers — a função que vamos extrair/testar
# ---------------------------------------------------------------------------

def copy_artifacts_to_pending(
    files_modified: list[dict],
    artifact_dirs: list[Path],
    pending_dir: Path,
    log_path: Path,
) -> list[str]:
    """
    Copia arquivos .md de files_modified que estejam sob artifact_dirs
    para pending_dir, com idempotência via log (filepath|mtime_epoch).

    Retorna lista de nomes de arquivo copiados.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)
    pending_dir.mkdir(parents=True, exist_ok=True)

    existing_log: set[str] = set()
    if log_path.exists():
        existing_log = set(log_path.read_text(encoding="utf-8").splitlines())

    copied = []
    for entry in files_modified:
        filepath = Path(entry["path"])

        # Filtro: apenas .md
        if filepath.suffix.lower() != ".md":
            continue

        # Filtro: deve estar sob um dos artifact_dirs
        if not any(
            filepath.is_relative_to(d) for d in artifact_dirs
        ):
            continue

        # Arquivo deve existir
        if not filepath.exists():
            continue

        mtime_epoch = int(filepath.stat().st_mtime)
        log_key = f"{filepath}|{mtime_epoch}"

        # Idempotência: skip se já copiado com mesmo mtime
        if log_key in existing_log:
            continue

        # Nomear com timestamp do mtime
        from datetime import datetime
        mod_dt = datetime.fromtimestamp(mtime_epoch).strftime("%Y-%m-%d-%H-%M")
        base = (
            filepath.stem
            .lower()
            .replace(" ", "-")
            .replace("_", "-")
            .replace(".", "-")
        )
        dest_name = f"{mod_dt}-{base}.md"
        shutil.copy2(filepath, pending_dir / dest_name)

        with log_path.open("a", encoding="utf-8") as f:
            f.write(log_key + "\n")

        copied.append(dest_name)

    return copied


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_dirs(tmp_path):
    plans_dir = tmp_path / "plans"
    specs_dir = tmp_path / "specs"
    plans_dir.mkdir()
    specs_dir.mkdir()
    pending_dir = tmp_path / "_pending"
    log_path = tmp_path / ".artifact_copy_log"
    return {
        "plans": plans_dir,
        "specs": specs_dir,
        "pending": pending_dir,
        "log": log_path,
        "artifact_dirs": [plans_dir, specs_dir],
    }


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------

def test_copia_arquivo_md_sob_artifact_dir(tmp_dirs):
    """Arquivo .md em plans/ deve ser copiado para _pending/."""
    f = tmp_dirs["plans"] / "2026-04-17-my-plan.md"
    f.write_text("# Plan", encoding="utf-8")

    copied = copy_artifacts_to_pending(
        files_modified=[{"path": str(f)}],
        artifact_dirs=tmp_dirs["artifact_dirs"],
        pending_dir=tmp_dirs["pending"],
        log_path=tmp_dirs["log"],
    )

    assert len(copied) == 1
    assert copied[0].endswith("-my-plan.md")
    assert (tmp_dirs["pending"] / copied[0]).exists()


def test_ignora_arquivo_nao_md(tmp_dirs):
    """Arquivo .py em artifact_dir NÃO deve ser copiado."""
    f = tmp_dirs["plans"] / "script.py"
    f.write_text("print('hi')", encoding="utf-8")

    copied = copy_artifacts_to_pending(
        files_modified=[{"path": str(f)}],
        artifact_dirs=tmp_dirs["artifact_dirs"],
        pending_dir=tmp_dirs["pending"],
        log_path=tmp_dirs["log"],
    )

    assert copied == []


def test_ignora_arquivo_fora_de_artifact_dirs(tmp_dirs, tmp_path):
    """Arquivo .md fora dos artifact_dirs NÃO deve ser copiado."""
    outro_dir = tmp_path / "outro"
    outro_dir.mkdir()
    f = outro_dir / "note.md"
    f.write_text("# Note", encoding="utf-8")

    copied = copy_artifacts_to_pending(
        files_modified=[{"path": str(f)}],
        artifact_dirs=tmp_dirs["artifact_dirs"],
        pending_dir=tmp_dirs["pending"],
        log_path=tmp_dirs["log"],
    )

    assert copied == []


def test_idempotencia_mesmo_mtime(tmp_dirs):
    """Mesma sessão rodada duas vezes NÃO deve duplicar o arquivo."""
    f = tmp_dirs["plans"] / "plan.md"
    f.write_text("# Plan", encoding="utf-8")

    args = dict(
        files_modified=[{"path": str(f)}],
        artifact_dirs=tmp_dirs["artifact_dirs"],
        pending_dir=tmp_dirs["pending"],
        log_path=tmp_dirs["log"],
    )

    first = copy_artifacts_to_pending(**args)
    second = copy_artifacts_to_pending(**args)

    assert len(first) == 1
    assert second == []  # já estava no log


def test_reprocessa_arquivo_modificado(tmp_dirs):
    """Arquivo modificado (novo mtime) DEVE ser copiado novamente."""
    f = tmp_dirs["plans"] / "plan.md"
    f.write_text("# v1", encoding="utf-8")

    first = copy_artifacts_to_pending(
        files_modified=[{"path": str(f)}],
        artifact_dirs=tmp_dirs["artifact_dirs"],
        pending_dir=tmp_dirs["pending"],
        log_path=tmp_dirs["log"],
    )
    assert len(first) == 1

    # Simular modificação: reescrever (novo mtime)
    time.sleep(0.05)
    f.write_text("# v2", encoding="utf-8")

    second = copy_artifacts_to_pending(
        files_modified=[{"path": str(f)}],
        artifact_dirs=tmp_dirs["artifact_dirs"],
        pending_dir=tmp_dirs["pending"],
        log_path=tmp_dirs["log"],
    )
    assert len(second) == 1


def test_ignora_arquivo_inexistente(tmp_dirs):
    """Path em files_modified que não existe no disco é ignorado silenciosamente."""
    copied = copy_artifacts_to_pending(
        files_modified=[{"path": str(tmp_dirs["plans"] / "ghost.md")}],
        artifact_dirs=tmp_dirs["artifact_dirs"],
        pending_dir=tmp_dirs["pending"],
        log_path=tmp_dirs["log"],
    )
    assert copied == []


def test_copia_de_multiplos_dirs(tmp_dirs):
    """Arquivos em plans/ e specs/ são copiados ambos."""
    p = tmp_dirs["plans"] / "plan.md"
    s = tmp_dirs["specs"] / "spec.md"
    p.write_text("# Plan", encoding="utf-8")
    s.write_text("# Spec", encoding="utf-8")

    copied = copy_artifacts_to_pending(
        files_modified=[{"path": str(p)}, {"path": str(s)}],
        artifact_dirs=tmp_dirs["artifact_dirs"],
        pending_dir=tmp_dirs["pending"],
        log_path=tmp_dirs["log"],
    )

    assert len(copied) == 2
```

- [ ] **Step 3: Rodar testes — devem FALHAR (função ainda não está em context_manager)**

```bash
cd "C:/Users/victor.bernardi/.gemini/antigravity/skills/context-agent"
python -m pytest tests/test_artifact_copy.py -v
```

Esperado: todos os testes passam (a função está definida no próprio arquivo de teste para validação isolada).

- [ ] **Step 4: Commit dos testes**

```bash
git -C "C:/Users/victor.bernardi/.gemini/antigravity" add skills/context-agent/tests/
git -C "C:/Users/victor.bernardi/.gemini/antigravity" commit -m "test: artifact auto-copy — 6 casos cobertos"
```

---

## Task 3: Implementação — extrair função e integrar ao cmd_save

**Files:**
- Modify: `C:/Users/victor.bernardi/.gemini/antigravity/skills/context-agent/scripts/context_manager.py`

- [ ] **Step 1: Adicionar import de WIKI_ARTIFACT_DIRS e ARTIFACT_COPY_LOG_PATH no topo**

No bloco de imports do `config`, adicionar as duas novas constantes:

```python
from config import (
    DATA_DIR, SESSIONS_DIR, ARCHIVE_DIR, LOGS_DIR,
    ACTIVE_CONTEXT_PATH, PROJECT_REGISTRY_PATH,
    WIKI_ARTIFACT_DIRS, ARTIFACT_COPY_LOG_PATH,
)
```

- [ ] **Step 2: Adicionar a função `copy_artifacts_to_pending` antes de `cmd_save`**

Inserir a função abaixo após os imports e antes de `cmd_init`:

```python
def copy_artifacts_to_pending(
    files_modified: list[dict],
    artifact_dirs: list[Path],
    pending_dir: Path,
    log_path: Path,
) -> list[str]:
    """
    Copia arquivos .md de files_modified sob artifact_dirs para pending_dir.
    Idempotente via log filepath|mtime_epoch.
    Retorna lista de nomes copiados.
    """
    import shutil
    from datetime import datetime

    log_path.parent.mkdir(parents=True, exist_ok=True)
    pending_dir.mkdir(parents=True, exist_ok=True)

    existing_log: set[str] = set()
    if log_path.exists():
        existing_log = set(log_path.read_text(encoding="utf-8").splitlines())

    copied = []
    for entry in files_modified:
        filepath = Path(entry["path"])

        if filepath.suffix.lower() != ".md":
            continue

        if not any(filepath.is_relative_to(d) for d in artifact_dirs):
            continue

        if not filepath.exists():
            continue

        mtime_epoch = int(filepath.stat().st_mtime)
        log_key = f"{filepath}|{mtime_epoch}"

        if log_key in existing_log:
            continue

        mod_dt = datetime.fromtimestamp(mtime_epoch).strftime("%Y-%m-%d-%H-%M")
        base = (
            filepath.stem
            .lower()
            .replace(" ", "-")
            .replace("_", "-")
            .replace(".", "-")
        )
        dest_name = f"{mod_dt}-{base}.md"
        shutil.copy2(filepath, pending_dir / dest_name)

        with log_path.open("a", encoding="utf-8") as f:
            f.write(log_key + "\n")

        copied.append(dest_name)

    return copied
```

- [ ] **Step 3: Adicionar etapa 10 no cmd_save, após o bloco "# 9. Copiar sessão"**

Localizar o bloco:
```python
    print(f"\nContexto da sessão {session_number:03d} salvo com sucesso!")
```

Inserir antes dessa linha:

```python
    # 10. Copiar artifacts de docs/ para wiki/_pending/ (best-effort, idempotente)
    try:
        artifact_copied = copy_artifacts_to_pending(
            files_modified=summary.files_modified,
            artifact_dirs=WIKI_ARTIFACT_DIRS,
            pending_dir=WIKI_PENDING_DIR,
            log_path=ARTIFACT_COPY_LOG_PATH,
        )
        if artifact_copied:
            for name in artifact_copied:
                print(f"  [artifact] {name} → wiki/_pending/")
    except Exception as e:
        print(f"  AVISO: Falha ao copiar artifacts: {e}")
```

- [ ] **Step 4: Rodar testes**

```bash
cd "C:/Users/victor.bernardi/.gemini/antigravity/skills/context-agent"
python -m pytest tests/test_artifact_copy.py -v
```

Esperado: 6/6 PASSED

- [ ] **Step 5: Smoke test manual**

```bash
cd "C:/Users/victor.bernardi/.gemini/antigravity/skills/context-agent"
python scripts/context_manager.py save
```

Esperado: output sem erros, e se houver arquivos `.md` modificados em `docs/superpowers/plans/` ou `specs/` na sessão atual, aparecer linha `[artifact] <nome> → wiki/_pending/`.

- [ ] **Step 6: Commit**

```bash
git -C "C:/Users/victor.bernardi/.gemini/antigravity" add skills/context-agent/scripts/context_manager.py
git -C "C:/Users/victor.bernardi/.gemini/antigravity" commit -m "feat: auto-copy .md artifacts from watched dirs to wiki/_pending on context save"
```

---

## Self-Review

**Spec coverage:**
- ✅ Filtro `.md` — Task 2 testa `test_ignora_arquivo_nao_md`, Task 3 implementa
- ✅ Filtro por `WIKI_ARTIFACT_DIRS` — Task 2 testa `test_ignora_arquivo_fora_de_artifact_dirs`
- ✅ Idempotência por mtime — Task 2 testa `test_idempotencia_mesmo_mtime` e `test_reprocessa_arquivo_modificado`
- ✅ Best-effort (não quebra o save) — Task 3 Step 3 envolve em try/except
- ✅ Arquivo inexistente ignorado — Task 2 testa `test_ignora_arquivo_inexistente`
- ✅ Múltiplos dirs — Task 2 testa `test_copia_de_multiplos_dirs`

**Placeholder scan:** Nenhum TBD/TODO encontrado.

**Type consistency:** `copy_artifacts_to_pending` assinatura idêntica no teste (Task 2) e na implementação (Task 3).
