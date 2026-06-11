# Carga Total 2026 e Perfil Persistente Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Configurar o scraper de Detalhamento de Peças para realizar carga completa do ano de 2026 a cada rodada (sobrescrevendo o parquet) e migrar o login para contexto persistente do Chromium, evitando expiração frequente de sessão.

**Architecture:** 
O Playwright usará uma pasta de perfil de usuário persistente compartilhada (`browser_state/user_profile`) para manter a sessão ativa indefinidamente. O script de autenticação abrirá este perfil em modo visual (`headless=False`) para o login inicial, e o scraper o abrirá de forma oculta (`headless=True`). A carga de 2026 será simplificada para extrair sempre todo o ano de 2026 (01/01/2026 até hoje), substituindo o parquet anterior por completo na gravação.

**Tech Stack:** Python 3.13, Playwright, Pandas, PyArrow, Pytest.

---

### Task 1: Ajuste de Configurações de Diretórios (Paths)

**Files:**
- Modify: `projects/dashboard-inova-data-export/src/config.py`
- Modify: `projects/Detalhamento-Pecas/src/config.py`

**Step 1: Ajustar `dashboard-inova-data-export/src/config.py`**
Remover a constante `STATE_FILE` e adicionar a constante `USER_PROFILE_DIR`:
```python
USER_PROFILE_DIR = BROWSER_STATE / 'user_profile'
```

**Step 2: Ajustar `projects/Detalhamento-Pecas/src/config.py`**
Ajustar o caminho de `BROWSER_STATE` para apontar para o projeto do exportador central e definir a mesma constante `USER_PROFILE_DIR`:
```python
BROWSER_STATE = Path('C:/Projetos/Inova/projects/dashboard-inova-data-export/browser_state')
USER_PROFILE_DIR = BROWSER_STATE / 'user_profile'
```

---

### Task 2: Refatoração da Autenticação (`authenticate.py`)

**Files:**
- Modify: `projects/dashboard-inova-data-export/authenticate.py`

**Step 1: Modificar `authenticate.py` para usar Contexto Persistente**
Alterar a inicialização do navegador para usar `launch_persistent_context` e remover a lógica que salvava o `state.json`.

Modificar o corpo da função `main()`:
```python
def main():
    print('=== Autenticacao Power BI (Contexto Persistente) ===')
    print(f'Diretorio de Perfil: {USER_PROFILE_DIR}')
    print()

    with sync_playwright() as p:
        # Abre o contexto persistente com o perfil do disco
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_PROFILE_DIR),
            headless=False,
            args=['--start-maximized'],
            viewport=VIEWPORT
        )
        page = context.pages[0] if context.pages else context.new_page()

        print(f'Abrindo: {REPORT_URL}')
        page.goto(REPORT_URL, wait_until='domcontentloaded', timeout=60000)

        print()
        print('>> Faca login no browser que abriu.')
        print('>> Aguarde o relatorio carregar completamente.')
        print('>> Quando estiver pronto, pressione ENTER aqui.')
        input()

        context.close() # O Chromium persistirá os cookies no disco ao fechar

    print('Perfil persistente atualizado com sucesso!')
```

---

### Task 3: Refatoração da Extração (`extract.py`)

**Files:**
- Modify: `projects/Detalhamento-Pecas/src/extract.py`

**Step 1: Adaptar `extract.py` para usar o perfil de navegador persistente**
Remover a leitura do arquivo `state.json` e inicializar o Playwright com `launch_persistent_context` em modo headless.

Modificar a função `extrair_detalhamento_pecas`:
```python
def extrair_detalhamento_pecas(data_inicio: datetime, data_fim: datetime) -> pd.DataFrame:
    if not USER_PROFILE_DIR.exists():
        raise FileNotFoundError(
            f"Diretorio de perfil persistente nao encontrado em {USER_PROFILE_DIR}.\n"
            "Execute authenticate.py em dashboard-inova-data-export primeiro."
        )

    logger.info(f"Extraindo {data_inicio.date()} a {data_fim.date()} usando perfil persistente")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_PROFILE_DIR),
            headless=True,
            viewport=VIEWPORT
        )
        page = context.pages[0] if context.pages else context.new_page()

        try:
            logger.info("Acessando Power BI...")
            page.goto(REPORT_URL, wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
            time.sleep(NAVIGATION_DELAY)

            pbi_iframe = page.frame_locator('iframe[src*="app.powerbi.com"]')

            logger.info("Navegando para aba 'Detalhamento Peças'")
            aba = pbi_iframe.get_by_text("Detalhamento Peças", exact=True).first
            aba.wait_for(state="visible", timeout=60000)
            aba.click(force=True, timeout=15000)
            time.sleep(PAGE_DELAY)

            _aplicar_filtros_data(pbi_iframe, data_inicio, data_fim, page)
            time.sleep(RENDER_WAIT)

            arquivo_xlsx = _exportar_tabela(pbi_iframe, page)

        finally:
            context.close()

    df = pd.read_excel(arquivo_xlsx, engine="openpyxl")
    logger.info(f"Excel lido: {len(df)} linhas (bruto, incluindo metadata)")
    return df
```

---

### Task 4: Ajuste do Range e Sobrescrita de 2026 (`run.py`)

**Files:**
- Modify: `projects/Detalhamento-Pecas/run.py`

**Step 1: Alterar a função de cálculo do range de 2026**
Modificar `_calcular_range_2026` para retornar sempre o ano cheio desde 01/01/2026 até hoje.

Modificar em `projects/Detalhamento-Pecas/run.py`:
```python
def _calcular_range_2026(parquet_path):
    # Carga completa a cada rodada: de 01/01/2026 ate hoje
    return datetime(2026, 1, 1), datetime.now()
```

---

### Task 5: Re-autenticação Interativa (Login Inicial)

**Files:**
- Create: `projects/dashboard-inova-data-export/browser_state/user_profile/`

**Step 1: Rodar o script de autenticação**
Executar o script interativo para que o usuário faça o login inicial do Power BI, gerando o diretório de perfil persistente.
Comando:
```bash
cd C:/Projetos/Inova/projects/dashboard-inova-data-export
.venv/Scripts/python.exe authenticate.py
```
**Expected:** O navegador abre, o usuário faz o login, aperta ENTER no terminal e a pasta `user_profile/` é criada com sucesso.

---

### Task 6: Execução da Carga de Produção de 2026 e Validação

**Files:**
- Create: `shared/data/detalhamento_vendas_2026.parquet`

**Step 1: Executar a extração headless**
Rodar o script de carga total de 2026.
Comando:
```bash
cd C:/Projetos/Inova/projects/Detalhamento-Pecas
$env:PYTHONIOENCODING="utf-8"; .venv/Scripts/python.exe run.py --ano 2026
```
**Expected:** Extração concluída com sucesso e gravação do arquivo `/shared/data/detalhamento_vendas_2026.parquet`.

**Step 2: Validação E2E contra Power BI**
Visualizar a quantidade de linhas e soma total do Valor Líquido gerada e validar manualmente contra os números do Power BI.
