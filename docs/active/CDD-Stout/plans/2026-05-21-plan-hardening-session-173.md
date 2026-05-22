# Hardening CDD — Plano de Implementação (Session 173)

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Corrigir 6 fragilidades do motor CDD que o failure-log provou causarem falhas reais.

**Architecture:** Mudanças cirúrgicas e aditivas — skipif em testes, os.getenv com fallback no launcher, try/except ImportError nas ferramentas, atualização YAML no catálogo, remoção de 4 skills casca vazia, sync de templates.

**Tech Stack:** Python 3.10+, pytest, PyYAML, PowerShell (mklink)

**Spec:** `docs/specs/2026-05-21-spec-hardening-session-173.md`

---

### Task 1: Adicionar skipif condicional em test_guardrail_v2.py

**Files:**
- Modify: `tests/test_guardrail_v2.py:1-10` (adicionar import + flag)
- Modify: `tests/test_guardrail_v2.py:40-50` (decorar test_powershell_guard_blocks_existing)

**Step 1: Adicionar shutil.which e flag no topo**

Adicionar após `import subprocess`:
```python
import shutil

_HAS_POWERSHELL = shutil.which("powershell.exe") is not None
```

**Step 2: Decorar o único teste que depende de powershell.exe**

No `test_powershell_guard_blocks_existing`, adicionar decorator:
```python
@pytest.mark.skipif(not _HAS_POWERSHELL, reason="powershell.exe não disponível no PATH")
def test_powershell_guard_blocks_existing(temp_file):
```

**Step 3: Rodar testes**

```bash
pytest tests/test_guardrail_v2.py -v
```
Expected: 6 passed, 1 skipped (se powershell indisponível) ou 7 passed.

**Step 4: Commit**

```bash
git add tests/test_guardrail_v2.py
git commit -m "test: add skipif for powershell dependency in test_guardrail_v2"
```

---

### Task 2: Adicionar skipif condicional em test_e2e_integration.py

**Files:**
- Modify: `tests/test_e2e_integration.py:1-10`

**Step 1: Verificar dependências externas**

O arquivo faz patch de GitGuard e usa mocks — nenhuma dependência de binário externo. Adicionar `import shutil` como boa prática.

**Step 2: Rodar testes**

```bash
pytest tests/test_e2e_integration.py -v
```
Expected: 7 passed.

**Step 3: Commit**

```bash
git add tests/test_e2e_integration.py
git commit -m "test: verify no external deps needed in test_e2e_integration"
```

---

### Task 3: Corrigir path frágil no launcher.py

**Files:**
- Modify: `skills/stout-cdd-orchestrator/scripts/launcher.py:8-11` (constantes de path)
- Modify: `skills/stout-cdd-orchestrator/scripts/launcher.py:51` (uso do path frágil)

**Step 1: Adicionar import os se ausente**

**Step 2: Substituir a constante CDD_PROJECT_SKILLS_DIR**

```python
CDD_PROJECT_SKILLS_DIR = Path(os.getenv("STOUT_SKILLS_PATH", STOUT_ORCHESTRATOR_DIR.parent))
```

**Step 3: Substituir o path frágil na linha 51**

```python
skill_base_path = Path(os.getenv("STOUT_GLOBAL_SKILLS_PATH", str(CDD_PROJECT_SKILLS_DIR.parent.parent)))
```

**Step 4: Testar o launcher**

```bash
python skills/stout-cdd-orchestrator/scripts/launcher.py --skill stout-immunity-gate
```

**Step 5: Commit**

```bash
git add skills/stout-cdd-orchestrator/scripts/launcher.py
git commit -m "fix: replace brittle path with env var fallback in launcher"
```

---

### Task 4: Remover 4 skills casca vazia + limpar referências no rules.yaml e registry.json

**Files:**
- Remove: `skills/cdd_technical_skill/`
- Remove: `skills/self_healing_skill/`
- Remove: `skills/stout_knowledge_fallback/`
- Remove: `skills/welcome_skill/`
- Modify: `data/config/rules.yaml` (remover 4 regras órfãs)
- Modify: `skills/stout-skill-registry/registry.json` (remover 4 entradas)
- Modify: `data/config/skills_catalog.yaml` (sincronizar com skills restantes)

**Step 1: Remover as pastas**

```powershell
cmd /c "rmdir /s /q skills\cdd_technical_skill"
cmd /c "rmdir /s /q skills\self_healing_skill"
cmd /c "rmdir /s /q skills\stout_knowledge_fallback"
cmd /c "rmdir /s /q skills\welcome_skill"
```

**Step 2: Remover as 4 regras órfãs do rules.yaml**

Remover as regras: `self_healing_rule`, `welcome_rule`, `cdd_technical_rule`, `fallback_knowledge_rule`.

**Step 3: Remover as 4 entradas do registry.json**

Remover entradas: `stout-knowledge-fallback`, `stout-cdd-technical`, `stout-self-healing`, `stout-welcome`.

**Step 4: Sincronizar skills_catalog.yaml**

Rodar `python scripts/audit_skills.py` e adicionar skills faltantes (as 6 restantes que não são cascas vazias).

**Step 5: Validar consistência**

```bash
python scripts/audit_skills.py
```
Expected: 20 skills no diretório, 20 no catálogo, 0 diffs.

**Step 6: Commit**

```bash
git add skills/ data/config/rules.yaml skills/stout-skill-registry/registry.json data/config/skills_catalog.yaml
git commit -m "chore: remove 4 empty shell skills and orphan references"
```

---

### Task 5: Sincronizar skills_catalog.yaml com skills/

**Files:**
- Modify: `data/config/skills_catalog.yaml`

**Step 1: Rodar auditoria**
**Step 2: Adicionar skills faltantes (padrão YAML do catálogo)**
**Step 3: Validar contra schema**
**Step 4: Re-rodar auditoria — 0 diffs**
**Step 5: Commit**

---

### Task 6: Adicionar import guard nas ferramentas de governança

**Files:**
- Modify: `src/tools/sentinel_agent.py:1-8`
- Modify: `src/tools/rule_simulator.py:1-20`

**Step 1: sentinel_agent.py — guard para PyYAML**

```python
try:
    import yaml
except ImportError:
    sys.exit("ERRO: PyYAML não instalado. Execute: pip install pyyaml")
```

**Step 2: gcc_analytics.py — já tem guard para plotly/jinja2. OK.**

**Step 3: rule_simulator.py — verificar se src.config carrega**

**Step 4: Smoke test nas 3 ferramentas**

**Step 5: Commit**

```bash
git add src/tools/sentinel_agent.py
git commit -m "fix: add import guard for PyYAML in sentinel_agent"
```

---

### Task 7: Sincronizar stout_promote.py e post_approve.py com templates stout-init

**Files:**
- Overwrite local: `skills/stout-init/addons/cdd/templates/tools/stout_promote.py`
- Overwrite local: `skills/stout-init/addons/cdd/templates/tools/post_approve.py`
- Overwrite global: `%USERPROFILE%\.shared-ai-memory\skills\stout-init\addons\cdd\templates\tools\*.py`

**Step 1: Verificar diffs**

```powershell
cmd /c "fc /b src\tools\stout_promote.py skills\stout-init\addons\cdd\templates\tools\stout_promote.py"
```

**Step 2: Copiar src/tools → templates locais**

**Step 3: Copiar src/tools → templates globais**

**Step 4: Verificar que diffs sumiram**

**Step 5: Commit**

```bash
git add skills/stout-init/addons/cdd/templates/tools/
git commit -m "fix: sync stout_promote and post_approve with stout-init templates"
```

---

### Task 8: Rodar context_manager.py maintain

**Step 1:** `python "%USERPROFILE%\.shared-ai-memory\skills\process-context-agent\scripts\context_manager.py" maintain`

**Step 2:** Verificar ACTIVE_CONTEXT.md limpo

---

## Verificação Final

```bash
pytest tests/ -v
```

Expected: 0 failures, skips apenas para dependências externas indisponíveis.
