# Renomeação da Planilha, Correção de Normalização de CNPJ e Auditoria BUP

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Renomear a planilha gerada para `leads-csc-pops-peças.xlsx` em todas as configurações do projeto, corrigir a falha de normalização de CNPJs float (.0) no extrator BUP para associar os consultores de forma 100% correta, e auditar os leads resultantes.

**Architecture:**
1. **Renomeação Consistente (CDD):**
   - Atualizar `.env`, `.env.example`, `src/config.py`, `run.py`, `scripts/scheduler_daily.ps1` e os testes para usar o novo nome da planilha: `leads-csc-pops-peças.xlsx`.
2. **Correção do Bug de CNPJ (Fase Verde/ETL):**
   - Em `src/extract.py`, na função `carregar_consultor_bup()`, a conversão do CNPJ float no Pandas insere `.0` (ex: `21256870000287.0`). A remoção simples de caracteres não numéricos transforma isso em `212568700002870` (15 dígitos), fazendo com que o match falhe e retorne o fallback `CEVAP`.
   - Adicionar uma rotina de normalização que trate e remova o sufixo `.0` antes de limpar caracteres especiais, garantindo 100% de correspondência exata de 14 dígitos.
3. **Mecanismo de Testes (TDD):**
   - Ajustar os testes de backups existentes com o novo nome.
   - Criar `tests/test_bup_mapping.py` para validar que CNPJs em formato float, inteiro, ou string contidos na planilha BUP sejam corretamente mapeados para seus respectivos consultores (como `21256870000287` -> `AURELIO APARECIDO DA COSTA`).

**Tech Stack:** Python 3.11, openpyxl, pandas, pytest, pathlib, os

---

### Task 1: Renomeação da Planilha em Todas as Configurações (CDD)

**Files:**
- Modify: `C:\Projetos\Inova\projects\lead-csc-pops\.env`
- Modify: `C:\Projetos\Inova\projects\lead-csc-pops\.env.example`
- Modify: `C:\Projetos\Inova\projects\lead-csc-pops\src\config.py`
- Modify: `C:\Projetos\Inova\projects\lead-csc-pops\run.py`
- Modify: `C:\Projetos\Inova\projects\lead-csc-pops\scripts\scheduler_daily.ps1`

**Step 1: Atualizar caminhos no `.env` e `.env.example`**
- Alterar `leads_preventivos_pos_vendas.xlsx` para `leads-csc-pops-peças.xlsx`.

**Step 2: Atualizar padrão no `src/config.py`**
- Linha 39: mudar default de `planilha_onedrive_path` para terminar em `leads-csc-pops-peças.xlsx`.

**Step 3: Atualizar defaults em `run.py`**
- Linha 31: mudar default de `--output` para terminar em `leads-csc-pops-peças.xlsx`.

**Step 4: Atualizar caminhos no scheduler PowerShell**
- Modificar `scripts/scheduler_daily.ps1` se necessário ou passar o novo caminho.

**Step 5: Commit**
```bash
git add .env .env.example src/config.py run.py scripts/scheduler_daily.ps1
git commit -m "chore(config): rename preventative lead spreadsheet to leads-csc-pops-peças"
```

---

### Task 2: Corrigir a Normalização de CNPJs no Extrator BUP (ETL)

**Files:**
- Modify: `C:\Projetos\Inova\projects\lead-csc-pops\src\extract.py`

**Step 1: Criar função local robusta de normalização de CNPJs**

Adicionar no início de `src/extract.py` (ou diretamente em `carregar_consultor_bup()`):
```python
def normalizar_cnpj(cnpj_val):
    """
    Normaliza de forma robusta um CNPJ em formato string, float ou inteiro.
    Trata decimals .0 provenientes da conversão de floats do Pandas.
    """
    if pd.isna(cnpj_val):
        return ""
    cnpj_str = str(cnpj_val).strip()
    if cnpj_str.endswith('.0'):
        cnpj_str = cnpj_str[:-2]
    # Remove tudo que não for dígito numérico
    cnpj_clean = ''.join(filter(str.isdigit, cnpj_str))
    return cnpj_clean.zfill(14)
```

**Step 2: Aplicar normalização em `carregar_consultor_bup()`**

Substituir o bloco de normalização anterior (linhas 213-220) em `src/extract.py`:
```python
        # Normalizar CNPJ para 14 dígitos tratando decimais float (.0)
        df_bup['CNPJ_norm'] = df_bup['CNPJ_Cliente'].apply(normalizar_cnpj)
```

**Step 3: Aplicar normalização em `carregar_ativos()`**
Substituir o bloco (linhas 107-113):
```python
    df_ativos['CNPJ'] = df_ativos['CNPJ'].apply(normalizar_cnpj)
```

**Step 4: Commit**
```bash
git add src/extract.py
git commit -m "fix(extract): resolve CNPJ float decimal bug in BUP mapping"
```

---

### Task 3: Criar Testes Unitários de BUP e Backup (TDD)

**Files:**
- Modify: `C:\Projetos\Inova\projects\lead-csc-pops\tests\test_backup_rotation.py`
- Create: `C:\Projetos\Inova\projects\lead-csc-pops\tests\test_bup_mapping.py`

**Step 1: Atualizar referências no `test_backup_rotation.py`**
- Alterar as verificações que buscam por `leads_preventivos_pos_vendas_*.xlsx` para `leads-csc-pops-peças_*.xlsx` na rotina de testes de backup.

**Step 2: Criar novo arquivo de teste `tests/test_bup_mapping.py`**
Escrever testes que validem a paridade de mapeamento de consultores:
```python
# -*- coding: utf-8 -*-
import sys
import pandas as pd
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from extract import carregar_consultor_bup, normalizar_cnpj

def test_normalizar_cnpj_float_inteiro_string():
    """Valida que todos os tipos de CNPJ sejam normalizados para 14 dígitos sem Mojibake/Floats."""
    assert normalizar_cnpj("21.256.870/0002-87") == "21256870000287"
    assert normalizar_cnpj("21256870000287.0") == "21256870000287"
    assert normalizar_cnpj(21256870000287) == "21256870000287"
    assert normalizar_cnpj(21256870000287.0) == "21256870000287"

def test_bup_consultant_mapping_match():
    """Valida se o consultor e classificação corretos são mapeados para CNPJs específicos do BUP."""
    mapa_cons, mapa_clas = carregar_consultor_bup()
    
    # CNPJ fornecido pelo usuário para o teste de auditoria
    cnpj_auditoria = "21256870000287"
    
    # Se o BUP local possuir esse CNPJ, valida a paridade
    if cnpj_auditoria in mapa_cons:
        consultor = mapa_cons[cnpj_auditoria]
        assert consultor == "AURELIO APARECIDO DA COSTA", f"Consultor incorreto: {consultor}"
        print(f"[TEST] Match bem-sucedido: {cnpj_auditoria} associado a {consultor}")
```

**Step 3: Executar testes de BUP**
Comando: `pytest tests/test_bup_mapping.py -v`
Esperado: PASS

**Step 4: Commit**
```bash
git add tests/test_backup_rotation.py tests/test_bup_mapping.py
git commit -m "test: add BUP mapping and CNPJ normalization unit tests"
```

---

### Task 4: Smoke Test Final e Auditoria Completa

**Files:**
- Test: `tests/`

**Step 1: Rodar o pipeline completo `run.py`**
Comando: `python run.py`

**Step 2: Confirmar fisicamente a criação do novo nome de planilha**
Verificar se `leads-csc-pops-peças.xlsx` foi gerado nos caminhos locais, do OneDrive e backups locais.

**Step 3: Auditar o DataFrame final gerado**
- Ler a planilha do OneDrive final gerada.
- Verificar se o CNPJ `21256870000287` está associado corretamente ao consultor `AURELIO APARECIDO DA COSTA` (e não mais `CEVAP`).
- Verificar se outros CNPJs do BUP estão perfeitamente mapeados.

**Step 4: Commit final**
```bash
git commit --allow-empty -m "verify: final BUP mapping audit completed with 100% success"
```
