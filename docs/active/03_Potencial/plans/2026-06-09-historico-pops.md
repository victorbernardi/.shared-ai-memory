# Histórico Incremental de PoPS Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Implementar o armazenamento histórico e incremental em formato Parquet para as colunas selecionadas da extração do PoPS, registrando no máximo 1 modificação diária por chassi somente quando houver variação de horas ou telemetria.

**Architecture:** O processo será encapsulado em um novo módulo `historical_pops.py`. A cada execução do `00_PoPS_Extractor/run.py`, os dados transformados serão processados pelo novo módulo, comparados com o arquivo de histórico acumulado `00_PoPS_Extractor/data/historical_pops/pops_incremental_history.parquet` (SCD Tipo 2 chassi a chassi) e gravados de forma idempotente.

**Tech Stack:** Python, Pandas, PyArrow, Pytest.

---

### Task 1: Criar a suíte de testes e o esqueleto de histórico

**Files:**
- Create: `C:/Projetos/Inova/pipelines/potencial-clientes/00_PoPS_Extractor/tests/test_historical_pops.py`
- Create: `C:/Projetos/Inova/pipelines/potencial-clientes/00_PoPS_Extractor/src/historical_pops.py`

**Step 1: Write the failing test**
Criar um teste pytest em `tests/test_historical_pops.py` contendo:
- Teste para inicialização de histórico inexistente.
- Teste de não-duplicação se dados forem idênticos.
- Teste de inserção incremental se houver variação no horímetro ou na telemetria.
- Teste de sobreposição de registros com a mesma data (`Snapshot_Date`).

```python
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from historical_pops import update_historical_pops

def test_pops_history_flow(tmp_path):
    history_file = tmp_path / "pops_incremental_history.parquet"
    
    # DataFrame amostra do dia 2026-06-08
    df_day1 = pd.DataFrame([{
        "Serial Number": "CHASSI_X",
        "Forecasted Machine Hours": 1000.0,
        "aorLastLocationDate": "2026-06-08 10:00:00",
        "Dealer Location": "SERRA",
        "Last Serviced": "2026-06-05"
    }])
    
    # 1. Primeira execução: inicializa histórico
    update_historical_pops(df_day1, tmp_path, current_date="2026-06-08")
    assert history_file.exists()
    
    df_hist = pd.read_parquet(history_file)
    assert len(df_hist) == 1
    assert df_hist.iloc[0]["Snapshot_Date"] == "2026-06-08"
    
    # 2. Segunda execução no mesmo dia sem alterações: não duplica
    update_historical_pops(df_day1, tmp_path, current_date="2026-06-08")
    df_hist = pd.read_parquet(history_file)
    assert len(df_hist) == 1
    
    # 3. Execução no dia seguinte sem alterações: não insere nova linha
    update_historical_pops(df_day1, tmp_path, current_date="2026-06-09")
    df_hist = pd.read_parquet(history_file)
    assert len(df_hist) == 1
    
    # 4. Execução no dia seguinte com alteração de horímetro: insere nova linha
    df_day2 = df_day1.copy()
    df_day2["Forecasted Machine Hours"] = 1050.0
    update_historical_pops(df_day2, tmp_path, current_date="2026-06-09")
    df_hist = pd.read_parquet(history_file)
    assert len(df_hist) == 2
    assert df_hist.iloc[1]["Snapshot_Date"] == "2026-06-09"
    assert df_hist.iloc[1]["Forecasted Machine Hours"] == 1050.0
    
    # 5. Execução no mesmo dia com nova alteração (intradia): sobrepõe em vez de duplicar
    df_day2_v2 = df_day2.copy()
    df_day2_v2["Forecasted Machine Hours"] = 1060.0
    update_historical_pops(df_day2_v2, tmp_path, current_date="2026-06-09")
    df_hist = pd.read_parquet(history_file)
    assert len(df_hist) == 2
    assert df_hist.iloc[1]["Snapshot_Date"] == "2026-06-09"
    assert df_hist.iloc[1]["Forecasted Machine Hours"] == 1060.0
```

**Step 2: Run test to verify it fails**
Executar o teste usando pytest no ambiente do `00_PoPS_Extractor`:
`pytest C:/Projetos/Inova/pipelines/potencial-clientes/00_PoPS_Extractor/tests/test_historical_pops.py -v`
*Esperado:* Falhar (ModuleNotFoundError ou ImportError para `historical_pops`).

**Step 3: Write minimal implementation**
Criar a função `update_historical_pops` em `src/historical_pops.py` que execute a lógica de comparação incremental:

```python
import os
import pandas as pd
from pathlib import Path
from datetime import datetime

HISTORICAL_COLS = [
    "Serial Number", "Average Labor Revenue", "Average Parts Revenue",
    "Dealer Account Number", "Dealer Location", "Servicing Location Account",
    "Last Serviced", "Invoice Number", "repairType", "invoiceType",
    "Last Serviced Account", "AOR Indicator", "aorLastLocationDate",
    "aorLastLocationType", "Machine Serviced", "Work Order Hours Reported",
    "Forecasted Machine Hours"
]

def update_historical_pops(df_current: pd.DataFrame, data_dir: Path, current_date: str = None) -> None:
    if current_date is None:
        current_date = datetime.now().strftime("%Y-%m-%d")
        
    data_dir.mkdir(parents=True, exist_ok=True)
    history_file = data_dir / "pops_incremental_history.parquet"
    
    # Filtrar apenas as colunas desejadas do dataframe atual
    cols_to_use = [c for c in HISTORICAL_COLS if c in df_current.columns]
    df_curr_filtered = df_current[cols_to_use].copy()
    df_curr_filtered["Snapshot_Date"] = current_date
    
    # Forçar chassi (Serial Number) a ser string
    if "Serial Number" in df_curr_filtered.columns:
        df_curr_filtered["Serial Number"] = df_curr_filtered["Serial Number"].astype(str).str.strip()
    else:
        return
        
    if not history_file.exists():
        # Inicializa o histórico
        df_curr_filtered.to_parquet(history_file, index=False, compression="snappy")
        return
        
    # Carrega o histórico existente
    df_hist = pd.read_parquet(history_file)
    df_hist["Serial Number"] = df_hist["Serial Number"].astype(str).str.strip()
    
    new_rows = []
    
    for _, row in df_curr_filtered.iterrows():
        chassi = row["Serial Number"]
        
        # Filtrar o histórico para esse chassi específico
        chassi_hist = df_hist[df_hist["Serial Number"] == chassi]
        
        if chassi_hist.empty:
            # Chassi inédito, adicionar direto
            new_rows.append(row)
        else:
            # Pegar o registro mais recente do chassi no histórico
            last_record = chassi_hist.sort_values("Snapshot_Date").iloc[-1]
            
            # Comparar horímetro e telemetria
            curr_hours = row.get("Forecasted Machine Hours")
            hist_hours = last_record.get("Forecasted Machine Hours")
            curr_tele = str(row.get("aorLastLocationDate"))
            hist_tele = str(last_record.get("aorLastLocationDate"))
            
            if curr_hours != hist_hours or curr_tele != hist_tele:
                # Mudou! 
                if last_record["Snapshot_Date"] == current_date:
                    # Sobrescrever o registro de hoje no dataframe histórico existente
                    idx_to_replace = last_record.name # Pega o índice original do pandas
                    for col in cols_to_use:
                        df_hist.at[idx_to_replace, col] = row[col]
                else:
                    new_rows.append(row)
                    
    if new_rows:
        df_new = pd.DataFrame(new_rows)
        df_hist = pd.concat([df_hist, df_new], ignore_index=True)
        
    # Grava de volta no histórico
    df_hist.to_parquet(history_file, index=False, compression="snappy")
```

**Step 4: Run test to verify it passes**
Rodar novamente o teste:
`pytest C:/Projetos/Inova/pipelines/potencial-clientes/00_PoPS_Extractor/tests/test_historical_pops.py -v`
*Esperado:* PASS.

**Step 5: Commit**
```bash
git add C:/Projetos/Inova/pipelines/potencial-clientes/00_PoPS_Extractor/tests/test_historical_pops.py C:/Projetos/Inova/pipelines/potencial-clientes/00_PoPS_Extractor/src/historical_pops.py
git commit -m "feat: add incremental historical tracking for PoPS chassis"
```

---

### Task 2: Integrar o histórico no Runner principal (run.py)

**Files:**
- Modify: `C:/Projetos/Inova/pipelines/potencial-clientes/00_PoPS_Extractor/run.py`

**Step 1: Write the failing test**
Adicionar em `tests/test_pops_governance.py` a validação de que `update_historical_pops` é acionada durante a execução principal de `run.main()`.

```python
# Modificar test_pops_governance.py para interceptar e validar a chamada de histórico
```

**Step 2: Run test to verify it fails**
Executar a suíte de testes de governança:
`pytest C:/Projetos/Inova/pipelines/potencial-clientes/00_PoPS_Extractor/tests/test_pops_governance.py -v`
*Esperado:* Falhar pois o método de histórico não está integrado no `run.py`.

**Step 3: Write minimal implementation**
Modificar `C:/Projetos/Inova/pipelines/potencial-clientes/00_PoPS_Extractor/run.py` para importar e acionar a atualização de histórico após salvar a extração atual.

```python
# Em run.py:
# Importar o novo módulo
from historical_pops import update_historical_pops

# No final de main():
    # 3. Load
    log.info("[3/3] Salvando Product_details_full...")
    stats = save(df, SHARED_DATA, DATA_DIR)
    
    # Histórico Incremental
    log.info("[Bônus] Atualizando banco de histórico incremental do PoPS...")
    historical_dir = DATA_DIR / "historical_pops"
    update_historical_pops(df, historical_dir)
```

**Step 4: Run test to verify it passes**
Rodar os testes:
`pytest C:/Projetos/Inova/pipelines/potencial-clientes/00_PoPS_Extractor/tests/test_pops_governance.py -v`
*Esperado:* PASS.

**Step 5: Commit**
```bash
git add C:/Projetos/Inova/pipelines/potencial-clientes/00_PoPS_Extractor/run.py
git commit -m "feat: integrate update_historical_pops into main run execution"
```

---

### Task 3: Configurar diretório de dados histórico e higiene física (.gitignore)

**Files:**
- Create: `C:/Projetos/Inova/pipelines/potencial-clientes/00_PoPS_Extractor/data/historical_pops/.gitignore`

**Step 1: Write failing test**
Criar um teste simples para garantir que a pasta do histórico possua o arquivo `.gitignore` ignorando todos os arquivos parquet locais.

```python
def test_gitignore_historical_exists():
    path = Path("C:/Projetos/Inova/pipelines/potencial-clientes/00_PoPS_Extractor/data/historical_pops/.gitignore")
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "*.parquet" in content
```

**Step 2: Run test to verify it fails**
Executar teste:
`pytest C:/Projetos/Inova/pipelines/potencial-clientes/00_PoPS_Extractor/tests/test_historical_pops.py::test_gitignore_historical_exists`
*Esperado:* FAIL.

**Step 3: Write minimal implementation**
Escrever `.gitignore` em `C:/Projetos/Inova/pipelines/potencial-clientes/00_PoPS_Extractor/data/historical_pops/.gitignore`:

```text
# Ignorar arquivos parquet de dados no git público
*.parquet
```

**Step 4: Run test to verify it passes**
Rodar teste:
`pytest C:/Projetos/Inova/pipelines/potencial-clientes/00_PoPS_Extractor/tests/test_historical_pops.py::test_gitignore_historical_exists`
*Esperado:* PASS.

**Step 5: Commit**
```bash
git add C:/Projetos/Inova/pipelines/potencial-clientes/00_PoPS_Extractor/data/historical_pops/.gitignore
git commit -m "chore: add gitignore for historical pops parquet files"
```
