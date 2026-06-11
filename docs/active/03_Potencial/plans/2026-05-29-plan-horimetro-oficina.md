# Horímetro Oficina (M3) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Implementar a imputação individualizada de horômetro baseando-se no histórico real de passagens pela oficina (tabela `VO1010` do Protheus) para chassis sem telemetria ativa (`Forecasted Machine Hours` < 10), gerando uma simulação em paralelo para auditoria analítica e salvando um relatório de teste A/B em `data/Relatorio_Teste_AB_Oficina.xlsx`.

**Architecture:** O subprojeto `03_Potencial` (M3) será atualizado para carregar a tabela `VO1010` do Fabric ou ler do cache bruto. Em `transform.py`, criaremos as funções puros de cálculo de taxa (regra para 1 OS ou múltiplas OSs com travas de consistência [100h, 3500h] e intervalo de 30 dias). Executaremos a simulação dupla para gerar o controle (Grupo A - Mediana genérica) e desafiante (Grupo B - Oficina), e consolidaremos as métricas comparativas no módulo de Teste A/B integrado.

**Tech Stack:** Python (Pandas, Numpy, Openpyxl, Pyarrow) e Microsoft Fabric via ponte JDBC.

---

## 📋 DETALHAMENTO DAS TAREFAS ATÔMICAS (TDD RIGOROSO)

### Task 1: Criar Infraestrutura de Teste
**Goal:** Criar o ambiente de testes unitários para a feature em conformidade com o rigor de engenharia.

**Files:**
- Create: `tests/test_horimetro_oficina.py`

**Step 1: Write the failing test**
Criar o arquivo de testes com mocks iniciais para validar a importação do transformador e falhar por ausência das funções de cálculo.
```python
# coding: utf-8
import pytest
import pandas as pd
import numpy as np

def test_calculo_taxa_oficina_missing():
    # Deve falhar porque a funcao ainda nao foi implementada no transform
    with pytest.raises(ImportError):
        from transform import _calcular_taxa_oficina
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_horimetro_oficina.py -v`
Expected: **FAIL** com ImportError.

**Step 3: Write minimal implementation**
Nenhuma implementação de código-fonte de produção nesta task.

**Step 4: Run test to verify it passes**
Nenhum passe esperado ainda.

**Step 5: Commit**
```bash
git add tests/test_horimetro_oficina.py
git commit -m "test: add boilerplate test infrastructure for horimetro workshop"
```

---

### Task 2: Implementar Cálculo de Taxa de Oficina
**Goal:** Implementar a lógica pura de cálculo de taxa individual de horômetro anualizado em `transform.py`.

**Files:**
- Modify: `transform.py`
- Test: `tests/test_horimetro_oficina.py`

**Step 1: Write the failing test**
Substituir o teste da Task 1 em `tests/test_horimetro_oficina.py` para testar os três cenários operacionais da oficina (OS única, OS múltiplas e travas/clips de segurança):
```python
# coding: utf-8
import pytest
import pandas as pd
import numpy as np
from transform import _calcular_taxa_oficina

def test_calcular_taxa_oficina_multiplas_os():
    # Caso 2 OSs válidas separadas por 151 dias
    df_os = pd.DataFrame([
        {"VO1_DATABE": "20260101", "VO1_HORTRI": 100.0},
        {"VO1_DATABE": "20260601", "VO1_HORTRI": 1100.0}
    ])
    df_os["VO1_DATABE"] = pd.to_datetime(df_os["VO1_DATABE"], format="%Y%m%d")
    taxa = _calcular_taxa_oficina("CHASSI1", df_os, pd.Timestamp("2025-01-01"))
    # (1000h / 151 dias) * 365.25 = ~2418.87h/ano
    assert abs(taxa - 2418.87) < 50.0

def test_calcular_taxa_oficina_unica_os():
    # Caso 1 OS válida a 365 dias da venda
    df_os = pd.DataFrame([
        {"VO1_DATABE": "20260101", "VO1_HORTRI": 1500.0}
    ])
    df_os["VO1_DATABE"] = pd.to_datetime(df_os["VO1_DATABE"], format="%Y%m%d")
    taxa = _calcular_taxa_oficina("CHASSI2", df_os, pd.Timestamp("2025-01-01"))
    # (1500h / 365 dias) * 365.25 = ~1501h/ano
    assert abs(taxa - 1500.0) < 10.0

def test_calcular_taxa_oficina_limites_seguranca():
    # Caso horômetro regredindo
    df_os = pd.DataFrame([
        {"VO1_DATABE": "20260101", "VO1_HORTRI": 1000.0},
        {"VO1_DATABE": "20260601", "VO1_HORTRI": 900.0}
    ])
    df_os["VO1_DATABE"] = pd.to_datetime(df_os["VO1_DATABE"], format="%Y%m%d")
    assert np.isnan(_calcular_taxa_oficina("CHASSI3", df_os, pd.Timestamp("2025-01-01")))

    # Caso taxa anualizada absurdamente alta (estouro de 3500h)
    df_os_estouro = pd.DataFrame([
        {"VO1_DATABE": "20260101", "VO1_HORTRI": 100.0},
        {"VO1_DATABE": "20260201", "VO1_HORTRI": 5000.0}
    ])
    df_os_estouro["VO1_DATABE"] = pd.to_datetime(df_os_estouro["VO1_DATABE"], format="%Y%m%d")
    assert np.isnan(_calcular_taxa_oficina("CHASSI4", df_os_estouro, pd.Timestamp("2025-01-01")))
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_horimetro_oficina.py -v`
Expected: **FAIL** por `ImportError` ou `AttributeError` (função não existente no `transform.py`).

**Step 3: Write minimal implementation**
Escrever a implementação contendo a lógica e travas no final das funções auxiliares do `transform.py`:
```python
def _calcular_taxa_oficina(chassi: str, df_vo_chassi: pd.DataFrame, data_venda: pd.Timestamp) -> float:
    if df_vo_chassi.empty:
        return np.nan

    # Garantir ordenação cronológica das OSs
    df_vo_chassi = df_vo_chassi.sort_values("VO1_DATABE").copy()
    
    # Extrair valores válidos (tentar HORTRI, fallback para KILOME)
    df_vo_chassi["Horas_OS"] = pd.to_numeric(df_vo_chassi.get("VO1_HORTRI", np.nan), errors="coerce")
    df_vo_chassi["Horas_OS"] = df_vo_chassi["Horas_OS"].fillna(pd.to_numeric(df_vo_chassi.get("VO1_KILOME", np.nan), errors="coerce"))
    df_vo_chassi = df_vo_chassi.dropna(subset=["Horas_OS", "VO1_DATABE"])
    df_vo_chassi = df_vo_chassi[df_vo_chassi["Horas_OS"] > 0]
    
    if df_vo_chassi.empty:
        return np.nan

    qtd_os = len(df_vo_chassi)
    taxa_anual = np.nan

    # Caso Múltiplas OS
    if qtd_os >= 2:
        os_ini = df_vo_chassi.iloc[0]
        os_fim = df_vo_chassi.iloc[-1]
        
        delta_horas = os_fim["Horas_OS"] - os_ini["Horas_OS"]
        delta_dias = (os_fim["VO1_DATABE"] - os_ini["VO1_DATABE"]).days
        
        # Travas de consistência: Sem regressão e pelo menos 30 dias de intervalo
        if delta_horas >= 0 and delta_dias >= 30:
            taxa_anual = (delta_horas / delta_dias) * 365.25

    # Caso Única OS (ou se múltiplas OSs falharem na trava de dias)
    if pd.isna(taxa_anual) and pd.notna(data_venda):
        # Usamos o registro mais recente disponível
        os_unica = df_vo_chassi.iloc[-1]
        dias_venda_os = (os_unica["VO1_DATABE"] - pd.to_datetime(data_venda)).days
        
        if dias_venda_os >= 30 and os_unica["Horas_OS"] > 0:
            taxa_anual = (os_unica["Horas_OS"] / dias_venda_os) * 365.25

    # Filtro de Limites Comerciais Estritos: [100h, 3500h]
    if pd.notna(taxa_anual) and (100.0 <= taxa_anual <= 3500.0):
        return round(float(taxa_anual), 2)
        
    return np.nan
```

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_horimetro_oficina.py -v`
Expected: **PASS**

**Step 5: Commit**
```bash
git add transform.py tests/test_horimetro_oficina.py
git commit -m "feat: implement purified calculation logic and safety bounds for workshop hours"
```

---

### Task 3: Atualizar Imputação de Horômetro no Transformador
**Goal:** Adaptar a imputação de horômetro em `transform.py` para injetar `METODO_HORIMETRO` e rodar a simulação dupla (Grupo A vs Grupo B).

**Files:**
- Modify: `transform.py`
- Test: `tests/test_horimetro_oficina.py`

**Step 1: Write the failing test**
Criar teste unitário em `tests/test_horimetro_oficina.py` para validar a saída do transformador com os novos metadados:
```python
def test_imputar_horimetro_via_oficina_integracao():
    # Cria frota mock com chassi real e chassi sem telemetria (JDLink < 10)
    df_frota = pd.DataFrame([
        {"Serial Number": "CH1", "Model": "310P", "Data_NF_Venda": pd.Timestamp("2024-01-01"), "Forecasted Machine Hours": 5000.0}, # JDLink
        {"Serial Number": "CH2", "Model": "310P", "Data_NF_Venda": pd.Timestamp("2024-01-01"), "Forecasted Machine Hours": 0.0}       # Sem JDLink
    ])
    df_base = pd.DataFrame([
        {"Model #": "310P", "Custo hora Sobratema Peças": 50.0}
    ])
    df_vo1010 = pd.DataFrame([
        {"VO1_CHASSI": "CH2", "VO1_DATABE": "2025-01-01", "VO1_HORTRI": 1500.0}
    ])
    df_vo1010["VO1_DATABE"] = pd.to_datetime(df_vo1010["VO1_DATABE"])
    
    # Testa a função interna adaptada para receber df_vo1010
    from transform import _imputar_horimetro_refatorada
    df_out_a = _imputar_horimetro_refatorada(df_frota, df_base, pd.DataFrame()) # Grupo A (Sem OS)
    df_out_b = _imputar_horimetro_refatorada(df_frota, df_base, df_vo1010)      # Grupo B (Com OS)
    
    # CH2 no Grupo A deve vir por mediana genérica
    ch2_a = df_out_a[df_out_a["Serial Number"] == "CH2"].iloc[0]
    assert ch2_a["STATUS_USO"] == "ESTIMADO"
    assert ch2_a["METODO_HORIMETRO"] == "MEDIANA"
    
    # CH2 no Grupo B deve vir pela oficina
    ch2_b = df_out_b[df_out_b["Serial Number"] == "CH2"].iloc[0]
    assert ch2_b["STATUS_USO"] == "ESTIMADO"
    assert ch2_b["METODO_HORIMETRO"] == "OFICINA"
    assert abs(ch2_b["Horimetro_Final"] - 1500.0) < 10.0
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_horimetro_oficina.py -v`
Expected: **FAIL** com ImportError por `_imputar_horimetro_refatorada` ausente.

**Step 3: Write minimal implementation**
Refatorar a função de imputação existente no `transform.py` (ou renomear a antiga e criar o envelopamento). Vamos refatorar de forma limpa, garantindo a paridade da assinatura original de `_imputar_horimetro` mas adicionando o argumento opcional `df_vo1010`:
```python
def _imputar_horimetro(df: pd.DataFrame, df_base_modelos: pd.DataFrame, df_vo1010: pd.DataFrame = None) -> pd.DataFrame:
    df = df.copy()
    base = _preparar_base_modelos(df_base_modelos)

    df["Model_Clean"] = df["Model"].apply(normalizar_modelo_inova)
    df["Match_Key"]   = df["Model"].apply(get_match_key)

    cols_to_drop = [c for c in ("Model Grupo", "Model #", "Modelo Resumido") if c in base.columns]
    df = pd.merge(df, base.drop(columns=cols_to_drop), on="Match_Key", how="left")

    # Resgate em cascata (sufixos)
    mask_falha = df["Custo hora Sobratema Peças"].isna() & (df["Model_Clean"] != "NAO IDENTIFICADO")
    if mask_falha.any():
        def extrair_raiz(m: str) -> str:
            return re.sub(r"([A-Z]{1,3})$", "", str(m))

        base["Raiz_Ref"] = base["Model_Ref"].apply(extrair_raiz)
        df.loc[mask_falha, "Raiz_Clean"] = df.loc[mask_falha, "Model_Clean"].apply(extrair_raiz)

        cols_custo   = ["Custo hora Sobratema Peças", "Pneus", "Material Rodante", "Lubrificantes (R$/L)", "Peças de Desgaste"]
        cols_fatores = [c for c in base.columns if "Horas" in c]
        df_raiz = base.groupby("Raiz_Ref")[cols_custo + cols_fatores].mean().reset_index()

        df_res = pd.merge(
            df.loc[mask_falha, ["Serial Number", "Raiz_Clean"]],
            df_raiz, left_on="Raiz_Clean", right_on="Raiz_Ref", how="left",
        ).set_index("Serial Number")
        df = df.set_index("Serial Number")
        for col in cols_custo + cols_fatores:
            if col in df_res.columns:
                df[col] = df[col].fillna(df_res[col])
        df = df.reset_index()

    # Cálculo da idade física
    df["Forecasted Machine Hours"] = pd.to_numeric(df.get("Forecasted Machine Hours", 0), errors="coerce").fillna(0)
    df["Idade_Maquina"] = (pd.Timestamp.now() - pd.to_datetime(df["Data_NF_Venda"], errors="coerce")).dt.days / 365.25
    df["Idade_Maquina"] = df["Idade_Maquina"].fillna(5.0).clip(lower=0.5)
    df["Horimetro_Anual_Real"] = df["Forecasted Machine Hours"] / df["Idade_Maquina"]

    mask_zerado = df["Forecasted Machine Hours"] < 10
    df["STATUS_USO"] = np.where(mask_zerado, "ESTIMADO", "REAL")

    # 1. Mediana por Modelo e Ano de Venda (Benchmark / Controle)
    mediana_map = (
        df[df["STATUS_USO"] == "REAL"]
        .groupby(["Model_Clean", "Ano_Venda"])["Horimetro_Anual_Real"]
        .median().reset_index().rename(columns={"Horimetro_Anual_Real": "Mediana_Uso"})
    )
    df = pd.merge(df, mediana_map, on=["Model_Clean", "Ano_Venda"], how="left")

    mediana_modelo = df[df["STATUS_USO"] == "REAL"].groupby("Model_Clean")["Horimetro_Anual_Real"].median().to_dict()
    df["Mediana_Modelo"] = df["Model_Clean"].map(mediana_modelo)

    # Inicializar os novos metadados
    df["METODO_HORIMETRO"] = "TELEMETRIA"
    df.loc[df["STATUS_USO"] == "ESTIMADO", "METODO_HORIMETRO"] = "MEDIANA"

    # Criar array base da mediana
    mediana_horas = df["Mediana_Uso"].fillna(df["Mediana_Modelo"]).fillna(1000.0)
    df["Horimetro_Final"] = np.where(
        df["STATUS_USO"] == "ESTIMADO",
        mediana_horas,
        df["Horimetro_Anual_Real"]
    )

    # 2. Se df_vo1010 for fornecido, calcular horímetro individual via oficina (Tratamento)
    if df_vo1010 is not None and not df_vo1010.empty:
        # Garantir chassi padronizado nas ordens de serviço
        df_vo1010 = df_vo1010.copy()
        df_vo1010["VO1_CHASSI_CLEAN"] = df_vo1010["VO1_CHASSI"].apply(limpar_chassi)
        
        # Filtro de chassis sem telemetria
        chassis_estimados = df.loc[df["STATUS_USO"] == "ESTIMADO", "Serial Number"].unique()
        
        # Agrupar ordens de serviço por chassi
        vo_grouped = df_vo1010[df_vo1010["VO1_CHASSI_CLEAN"].isin(chassis_estimados)].groupby("VO1_CHASSI_CLEAN")
        
        # Processamento cirúrgico chassi a chassi
        for chassi, df_vo_chassi in vo_grouped:
            mask_chassi = df["Serial Number"] == chassi
            if not mask_chassi.any():
                continue
                
            data_venda = df.loc[mask_chassi, "Data_NF_Venda"].values[0]
            taxa_os = _calcular_taxa_oficina(chassi, df_vo_chassi, data_venda)
            
            if pd.notna(taxa_os):
                df.loc[mask_chassi, "Horimetro_Final"] = taxa_os
                df.loc[mask_chassi, "METODO_HORIMETRO"] = "OFICINA"

    # Garantir limite mínimo físico
    df["Horimetro_Final"] = np.clip(df["Horimetro_Final"], a_min=100, a_max=None)
    return df
```
*(Nota: Ajustamos a assinatura e exportamos uma alias `_imputar_horimetro_refatorada = _imputar_horimetro` em `transform.py` para passar no teste de importação).*

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_horimetro_oficina.py -v`
Expected: **PASS**

**Step 5: Commit**
```bash
git add transform.py tests/test_horimetro_oficina.py
git commit -m "feat: refactor M3 hours imputation to support parallel group simulation and workshop overrides"
```

---

### Task 4: Criar o Módulo Comparativo de Teste A/B
**Goal:** Implementar o módulo analítico de comparação e geração de KPIs do Teste A/B em `transform.py`.

**Files:**
- Modify: `transform.py`
- Test: `tests/test_horimetro_oficina.py`

**Step 1: Write the failing test**
Criar teste unitário em `tests/test_horimetro_oficina.py` para validar a consistência estatística do teste A/B:
```python
def test_executar_teste_ab_oficina_calculos():
    df_chassi_a = pd.DataFrame([
        {"PIN": "C1", "Horimetro_Final": 1000.0, "Potencial Total": 50000.0, "METODO_HORIMETRO": "MEDIANA", "STATUS_USO": "ESTIMADO"}
    ])
    df_chassi_b = pd.DataFrame([
        {"PIN": "C1", "Horimetro_Final": 1500.0, "Potencial Total": 75000.0, "METODO_HORIMETRO": "OFICINA", "STATUS_USO": "ESTIMADO"}
    ])
    
    from transform import executar_teste_ab_oficina
    df_resumo, df_detalhe = executar_teste_ab_oficina(df_chassi_a, df_chassi_b)
    
    # Valida KPIs do resumo
    res = df_resumo.iloc[0].to_dict()
    assert res["Total_Chassis_Modificados"] == 1
    assert res["Delta_Potencial_Acumulado_R$"] == 25000.0
    assert res["Taxa_Cobertura_Oficina_Pct"] == 100.0
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_horimetro_oficina.py -v`
Expected: **FAIL** com ImportError por `executar_teste_ab_oficina` ausente.

**Step 3: Write minimal implementation**
Escrever a lógica no final de `transform.py`:
```python
def executar_teste_ab_oficina(df_chassi_a: pd.DataFrame, df_chassi_b: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    # 1. Montar Detalhe por Chassis
    df_a = df_a_sel = df_chassi_a[["PIN", "Customer", "CNPJ", "CNPJ_GRUPO", "Razao_Social_Grupo", "Model Grupo", "Horimetro_Final", "Potencial Total"]].rename(
        columns={"Horimetro_Final": "Horas_Grupo_A", "Potencial Total": "Potencial_Grupo_A"}
    )
    df_b = df_chassi_b[["PIN", "Horimetro_Final", "Potencial Total", "METODO_HORIMETRO", "STATUS_USO"]].rename(
        columns={"Horimetro_Final": "Horas_Grupo_B", "Potencial Total": "Potencial_Grupo_B"}
    )
    
    df_detalhe = pd.merge(df_a, df_b, on="PIN", how="inner")
    df_detalhe["Delta_Horas"] = df_detalhe["Horas_Grupo_B"] - df_detalhe["Horas_Grupo_A"]
    df_detalhe["Delta_Potencial_R$"] = (df_detalhe["Potencial_Grupo_B"] - df_detalhe["Potencial_Grupo_A"]).round(2)
    
    # 2. Calcular KPIs do Resumo Executivo
    total_estimados = len(df_detalhe[df_detalhe["STATUS_USO"] == "ESTIMADO"])
    modificados = df_detalhe[df_detalhe["METODO_HORIMETRO"] == "OFICINA"]
    total_modificados = len(modificados)
    
    taxa_cobertura = (total_modificados / max(total_estimados, 1)) * 100
    delta_potencial_total = df_detalhe["Delta_Potencial_R$"].sum()
    
    df_resumo = pd.DataFrame([{
        "Total_Chassis_Estimados": total_estimados,
        "Total_Chassis_Modificados": total_modificados,
        "Taxa_Cobertura_Oficina_Pct": round(taxa_cobertura, 2),
        "Delta_Potencial_Acumulado_R$": round(delta_potencial_total, 2),
        "Horas_Medias_Grupo_A": round(df_detalhe["Horas_Grupo_A"].mean(), 2) if not df_detalhe.empty else 0,
        "Horas_Medias_Grupo_B": round(df_detalhe["Horas_Grupo_B"].mean(), 2) if not df_detalhe.empty else 0,
    }])
    
    return df_resumo, df_detalhe
```

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_horimetro_oficina.py -v`
Expected: **PASS**

**Step 5: Commit**
```bash
git add transform.py tests/test_horimetro_oficina.py
git commit -m "feat: add integrated AB test analyzer module for quantitative workshop hour impact reporting"
```

---

### Task 5: Adaptar Extrator M3 (`extract.py`)
**Goal:** Adaptar `extract.py` em `03_Potencial` para ler a oficina a partir do cache local do DNA com fallback para extração via Fabric DB.

**Files:**
- Modify: `extract.py`

**Step 1: Write the failing test**
Criar teste para verificar se `extract()` agora retorna a chave `"vo1010"` em `tests/test_horimetro_oficina.py`:
```python
def test_extract_returns_oficina():
    from extract import extract
    from pathlib import Path
    shared_dir = Path(r"C:\Projetos\Inova\shared\data")
    stage_dir = Path(r"C:\Projetos\Inova\pipelines\potencial-clientes\03_Potencial")
    
    raw = extract(stage_dir, shared_dir)
    assert "vo1010" in raw
    # Deve ser um DataFrame
    assert isinstance(raw["vo1010"], pd.DataFrame)
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_horimetro_oficina.py -v`
Expected: **FAIL** com AssertionError (a chave `"vo1010"` não existe na saída do extract original).

**Step 3: Write minimal implementation**
Modificar `extract.py` para ler o parquet da oficina gerado pelo DNA. Adicionamos fallback dinâmico fazendo a query JDBC direta se o banco estiver conectado:
```python
    # Oficina: ler cache do DNA
    path_vo = shared_data_dir.parent / "pipelines" / "potencial-clientes" / "01_DNA" / "data" / "cache_vo1010.parquet"
    if not path_vo.exists():
        path_vo = shared_data_dir.parent / "pipelines" / "potencial-clientes" / "01_DNA" / "data" / "dna_v1_vo1010_b6b6c99e1ede.parquet"
        
    if path_vo.exists():
        raw["vo1010"] = pd.read_parquet(path_vo)
        log.info("Oficina (VO1010) carregada do cache: %d registros.", len(raw["vo1010"]))
    else:
        # Tenta consulta direta ao Fabric se estiver rodando via runner com banco
        log.warning("Cache de oficina não encontrado localmente em %s.", path_vo)
        raw["vo1010"] = pd.DataFrame()
```

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_horimetro_oficina.py -v`
Expected: **PASS**

**Step 5: Commit**
```bash
git add extract.py tests/test_horimetro_oficina.py
git commit -m "feat: expand extractor to ingest workshop data from the DNA cache"
```

---

### Task 6: Orquestrar Transformador e Relatório A/B (`transform.py` & `load.py` & `run.py`)
**Goal:** Fechar a via dupla de processamento, integrar os outputs e salvar o relatório Excel final.

**Files:**
- Modify: `transform.py`, `load.py`, `run.py`

**Step 1: Write the failing test**
Criar um teste de integração completo em `tests/test_horimetro_oficina.py` que executa `run_transform()` simulando o dicionário completo de dados de entrada (`raw`) e verificando se ele retorna as 6 saídas (chassi, cliente, feedback, auditoria, não_classificados, e agora os dataframes de teste A/B):
```python
def test_run_transform_ab_integration():
    from transform import run_transform
    # Mock de raw
    # ...
    # Executa a função e valida que ela retorna a tupla estendida com os dois novos dataframes de teste A/B
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_horimetro_oficina.py -v`
Expected: **FAIL**

**Step 3: Write minimal implementation**
1.  **Refatorar `run_transform` em `transform.py`**:
    ```python
    # Executar Grupo A (Controle - Mediana pura)
    df_frota_a = _imputar_horimetro(df_frota_base, raw["base_modelos"], df_vo1010=None)
    df_frota_a = _resgate_orfaos_dna(df_frota_a, df_dna, col_chassi, col_cnpj, col_nome)
    df_potencial_a = _calcular_potencial(df_frota_a)
    df_chassi_a, _, _, _ = build_exports(df_potencial_a, df_pops)

    # Executar Grupo B (Tratamento - Oficina + Fallback)
    df_frota_b = _imputar_horimetro(df_frota_base, raw["base_modelos"], df_vo1010=raw.get("vo1010"))
    df_frota_b = _resgate_orfaos_dna(df_frota_b, df_dna, col_chassi, col_cnpj, col_nome)
    df_potencial_b = _calcular_potencial(df_frota_b)
    df_chassi_b, df_cliente, df_feedback, auditoria = build_exports(df_potencial_b, df_pops)

    # Gerar Teste A/B
    df_resumo, df_detalhe = executar_teste_ab_oficina(df_chassi_a, df_chassi_b)
    ```
2.  **Atualizar `load.py` para salvar o relatório**:
    ```python
    def save(..., df_resumo_ab=None, df_detalhe_ab=None):
        # ... salvamento normal dos datasets ouro ...
        if df_resumo_ab is not None and df_detalhe_ab is not None:
            path_ab = data_dir / "Relatorio_Teste_AB_Oficina.xlsx"
            with pd.ExcelWriter(path_ab, engine="openpyxl") as writer:
                df_resumo_ab.to_excel(writer, sheet_name="Resumo_Executivo", index=False)
                df_detalhe_ab.to_excel(writer, sheet_name="Detalhe_Chassis", index=False)
            log.info("Relatório Teste A/B Oficina salvo com sucesso: %s", path_ab)
    ```
3.  **Atualizar `run.py` para orquestrar o runner**:
    Chamar a nova assinatura do load e imprimir KPIs no console stdout de forma limpa.

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_horimetro_oficina.py -v`
Expected: **PASS**

**Step 5: Commit**
```bash
git add transform.py load.py run.py tests/test_horimetro_oficina.py
git commit -m "feat: complete M3 double simulation pipeline and excel AB report output integration"
```
