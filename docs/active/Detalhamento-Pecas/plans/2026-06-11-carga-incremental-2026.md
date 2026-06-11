# Carga Incremental 2026 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Realizar a carga incremental de dados do ano de 2026 no Power BI e corrigir o bug de sobrescrita histórica de parquets nas cargas subsequentes de 2026.

**Architecture:** 
O scraper Playwright extrai dados de 2026 incrementalmente a partir da última data de emissão presente no arquivo de destino. Para evitar que os dados históricos sejam sobrescritos na gravação, alteraremos o fluxo para carregar o parquet existente (se houver), concatenar com os novos dados extraídos, de-duplicar os registros usando a chave primária (`['Nota Fiscal', 'Data Emissão', 'CNPJ']`), validar a variação do total acumulado contra o acumulado anterior e salvar o parquet completo.

**Tech Stack:** Python 3.13, Playwright (Chromium), Pandas, PyArrow, Pytest.

---

### Task 1: Re-autenticação da Sessão Expirada com o Power BI

**Files:**
- Modify: `projects/dashboard-inova-data-export/browser_state/state.json` (gerado/atualizado pelo script de auth)
- Run: `projects/dashboard-inova-data-export/authenticate.py`

**Step 1: Iniciar script de autenticação interativa**
Para gerar um novo token de sessão e salvá-lo no `state.json` compartilhado, iniciaremos o script `authenticate.py` que abrirá uma janela visível do navegador para o usuário fazer login.
Executar no terminal:
```bash
cd C:/Projetos/Inova/projects/dashboard-inova-data-export
.venv/Scripts/python.exe authenticate.py
```

**Step 2: Realizar login e aguardar confirmação**
O usuário irá efetuar o login interativo na tela do Chromium que abrirá. Após o carregamento completo do dashboard no navegador, o usuário (ou agente) pressionará **ENTER** no terminal para persistir o estado da sessão em `browser_state/state.json`.

---

### Task 2: Refatoração do `run.py` para Suporte a Concatenação e De-duplicação

**Files:**
- Modify: `projects/Detalhamento-Pecas/run.py`

**Step 1: Alterar a lógica de salvamento e validação de threshold**
Modificaremos o arquivo `run.py` para carregar os dados históricos existentes e concatená-los com a nova extração. A validação de threshold também passará a comparar o novo acumulado consolidado contra o acumulado anterior.

Modificar `projects/Detalhamento-Pecas/run.py` na seção final do fluxo:
```python
    print('[4/5] Validando e Concatenando com histórico...')
    df_ant = carregar_parquet_se_existir(parquet_destino)
    
    if df_ant is not None and not df_ant.empty:
        # Concatenar novos dados com o histórico existente
        df_consolidado = pd.concat([df_ant, df_limpo], ignore_index=True)
        # De-duplicar com base na chave primária de venda
        df_consolidado = df_consolidado.drop_duplicates(subset=['Nota Fiscal', 'Data Emissão', 'CNPJ'], keep='last')
        
        # Validar variação do acumulado consolidado em relação ao acumulado anterior
        col = next((c for c in df_limpo.columns if 'valor' in c.lower() or 'total' in c.lower()), None)
        if col and not validar_threshold(df_consolidado, df_ant, col, VALIDATION_THRESHOLD):
            print('[ERRO] Threshold de variação violado para o total acumulado. Abortando.')
            sys.exit(1)
        df_final = df_consolidado
    else:
        df_final = df_limpo
        print('      -> OK (Carga inicial: nenhum histórico encontrado)')

    print(f'[5/5] Salvando {parquet_destino.name}...')
    salvar_parquet(df_final, parquet_destino)
```

---

### Task 3: Adicionar Testes Unitários de Integração para Concatenação e De-duplicação

**Files:**
- Modify: `projects/Detalhamento-Pecas/tests/test_load.py`

**Step 1: Escrever teste de concatenação e de-duplicação**
Adicionar um teste automatizado no arquivo de testes para garantir que novos registros são adicionados ao histórico e registros idênticos (duplicatas) são de-duplicados corretamente, priorizando a versão mais recente.

Escrever no final de `projects/Detalhamento-Pecas/tests/test_load.py`:
```python
def test_salvar_parquet_incremental_concatena_e_deduplica(tmp_path):
    from load import salvar_parquet, carregar_parquet_se_existir
    import pandas as pd
    
    destino = tmp_path / "test_incremental.parquet"
    
    # Dado um arquivo inicial de histórico
    df_historico = pd.DataFrame({
        "Nota Fiscal": ["NF001", "NF002"],
        "Data Emissão": ["2026-06-10", "2026-06-10"],
        "CNPJ": ["12345678000100", "98765432000199"],
        "Valor": [1000.0, 2000.0]
    })
    salvar_parquet(df_historico, destino)
    
    # E novos dados contendo uma atualização e um novo registro
    df_novos = pd.DataFrame({
        "Nota Fiscal": ["NF002", "NF003"],
        "Data Emissão": ["2026-06-10", "2026-06-11"],
        "CNPJ": ["98765432000199", "11112222000133"],
        "Valor": [2500.0, 3000.0] # NF002 atualizada de 2000 para 2500
    })
    
    # Quando fazemos a lógica de concatenação
    df_anterior = carregar_parquet_se_existir(destino)
    df_consolidado = pd.concat([df_anterior, df_novos], ignore_index=True)
    df_final = df_consolidado.drop_duplicates(subset=['Nota Fiscal', 'Data Emissão', 'CNPJ'], keep='last')
    salvar_parquet(df_final, destino)
    
    # Então o parquet resultante deve conter 3 registros (NF001, NF002 atualizada, NF003)
    df_resultado = carregar_parquet_se_existir(destino)
    assert df_resultado is not None
    assert len(df_resultado) == 3
    
    # E os valores devem corresponder aos atualizados
    assert df_resultado.loc[df_resultado["Nota Fiscal"] == "NF002", "Valor"].values[0] == 2500.0
    assert df_resultado.loc[df_resultado["Nota Fiscal"] == "NF003", "Valor"].values[0] == 3000.0
```

**Step 2: Executar testes locais**
Executar a suíte de testes locais para validar o comportamento e os testes criados:
```bash
cd C:/Projetos/Inova/projects/Detalhamento-Pecas
.venv/Scripts/pytest tests/test_load.py -v
```
**Expected:** Todos os testes de load passam com sucesso (incluindo o novo teste incremental).

---

### Task 4: Executar Carga de Produção 2026

**Files:**
- Create: `shared/data/detalhamento_vendas_2026.parquet`

**Step 1: Rodar a primeira carga completa de 2026**
Com a sessão re-autenticada, executaremos a primeira carga de 2026 (que obterá dados desde 01/01/2026 até hoje).
Executar no terminal:
```bash
cd C:/Projetos/Inova/projects/Detalhamento-Pecas
$env:PYTHONIOENCODING="utf-8"; .venv/Scripts/python.exe run.py --ano 2026
```
**Expected:** Extração e gravação em `shared/data/detalhamento_vendas_2026.parquet` com sucesso.

**Step 2: Verificar integridade dos dados contra Power BI**
- Ler a quantidade de linhas e soma do Valor Líquido gerados no arquivo `detalhamento_vendas_2026.parquet`.
- Solicitar ao usuário a validação visual do total contra os números expostos no relatório do Power BI.

---

### Task 5: Validar Governança de Recência

**Files:**
- Modify: `C:/Projetos/Inova/shared/recency_status.md` (automatizado no pós-run)

**Step 1: Verificar se os logs de recência foram registrados**
Após a finalização do script, verificar se o status de recência de 2026 foi corretamente atualizado no arquivo `shared/recency_status.md` e se o relatório geral de recência roda sem erros.
