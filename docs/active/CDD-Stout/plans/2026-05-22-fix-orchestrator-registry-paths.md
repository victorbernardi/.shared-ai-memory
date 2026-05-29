# Fix Orchestrator & Registry Paths — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corrigir os paths legados no `launcher.py` e `registry.json` do `stout-cdd-orchestrator` em dois contextos independentes (Projeto CDD e Golden Copy), garantindo que o orchestrator encontre as skills corretamente em cada ambiente.

**Architecture:** O orchestrator existe como cópia física independente em dois locais. O `launcher.py` usa `Path(__file__)` para calcular paths relativos — quando invocado no projeto CDD, resolve para `skills/` local; quando invocado via golden copy, resolve para `~/.shared-ai-memory/skills/`. Cada cópia precisa de um `registry.json` com paths compatíveis com seu contexto. O `launcher.py` já suporta override via `STOUT_SKILLS_PATH` e `STOUT_GLOBAL_SKILLS_PATH` — a correção é nos fallbacks hardcoded.

**Tech Stack:** Python 3.x, pathlib, json, pytest

---

## Mapa de Arquivos

| Arquivo | Ação | Contexto |
|---|---|---|
| `skills/stout-cdd-orchestrator/scripts/launcher.py` | Modificar | Projeto CDD |
| `skills/stout-skill-registry/registry.json` | Modificar | Projeto CDD |
| `~/.shared-ai-memory/skills/stout-cdd-orchestrator/scripts/launcher.py` | Modificar | Golden Copy |
| `~/.shared-ai-memory/skills/stout-skill-registry/registry.json` | Modificar | Golden Copy |
| `tests/test_orchestrator_paths.py` | Criar | Projeto CDD |

**Paths de referência:**

- Raiz projeto CDD: `C:\Projetos\Stout\Projetos\Configuration-Driven Development`
- Skills projeto CDD: `C:\Projetos\Stout\Projetos\Configuration-Driven Development\skills`
- Skills golden copy: `C:\Users\victor.bernardi\.shared-ai-memory\skills`

---

## Task 1: Testes para o launcher do Projeto CDD

**Files:**

- Create: `tests/test_orchestrator_paths.py`

- [ ] **Step 1: Escrever os testes de comportamento**

```python
# tests/test_orchestrator_paths.py
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
LAUNCHER = PROJECT_ROOT / "skills" / "stout-cdd-orchestrator" / "scripts" / "launcher.py"
REGISTRY = PROJECT_ROOT / "skills" / "stout-skill-registry" / "registry.json"
SKILLS_DIR = PROJECT_ROOT / "skills"

def _load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))

def test_registry_exists():
    assert REGISTRY.exists(), f"registry.json não encontrado em {REGISTRY}"

def test_all_registry_paths_exist():
    data = _load_registry()
    missing = []
    for skill in data["skills"]:
        skill_md = PROJECT_ROOT / skill["path"] / "SKILL.md"
        if not skill_md.exists():
            missing.append(f"{skill['name']} -> {skill['path']}")
    assert not missing, "Skills com path inválido no registry:\n" + "\n".join(missing)

def test_launcher_resolves_skills_dir(monkeypatch, tmp_path):
    """Garante que CDD_PROJECT_SKILLS_DIR aponta para skills/ do projeto."""
    monkeypatch.delenv("STOUT_SKILLS_PATH", raising=False)

    spec = {}
    exec(LAUNCHER.read_text(encoding="utf-8"), spec)

    # Quando sem env var, o fallback deve ser o pai do launcher (skills/)
    # O path calculado deve conter 'skills' e existir
    # Verificamos indiretamente: registry deve ser encontrável
    registry_via_launcher = spec.get("REGISTRY_PATH") or (
        Path(spec["CDD_PROJECT_SKILLS_DIR"]) / "stout-skill-registry" / "registry.json"
    )
    assert Path(str(registry_via_launcher)).exists()

def test_launcher_skill_base_path_finds_skill_md(monkeypatch):
    """Garante que skill_base_path leva ao SKILL.md de uma skill existente."""
    monkeypatch.delenv("STOUT_GLOBAL_SKILLS_PATH", raising=False)
    monkeypatch.delenv("STOUT_SKILLS_PATH", raising=False)

    data = _load_registry()
    first_skill = next(s for s in data["skills"] if (PROJECT_ROOT / s["path"] / "SKILL.md").exists())

    # Simula o que launch_skill faz para calcular skill_path
    # Após a correção, skill_base_path deve ser SKILLS_DIR
    # e skill_path = SKILLS_DIR / first_skill["path"] / "SKILL.md"
    # O path no registry após correção será "skills/X", então:
    skill_md = SKILLS_DIR / first_skill["path"] / "SKILL.md"
    assert skill_md.exists(), f"SKILL.md não encontrado via path do registry: {skill_md}"
```text

- [ ] **Step 2: Rodar os testes — esperar falha**

```bash
cd "C:\Projetos\Stout\Projetos\Configuration-Driven Development"
python -m pytest tests/test_orchestrator_paths.py -v
```text

Saída esperada: `FAILED test_all_registry_paths_exist` e `FAILED test_launcher_skill_base_path_finds_skill_md` (paths legados)

---

## Task 2: Corrigir registry.json do Projeto CDD

**Files:**

- Modify: `skills/stout-skill-registry/registry.json`

Substituir todos os paths `skills/cdd-project-skills/X` por `skills/X`.
Skills ausentes fisicamente (`stout-governance-orchestration-engine`) devem ter `"status": "inactive"`.

- [ ] **Step 1: Aplicar a correção**

Substituir o conteúdo do campo `"skills"` do arquivo `skills/stout-skill-registry/registry.json`.
Para cada entry, alterar:

| De | Para |
|---|---|
| `"skills/cdd-project-skills/stout-skill-registry"` | `"skills/stout-skill-registry"` |
| `"skills/cdd-project-skills/stout-skill-auditor"` | `"skills/stout-skill-auditor"` |
| `"skills/cdd-project-skills/stout-improve-skill"` | `"skills/stout-improve-skill"` |
| `"skills/cdd-project-skills/stout-create-skill"` | `"skills/stout-create-skill"` |
| `"skills/cdd-project-skills/stout-immunity-gate"` | `"skills/stout-immunity-gate"` |
| `"skills/cdd-project-skills/stout-dev-tdd"` | `"skills/stout-dev-tdd"` |
| `"skills/cdd-project-skills/stout-brainstorming"` | `"skills/stout-brainstorming"` |
| `"skills/cdd-project-skills/stout-writing-plans"` | `"skills/stout-writing-plans"` |
| `"skills/cdd-project-skills/stout-adr"` | `"skills/stout-adr"` |
| `"skills/cdd-project-skills/stout-systematic-debugging"` | `"skills/stout-systematic-debugging"` |
| `"skills/cdd-project-skills/stout-spec-validation"` | `"skills/stout-spec-validation"` |
| `"skills/cdd-project-skills/stout-init"` | `"skills/stout-init"` |
| `"skills/cdd-project-skills/stout-cdd-orchestrator"` | `"skills/stout-cdd-orchestrator"` |
| `"skills/cdd-project-skills/stout-commit"` | `"skills/stout-commit"` |
| `"governance-orchestration-engine"` | `"skills/stout-governance-orchestration-engine"` + `"status": "inactive"` |

Também atualizar `"last_updated": "2026-05-22"`.

- [ ] **Step 2: Rodar testes para validar**

```bash
python -m pytest tests/test_orchestrator_paths.py::test_registry_exists tests/test_orchestrator_paths.py::test_all_registry_paths_exist -v
```text

Saída esperada: ambos `PASSED`

---

## Task 3: Corrigir launcher.py do Projeto CDD

**Files:**

- Modify: `skills/stout-cdd-orchestrator/scripts/launcher.py`

O problema está em dois fallbacks:

1. `CDD_PROJECT_SKILLS_DIR` — fallback atual: `STOUT_ORCHESTRATOR_DIR.parent` (já correto, é `skills/`)
2. `skill_base_path` — fallback atual: `CDD_PROJECT_SKILLS_DIR.parent.parent` (errado — sobe dois níveis além de `skills/`)

No contexto do projeto CDD, `skill_base_path` deve ser igual a `CDD_PROJECT_SKILLS_DIR`, pois os paths do registry já incluem `skills/X` como path relativo à raiz do projeto. Portanto, `skill_base_path / skill['path']` = `project_root / skills / stout-init` — mas `skill['path']` já começa com `skills/`, criando duplicação.

**Solução correta:** o registry usa paths relativos à raiz do projeto (`skills/X`), então `skill_base_path` deve ser a **raiz do projeto** (pai de `skills/`), não `skills/` em si.

- [ ] **Step 1: Aplicar a correção no launcher.py do projeto CDD**

Alterar a linha 52 de:

```python
skill_base_path = Path(os.getenv("STOUT_GLOBAL_SKILLS_PATH", str(CDD_PROJECT_SKILLS_DIR.parent.parent)))
```text

Para:

```python
skill_base_path = Path(os.getenv("STOUT_GLOBAL_SKILLS_PATH", str(CDD_PROJECT_SKILLS_DIR.parent)))
```text

Isso faz `skill_base_path` = raiz do projeto CDD. Com `skill['path']` = `"skills/stout-init"`, o path final será:
`project_root / skills / stout-init / SKILL.md` ✅

- [ ] **Step 2: Rodar todos os testes**

```bash
python -m pytest tests/test_orchestrator_paths.py -v
```text

Saída esperada: todos `PASSED`

- [ ] **Step 3: Teste de smoke manual**

```bash
python skills/stout-cdd-orchestrator/scripts/launcher.py --skill stout-init
```text

Saída esperada: sem `[AVISO] SKILL.md não encontrado`, exibição das instruções do `stout-init`.

- [ ] **Step 4: Commit**

```bash
git add skills/stout-skill-registry/registry.json skills/stout-cdd-orchestrator/scripts/launcher.py tests/test_orchestrator_paths.py
git commit -m "fix: corrige paths legados no registry e launcher do orchestrator (projeto CDD)"
```text

---

## Task 4: Corrigir registry.json do Golden Copy

**Files:**

- Modify: `C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-skill-registry\registry.json`

No golden copy, os paths devem ser relativos ao home do usuário (`C:\Users\victor.bernardi`).
Skills físicas existem em `~/.shared-ai-memory/skills/X`, portanto o path correto é `.shared-ai-memory/skills/X`.

Skills ausentes no golden copy (`stout-knowledge-fallback`, `stout-cdd-technical`, `stout-self-healing`, `stout-welcome`, `stout-governance-orchestration-engine`) devem ter `"status": "inactive"`.

- [ ] **Step 1: Aplicar a correção**

Para cada entry no golden copy registry, alterar:

| De | Para |
|---|---|
| `"skills/cdd-project-skills/stout-skill-registry"` | `".shared-ai-memory/skills/stout-skill-registry"` |
| `"skills/cdd-project-skills/stout-skill-auditor"` | `".shared-ai-memory/skills/stout-skill-auditor"` |
| `"skills/cdd-project-skills/stout-improve-skill"` | `".shared-ai-memory/skills/stout-improve-skill"` |
| `"skills/cdd-project-skills/stout-create-skill"` | `".shared-ai-memory/skills/stout-create-skill"` |
| `"skills/cdd-project-skills/stout-immunity-gate"` | `".shared-ai-memory/skills/stout-immunity-gate"` |
| `"skills/cdd-project-skills/stout-dev-tdd"` | `".shared-ai-memory/skills/stout-dev-tdd"` |
| `"skills/cdd-project-skills/stout-brainstorming"` | `".shared-ai-memory/skills/stout-brainstorming"` |
| `"skills/cdd-project-skills/stout-writing-plans"` | `".shared-ai-memory/skills/stout-writing-plans"` |
| `"skills/cdd-project-skills/stout-adr"` | `".shared-ai-memory/skills/stout-adr"` |
| `"skills/cdd-project-skills/stout-systematic-debugging"` | `".shared-ai-memory/skills/stout-systematic-debugging"` |
| `"skills/cdd-project-skills/stout-spec-validation"` | `".shared-ai-memory/skills/stout-spec-validation"` |
| `"skills/cdd-project-skills/stout-init"` | `".shared-ai-memory/skills/stout-init"` |
| `"skills/cdd-project-skills/stout-cdd-orchestrator"` | `".shared-ai-memory/skills/stout-cdd-orchestrator"` |
| `"skills/cdd-project-skills/stout-commit"` | `".shared-ai-memory/skills/stout-commit"` |
| `"skills/cdd-project-skills/stout_knowledge_fallback"` | `".shared-ai-memory/skills/stout-knowledge-fallback"` + `"status": "inactive"` |
| `"skills/cdd-project-skills/cdd_technical_skill"` | `".shared-ai-memory/skills/stout-cdd-technical"` + `"status": "inactive"` |
| `"skills/cdd-project-skills/self_healing_skill"` | `".shared-ai-memory/skills/stout-self-healing"` + `"status": "inactive"` |
| `"skills/cdd-project-skills/welcome_skill"` | `".shared-ai-memory/skills/stout-welcome"` + `"status": "inactive"` |
| `"governance-orchestration-engine"` | `".shared-ai-memory/skills/stout-governance-orchestration-engine"` + `"status": "inactive"` |

Atualizar `"last_updated": "2026-05-22"`.

- [ ] **Step 2: Validar com script Python**

```bash
python -c "
import json
from pathlib import Path
home = Path.home()
r = home / '.shared-ai-memory/skills/stout-skill-registry/registry.json'
data = json.loads(r.read_text(encoding='utf-8'))
missing = [(s['name'], s['path']) for s in data['skills'] if s.get('status') != 'inactive' and not (home / s['path'] / 'SKILL.md').exists()]
print('MISS:', missing or 'nenhum')
ok = [(s['name']) for s in data['skills'] if s.get('status') != 'inactive' and (home / s['path'] / 'SKILL.md').exists()]
print('OK:', ok)
"
```text

Saída esperada: `MISS: nenhum` e lista de skills ativas.

---

## Task 5: Corrigir launcher.py do Golden Copy

**Files:**

- Modify: `C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-cdd-orchestrator\scripts\launcher.py`

Sincronizar o golden copy com a versão do projeto CDD (que já tem `os.getenv`) e corrigir o fallback do `skill_base_path`.

No golden copy, `CDD_PROJECT_SKILLS_DIR` = `~/.shared-ai-memory/skills/`.
O registry usa paths como `.shared-ai-memory/skills/X`, relativos ao home.
Portanto `skill_base_path` deve ser o **home do usuário** (`Path.home()`).

- [ ] **Step 1: Aplicar a correção no golden copy**

Substituir o conteúdo completo de `launcher.py` do golden copy por:

```python
import sys
import os
import json
import argparse
import io
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SCRIPTS_DIR = Path(__file__).parent
STOUT_ORCHESTRATOR_DIR = SCRIPTS_DIR.parent
CDD_PROJECT_SKILLS_DIR = Path(os.getenv("STOUT_SKILLS_PATH", str(STOUT_ORCHESTRATOR_DIR.parent)))
REGISTRY_PATH = CDD_PROJECT_SKILLS_DIR / "stout-skill-registry" / "registry.json"

KARPATHY_LAWS = """
[LEI GLOBAL - KARPATHY LAWS]
1. Pense Antes de Codificar: Não assuma interpretações. Explicite trade-offs.
2. Simplicidade Primeiro: Código mínimo necessário. Sem overengineering.
3. Mudanças Cirúrgicas: Toque apenas no necessário. Match existing style.
4. Execução Orientada a Metas: Defina critérios de sucesso e loops (TDD).
"""

def load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        print(f"[ERRO] Registro CDD não encontrado em: {REGISTRY_PATH}")
        sys.exit(1)
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def launch_skill(skill_name: str) -> None:
    data = load_registry()
    skill = next((s for s in data["skills"] if s["name"] == skill_name), None)

    if not skill:
        print(f"[ERRO] Skill '{skill_name}' não registrada no registry.json.")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  STOUT CDD ORCHESTRATOR V1.2.0 - Ativando: {skill['name']} (Tier {skill['tier']})")
    print(f"{'='*60}\n")

    print(f"[PAPEL] {skill['role']}")
    print(f"\n[GLOBAL_GUARDRAILS]")
    print(KARPATHY_LAWS)

    # skill['path'] é relativo ao home: ".shared-ai-memory/skills/X"
    skill_base_path = Path(os.getenv("STOUT_GLOBAL_SKILLS_PATH", str(Path.home())))
    skill_path = skill_base_path / skill['path'] / "SKILL.md"

    if skill_path.exists():
        print(f"\n[SKILL_INSTRUCTIONS] (from {skill['path']}/SKILL.md)")
        with open(skill_path, 'r', encoding='utf-8') as f:
            print(f.read())
    else:
        print(f"\n[AVISO] SKILL.md não encontrado em: {skill_path}")

    if skill.get("triggers"):
        print(f"\n[TRIGGERS]")
        for trigger in skill["triggers"]:
            print(f"  - {trigger}")

    print(f"\n[OK] Skill '{skill_name}' orquestrada com sucesso.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", required=True, help="Nome da skill a ser ativada")
    args = parser.parse_args()
    launch_skill(args.skill)
```text

- [ ] **Step 2: Teste de smoke manual**

```bash
python C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-cdd-orchestrator\scripts\launcher.py --skill stout-init
```text

Saída esperada: exibição das instruções do `stout-init` sem `[AVISO]`.

- [ ] **Step 3: Smoke com uma skill inactive (deve mostrar AVISO, não crash)**

```bash
python C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-cdd-orchestrator\scripts\launcher.py --skill stout-welcome
```text

Saída esperada: `[AVISO] SKILL.md não encontrado` — sem crash, exit 0.

---

## Self-Review

**Cobertura:**

- ✅ Correção do registry.json do projeto CDD (Task 2)
- ✅ Correção do launcher.py do projeto CDD (Task 3)
- ✅ Correção do registry.json do golden copy (Task 4)
- ✅ Correção do launcher.py do golden copy (Task 5)
- ✅ Testes automatizados cobrindo os dois comportamentos críticos (Task 1)

**Gaps identificados:**

- Skills `inactive` no golden copy (`stout-welcome`, `stout-self-healing`, etc.) não têm cobertura de teste — são backlog V6.12, não bloqueiam este fix.
- O `stout-governance-orchestration-engine` não existe fisicamente em nenhum dos dois contextos — marcado como `inactive` em ambos.
