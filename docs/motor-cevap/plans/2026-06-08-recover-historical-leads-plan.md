# [Recuperação Histórica de Leads] Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Recuperar contatos e observações inseridos em planilhas históricas antigas do CEVAP e reinseri-los de forma higienizada na planilha ativa do OneDrive para leads que estão como Pendentes.

**Architecture:** Script de recuperação autônomo e temporário (`recover_historical_leads.py`) que varre recursivamente a pasta `data/`, ordena os arquivos cronologicamente a partir do timestamp do nome, extrai os registros preenchidos mais recentes e mescla-os na planilha atual de forma direcionada apenas aos registros com status "Pendente".

**Tech Stack:** Python 3.12, Pandas, Openpyxl, Pytest

---

### Task 1: Criar Testes Unitários de Recuperação

**Files:**
- Create: `tests/test_recovery.py`

**Step 1: Escrever código do teste unitário**
```python
import pandas as pd
import pytest
from pathlib import Path
import sys
import shutil

# Garantir imports corretos
_scripts_dir = Path(__file__).parents[1] / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

def test_resolve_conflicts_chronologically(tmp_path):
    # Criar dados mock de teste
    # Arquivo antigo (2026-05-01):
    df_old = pd.DataFrame({
        "CNPJ_Cliente": ["12345678000199", "98765432000188"],
        "Nome_Cliente": ["Cliente A", "Cliente B"],
        "Data_Tentativa_1": ["01/05/2026", ""],
        "Status_Contato_1": ["Venda", "Pendente"],
        "Observacao": ["Vendido na planilha antiga", ""]
    })
    
    # Arquivo mais recente (2026-05-10):
    df_new = pd.DataFrame({
        "CNPJ_Cliente": ["12345678000199", "98765432000188"],
        "Nome_Cliente": ["Cliente A", "Cliente B"],
        "Data_Tentativa_1": ["10/05/2026", "10/05/2026"],
        "Status_Contato_1": ["Nao Venda", "Sem Contato"],
        "Observacao": ["Nao aceitou na mais recente", "Nao atendeu"]
    })

    # Planilha atual onde o Cliente B está Pendente e o A está resolvido como Venda
    df_atual = pd.DataFrame({
        "CNPJ_Cliente": ["12345678000199", "98765432000188"],
        "Nome_Cliente": ["Cliente A", "Cliente B"],
        "Data_Tentativa_1": ["12/05/2026", ""],
        "Status_Contato_1": ["Venda", "Pendente"],
        "Observacao": ["Vendido na atual", ""]
    })

    # Mocking das funções internas de recover_historical_leads
    from recover_historical_leads import process_recovery_in_memory
    
    recovered = process_recovery_in_memory(df_atual, [df_new, df_old])
    
    # Cliente A: Já estava como "Venda" na atual (Ciclo Fechado) -> Deve permanecer inalterado
    assert recovered.loc[recovered["CNPJ_Cliente"] == "12345678000199", "Observacao"].values[0] == "Vendido na atual"
    
    # Cliente B: Estava "Pendente" na atual -> Deve recuperar o preenchimento da df_new (mais recente que a antiga)
    assert recovered.loc[recovered["CNPJ_Cliente"] == "98765432000188", "Status_Contato_1"].values[0] == "Sem Contato"
    assert recovered.loc[recovered["CNPJ_Cliente"] == "98765432000188", "Observacao"].values[0] == "Nao atendeu"
```

**Step 2: Rodar teste para verificar que falha por falta do módulo**
Run: `pytest tests/test_recovery.py`
Expected: FAIL (ModuleNotFoundError)

---

### Task 2: Desenvolver o Script de Recuperação

**Files:**
- Create: `scripts/recover_historical_leads.py`
- Test: `tests/test_recovery.py`

**Step 1: Implementar o script com a lógica descrita na especificação**
```python
import pandas as pd
import re
import os
from pathlib import Path
from datetime import datetime

COLUNAS_CONTROLE = [
    "Data_Tentativa_1", "Status_Contato_1",
    "Data_Tentativa_2", "Status_Contato_2", "Observacao"
]

def clean_cnpj(val):
    if pd.isna(val):
        return ""
    cleaned = re.sub(r"\D", "", str(val))
    return cleaned.zfill(14)

def normalizar_status(val):
    if pd.isna(val) or str(val).strip() == "" or str(val).strip().lower() == "pendente":
        return "Pendente"
    val_clean = str(val).strip().lower()
    if "não venda" in val_clean or "nao venda" in val_clean:
        return "Nao Venda"
    if "venda" in val_clean:
        return "Venda"
    if "sem contato" in val_clean or "sem_contato" in val_clean:
        return "Sem Contato"
    return str(val).strip()

def process_recovery_in_memory(df_atual, dfs_historicas):
    """
    df_atual: DataFrame da planilha ativa
    dfs_historicas: Lista de DataFrames historicos ordenados do mais recente para o mais antigo
    """
    df_res = df_atual.copy()
    df_res["CNPJ_Cliente"] = df_res["CNPJ_Cliente"].apply(clean_cnpj)
    
    # Identificar quais leads estão com ciclo em aberto (Pendentes)
    leads_pendentes = df_res[
        (df_res["Status_Contato_1"].fillna("").str.lower() == "pendente") |
        (df_res["Status_Contato_1"].isna()) |
        (df_res["Status_Contato_1"] == "")
    ]["CNPJ_Cliente"].unique()
    
    # Construir mapa consolidado dos preenchimentos historicos mais recentes
    preenchimento_map = {}
    
    for df_hist in dfs_historicas:
        df_h = df_hist.copy()
        if "CNPJ_Cliente" not in df_h.columns:
            continue
        df_h["CNPJ_Cliente"] = df_h["CNPJ_Cliente"].apply(clean_cnpj)
        
        # Filtrar linhas que possuem algum dado preenchido de fato nas colunas de controle
        for _, row in df_h.iterrows():
            cnpj = row["CNPJ_Cliente"]
            if not cnpj:
                continue
            if cnpj not in leads_pendentes:
                continue
            if cnpj in preenchimento_map:
                continue # Ja pegamos da planilha mais recente
                
            # Verificar se tem algum dado preenchido
            has_data = False
            for col in COLUNAS_CONTROLE:
                if col in row and pd.notna(row[col]) and str(row[col]).strip() != "" and str(row[col]).strip().lower() != "pendente":
                    has_data = True
                    break
            
            if has_data:
                preenchimento_map[cnpj] = {
                    col: row[col] if col in row and pd.notna(row[col]) else ""
                    for col in COLUNAS_CONTROLE
                }
                
    # Aplicar o resgate no DataFrame atual
    updates_count = 0
    for idx, row in df_res.iterrows():
        cnpj = row["CNPJ_Cliente"]
        if cnpj in preenchimento_map:
            for col in COLUNAS_CONTROLE:
                val = preenchimento_map[cnpj][col]
                if col in ["Status_Contato_1", "Status_Contato_2"]:
                    val = normalizar_status(val)
                df_res.at[idx, col] = val
            updates_count += 1
            
    print(f"[PROCESSADOR] {updates_count} leads pendentes foram atualizados com dados historicos.")
    return df_res

def run_recovery(dry_run=True):
    # Definicao de caminhos
    base_dir = Path(__file__).parents[1]
    data_dir = base_dir / "data"
    onedrive_path = Path(r"C:\Users\victor.bernardi\OneDrive - INOVA EQUIPAMENTOS LTDA\Documentos\CEVAP_ATIVACAO.xlsx")
    
    # 1. Carregar planilha atual
    if not onedrive_path.exists():
        # Fallback para a mais recente na pasta data
        xlsx_files = list(data_dir.glob("CEVAP_ATIVACAO_*.xlsx"))
        if not xlsx_files:
            print("[ERRO] Nenhuma planilha atual encontrada!")
            return
        xlsx_files.sort()
        target_path = xlsx_files[-1]
    else:
        target_path = onedrive_path
        
    print(f"[RECOVERY] Lendo planilha ativa de: {target_path}")
    df_atual = pd.read_excel(target_path)
    
    # 2. Varrer e carregar planilhas historicas
    xlsx_files = list(data_dir.glob("CEVAP_ATIVACAO_*.xlsx"))
    
    # Extrair timestamp e ordenar decrescente
    file_map = []
    for f in xlsx_files:
        match = re.search(r"(\d{8}_\d{4})", f.name)
        if match:
            dt = datetime.strptime(match.group(1), "%Y%m%d_%H%M")
            file_map.append((dt, f))
            
    file_map.sort(key=lambda x: x[0], reverse=True)
    
    dfs_historicas = []
    for dt, f in file_map:
        try:
            df = pd.read_excel(f)
            dfs_historicas.append(df)
            print(f"[RECOVERY] Carregado historico: {f.name} ({dt})")
        except Exception as e:
            print(f"[AVISO] Ignorando arquivo corrompido: {f.name}. Erro: {e}")
            
    # 3. Executar o processador de mesclagem
    df_final = process_recovery_in_memory(df_atual, dfs_historicas)
    
    # 4. Gerar relatorio Markdown
    report_filename = f"{datetime.now().strftime('%Y-%m-%d')}-auditoria-leads.md"
    report_path = base_dir / "docs" / "specs" / report_filename
    
    # Calcular diferencas para auditoria
    changes = []
    df_atual["CNPJ_Cliente"] = df_atual["CNPJ_Cliente"].apply(clean_cnpj)
    for idx, row in df_final.iterrows():
        cnpj = row["CNPJ_Cliente"]
        original_row = df_atual[df_atual["CNPJ_Cliente"] == cnpj]
        if original_row.empty:
            continue
        orig = original_row.iloc[0]
        
        # Mudou alguma coluna de controle?
        changed = False
        for col in COLUNAS_CONTROLE:
            if str(row[col]) != str(orig[col]):
                changed = True
                break
        if changed:
            changes.append({
                "CNPJ": cnpj,
                "Nome": row["Nome_Cliente"],
                "Orig_Status": orig["Status_Contato_1"],
                "New_Status": row["Status_Contato_1"],
                "Orig_Obs": orig["Observacao"],
                "New_Obs": row["Observacao"]
            })
            
    # Escrever arquivo de relatorio
    with open(report_path, "w", encoding="utf-8") as f_rep:
        f_rep.write(f"# Relatório de Auditoria de Recuperação de Leads\n\n")
        f_rep.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        f_rep.write(f"Modo Dry-Run: {dry_run}\n\n")
        f_rep.write(f"Total de leads recuperados do histórico: {len(changes)}\n\n")
        f_rep.write(f"## Detalhes das Alterações Propostas\n\n")
        f_rep.write(f"| CNPJ | Cliente | Status Anterior | Novo Status | Obs Anterior | Nova Obs |\n")
        f_rep.write(f"|---|---|---|---|---|---|\n")
        for c in changes:
            f_rep.write(f"| {c['CNPJ']} | {c['Nome']} | {c['Orig_Status']} | {c['New_Status']} | {c['Orig_Obs']} | {c['New_Obs']} |\n")
            
    print(f"[RECOVERY] Relatorio gravado em: {report_path}")
    
    # 5. Salvar de verdade se nao for dry-run
    if not dry_run:
        df_final.to_excel(target_path, index=False, engine="openpyxl")
        # Re-aplicar protecoes de planilha do motor principal
        from consolidate_cevap import _aplicar_protecao_excel
        _aplicar_protecao_excel(str(target_path), COLUNAS_CONTROLE)
        print(f"[OK] Alteracoes salvas fisicamente em: {target_path}")

if __name__ == "__main__":
    import sys
    dry = True
    if len(sys.argv) > 1 and sys.argv[1] == "--write":
        dry = False
    run_recovery(dry_run=dry)
```

**Step 2: Rodar o teste unitário**
Run: `pytest tests/test_recovery.py`
Expected: PASS

---

### Task 3: Gerar Relatório Dry-Run para Aprovação

**Files:**
- Test: Execução do script `scripts/recover_historical_leads.py`

**Step 1: Rodar o script no modo Dry-Run**
Run: `python C:/Projetos/Inova/projects/motor-cevap/scripts/recover_historical_leads.py`
Expected: Execução bem-sucedida gerando o relatório Markdown de auditoria sem alterar o arquivo principal.

**Step 2: Submeter relatório para análise humana**
Aguardar validação humana das alterações no arquivo gerado em `docs/specs/YYYY-MM-DD-auditoria-leads.md`.
