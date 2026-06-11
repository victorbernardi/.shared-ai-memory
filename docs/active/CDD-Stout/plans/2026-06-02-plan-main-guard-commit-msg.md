# Main Guard — commit-msg Hook Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Adicionar bloqueio de commits diretos em `main`/`master` ao hook `commit-msg` de todos os repositórios do ecossistema, com escape via footer `Allow-Main: true`.

**Architecture:** O hook `commit-msg` recebe o arquivo de mensagem como `sys.argv[1]`. Extraímos a lógica do guard em `_check_main_guard(msg, branch) -> int` para permitir testes unitários via `importlib`. O hook delega ao `branch_policy_validator.py` após o guard — sem alterações no validator.

**Tech Stack:** Python 3.11+, pytest, unittest.mock, importlib

**Spec:** `docs/specs/2026-06-02-spec-main-guard-commit-msg.md`

---

## Task 1: Escrever testes para o main-guard (RED)

**Files:**

- Create: `tests/test_commit_msg_guard.py`

**Step 1: Criar o arquivo de teste**

```python
# tests/test_commit_msg_guard.py
import importlib.util
import sys
from pathlib import Path

import pytest


def _load_hook():
    """Carrega o template do hook como módulo sem executar __main__."""
    path = Path("templates/cdd/hooks/commit-msg")
    spec = importlib.util.spec_from_file_location("commit_msg_hook", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def hook():
    return _load_hook()


def test_bloqueia_main_sem_escape(hook):
    assert hook._check_main_guard("feat: algo", "main") == 1


def test_bloqueia_master_sem_escape(hook):
    assert hook._check_main_guard("fix: algo", "master") == 1


def test_permite_main_com_escape(hook):
    msg = "chore: release\n\nRelease direto.\n\nAllow-Main: true"
    assert hook._check_main_guard(msg, "main") == 0


def test_permite_feature_branch(hook):
    assert hook._check_main_guard("feat: algo", "feat/minha-feature") == 0


def test_permite_feature_branch_sem_escape(hook):
    assert hook._check_main_guard("feat: algo\n\nAllow-Main: true", "feat/x") == 0


def test_escape_case_sensitive(hook):
    """allow-main: true (lowercase) NÃO deve liberar."""
    assert hook._check_main_guard("feat: algo\n\nallow-main: true", "main") == 1
```

**Step 2: Rodar para confirmar FALHA (hook ainda não modificado)**

```powershell
$env:PYTHONIOENCODING="utf-8"; python -m pytest tests/test_commit_msg_guard.py -v
```

Saída esperada: `ERROR` ou `FAILED` — `_check_main_guard` não existe ainda.

---

## Task 2: Implementar main-guard no template do hook (GREEN)

**Files:**

- Modify: `templates/cdd/hooks/commit-msg`

**Step 1: Ler o arquivo atual**

Ler `templates/cdd/hooks/commit-msg` para obter o conteúdo exato antes de editar.

**Step 2: Substituir o conteúdo completo do template**

O novo `templates/cdd/hooks/commit-msg` deve ser:

```python
#!/usr/bin/env python
"""commit-msg hook: main-guard + branch policy validation."""
import subprocess
import sys
from pathlib import Path


def _check_main_guard(msg: str, branch: str) -> int:
    """Bloqueia commits diretos em main/master. Retorna 1 se bloqueado, 0 se ok."""
    if branch in ("main", "master") and "Allow-Main: true" not in msg:
        print(
            "\n[main-guard] BLOQUEADO: commits diretos em 'main' não são permitidos.\n"
            "  Para liberar, adicione ao footer do commit:\n\n"
            "    Allow-Main: true\n",
            file=sys.stderr,
        )
        return 1
    return 0


def _find_validator() -> Path | None:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        return None
    root = Path(result.stdout.strip())
    for candidate in [
        root / "src" / "branch_policy_validator.py",
        root / "branch_policy_validator.py",
    ]:
        if candidate.exists():
            return candidate
    return None


def main() -> int:
    msg = Path(sys.argv[1]).read_text(encoding="utf-8")
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True, text=True, encoding="utf-8",
    ).stdout.strip()

    rc = _check_main_guard(msg, branch)
    if rc != 0:
        return rc

    validator = _find_validator()
    if validator is None:
        return 0
    return subprocess.run([sys.executable, str(validator)]).returncode


if __name__ == "__main__":
    sys.exit(main())
```

**Step 3: Rodar testes para confirmar PASS**

```powershell
$env:PYTHONIOENCODING="utf-8"; python -m pytest tests/test_commit_msg_guard.py -v
```

Saída esperada: `6 passed`.

---

## Task 3: Deploy do hook atualizado nos 4 repositórios ativos

**Files:**

- Modify: `.git/hooks/commit-msg` (CDD)
- Modify: `C:\Projetos\Stout\.git\hooks\commit-msg`
- Modify: `C:\Projetos\Inova\.git\hooks\commit-msg`
- Modify: `C:\Projetos\Stout\Projetos\NotebookLM\.git\hooks\commit-msg`

**Step 1: Ler cada arquivo antes de editar**

Ler os 4 arquivos para verificar o conteúdo atual.

**Step 2: Aplicar a mesma mudança em cada um**

Nos hooks de CDD e NotebookLM, o `_find_validator` já existe com lógica de busca em `src/`. Apenas adicionar `_check_main_guard` e refatorar o bloco de execução para `main()`.

Nos hooks de Stout e Inova, o `_find_validator` busca apenas na raiz — manter essa diferença.

Estrutura final idêntica ao template, exceto o `_find_validator` que já existe em cada hook com sua busca específica.

**Step 3: Verificar deploy**

```powershell
foreach ($path in @(
    "C:\Projetos\Stout\Projetos\Configuration-Driven Development\.git\hooks\commit-msg",
    "C:\Projetos\Stout\.git\hooks\commit-msg",
    "C:\Projetos\Inova\.git\hooks\commit-msg",
    "C:\Projetos\Stout\Projetos\NotebookLM\.git\hooks\commit-msg"
)) {
    $has = Select-String -Path $path -Pattern "_check_main_guard" -Quiet
    "$path : $has"
}
```

Saída esperada: todos `True`.

---

## Task 4: Regressão completa + commit

**Files:**

- Stage: `templates/cdd/hooks/commit-msg`
- Stage: `tests/test_commit_msg_guard.py`

**Step 1: Rodar suite completa**

```powershell
$env:PYTHONIOENCODING="utf-8"; python -m pytest tests/ -q
```

Saída esperada: `86 passed` (80 existentes + 6 novos).

**Step 2: Verificar o que será commitado**

```powershell
git status --short
git diff --staged
```

Confirmar que apenas `templates/cdd/hooks/commit-msg` e `tests/test_commit_msg_guard.py` estão staged. Os hooks em `.git/hooks/` são locais e não aparecem no status.

**Step 3: Commit**

```powershell
git add templates/cdd/hooks/commit-msg tests/test_commit_msg_guard.py
git commit -m "feat(main-guard): block direct commits to main/master in commit-msg hook

Add _check_main_guard() to commit-msg hook to prevent direct commits on
main/master. Escape hatch via footer 'Allow-Main: true' for legitimate
direct merges. Deployed to 4 active repos (Stout, Inova, CDD, NotebookLM).

Allow-Main: true"
```

**Step 4: Confirmar commit**

```powershell
git log --oneline -3
```

Saída esperada: novo commit no topo.
