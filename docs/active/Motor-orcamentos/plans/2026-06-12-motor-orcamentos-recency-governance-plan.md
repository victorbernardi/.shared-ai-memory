# Motor Orçamentos Recency Governance Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Integrar o Motor de Orçamentos (08_Motor_Orcamentos) à malha de governança de recência do ecossistema Inova (Pre-flight sensor e Post-flight actuador) e incluí-lo na esteira de orquestração do ligar_motores.py.

**Architecture:** Adicionar o Pre-flight e Post-flight check ao run.py do Motor-orçamentos. Atualizar o script de recência shared/generate_recency_report.py para ler os arquivos gerados automaticamente em vez de tabelas manuais. Adicionar o Motor de Orçamentos ao ligar_motores.py.

**Tech Stack:** Python 3.10+, subprocess, pathlib, pytest.

---

### Task 1: Update Global Recency Report (TDD)

**Files:**
- Modify: `C:\Projetos\Inova\shared\generate_recency_report.py`
- Create: `C:\Projetos\Inova\pipelines\potencial-clientes\Motor-orçamentos\tests\test_governance.py`

**Step 1: Write the failing test**
Create `C:\Projetos\Inova\pipelines\potencial-clientes\Motor-orçamentos\tests\test_governance.py`.
```python
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

def test_generate_report_motor_orcamentos_paths():
    shared_dir = Path(__file__).parents[3] / "shared"
    sys.path.insert(0, str(shared_dir))
    
    import generate_recency_report
    # We inspect the code text directly since the dict is local to the function
    script_text = (shared_dir / "generate_recency_report.py").read_text(encoding="utf-8")
    
    # Assert paths pointing to Motor-orçamentos/data/output instead of shared_data
    assert '"Motor-orçamentos"' in script_text
    assert '"orcamentos_abertos_enriquecidos.xlsx"' in script_text
    assert '"tabela_orçamentos_cancelados.xlsx"' in script_text
    
    # Assert manual is False for both
    # We can test by calling generate_report or checking source config indirectly if exposed,
    # but inspecting code is safer since the dictionary is local to generate_report().
```

**Step 2: Run test to verify it fails**
Run command in power shell (virtual env of pipeline or python):
`pytest C:\Projetos\Inova\pipelines\potencial-clientes\Motor-orçamentos\tests\test_governance.py -k test_generate_report_motor_orcamentos_paths -v`
Expected: FAIL (or Import/AttributeError)

**Step 3: Implement minimal code**
Modify `C:\Projetos\Inova\shared\generate_recency_report.py` sources dictionary:
```python
        "Orçamentos Abertos": {
            "path": shared_dir.parent / "pipelines" / "potencial-clientes" / "Motor-orçamentos" / "data" / "output" / "orcamentos_abertos_enriquecidos.xlsx",
            "manual": False,
            "display": "orcamentos_abertos_enriquecidos.xlsx"
        },
        "Orçamentos Cancelados": {
            "path": shared_dir.parent / "pipelines" / "potencial-clientes" / "Motor-orçamentos" / "data" / "output" / "tabela_orçamentos_cancelados.xlsx",
            "manual": False,
            "display": "tabela_orçamentos_cancelados.xlsx"
        },
```

**Step 4: Run test to verify it passes**
Run: `pytest C:\Projetos\Inova\pipelines\potencial-clientes\Motor-orçamentos\tests\test_governance.py -k test_generate_report_motor_orcamentos_paths -v`
Expected: PASS

**Step 5: Commit**
```bash
git add C:\Projetos\Inova\shared\generate_recency_report.py C:\Projetos\Inova\pipelines\potencial-clientes\Motor-orçamentos\tests\test_governance.py
git commit -m "feat(shared): update recency report to point to motor-orcamentos outputs"
```

---

### Task 2: Integrate Pre-flight and Post-flight into Motor-orçamentos/run.py (TDD)

**Files:**
- Modify: `C:\Projetos\Inova\pipelines\potencial-clientes\Motor-orçamentos\run.py`
- Modify: `C:\Projetos\Inova\pipelines\potencial-clientes\Motor-orçamentos\tests\test_governance.py`

**Step 1: Write the failing test for Pre/Post-flight in run.py**
Add to `C:\Projetos\Inova\pipelines\potencial-clientes\Motor-orçamentos\tests\test_governance.py`:
```python
from unittest.mock import patch, MagicMock

def test_motor_orcamentos_pre_postflight_invocation():
    project_root = Path(__file__).parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    import run
    
    mock_df = MagicMock()
    mock_df.empty = False
    
    with patch("run.subprocess.run") as mock_subprocess_run, \
         patch("run.extrair_orcamentos_abertos", return_value=mock_df), \
         patch("run.limpar_orcamentos_abertos", return_value=mock_df), \
         patch("run.enriquecer_orcamentos_abertos", return_value=mock_df), \
         patch("run.extrair_orcamentos_cancelados_fabric", return_value=mock_df), \
         patch("run.limpar_orcamentos_cancelados", return_value=mock_df), \
         patch("run.run_preflight") as mock_preflight:
            
        run.main()
        
        # Verify preflight was called
        mock_preflight.assert_called_once()
        
        # Verify generate_recency_report.py was called via subprocess
        args = mock_subprocess_run.call_args[0][0] if mock_subprocess_run.call_args else []
        assert any("generate_recency_report.py" in str(arg) for arg in args)
```

**Step 2: Run test to verify it fails**
Run: `pytest C:\Projetos\Inova\pipelines\potencial-clientes\Motor-orçamentos\tests\test_governance.py -k test_motor_orcamentos_pre_postflight_invocation -v`
Expected: FAIL (AttributeError on run_preflight or fail to assert)

**Step 3: Implement minimal code**
Modify `C:\Projetos\Inova\pipelines\potencial-clientes\Motor-orçamentos\run.py` to:
1. Setup `_shared_dir` and import/wrap `run_preflight`.
2. Call `run_preflight` at the start of `main()`.
3. Call `generate_recency_report.py` at the end of `main()`.

Changes to apply in `run.py`:
```python
# Import at top of run.py
_shared_dir = Path(__file__).resolve().parents[3] / "shared"
if str(_shared_dir) not in sys.path:
    sys.path.insert(0, str(_shared_dir))

from governance_sensor import run_preflight
```

Modify `main()` inside `run.py`:
```python
def main():
    print("===== PIPELINE DE EXTRAÇÃO DE ORÇAMENTOS =====")
    
    # 0. Pre-flight Governance Check
    print("\n[0/2] Iniciando Pre-flight Governance Check...")
    run_preflight(str(_shared_dir), fail_fast=False)
    
    # Definindo período padrão (Janeiro de 2025 até hoje)
    data_inicio = datetime(2025, 1, 1)
    data_fim = datetime.now()
    
    # ... (rest of extraction logic) ...
    
    # Post-flight: Atualizando Relatório de Recência
    print("\nPost-flight: Atualizando Relatório de Recência...")
    import subprocess
    report_script = _shared_dir / "generate_recency_report.py"
    subprocess.run([sys.executable, str(report_script)], check=False)
```

**Step 4: Run test to verify it passes**
Run: `pytest C:\Projetos\Inova\pipelines\potencial-clientes\Motor-orçamentos\tests\test_governance.py -v`
Expected: PASS

**Step 5: Commit**
```bash
git add C:\Projetos\Inova\pipelines\potencial-clientes\Motor-orçamentos\run.py C:\Projetos\Inova\pipelines\potencial-clientes\Motor-orçamentos\tests\test_governance.py
git commit -m "feat(motor-orcamentos): integrate pre-flight and post-flight governance checks"
```

---

### Task 3: Integrate into Pipeline Orchestrator (ligar_motores.py)

**Files:**
- Modify: `C:\Projetos\Inova\pipelines\potencial-clientes\ligar_motores.py`

**Step 1: Modify ligar_motores.py**
Add the Motor de Orçamentos to the list of `motores` at the end of the chain.
```python
        ("08 - Motor Orçamentos", rf"{base}\Motor-orçamentos\run.py"),
```

**Step 2: Dry Run / Manual Verification**
Ensure that running `ligar_motores.py` triggers the Motor de Orçamentos without syntax errors.

**Step 3: Commit**
```bash
git add C:\Projetos\Inova\pipelines\potencial-clientes\ligar_motores.py
git commit -m "feat(pipeline): add motor-orcamentos to ligar_motores.py execution list"
```
