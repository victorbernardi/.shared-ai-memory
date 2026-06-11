# Validação de Recência Temporal no Motor CEVAP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Implement the same robust and decoupled recency validation as in BUP for the Motor CEVAP engine, showing visible warnings/tables at startup and including proper TDD coverage.

**Architecture:** We will add the `check_recency_report` function in `consolidate_cevap.py` (parsing the shared markdown status file `recency_status.md`) and trigger it at initialization of the motor. We will also implement a dedicated unit test suite using pytest to ensure high-fidelity verification under TDD guidelines.

**Tech Stack:** Python 3.x, pandas, pytest

---

### Task 1: Implement `check_recency_report` function in `consolidate_cevap.py`

**Files:**
- Create: `c:\Projetos\Inova\projects\motor-cevap\Motor CEVAP\tests\test_cevap_recency_alert.py`
- Modify: `c:\Projetos\Inova\projects\motor-cevap\Motor CEVAP\scripts\consolidate_cevap.py`

**Step 1: Write the failing test**
Create `c:\Projetos\Inova\projects\motor-cevap\Motor CEVAP\tests\test_cevap_recency_alert.py` with basic assertions for `check_recency_report`.

```python
import pytest
from pathlib import Path
import sys
import os

# Adiciona scripts ao path
scripts_dir = Path(__file__).parents[1] / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from consolidate_cevap import check_recency_report

def test_check_recency_report_no_file(tmp_path, monkeypatch):
    # Mock do _shared_dir para apontar para um diretório temporário sem o markdown
    monkeypatch.setattr("consolidate_cevap._shared_dir", tmp_path)
    outdated = check_recency_report()
    assert outdated == []
```

**Step 2: Run test to verify it fails**
Run: `pytest "c:\Projetos\Inova\projects\motor-cevap\Motor CEVAP\tests\test_cevap_recency_alert.py"`
Expected: FAIL (ImportError or AttributeException because `check_recency_report` is not defined in `consolidate_cevap.py`).

**Step 3: Write minimal implementation**
Inject `check_recency_report` at the beginning of `consolidate_cevap.py` (e.g., right after global variables).

```python
def check_recency_report():
    """Lê o relatório recency_status.md do shared e alerta se houver fontes desatualizadas."""
    recency_file = _shared_dir / "recency_status.md"
    outdated = []
    
    if not recency_file.exists():
        print(f"INFO: Relatório de recência não encontrado em {recency_file}. Pulando validação.")
        return outdated
        
    try:
        with recency_file.open("r", encoding="utf-8") as f:
            lines = f.readlines()
            
        table_started = False
        table_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("|"):
                table_lines.append(stripped)
                if "Status de Recência" in stripped:
                    table_started = True
                    continue
                if table_started and not any(x in stripped for x in [":---", "---:"]):
                    parts = [p.strip() for p in stripped.split("|")]
                    if len(parts) >= 4:
                        fonte = parts[1]
                        status = parts[3]
                        if "🟡 Desatualizado" in status or "🔴 Ausente" in status:
                            outdated.append(fonte)
                            
        if outdated:
            print("\n" + "=" * 80)
            print("⚠️  ALERTA DE GOVERNANÇA: HÁ FONTES DESATUALIZADAS OU AUSENTES!")
            print("=" * 80)
            print("As seguintes fontes analíticas estão obsoletas e requerem atenção:")
            for f in outdated:
                print(f"  - 🔴 {f}")
            print("\nConsulte a tabela de recência abaixo para detalhes:")
            print("-" * 80)
            for t_line in table_lines:
                print(t_line)
            print("=" * 80)
            print("AVISO: Prosseguindo com a consolidação do Motor CEVAP...\n")
        else:
            print("\n🟢 SUCESSO: Todas as fontes de dados de ingestão estão atualizadas!\n")
            
    except Exception as e:
        print(f"AVISO: Erro ao analisar o relatório de recência: {e}")
        
    return outdated
```

**Step 4: Run test to verify it passes**
Run: `pytest "c:\Projetos\Inova\projects\motor-cevap\Motor CEVAP\tests\test_cevap_recency_alert.py"`
Expected: PASS

**Step 5: Commit**
Run: `git add scripts/consolidate_cevap.py tests/test_cevap_recency_alert.py`
Run: `git commit -m "feat: add check_recency_report to consolidate_cevap"`

---

### Task 2: Integrate `check_recency_report` inside `run_consolidation`

**Files:**
- Modify: `c:\Projetos\Inova\projects\motor-cevap\Motor CEVAP\scripts\consolidate_cevap.py`
- Test: `c:\Projetos\Inova\projects\motor-cevap\Motor CEVAP\tests\test_cevap_recency_alert.py`

**Step 1: Write the failing test**
Add a test asserting that `check_recency_report` is called upon starting `run_consolidation` in `test_cevap_recency_alert.py`.

```python
def test_recency_validation_in_consolidation(monkeypatch):
    called = False
    def mock_check():
        nonlocal called
        called = True
        return []
    
    monkeypatch.setattr("consolidate_cevap.check_recency_report", mock_check)
    # Mock das cargas para evitar acessar o Fabric/Parquet reais durantes testes unitários
    monkeypatch.setattr("os.path.exists", lambda x: False)
    
    from consolidate_cevap import run_consolidation
    run_consolidation()
    
    assert called is True
```

**Step 2: Run test to verify it fails**
Run: `pytest "c:\Projetos\Inova\projects\motor-cevap\Motor CEVAP\tests\test_cevap_recency_alert.py"`
Expected: FAIL (AssertionError: called is False).

**Step 3: Call `check_recency_report` inside `run_consolidation`**
Modify `run_consolidation` in `consolidate_cevap.py` to invoke `check_recency_report()` right at the start.

```python
def run_consolidation():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    hoje = datetime(2026, 5, 5)
    print(f"--- INICIANDO CONSOLIDAÇÃO MOTOR CEVAP (Sessão: {timestamp}) ---")
    
    # Validação de recência física temporal
    check_recency_report()
    
    # 1. CARGA M5 (Base de Segmentação)
    ...
```

**Step 4: Run test to verify it passes**
Run: `pytest "c:\Projetos\Inova\projects\motor-cevap\Motor CEVAP\tests\test_cevap_recency_alert.py"`
Expected: PASS

**Step 5: Commit**
Run: `git add scripts/consolidate_cevap.py tests/test_cevap_recency_alert.py`
Run: `git commit -m "feat: integrate check_recency_report into cevap run_consolidation"`
