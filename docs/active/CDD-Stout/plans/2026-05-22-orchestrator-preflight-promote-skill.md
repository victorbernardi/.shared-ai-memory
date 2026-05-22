# Orchestrator Preflight + Registry promoted_at + stout-promote-skill

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tornar o `stout-cdd-orchestrator` capaz de barrar execuções quando dependências estão ausentes, registrar promoções no registry, e criar a skill `stout-promote-skill` para promover skills do projeto CDD ao golden copy com auditoria e aprovação.

**Architecture:** Um módulo `preflight.py` isolado verifica dependências de primeiro nível antes de qualquer skill ser lançada pelo orchestrator. O `registry.json` ganha o campo `promoted_at` para rastrear quando cada skill foi promovida ao golden copy. A `stout-promote-skill` orquestra `audit_skills.py` + `promote_skills.py` com dry-run e gate de aprovação humana.

**Tech Stack:** Python 3.x, pathlib, json, pytest, scripts existentes `scripts/audit_skills.py` e `scripts/promote_skills.py`

**Ordem obrigatória:** Task 1 → Task 2 → Task 3 → Task 4 → Task 5 (cada uma depende da anterior)

---

## Mapa de Arquivos

| Arquivo | Ação | Responsabilidade |
|---|---|---|
| `skills/stout-cdd-orchestrator/scripts/preflight.py` | Criar | Verificar dependências de primeiro nível de uma skill |
| `skills/stout-cdd-orchestrator/scripts/launcher.py` | Modificar | Chamar preflight antes de lançar qualquer skill |
| `skills/stout-skill-registry/registry.json` | Modificar | Adicionar campo `promoted_at` a cada skill |
| `~/.shared-ai-memory/skills/stout-skill-registry/registry.json` | Modificar | Idem para o golden copy |
| `scripts/promote_skills.py` | Modificar | Atualizar `promoted_at` no registry após promoção |
| `skills/stout-promote-skill/SKILL.md` | Criar | Skill de promoção com fluxo audit → dry-run → approve → promote |
| `skills/stout-promote-skill/scripts/promote_runner.py` | Criar | Orquestra audit + promote com gate interativo |
| `tests/test_preflight.py` | Criar | Testes do módulo preflight |
| `tests/test_promote_runner.py` | Criar | Testes do promote_runner |

**Paths de referência:**

- Raiz projeto CDD: `C:\Projetos\Stout\Projetos\Configuration-Driven Development`
- Registry projeto: `skills/stout-skill-registry/registry.json`
- Registry golden copy: `C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-skill-registry\registry.json`
- Golden copy skills: `C:\Users\victor.bernardi\.shared-ai-memory\skills`

---

## Task 1: Módulo preflight.py

**Files:**

- Create: `skills/stout-cdd-orchestrator/scripts/preflight.py`
- Test: `tests/test_preflight.py`

- [ ] **Step 1: Escrever teste — skill sem dependências passa**

```python
# tests/test_preflight.py
import json
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"
REGISTRY = SKILLS_DIR / "stout-skill-registry" / "registry.json"


def _write_tmp_registry(tmp_path: Path, skills: list) -> Path:
    r = tmp_path / "registry.json"
    r.write_text(json.dumps({"skills": skills}), encoding="utf-8")
    return r


def test_no_dependencies_passes(tmp_path):
    registry = _write_tmp_registry(tmp_path, [
        {"name": "stout-commit", "dependencies": []}
    ])
    skills_dir = tmp_path / "skills"
    (skills_dir / "stout-commit").mkdir(parents=True)

    from skills.stout_cdd_orchestrator.scripts.preflight import check_dependencies
    missing = check_dependencies("stout-commit", registry, skills_dir)
    assert missing == []
```

- [ ] **Step 2: Rodar — esperar ImportError**

```bash
cd "C:\Projetos\Stout\Projetos\Configuration-Driven Development"
python -m pytest tests/test_preflight.py::test_no_dependencies_passes -v
```

Esperado: `ImportError` ou `ModuleNotFoundError`

- [ ] **Step 3: Criar preflight.py**

```python
# skills/stout-cdd-orchestrator/scripts/preflight.py
import json
import sys
from pathlib import Path


def check_dependencies(skill_name: str, registry_path: Path, skills_dir: Path) -> list[str]:
    """Return list of missing first-level dependency names. Empty = all present."""
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    skill = next((s for s in data["skills"] if s["name"] == skill_name), None)
    if skill is None:
        return []
    missing = []
    for dep in skill.get("dependencies") or []:
        if not (skills_dir / dep).exists():
            missing.append(dep)
    return missing


def run_preflight(skill_name: str, registry_path: Path, skills_dir: Path) -> bool:
    """Print missing dependencies and return False if any are missing."""
    missing = check_dependencies(skill_name, registry_path, skills_dir)
    if not missing:
        return True
    print(f"\n[PREFLIGHT FAIL] Skill '{skill_name}' requer dependências não instaladas:")
    for dep in missing:
        print(f"  - {dep}  (instale em skills/{dep}/)")
    print("\nInstale as skills ausentes antes de continuar.")
    return False
```

- [ ] **Step 4: Ajustar import no teste e rodar**

Substituir o import no teste por import direto de arquivo:

```python
import importlib.util, sys

def _load_preflight():
    spec = importlib.util.spec_from_file_location(
        "preflight",
        Path(__file__).parent.parent / "skills/stout-cdd-orchestrator/scripts/preflight.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

preflight = _load_preflight()
```

Substituir `from skills.stout_cdd_orchestrator...` por `preflight.check_dependencies(...)` no teste.

```bash
python -m pytest tests/test_preflight.py::test_no_dependencies_passes -v
```

Esperado: `PASSED`

- [ ] **Step 5: Escrever teste — dependência presente passa**

```python
def test_dependency_present_passes(tmp_path):
    registry = _write_tmp_registry(tmp_path, [
        {"name": "stout-promote-skill", "dependencies": ["stout-skill-auditor"]}
    ])
    skills_dir = tmp_path / "skills"
    (skills_dir / "stout-skill-auditor").mkdir(parents=True)

    preflight = _load_preflight()
    missing = preflight.check_dependencies("stout-promote-skill", registry, skills_dir)
    assert missing == []
```

- [ ] **Step 6: Rodar — esperar PASSED**

```bash
python -m pytest tests/test_preflight.py::test_dependency_present_passes -v
```

- [ ] **Step 7: Escrever teste — dependência ausente retorna nome**

```python
def test_missing_dependency_returned(tmp_path):
    registry = _write_tmp_registry(tmp_path, [
        {"name": "stout-promote-skill", "dependencies": ["stout-skill-auditor"]}
    ])
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir(parents=True)
    # stout-skill-auditor NOT created

    preflight = _load_preflight()
    missing = preflight.check_dependencies("stout-promote-skill", registry, skills_dir)
    assert missing == ["stout-skill-auditor"]
```

- [ ] **Step 8: Rodar — esperar PASSED**

```bash
python -m pytest tests/test_preflight.py -v
```

Esperado: 3 PASSED

- [ ] **Step 9: Commit**

```bash
git add skills/stout-cdd-orchestrator/scripts/preflight.py tests/test_preflight.py
git commit -m "feat: adiciona preflight.py ao orchestrator para verificação de dependências"
```

---

## Task 2: Integrar preflight no launcher.py

**Files:**

- Modify: `skills/stout-cdd-orchestrator/scripts/launcher.py:12-16`

- [ ] **Step 1: Atualizar launcher.py**

Adicionar após as constantes de path (linha 14, após `REGISTRY_PATH = ...`):

```python
SCRIPTS_DIR_LOCAL = Path(__file__).parent
```

Substituir a função `launch_skill` para chamar preflight antes de continuar:

```python
def launch_skill(skill_name: str) -> None:
    # Preflight: verifica dependências antes de qualquer ação
    from preflight import run_preflight
    if not run_preflight(skill_name, REGISTRY_PATH, GLOBAL_SKILLS_DIR):
        sys.exit(1)

    data = load_registry()
    skill = next((s for s in data["skills"] if s["name"] == skill_name), None)

    if not skill:
        print(f"[ERRO] Skill '{skill_name}' não registrada no registry.json.")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  STOUT CDD ORCHESTRATOR V1.3.0 - Ativando: {skill['name']} (Tier {skill['tier']})")
    print(f"{'='*60}\n")

    print(f"[PAPEL] {skill['role']}")
    print(f"\n[GLOBAL_GUARDRAILS]")
    print(KARPATHY_LAWS)

    skill_base_path = Path(os.getenv("STOUT_GLOBAL_SKILLS_PATH", str(GLOBAL_SKILLS_DIR.parent)))
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
```

**Nota:** O import `from preflight import run_preflight` funciona porque `launcher.py` e `preflight.py` estão no mesmo diretório `scripts/`. Adicionar `sys.path.insert(0, str(Path(__file__).parent))` no topo do launcher para garantir isso.

- [ ] **Step 2: Smoke test — skill sem dependências passa normalmente**

```bash
cd "C:\Projetos\Stout\Projetos\Configuration-Driven Development"
python skills/stout-cdd-orchestrator/scripts/launcher.py --skill stout-init 2>&1 | head -5
```

Esperado: `STOUT CDD ORCHESTRATOR V1.3.0 - Ativando: stout-init`

- [ ] **Step 3: Smoke test — skill com dependência ausente é barrada**

Adicionar temporariamente uma dependência inexistente ao `stout-commit` no registry:

```json
"dependencies": ["skill-que-nao-existe"]
```

```bash
python skills/stout-cdd-orchestrator/scripts/launcher.py --skill stout-commit
```

Esperado:

```
[PREFLIGHT FAIL] Skill 'stout-commit' requer dependências não instaladas:
  - skill-que-nao-existe  (instale em skills/skill-que-nao-existe/)
```

Reverter a dependência temporária no registry após o teste.

- [ ] **Step 4: Aplicar mesma mudança ao golden copy**

Copiar `preflight.py` para o golden copy:

```bash
copy "skills\stout-cdd-orchestrator\scripts\preflight.py" "C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-cdd-orchestrator\scripts\preflight.py"
```

Aplicar as mesmas alterações em `C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-cdd-orchestrator\scripts\launcher.py`:

- Adicionar `sys.path.insert(0, str(Path(__file__).parent))`
- Adicionar chamada ao preflight no início de `launch_skill`
- Atualizar versão para `V1.3.0`
- Usar `GLOBAL_SKILLS_DIR` (já renomeado na Task anterior)

- [ ] **Step 5: Commit**

```bash
git add skills/stout-cdd-orchestrator/scripts/launcher.py
git commit -m "feat: integra preflight no launcher do orchestrator"
```

---

## Task 3: Adicionar campo promoted_at ao registry

**Files:**

- Modify: `skills/stout-skill-registry/registry.json`
- Modify: `C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-skill-registry\registry.json`

O campo `promoted_at` é `null` para skills nunca promovidas ou uma string ISO date (`"2026-05-22"`) para skills já no golden copy.

- [ ] **Step 1: Adicionar promoted_at ao registry do projeto CDD**

Para cada skill em `skills/stout-skill-registry/registry.json`, adicionar o campo após `updated_at`:

- Skills que existem no golden copy com conteúdo igual: `"promoted_at": "2026-05-22"`
- Skills que nunca foram promovidas ou divergem: `"promoted_at": null`

Verificar quais existem no golden copy:

```bash
python -c "
from pathlib import Path
import json
proj = Path('skills/stout-skill-registry/registry.json')
golden = Path(r'C:\Users\victor.bernardi\.shared-ai-memory\skills')
data = json.loads(proj.read_text(encoding='utf-8'))
for s in data['skills']:
    exists = (golden / s['name']).exists()
    print(f'{\"EXISTS\" if exists else \"ABSENT\"} | {s[\"name\"]}')
"
```

Adicionar `"promoted_at": "2026-05-22"` às skills que existem no golden copy, `"promoted_at": null` às ausentes.

- [ ] **Step 2: Adicionar promoted_at ao registry do golden copy**

Aplicar o mesmo campo em `C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-skill-registry\registry.json`.

Para skills ativas no golden copy: `"promoted_at": "2026-05-22"`.
Para skills `inactive`: `"promoted_at": null`.

- [ ] **Step 3: Validar JSON**

```bash
python -c "
import json
from pathlib import Path
for path in [
    'skills/stout-skill-registry/registry.json',
    r'C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-skill-registry\registry.json'
]:
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    missing_field = [s['name'] for s in data['skills'] if 'promoted_at' not in s]
    print(f'{path}: missing_field={missing_field or \"nenhum\"}')
"
```

Esperado: `missing_field=nenhum` para ambos.

- [ ] **Step 4: Rodar testes existentes para garantir nenhuma regressão**

```bash
python -m pytest tests/test_orchestrator_paths.py -v
```

Esperado: 4 PASSED

- [ ] **Step 5: Commit**

```bash
git add skills/stout-skill-registry/registry.json
git commit -m "feat: adiciona campo promoted_at ao registry para rastreabilidade de promoções"
```

---

## Task 4: Atualizar promote_skills.py para gravar promoted_at

**Files:**

- Modify: `scripts/promote_skills.py:51-76`

- [ ] **Step 1: Adicionar função que atualiza promoted_at no registry**

Adicionar após a função `promote_skill` em `scripts/promote_skills.py`:

```python
def update_promoted_at(skill_name: str, registry_path: Path) -> None:
    """Set promoted_at to today in the project registry after a successful promotion."""
    if not registry_path.exists():
        return
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    for skill in data["skills"]:
        if skill["name"] == skill_name:
            skill["promoted_at"] = str(date.today())
            break
    registry_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
```

- [ ] **Step 2: Chamar update_promoted_at após promoção bem-sucedida**

Substituir o bloco `if not dry_run: shutil.copytree(...)` na função `promote_skill`:

```python
    actions.append(f"COPY {skill_name} -> Golden Copy")
    if not dry_run:
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        registry_path = SKILLS_ROOT.parent / "skills" / "stout-skill-registry" / "registry.json"
        update_promoted_at(skill_name, registry_path)

    return {"skill": skill_name, "status": "PROMOTED", "actions": actions}
```

- [ ] **Step 3: Smoke test manual em dry-run (sem alteração real)**

```bash
python scripts/promote_skills.py --dry-run 2>&1 | head -20
```

Esperado: lista de skills com `PROMOTED (dry-run)`, sem erros.

- [ ] **Step 4: Commit**

```bash
git add scripts/promote_skills.py
git commit -m "feat: promote_skills.py atualiza promoted_at no registry após promoção"
```

---

## Task 5: Criar stout-promote-skill

**Files:**

- Create: `skills/stout-promote-skill/SKILL.md`
- Create: `skills/stout-promote-skill/scripts/promote_runner.py`
- Test: `tests/test_promote_runner.py`

- [ ] **Step 1: Escrever teste — promote_runner detecta skills prontas para promoção**

```python
# tests/test_promote_runner.py
import json
import importlib.util
from pathlib import Path
from datetime import date

PROJECT_ROOT = Path(__file__).parent.parent


def _load_runner():
    spec = importlib.util.spec_from_file_location(
        "promote_runner",
        PROJECT_ROOT / "skills/stout-promote-skill/scripts/promote_runner.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_detects_never_promoted_skill(tmp_path):
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({"skills": [
        {"name": "stout-init", "status": "active", "promoted_at": None}
    ]}), encoding="utf-8")
    runner = _load_runner()
    pending = runner.get_pending_promotions(registry)
    assert "stout-init" in pending


def test_ignores_already_promoted_skill(tmp_path):
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({"skills": [
        {"name": "stout-init", "status": "active", "promoted_at": str(date.today())}
    ]}), encoding="utf-8")
    runner = _load_runner()
    pending = runner.get_pending_promotions(registry)
    assert "stout-init" not in pending


def test_ignores_inactive_skill(tmp_path):
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({"skills": [
        {"name": "stout-welcome", "status": "inactive", "promoted_at": None}
    ]}), encoding="utf-8")
    runner = _load_runner()
    pending = runner.get_pending_promotions(registry)
    assert "stout-welcome" not in pending
```

- [ ] **Step 2: Rodar — esperar ImportError**

```bash
python -m pytest tests/test_promote_runner.py -v
```

Esperado: `ModuleNotFoundError`

- [ ] **Step 3: Criar estrutura de diretórios**

```bash
mkdir "skills\stout-promote-skill"
mkdir "skills\stout-promote-skill\scripts"
```

- [ ] **Step 4: Criar promote_runner.py**

```python
# skills/stout-promote-skill/scripts/promote_runner.py
"""Runner interativo para promoção de skills CDD ao golden copy."""
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = PROJECT_ROOT / "skills" / "stout-skill-registry" / "registry.json"
AUDIT_SCRIPT = PROJECT_ROOT / "scripts" / "audit_skills.py"
PROMOTE_SCRIPT = PROJECT_ROOT / "scripts" / "promote_skills.py"


def get_pending_promotions(registry_path: Path) -> list[str]:
    """Return names of active skills with promoted_at == null."""
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    return [
        s["name"]
        for s in data["skills"]
        if s.get("status") == "active" and s.get("promoted_at") is None
    ]


def run_audit() -> dict[str, str]:
    """Run audit_skills.py and return {skill_name: status} from latest report."""
    result = subprocess.run(
        [sys.executable, str(AUDIT_SCRIPT)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("[ERRO] Falha ao rodar audit_skills.py:")
        print(result.stderr)
        sys.exit(1)

    from pathlib import Path as P
    import re
    audit_dir = PROJECT_ROOT / "docs" / "audits"
    reports = sorted(audit_dir.glob("skill-audit-*.json"))
    if not reports:
        print("[ERRO] Nenhum relatório de auditoria encontrado.")
        sys.exit(1)
    data = json.loads(reports[-1].read_text(encoding="utf-8"))
    return {r["skill"]: r["status"] for r in data["results"]}


def main() -> None:
    print("\n=== STOUT PROMOTE SKILL ===\n")

    # 1. Verificar dependências
    if not AUDIT_SCRIPT.exists():
        print(f"[ERRO] audit_skills.py não encontrado em: {AUDIT_SCRIPT}")
        sys.exit(1)
    if not PROMOTE_SCRIPT.exists():
        print(f"[ERRO] promote_skills.py não encontrado em: {PROMOTE_SCRIPT}")
        sys.exit(1)

    # 2. Rodar auditoria
    print("[1/4] Rodando auditoria de skills...")
    audit = run_audit()

    # 3. Identificar pendentes
    pending = get_pending_promotions(REGISTRY_PATH)
    ready = [s for s in pending if audit.get(s) == "PASS"]
    not_ready = [s for s in pending if audit.get(s) != "PASS"]

    print(f"\nSkills pendentes de promoção: {len(pending)}")
    if ready:
        print(f"\n  PRONTAS (audit PASS):")
        for s in ready:
            print(f"    [OK] {s}")
    if not_ready:
        print(f"\n  NÃO PRONTAS (audit FAIL/ausente):")
        for s in not_ready:
            print(f"    [--] {s}  (status: {audit.get(s, 'não auditada')})")

    if not ready:
        print("\nNenhuma skill pronta para promoção.")
        sys.exit(0)

    # 4. Escolha do usuário
    print("\nDigite o nome da skill a promover (ou 'todas' para promover todas prontas):")
    choice = input("> ").strip()

    if choice == "todas":
        to_promote = ready
    elif choice in ready:
        to_promote = [choice]
    else:
        print(f"[ERRO] '{choice}' não está na lista de skills prontas.")
        sys.exit(1)

    # 5. Dry-run
    print(f"\n[2/4] Dry-run para: {', '.join(to_promote)}")
    result = subprocess.run(
        [sys.executable, str(PROMOTE_SCRIPT), "--dry-run"],
        capture_output=True, text=True
    )
    print(result.stdout)

    # 6. Confirmação
    print("\n[3/4] Confirmar promoção? (s/N)")
    confirm = input("> ").strip().lower()
    if confirm != "s":
        print("Promoção cancelada.")
        sys.exit(0)

    # 7. Promoção real
    print("\n[4/4] Promovendo skills...")
    result = subprocess.run(
        [sys.executable, str(PROMOTE_SCRIPT)],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print("[ERRO]", result.stderr)
        sys.exit(1)

    print("\n[OK] Promoção concluída. Campo promoted_at atualizado no registry.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Rodar testes**

```bash
python -m pytest tests/test_promote_runner.py -v
```

Esperado: 3 PASSED

- [ ] **Step 6: Criar SKILL.md**

```markdown
---
name: stout-promote-skill
description: "Promove skills desenvolvidas no projeto CDD para o golden copy (~/.shared-ai-memory/skills/). Executa auditoria, exibe pendências, dry-run e gate de aprovação humana antes de copiar. Triggers: promover skill, promote skill, publicar skill, enviar para global."
version: 1.0.0
author: Victor
tier: 2
source: custom
date_added: "2026-05-22"
category: meta-governance
---

# stout-promote-skill

## Responsabilidade única

Promover skills do projeto CDD ao golden copy com auditoria, rastreabilidade e aprovação humana obrigatória.

## Quando Usar

- Quando uma skill foi desenvolvida e testada no projeto CDD e está pronta para ser usada globalmente.
- Para verificar quais skills estão pendentes de promoção (promoted_at == null e audit PASS).

## Pré-Requisitos

- `scripts/audit_skills.py` presente no projeto
- `scripts/promote_skills.py` presente no projeto
- Campo `promoted_at` no `skills/stout-skill-registry/registry.json`

## Como Usar

```bash
python skills/stout-promote-skill/scripts/promote_runner.py
```

## Fluxo

1. Roda `audit_skills.py` — gera relatório de qualidade
2. Exibe skills com `promoted_at = null` e audit PASS (prontas) vs FAIL (não prontas)
3. Usuário escolhe qual skill (ou todas) promover
4. Dry-run com preview do que será copiado
5. Confirmação humana obrigatória
6. Executa `promote_skills.py` e atualiza `promoted_at` no registry

## Escopo

Aplica-se apenas ao projeto CDD e projetos que sigam o padrão Stout com `registry.json` e scripts de audit/promote.

## Critérios de Conclusão

A skill é concluída quando `promote_runner.py` encerra com código 0 e o campo `promoted_at` da skill promovida está atualizado no `registry.json`.

```

- [ ] **Step 7: Registrar skill no registry do projeto**

Adicionar ao array `skills` em `skills/stout-skill-registry/registry.json`:

```json
{
  "name": "stout-promote-skill",
  "path": "skills/stout-promote-skill",
  "tier": 2,
  "category": "meta-governance",
  "role": "Promover skills do projeto CDD para o golden copy com auditoria e aprovação",
  "triggers": ["promover skill", "promote skill", "publicar skill", "enviar para global"],
  "dependencies": ["stout-skill-auditor"],
  "version": "1.0.0",
  "status": "active",
  "promoted_at": null,
  "created_at": "2026-05-22",
  "updated_at": "2026-05-22",
  "author": "Victor",
  "notes": "Nova skill — pendente de primeira promoção."
}
```

- [ ] **Step 8: Rodar todos os testes**

```bash
python -m pytest tests/ -v
```

Esperado: todos PASSED

- [ ] **Step 9: Commit**

```bash
git add skills/stout-promote-skill/ skills/stout-skill-registry/registry.json tests/test_promote_runner.py
git commit -m "feat: cria stout-promote-skill com runner interativo e gate de aprovação"
```

---

## Self-Review

**Cobertura:**

- ✅ preflight.py com testes (Task 1)
- ✅ launcher.py integrado ao preflight (Task 2)
- ✅ campo promoted_at no registry (Task 3)
- ✅ promote_skills.py grava promoted_at (Task 4)
- ✅ stout-promote-skill com runner + SKILL.md + registro no registry (Task 5)

**Gaps identificados:**

- O golden copy do `launcher.py` precisa da mesma mudança da Task 2 — coberto no Step 4 da Task 2.
- O `promote_runner.py` usa `input()` — os testes não cobrem o fluxo interativo (intencionalmente, YAGNI).
- Skills `inactive` são ignoradas pelo runner — comportamento correto, não é gap.
