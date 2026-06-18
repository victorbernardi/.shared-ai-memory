# Detalhamento de Peças — Plano de Implementação de Devoluções

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Implementar o scraper, pipeline de transformação, validação e persistência física da tabela "Detalhamento das Devoluções" do Power BI, consolidando em parquet de 2025-2026.

**Architecture:** A lógica de extração será dividida em dois scripts independentes (`extract.py` para vendas e `extract_devolucoes.py` para devoluções) rodando sob uma sessão Playwright isolada. O script principal `run.py` orquestrará a chamada de ambos sequencialmente, aplicando gates de validação dupla antes de persistir os dados no diretório compartilhado.

**Tech Stack:** Python 3.13, Playwright, pandas, pyarrow, openpyxl

---

### Task 1: Configuração de Constantes Físicas

**Files:**
* Modify: `src/config.py`
* Test: `tests/test_config.py`

**Step 1: Write the failing test**
Crie o arquivo `tests/test_config.py` com o teste que verifica a presença do caminho físico das devoluções.
```python
# -*- coding: utf-8 -*-
from pathlib import Path
import sys
sys.path.insert(0, 'src')
import config

def test_parquet_devolucoes_configured():
    assert hasattr(config, 'PARQUET_DEVOLUCOES')
    assert isinstance(config.PARQUET_DEVOLUCOES, Path)
    assert config.PARQUET_DEVOLUCOES.name == 'detalhamento_devolucoes_2025-2026.parquet'
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_config.py -v`
Expected: FAIL with `AttributeError` ou `ModuleNotFoundError`

**Step 3: Write minimal implementation**
Adicione a constante em `src/config.py`:
```python
PARQUET_DEVOLUCOES = SHARED_DATA_DIR / 'detalhamento_devolucoes_2025-2026.parquet'
```

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_config.py -v`
Expected: PASS

**Step 5: Commit**
```bash
git add src/config.py tests/test_config.py
git commit -m "chore: configurar caminho do parquet de devolucoes"
```

---

### Task 2: Script de Extração de Devoluções (Playwright)

**Files:**
* Create: `src/extract_devolucoes.py`
* Test: `tests/test_extract_devolucoes.py`

**Step 1: Write the failing test**
Crie um teste unitário que valide a importação e a assinatura do método de extração.
```python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'src')

def test_extract_devolucoes_signature():
    import extract_devolucoes
    assert hasattr(extract_devolucoes, 'extrair_detalhamento_devolucoes')
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_extract_devolucoes.py -v`
Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write minimal implementation**
Crie o arquivo `src/extract_devolucoes.py` com a lógica de extração focando no título de devoluções:
```python
# -*- coding: utf-8 -*-
import time
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
from playwright.sync_api import sync_playwright

from config import (
    REPORT_URL, USER_PROFILE_DIR, VIEWPORT,
    PAGE_LOAD_TIMEOUT, NAVIGATION_DELAY, PAGE_DELAY,
    DATE_FILTER_WAIT, RENDER_WAIT, OUTPUT_DIR
)
from extract import _formato_data_pbi, _aplicar_filtros_data

logger = logging.getLogger(__name__)

def _exportar_tabela_devolucoes(pbi_iframe, page) -> Path:
    logger.info("Localizando tabela 'Detalhamento das Devoluções'")
    page.keyboard.press("Escape")
    time.sleep(1)

    titulo = pbi_iframe.locator('h3').filter(has_text="Detalhamento das Devoluções").first
    titulo.wait_for(state="visible", timeout=30000)
    titulo.hover(force=True)
    time.sleep(3)

    btn = None
    for sel in [
        'button[aria-label="Mais opções"]',
        'button[title="Mais opções"]',
        'button[title="More options"]',
        '.vc-menu-trigger',
    ]:
        loc = pbi_iframe.locator(sel).first
        if loc.is_visible(timeout=3000):
            btn = loc
            logger.info(f"Botão mais opções encontrado: {sel}")
            break

    if btn is None:
        raise TimeoutError("Botão 'Mais opções' das devoluções não encontrado")

    btn.hover(force=True)
    time.sleep(1)
    btn.click(force=True)
    time.sleep(3)

    exportar = None
    for ctx, sel in [
        (page,       'div[role="menuitem"]:has-text("Exportar dados")'),
        (pbi_iframe, 'div[role="menuitem"]:has-text("Exportar dados")'),
        (page,       'div[role="menuitem"]:has-text("Export data")'),
        (pbi_iframe, 'div[role="menuitem"]:has-text("Export data")'),
        (page,       '[role="menuitem"]:has-text("Exportar")'),
        (pbi_iframe, '[role="menuitem"]:has-text("Exportar")'),
    ]:
        loc = ctx.locator(sel).first
        if loc.is_visible(timeout=3000):
            exportar = loc
            logger.info(f"Item exportar encontrado: {sel}")
            break

    if exportar is None:
        raise TimeoutError("Item 'Exportar dados' não encontrado para devoluções")

    exportar.click()
    time.sleep(3)

    with page.expect_download(timeout=300000) as dl_info:
        for ctx, sel_ok in [
            (pbi_iframe, 'button:has-text("Exportar")'),
            (pbi_iframe, 'button:has-text("Export")'),
            (page,       'button:has-text("Exportar")'),
            (page,       'button:has-text("Export")'),
        ]:
            loc = ctx.locator(sel_ok).first
            if loc.is_visible(timeout=2000):
                loc.click()
                break

    download = dl_info.value
    destino = OUTPUT_DIR / f"devolucoes_bruto_{int(time.time())}.xlsx"
    download.save_as(destino)
    logger.info(f"Download devoluções salvo: {destino}")
    return destino

def extrair_detalhamento_devolucoes(data_inicio: datetime, data_fim: datetime) -> pd.DataFrame:
    if not USER_PROFILE_DIR.exists():
        raise FileNotFoundError("Perfil persistente Playwright ausente.")

    logger.info(f"Extraindo devoluções no range {data_inicio.date()} a {data_fim.date()}")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_PROFILE_DIR),
            headless=False,
            viewport=VIEWPORT,
            locale="pt-BR"
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            page.goto(REPORT_URL, wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
            time.sleep(NAVIGATION_DELAY)

            btn_auth = page.locator('button:has-text("Autenticação Microsoft")').first
            if btn_auth.is_visible(timeout=5000):
                btn_auth.click()
                time.sleep(15)

            pbi_iframe = page.frame_locator('iframe[src*="app.powerbi.com"]')
            aba = pbi_iframe.get_by_text("Detalhamento Peças", exact=True).first
            aba.wait_for(state="visible", timeout=60000)
            aba.click(force=True)
            time.sleep(PAGE_DELAY)

            _aplicar_filtros_data(pbi_iframe, data_inicio, data_fim, page)
            time.sleep(RENDER_WAIT)

            arquivo_xlsx = _exportar_tabela_devolucoes(pbi_iframe, page)
        finally:
            context.close()

    df = pd.read_excel(arquivo_xlsx, engine="openpyxl")
    return df
```

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_extract_devolucoes.py -v`
Expected: PASS

**Step 5: Commit**
```bash
git add src/extract_devolucoes.py tests/test_extract_devolucoes.py
git commit -m "feat: implementar scraper de devolucoes"
```

---

### Task 3: Transformação e Schema de Devoluções

**Files:**
* Modify: `src/transform.py`
* Test: `tests/test_transform_devolucoes.py`

**Step 1: Write the failing test**
Crie `tests/test_transform_devolucoes.py` com testes de schema e limpeza de metadata de devoluções:
```python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'src')
import pandas as pd
import pytest
from transform import transformar

def test_transform_devolucoes_limpa_metadata():
    dados = {
        'Nota Fiscal': ['123', 'Total', 'Applied filters: Date is 2026', None],
        'Data Emissão': ['2026-06-17', 'Total', 'Applied filters', None],
        'CNPJ': ['12345678000199', 'Total', 'Applied filters', None],
        'Valor Bruto': [1500.0, 1500.0, 0.0, 0.0]
    }
    df = pd.DataFrame(dados)
    df_limpo = transformar(df)
    assert len(df_limpo) == 1
    assert df_limpo.iloc[0]['Nota Fiscal'] == '123'

def test_transform_devolucoes_schema_invalido():
    dados = {'Col1': [1], 'Col2': [2]}
    df = pd.DataFrame(dados)
    with pytest.raises(ValueError, match="Schema invalido"):
        transformar(df)
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_transform_devolucoes.py -v`
Expected: FAIL (se as regras em transform.py não cobrirem a coluna Valor Bruto ou falharem na limpeza genérica).

**Step 3: Write minimal implementation**
Verifique se `src/transform.py` já atende a essas regras. Como a função `transformar()` já busca por `Nota Fiscal`, `Data Emissão` e `CNPJ` e remove metadata com base nisso, ela é compatível. Garantir que eventuais discrepâncias na coluna de valor de threshold sejam aceitas dinamicamente.

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_transform_devolucoes.py -v`
Expected: PASS

**Step 5: Commit**
```bash
git add tests/test_transform_devolucoes.py
git commit -m "test: adicionar testes de transformacao para devolucoes"
```

---

### Task 4: Atualização do Runner Principal (run.py)

**Files:**
* Modify: `run.py`
* Test: Execução manual E2E de simulação

**Step 1: Write the failing test**
(O teste aqui será a validação de fluxo via teste de integração ou alteração direta do runner para acoplar o gate duplo).

**Step 2: Run test to verify it fails**
N/A (Cenário E2E de rede).

**Step 3: Write minimal implementation**
Modifique `run.py` para incluir a orquestração dupla:
```python
# Modificar importações para trazer extract_devolucoes
from extract_devolucoes import extrair_detalhamento_devolucoes
from config import PARQUET_2025, PARQUET_2026, PARQUET_DEVOLUCOES, SHARED_DIR, VALIDATION_THRESHOLD

# ... no método main() de run.py ...
    # Extração de Vendas existente
    print('[2/5] Extraindo Vendas...')
    df_bruto_vendas = _extrair_com_retry(data_inicio, data_fim)
    df_limpo_vendas = transformar(df_bruto_vendas)
    
    # Extração de Devoluções (sempre de 01/01/2025 até hoje)
    print('[2.5/5] Extraindo Devoluções (2025-Hoje)...')
    data_inicio_dev = datetime(2025, 1, 1)
    data_fim_dev = datetime.now()
    
    # Executa scraper de devoluções com retry
    ultimo_erro = None
    df_bruto_devolucoes = None
    for attempt in range(3):
        try:
            df_bruto_devolucoes = extrair_detalhamento_devolucoes(data_inicio_dev, data_fim_dev)
            break
        except Exception as e:
            ultimo_erro = e
            time.sleep(5)
    if df_bruto_devolucoes is None:
        raise RuntimeError(f"Scrape de devoluções falhou: {ultimo_erro}")
        
    df_limpo_devolucoes = transformar(df_bruto_devolucoes)
    
    # Validando threshold de Vendas
    print('[4/5] Validando threshold de Vendas...')
    df_ant_vendas = carregar_parquet_se_existir(parquet_destino)
    col_vendas = next((c for c in df_limpo_vendas.columns if 'valor' in c.lower() or 'total' in c.lower()), None)
    if col_vendas and not validar_threshold(df_limpo_vendas, df_ant_vendas, col_vendas, VALIDATION_THRESHOLD):
        print('[ERRO] Threshold de Vendas violado. Abortando.')
        sys.exit(1)
        
    # Validando threshold de Devoluções
    print('      Validando threshold de Devoluções...')
    df_ant_devolucoes = carregar_parquet_se_existir(PARQUET_DEVOLUCOES)
    col_devolucoes = next((c for c in df_limpo_devolucoes.columns if 'valor' in c.lower() or 'total' in c.lower()), None)
    if col_devolucoes and not validar_threshold(df_limpo_devolucoes, df_ant_devolucoes, col_devolucoes, VALIDATION_THRESHOLD):
        print('[ERRO] Threshold de Devoluções violado. Abortando.')
        sys.exit(1)
    print('      -> OK (Ambos)')
    
    # Persistência
    print(f'[5/5] Salvando Parquets...')
    salvar_parquet(df_limpo_vendas, parquet_destino)
    salvar_parquet(df_limpo_devolucoes, PARQUET_DEVOLUCOES)
```

**Step 4: Run execution**
Execute o runner e confirme que ambas as tabelas passam pelo pipeline sem erros.

**Step 5: Commit**
```bash
git add run.py
git commit -m "feat: integrar scraper de devolucoes e gate de threshold duplo no run.py"
```

---

### Task 5: Integração com Governança de Recência

**Files:**
* Modify: `C:\Projetos\Inova\shared\generate_recency_report.py`
* Test: Rodar `python C:\Projetos\Inova\shared\generate_recency_report.py` e verificar `recency_status.md`

**Step 1: Write the failing test**
N/A (Script de relatório de recência é auto-contido).

**Step 2: Run script to verify it has no devoluções**
Verifique que `recency_status.md` não contém a linha de Devoluções.

**Step 3: Write minimal implementation**
Adicione no dicionário `sources` de `shared/generate_recency_report.py`:
```python
        "Detalhamento Pecas (Devoluções 2025-2026)": {
            "path": shared_data / "detalhamento_devolucoes_2025-2026.parquet",
            "manual": False,
            "display": "detalhamento_devolucoes_2025-2026.parquet"
        }
```

**Step 4: Run script to verify it passes**
Run: `python C:\Projetos\Inova\shared\generate_recency_report.py`
Expected: O log printa o salvamento do md, e a linha correspondente aparece como `🟢 Atualizado Hoje` ou `🟡 Desatualizado` se o arquivo físico foi gravado.

**Step 5: Commit**
```bash
git add C:\Projetos\Inova\shared\generate_recency_report.py
git commit -m "chore: adicionar detalhamento de devolucoes no relatorio de recencia"
```
