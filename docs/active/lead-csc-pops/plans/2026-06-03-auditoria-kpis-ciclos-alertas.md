# Auditoria KPIs e Arquitetura de Ciclos de Alertas — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use `stout-executing-plans` to implement this plan task-by-task.

**Goal:** Substituir `historico_tratativas.json` por `ciclos_alertas.json`, corrigir os 5 KPIs autossuficientes do Daily Report e eliminar dados fictícios — sem dependência de Fabric (expansão de query e KPIs de orçamento/NF são fase 2).

**Architecture:** Nova camada de persistência em `history.py` com ciclos por chassi+tipo (FPS/Rodante). `transform.py` fecha todos os ciclos do chassi ao processar tratativas. `load.py` calcula 5 KPIs reais de `ciclos_alertas.json` + `df_leads_final`. Nenhum KPI depende do Protheus/Fabric nesta entrega.

**Tech Stack:** Python 3.11, pandas, openpyxl, pytest, JSON, Parquet

**Spec:** `docs/specs/2026-06-03-auditoria-kpis-ciclos-alertas.md` (v2 — escopo reduzido)

**Python:** `C:\Projetos\Inova\.venv\Scripts\python.exe`
**Testes:** `C:\Projetos\Inova\.venv\Scripts\python.exe -m pytest tests/ -v`
**Projeto:** `C:\Projetos\Inova\projects\lead-csc-pops\`

---

## Task 1: Fundação — `ciclos_alertas.json` e funções em `history.py`

**Files:**

- Modify: `src/history.py`
- Modify: `tests/test_history.py`

**Cobre:** RF-01, RF-02 (parcial)

---

**Step 1: Escrever os testes RED**

Adicionar ao final de `tests/test_history.py`:

```python
# --- Testes para ciclos_alertas.json ---
try:
    from src.history import abrir_ciclo, fechar_ciclo, carregar_ciclos
except ImportError:
    def abrir_ciclo(*a, **kw): return []
    def fechar_ciclo(*a, **kw): return []
    def carregar_ciclos(caminho_json=None): return []

def test_carregar_ciclos_vazio(tmp_path):
    caminho = tmp_path / "ciclos.json"
    assert carregar_ciclos(caminho_json=str(caminho)) == []

def test_abrir_ciclo_fps(tmp_path):
    caminho = tmp_path / "ciclos.json"
    ciclos = abrir_ciclo("CHASSI_A", "FPS", 200.0, "Consultor X", caminho_json=str(caminho))
    assert len(ciclos) == 1
    assert ciclos[0]["Chassi"] == "CHASSI_A"
    assert ciclos[0]["Tipo_Alerta"] == "FPS"
    assert ciclos[0]["Horimetro_Inicio"] == 200.0
    assert ciclos[0]["Resultado"] is None
    assert ciclos[0]["Data_Fechamento"] is None
    # Campos de fase 2 reservados como null
    assert ciclos[0]["Valor_Orcamento"] is None
    assert ciclos[0]["Status_Orcamento"] is None

def test_abrir_dois_ciclos_mesmo_chassi(tmp_path):
    caminho = tmp_path / "ciclos.json"
    abrir_ciclo("CHASSI_B", "FPS", 200.0, "Consultor X", caminho_json=str(caminho))
    ciclos = abrir_ciclo("CHASSI_B", "Rodante", 1500.0, "Consultor X", caminho_json=str(caminho))
    assert len([c for c in ciclos if c["Tipo_Alerta"] == "FPS"]) == 1
    assert len([c for c in ciclos if c["Tipo_Alerta"] == "Rodante"]) == 1

def test_abrir_nao_duplica_ciclo_aberto(tmp_path):
    caminho = tmp_path / "ciclos.json"
    abrir_ciclo("CHASSI_X", "FPS", 200.0, "C", caminho_json=str(caminho))
    ciclos = abrir_ciclo("CHASSI_X", "FPS", 210.0, "C", caminho_json=str(caminho))
    abertos = [c for c in ciclos if c["Chassi"] == "CHASSI_X" and c["Resultado"] is None]
    assert len(abertos) == 1  # não abre segundo ciclo FPS se já há um aberto

def test_fechar_ciclo_fecha_todos_do_chassi(tmp_path):
    caminho = tmp_path / "ciclos.json"
    abrir_ciclo("CHASSI_C", "FPS", 200.0, "Consultor X", caminho_json=str(caminho))
    abrir_ciclo("CHASSI_C", "Rodante", 1500.0, "Consultor X", caminho_json=str(caminho))
    ciclos = fechar_ciclo("CHASSI_C", None, "Venda", 1600.0, None, 0.0, caminho_json=str(caminho))
    abertos = [c for c in ciclos if c["Chassi"] == "CHASSI_C" and c["Resultado"] is None]
    assert len(abertos) == 0
    fechados = [c for c in ciclos if c["Chassi"] == "CHASSI_C"]
    assert all(c["Resultado"] == "Venda" and c["Data_Fechamento"] is not None for c in fechados)
```

**Step 2: Rodar para confirmar RED**

```
C:\Projetos\Inova\.venv\Scripts\python.exe -m pytest tests/test_history.py -v -k "ciclo"
```

Esperado: `FAILED` — ImportError ou `AssertionError`.

**Step 3: Implementar em `src/history.py`**

Adicionar ao final, mantendo as funções legadas intactas:

```python
import datetime

CICLOS_PATH_DEFAULT = r"C:\Projetos\Inova\projects\lead-csc-pops\data\output\ciclos_alertas.json"

def carregar_ciclos(caminho_json=None):
    if caminho_json is None:
        caminho_json = CICLOS_PATH_DEFAULT
    path = Path(caminho_json)
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            dados = json.load(f)
            return dados if isinstance(dados, list) else []
    except Exception as e:
        print(f"[WARNING] Falha ao ler ciclos_alertas.json: {e}")
        return []

def _salvar_ciclos(ciclos, caminho_json):
    path = Path(caminho_json)
    os.makedirs(path.parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(ciclos, f, indent=4, ensure_ascii=False)

def _tem_ciclo_aberto(ciclos, chassi, tipo_alerta):
    return any(
        c["Chassi"] == chassi and c["Tipo_Alerta"] == tipo_alerta and c["Resultado"] is None
        for c in ciclos
    )

def abrir_ciclo(chassi, tipo_alerta, horimetro_inicio, consultor, caminho_json=None):
    if caminho_json is None:
        caminho_json = CICLOS_PATH_DEFAULT
    ciclos = carregar_ciclos(caminho_json)
    if _tem_ciclo_aberto(ciclos, chassi, tipo_alerta):
        return ciclos
    ciclos.append({
        "Chassi": chassi,
        "Tipo_Alerta": tipo_alerta,
        "Data_Inicio_Ciclo": datetime.date.today().isoformat(),
        "Horimetro_Inicio": float(horimetro_inicio),
        "Data_Fechamento": None,
        "Horimetro_Fechamento": None,
        "Resultado": None,
        "Consultor": consultor or "",
        "Observacoes": "",
        "Orcamento_Protheus": None,
        "Data_Orcamento": None,
        "Valor_Orcamento": None,
        "Tipo_Resolucao": None,
        "Status_Orcamento": None,
        "Data_Conversao_NF": None,
        "NF_Numero": None,
        "Valor_Faturado": None,
    })
    _salvar_ciclos(ciclos, caminho_json)
    return ciclos

def fechar_ciclo(chassi, tipo_alerta, resultado, horimetro_fechamento, orcamento, valor_orcamento, caminho_json=None):
    """
    Fecha ciclos de um chassi.
    - tipo_alerta=None: fecha TODOS os ciclos abertos do chassi (comportamento desta entrega).
    - tipo_alerta específico: fecha apenas aquele ciclo (reservado para a fase 2).
    """
    if caminho_json is None:
        caminho_json = CICLOS_PATH_DEFAULT
    ciclos = carregar_ciclos(caminho_json)
    hoje = datetime.date.today().isoformat()
    for c in ciclos:
        if c["Chassi"] != chassi or c["Resultado"] is not None:
            continue
        if tipo_alerta is None or c["Tipo_Alerta"] == tipo_alerta:
            c["Resultado"] = resultado
            c["Data_Fechamento"] = hoje
            c["Horimetro_Fechamento"] = float(horimetro_fechamento) if horimetro_fechamento is not None else None
            c["Orcamento_Protheus"] = orcamento
            c["Valor_Orcamento"] = float(valor_orcamento) if valor_orcamento else None
    _salvar_ciclos(ciclos, caminho_json)
    return ciclos
```

**Step 4: Confirmar GREEN + legados**

```
C:\Projetos\Inova\.venv\Scripts\python.exe -m pytest tests/test_history.py -v
```

Esperado: todos `PASSED`.

**Step 5: Commit**

```
git add src/history.py tests/test_history.py
git commit -m "feat(history): adicionar ciclos_alertas.json com abrir/fechar/carregar ciclos"
```

---

## Task 2: Migração dos registros legados

**Files:**

- Create: `scripts/migrar_historico_para_ciclos.py`

**Cobre:** RF-06

---

**Step 1: Criar script de migração**

```python
# scripts/migrar_historico_para_ciclos.py
# -*- coding: utf-8 -*-
"""
Migração única: historico_tratativas.json -> ciclos_alertas.json
Execute uma única vez. Valide a saída antes de deprecar o arquivo original.
"""
import sys, json, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.history import _salvar_ciclos, carregar_ciclos, CICLOS_PATH_DEFAULT

HISTORICO_PATH = r"C:\Projetos\Inova\projects\lead-csc-pops\data\output\historico_tratativas.json"

def inferir_tipo_alerta(gatilho: str) -> str:
    g = str(gatilho).upper()
    if "RODANTE" in g:
        return "Rodante"
    return "FPS"

def migrar():
    src = Path(HISTORICO_PATH)
    if not src.exists():
        print("[MIGRACAO] historico_tratativas.json nao encontrado. Nada a migrar.")
        return

    with open(src, encoding="utf-8") as f:
        historico = json.load(f)

    ciclos_existentes = carregar_ciclos(CICLOS_PATH_DEFAULT)
    chaves = {(c["Chassi"], c["Tipo_Alerta"], c.get("Data_Inicio_Ciclo")) for c in ciclos_existentes}

    novos = []
    for r in historico:
        chassi      = r.get("Chassi", "")
        tipo        = inferir_tipo_alerta(r.get("Gatilho", ""))
        data_inicio = str(r.get("Data_Tratativa", datetime.date.today().isoformat()))[:10]
        if (chassi, tipo, data_inicio) in chaves:
            continue
        valor_orc = float(r.get("Valor_Orcamento", 0.0)) or None
        novos.append({
            "Chassi":               chassi,
            "Tipo_Alerta":          tipo,
            "Data_Inicio_Ciclo":    data_inicio,
            "Horimetro_Inicio":     float(r.get("Horimetro_Base", 0.0)),
            "Data_Fechamento":      data_inicio,
            "Horimetro_Fechamento": float(r.get("Horimetro_Tratativa", 0.0)),
            "Resultado":            r.get("Retorno_Contato"),
            "Consultor":            r.get("Consultor", ""),
            "Observacoes":          r.get("Observacoes", ""),
            "Orcamento_Protheus":   r.get("Orcamento_Protheus") or None,
            "Data_Orcamento":       data_inicio if valor_orc else None,
            "Valor_Orcamento":      valor_orc,
            "Tipo_Resolucao":       None,
            "Status_Orcamento":     "Aberto" if r.get("Proposta_Gerada") else None,
            "Data_Conversao_NF":    None,
            "NF_Numero":            None,
            "Valor_Faturado":       None,
        })

    todos = ciclos_existentes + novos
    _salvar_ciclos(todos, CICLOS_PATH_DEFAULT)
    print(f"[MIGRACAO] {len(novos)} registros migrados. Total: {len(todos)}")

if __name__ == "__main__":
    migrar()
```

**Step 2: Executar**

```
C:\Projetos\Inova\.venv\Scripts\python.exe scripts/migrar_historico_para_ciclos.py
```

Esperado: `[MIGRACAO] 31 registros migrados. Total: 31`

**Step 3: Validar saída**

```
C:\Projetos\Inova\.venv\Scripts\python.exe -c "import json; from pathlib import Path; c=json.loads(Path('data/output/ciclos_alertas.json').read_text(encoding='utf-8')); print('Total:', len(c)); print('Campos:', len(c[0].keys())); print('Vendas:', len([x for x in c if x['Resultado']=='Venda']))"
```

Esperado: 31 registros, 17 campos.

**Step 4: Commit**

```
git add scripts/migrar_historico_para_ciclos.py data/output/ciclos_alertas.json
git commit -m "feat(history): migrar 31 registros historico_tratativas -> ciclos_alertas"
```

---

## Task 3: `transform.py` — fechar ciclos ao processar tratativas

**Files:**

- Modify: `src/transform.py`
- Modify: `tests/test_transform.py`

**Cobre:** RF-02, RF-04

---

**Step 1: Confirmar que `test_aplicar_reentrada` (Sem Contato) já passa**

```
C:\Projetos\Inova\.venv\Scripts\python.exe -m pytest tests/test_transform.py::test_aplicar_reentrada -v
```

Se `PASSED`: a lógica de horímetro já está correta (RF-04). Adicionar teste de integração com ciclos:

```python
def test_aplicar_reentrada_fecha_ciclos(tmp_path):
    from src.history import abrir_ciclo, carregar_ciclos
    caminho_ciclos = str(tmp_path / "ciclos.json")
    abrir_ciclo("CHASSI_VENDA", "FPS", 1000.0, "Consultor A", caminho_json=caminho_ciclos)
    abrir_ciclo("CHASSI_SEM_CONTATO", "FPS", 1000.0, "Consultor B", caminho_json=caminho_ciclos)

    df_ativos = pd.DataFrame({
        'Serial Number': ['CHASSI_VENDA', 'CHASSI_SEM_CONTATO'],
        'Work Order Hours Reported': [1210.0, 1100.0],
        'Horimetro_Base': [1000.0, 1000.0]
    })
    df_retorno = pd.DataFrame({
        'Chassi': ['CHASSI_VENDA', 'CHASSI_SEM_CONTATO'],
        'Retorno do Contato': ['Venda', 'Sem Contato']
    })

    aplicar_reentrada(df_retorno, df_ativos, caminho_ciclos=caminho_ciclos)

    ciclos = carregar_ciclos(caminho_ciclos)
    venda = next(c for c in ciclos if c["Chassi"] == "CHASSI_VENDA")
    sem = next(c for c in ciclos if c["Chassi"] == "CHASSI_SEM_CONTATO")
    assert venda["Resultado"] == "Venda"
    assert sem["Resultado"] is None
```

**Step 2: Rodar para confirmar RED**

```
C:\Projetos\Inova\.venv\Scripts\python.exe -m pytest tests/test_transform.py::test_aplicar_reentrada_fecha_ciclos -v
```

Esperado: `FAILED` — `aplicar_reentrada` não aceita `caminho_ciclos`.

**Step 3: Atualizar `aplicar_reentrada` em `src/transform.py`**

Adicionar import no topo: `from src.history import fechar_ciclo`

```python
def aplicar_reentrada(df_retorno, df_ativos, caminho_ciclos=None):
    if df_ativos.empty or df_retorno.empty:
        return df_ativos

    df_ativos = df_ativos.copy()
    leads_tratados = df_retorno[df_retorno['Retorno do Contato'].isin(['Venda', 'Venda Perdida'])]
    if leads_tratados.empty:
        return df_ativos

    dict_tratados = dict(zip(leads_tratados['Chassi'], leads_tratados['Retorno do Contato']))

    def atualizar_base(row):
        if row['Serial Number'] in dict_tratados:
            return row['Work Order Hours Reported']
        return row['Horimetro_Base']

    df_ativos['Horimetro_Base'] = df_ativos.apply(atualizar_base, axis=1)

    # Fecha todos os ciclos ativos de cada chassi tratado (tipo=None)
    for chassi, retorno in dict_tratados.items():
        h_arr = df_ativos.loc[df_ativos['Serial Number'] == chassi, 'Work Order Hours Reported'].values
        h = float(h_arr[0]) if len(h_arr) > 0 else 0.0
        fechar_ciclo(chassi, None, retorno, h, None, 0.0, caminho_json=caminho_ciclos)

    return df_ativos
```

**Step 4: Rodar testes**

```
C:\Projetos\Inova\.venv\Scripts\python.exe -m pytest tests/test_transform.py -v
```

Esperado: todos `PASSED`.

**Step 5: Commit**

```
git add src/transform.py tests/test_transform.py
git commit -m "feat(transform): fechar ciclos_alertas ao processar tratativas comerciais"
```

---

## Task 4: `run.py` — reset de `alertas_ocorrencias.parquet` e abertura de ciclos

**Files:**

- Modify: `run.py`

**Cobre:** RF-02, RF-03

---

**Step 1: Reset do parquet após `aplicar_reentrada` (~linha 193)**

```python
# Remove chassi tratados do parquet de ocorrencias para permitir novo ciclo
if not df_retorno.empty and ocorrencias_path.exists():
    chassis_tratados = set(
        df_retorno[df_retorno['Retorno do Contato'].isin(['Venda', 'Venda Perdida'])]['Chassi'].tolist()
    )
    if chassis_tratados:
        _df_oc = pd.read_parquet(ocorrencias_path)
        _df_oc = _df_oc[~_df_oc['Serial Number'].isin(chassis_tratados)]
        _df_oc.to_parquet(ocorrencias_path, index=False)
        print(f"   -> {len(chassis_tratados):,} chassis tratados removidos de alertas_ocorrencias.parquet.")
```

> Nota: `ocorrencias_path` é definido mais abaixo no fluxo atual (~linha 222). Mover sua definição para antes de `aplicar_reentrada`, ou referenciar `Path(args.output).parent / "alertas_ocorrencias.parquet"` diretamente neste bloco.

**Step 2: Abertura de ciclos após `df_leads_final` construído (~linha 335, antes da exportação)**

```python
# Abre ciclos no ciclos_alertas.json para cada lead ativo
from history import abrir_ciclo as _abrir_ciclo
ciclos_path = str(Path(args.output).parent / "ciclos_alertas.json")
for _, lead in df_leads_final.iterrows():
    chassi    = str(lead.get('Serial Number', ''))
    consultor = mapa_consultores.get(str(lead.get('CNPJ', '')), 'CEVAP')
    horimetro = float(lead.get('Work Order Hours Reported', 0.0))
    gatilho   = str(lead.get('Gatilho_Alerta', ''))
    if 'FPS' in gatilho:
        _abrir_ciclo(chassi, 'FPS', horimetro, consultor, caminho_json=ciclos_path)
    if 'Rodante' in gatilho:
        _abrir_ciclo(chassi, 'Rodante', horimetro, consultor, caminho_json=ciclos_path)
```

**Step 3: Passar `caminho_ciclos` na chamada de `aplicar_reentrada`**

Localizar `df_ativos = aplicar_reentrada(df_retorno, df_ativos)` e atualizar para:

```python
df_ativos = aplicar_reentrada(df_retorno, df_ativos, caminho_ciclos=str(Path(args.output).parent / "ciclos_alertas.json"))
```

**Step 4: Validação manual (smoke)**

```
C:\Projetos\Inova\.venv\Scripts\python.exe -c "import ast; src=open('run.py',encoding='utf-8').read(); ast.parse(src); print('run.py parseia OK')"
```

**Step 5: Commit**

```
git add run.py
git commit -m "feat(run): resetar alertas_ocorrencias e abrir ciclos em ciclos_alertas"
```

---

## Task 5: `load.py` — reescrever KPIs (5) e HTML

**Files:**

- Modify: `src/load.py`
- Create: `tests/test_kpis_dashboard.py`

**Cobre:** RF-05, RF-07

---

**Step 1: Escrever testes RED**

Criar `tests/test_kpis_dashboard.py`:

```python
import sys, json
from pathlib import Path
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from src.load import calcular_kpis_dashboard
except ImportError:
    def calcular_kpis_dashboard(df, caminho_ciclos=None): return {}

def ciclos_fixture(tmp_path, registros):
    p = tmp_path / "ciclos.json"
    p.write_text(json.dumps(registros, ensure_ascii=False), encoding="utf-8")
    return str(p)

def df_leads(retornos):
    return pd.DataFrame({
        'Serial Number': [f'CH{i}' for i in range(len(retornos))],
        'Retorno do Contato': retornos,
        'Potencial Peças Anual': [15000.0] * len(retornos),
    })

def test_sem_contato_nao_conta_como_adesao(tmp_path):
    ciclos = ciclos_fixture(tmp_path, [])
    kpis = calcular_kpis_dashboard(df_leads(['Sem Contato', 'Sem Contato', '']), caminho_ciclos=ciclos)
    assert kpis['taxa_adesao'] == 0.0
    assert kpis['leads_pendentes'] == 3

def test_adesao_conta_venda_e_perdida(tmp_path):
    ciclos = ciclos_fixture(tmp_path, [])
    kpis = calcular_kpis_dashboard(df_leads(['Venda', 'Venda Perdida', 'Sem Contato', '']), caminho_ciclos=ciclos)
    assert kpis['taxa_adesao'] == pytest.approx(50.0)
    assert kpis['leads_pendentes'] == 2

def test_conversao_acumulada(tmp_path):
    data = [
        {"Resultado": "Venda", "Data_Inicio_Ciclo": "2026-05-29", "Data_Fechamento": "2026-06-01"},
        {"Resultado": "Venda Perdida", "Data_Inicio_Ciclo": "2026-05-29", "Data_Fechamento": "2026-06-01"},
        {"Resultado": None, "Data_Inicio_Ciclo": "2026-05-29", "Data_Fechamento": None},
    ]
    ciclos = ciclos_fixture(tmp_path, data)
    kpis = calcular_kpis_dashboard(df_leads([]), caminho_ciclos=ciclos)
    assert kpis['taxa_conversao_acumulada'] == pytest.approx(50.0)

def test_aging_medio_real(tmp_path):
    data = [{"Resultado": "Venda", "Data_Inicio_Ciclo": "2026-05-29", "Data_Fechamento": "2026-06-03"}]
    ciclos = ciclos_fixture(tmp_path, data)
    kpis = calcular_kpis_dashboard(df_leads([]), caminho_ciclos=ciclos)
    assert kpis['aging_medio'] == pytest.approx(5.0)

def test_aging_nenhum_ciclo_fechado(tmp_path):
    ciclos = ciclos_fixture(tmp_path, [])
    kpis = calcular_kpis_dashboard(df_leads([]), caminho_ciclos=ciclos)
    assert kpis['aging_medio'] is None

def test_sem_fallback_ficticio(tmp_path):
    # Vendas sem valor NUNCA devem gerar R$15k ficticio nem chave de faturamento inventada
    data = [{"Resultado": "Venda", "Data_Inicio_Ciclo": "2026-05-29", "Data_Fechamento": "2026-06-01"}]
    ciclos = ciclos_fixture(tmp_path, data)
    kpis = calcular_kpis_dashboard(df_leads([]), caminho_ciclos=ciclos)
    assert 'faturamento_realizado_acumulado' not in kpis  # KPI de valor adiado p/ fase 2
    assert kpis['potencial_financeiro'] == 0.0  # df vazio -> sem potencial

def test_potencial_soma_m3(tmp_path):
    ciclos = ciclos_fixture(tmp_path, [])
    kpis = calcular_kpis_dashboard(df_leads(['', '', '']), caminho_ciclos=ciclos)
    assert kpis['potencial_financeiro'] == pytest.approx(45000.0)
```

**Step 2: Rodar para confirmar RED**

```
C:\Projetos\Inova\.venv\Scripts\python.exe -m pytest tests/test_kpis_dashboard.py -v
```

Esperado: `FAILED`.

**Step 3: Reescrever `calcular_kpis_dashboard` em `src/load.py`**

Substituir a função inteira (linhas 238-318 da versão atual):

```python
def calcular_kpis_dashboard(df_leads_final, caminho_ciclos=None):
    import datetime
    from src.history import carregar_ciclos

    if caminho_ciclos is None:
        caminho_ciclos = r"C:\Projetos\Inova\projects\lead-csc-pops\data\output\ciclos_alertas.json"
    ciclos = carregar_ciclos(caminho_ciclos)

    kpis = {
        'total_leads': len(df_leads_final),
        'leads_tratados': 0,
        'leads_pendentes': 0,
        'taxa_adesao': 0.0,
        'taxa_conversao_acumulada': 0.0,
        'aging_medio': None,
        'potencial_financeiro': 0.0,
    }

    # KPIs da planilha ativa (semana atual)
    if not df_leads_final.empty:
        retornos = df_leads_final['Retorno do Contato'].fillna('')
        mask_tratado = retornos.isin(['Venda', 'Venda Perdida'])
        kpis['leads_tratados'] = int(mask_tratado.sum())
        kpis['leads_pendentes'] = int((~mask_tratado).sum())
        kpis['taxa_adesao'] = (kpis['leads_tratados'] / kpis['total_leads']) * 100 if kpis['total_leads'] > 0 else 0.0
        if 'Potencial Peças Anual' in df_leads_final.columns:
            kpis['potencial_financeiro'] = float(df_leads_final['Potencial Peças Anual'].sum())

    # KPIs históricos dos ciclos fechados
    fechados = [c for c in ciclos if c.get("Resultado") is not None]
    vendas   = [c for c in fechados if c.get("Resultado") == "Venda"]
    perdidas = [c for c in fechados if c.get("Resultado") == "Venda Perdida"]
    total_decisoes = len(vendas) + len(perdidas)
    if total_decisoes > 0:
        kpis['taxa_conversao_acumulada'] = (len(vendas) / total_decisoes) * 100

    # Aging médio real
    agings = []
    for c in fechados:
        ini, fim = c.get("Data_Inicio_Ciclo"), c.get("Data_Fechamento")
        if ini and fim:
            try:
                agings.append((datetime.date.fromisoformat(fim) - datetime.date.fromisoformat(ini)).days)
            except ValueError:
                pass
    if agings:
        kpis['aging_medio'] = sum(agings) / len(agings)

    return kpis
```

**Step 4: Atualizar `gerar_html_report` — 4 cards + tabela, CSS condicional**

Substituir o bloco `.kpi-grid` (4 cards) e a tabela:

- Card 1: **Adesão Comercial (Semana)** — `{kpis['taxa_adesao']:.1f}%` — desc `{leads_tratados} de {total_leads} alertas tratados` — sem `success`
- Card 2: **Conversão Acumulada** — `{kpis['taxa_conversao_acumulada']:.1f}%` — `success` se `> 0`
- Card 3: **Leads Pendentes** — `{kpis['leads_pendentes']}` — desc `aguardando tratativa do consultor` — sem `success`
- Card 4: **Potencial Financeiro** — `R$ {kpis['potencial_financeiro']:,.2f}` — `success` se `> 0`

CSS condicional via f-string: `class="kpi-card{' success' if valor > 0 else ''}"`.

Tabela (Metodologia e Aging):

- Aging Médio: `f"{kpis['aging_medio']:.1f} dias"` se não `None`, senão `"N/A"`; status `"Excelente (< 4 dias)"` só se `aging_medio is not None and aging_medio < 4`, senão `"Sem dados suficientes"`
- Leads Tratados na Semana: `{kpis['leads_tratados']}`

Remover do template: card único "Faturamento Realizado", card "Conversão" com valor fixo, card "Aderência", linha "Potencial Financeiro de Alertas Ativos" duplicada (agora é card).

**Step 5: Rodar testes**

```
C:\Projetos\Inova\.venv\Scripts\python.exe -m pytest tests/test_kpis_dashboard.py tests/test_load_consultor.py -v
```

Esperado: todos `PASSED`.

**Step 6: Commit**

```
git add src/load.py tests/test_kpis_dashboard.py
git commit -m "feat(load): reescrever 5 KPIs com ciclos_alertas, remover fallback ficticio, CSS condicional"
```

---

## Task 6: Suite completa e validação do HTML gerado

**Files:** nenhum modificado

**Cobre:** validação E2E de todos os RF

---

**Step 1: Suite completa**

```
C:\Projetos\Inova\.venv\Scripts\python.exe -m pytest tests/ -v
```

Esperado: todos `PASSED`.

**Step 2: Gerar HTML de teste com dados mockados**

```
C:\Projetos\Inova\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'src'); from load import calcular_kpis_dashboard, gerar_html_report; import pandas as pd; df=pd.DataFrame({'Retorno do Contato':['Venda','Sem Contato',''],'Potencial Peças Anual':[15000.0,12000.0,8000.0]}); k=calcular_kpis_dashboard(df); print('KPIs:',k); gerar_html_report(k,'data/output/daily_report_kpis.html'); print('HTML gerado.')"
```

Verificar no browser:

- 4 cards; verdes apenas onde valor > 0
- Aging "N/A" quando não há ciclos fechados (ou valor real após migração)
- Nenhum R$15k fictício
- Sem card de Faturamento/Aderência/Valor

**Step 3: Commit final**

```
git add data/output/daily_report_kpis.html
git commit -m "test(suite): validar pipeline e HTML pos-refatoracao ciclos_alertas (5 KPIs)"
```
