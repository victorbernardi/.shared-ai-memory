# BUP Security Locks and Formatting Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Implement Excel security locks (VBA workbook blocking and sheet password protection), user validation rules (dates within 30 days and status dropdown lists), and styling (dotted border and FFFFC000 orange fill) in the BUP final spreadsheet, including a single-attempt write logic on OneDrive to avoid sharing link breaks.

**Architecture:** Update `scripts/consolidate_bup.py` to save a temporary local `.xlsx` spreadsheet, apply layout styles, validation rules, and sheet password (`PecasInova2026`) via `openpyxl`. If Excel COM is available (`win32com`), convert the spreadsheet to `.xlsm` injecting macro files that block copying/pasting. Save final files to OneDrive using single-attempt try-catch error logging to handle file concurrency.

**Tech Stack:** Python, Pandas, openpyxl, pywin32 (win32com), Pytest

---

### Task 1: Create Security Locks and Layout Unit Tests

**Files:**
- Create: `tests/test_bup_security_locks.py`

**Step 1: Write the failing tests**

```python
import pytest
import os
import openpyxl
from pathlib import Path

def test_sheet_protection_and_validations():
    # Arrange: Setup mock output path
    test_file = Path("data/test_output_security_locks.xlsx")
    test_file.parent.mkdir(exist_ok=True)
    
    # Create simple excel mock
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "BUP"
    # Column headers similar to BUP
    headers = [
        "CNPJ_Cliente", "Nome_Cliente", "Data_Tentativa_1", "Status_Contato_1",
        "Data_Tentativa_2", "Status_Contato_2", "Observacao"
    ]
    ws.append(headers)
    ws.append(["12345678000199", "Cliente Teste", "", "Pendente", "", "Pendente", ""])
    wb.save(test_file)
    
    # Import locally from consolidate_bup
    from scripts.consolidate_bup import _aplicar_protecao_excel
    
    # Act: Apply formatting and protection
    _aplicar_protecao_excel(test_file)
    
    # Assert
    wb_result = openpyxl.load_workbook(test_file)
    ws_result = wb_result.active
    
    # 1. Sheet must be protected with password
    assert ws_result.protection.sheet is True
    assert ws_result.protection.password is not None
    # 2. autoFilter and sort must be False (unblocked)
    assert ws_result.protection.autoFilter is False
    assert ws_result.protection.sort is False
    
    # 3. Editable cells must not be locked
    header_map = {ws_result.cell(row=1, column=c).value: c for c in range(1, ws_result.max_column + 1)}
    for col_name in ["Data_Tentativa_1", "Status_Contato_1", "Data_Tentativa_2", "Status_Contato_2", "Observacao"]:
        col_idx = header_map[col_name]
        cell = ws_result.cell(row=2, column=col_idx)
        assert cell.protection.locked is False
        # Style check: background FFFFC000 (orange)
        assert cell.fill.start_color.rgb == "FFFFC000"
        # Style check: dotted border
        assert cell.border.left.style == "dotted"
        assert cell.border.right.style == "dotted"
        assert cell.border.top.style == "dotted"
        assert cell.border.bottom.style == "dotted"
        
    # 4. Structured cell must be locked
    locked_cell = ws_result.cell(row=2, column=header_map["CNPJ_Cliente"])
    assert locked_cell.protection.locked is True or locked_cell.protection.locked is None
    
    # 5. Data validations must exist
    assert len(ws_result.data_validations.dataValidation) >= 2
    
    # Cleanup
    wb_result.close()
    if test_file.exists():
        test_file.unlink()
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_bup_security_locks.py -v`
Expected: FAIL with "ImportError: cannot import name '_aplicar_protecao_excel' from 'scripts.consolidate_bup'"

---

### Task 2: Implement VBA Constants and Support Functions in `consolidate_bup.py`

**Files:**
- Modify: `scripts/consolidate_bup.py` (Add constants, `_aplicar_protecao_excel`, `_converter_para_xlsm`, and `_corrigir_formato_datas_tentativa`)

**Step 1: Write the implementation**

Add the following imports at the top of `scripts/consolidate_bup.py`:
```python
from openpyxl import load_workbook
from openpyxl.styles import Protection, PatternFill, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter
from datetime import date, timedelta
```

Define constant globals and support functions in `scripts/consolidate_bup.py`:
```python
SENHA_PROTECAO = "PecasInova2026"
OUTPUT_NAME = "BUP_POS_VENDA"

_VBA_THISWORKBOOK = (
    "Private Sub Workbook_Activate()\r\n"
    "    Application.OnKey \"^c\", \"BloqCopiar\"\r\n"
    "    Application.OnKey \"^x\", \"BloqCopiar\"\r\n"
    "    Application.OnKey \"^v\", \"BloqColar\"\r\n"
    "    Application.OnKey \"^{INSERT}\", \"BloqCopiar\"\r\n"
    "    Application.OnKey \"+{INSERT}\", \"BloqColar\"\r\n"
    "    Application.OnKey \"+{DELETE}\", \"BloqCopiar\"\r\n"
    "End Sub\r\n"
    "\r\n"
    "Private Sub Workbook_Deactivate()\r\n"
    "    Application.OnKey \"^c\"\r\n"
    "    Application.OnKey \"^x\"\r\n"
    "    Application.OnKey \"^v\"\r\n"
    "    Application.OnKey \"^{INSERT}\"\r\n"
    "    Application.OnKey \"+{INSERT}\"\r\n"
    "    Application.OnKey \"+{DELETE}\"\r\n"
    "    Application.StatusBar = False\r\n"
    "End Sub\r\n"
    "\r\n"
    "Private Sub Workbook_SheetSelectionChange(ByVal Sh As Object, ByVal Target As Range)\r\n"
    "    Application.CutCopyMode = False\r\n"
    "End Sub\r\n"
    "\r\n"
    "Private Sub Workbook_SheetBeforeRightClick(ByVal Sh As Object, ByVal Target As Range, Cancel As Boolean)\r\n"
    "    Dim cell As Range\r\n"
    "    For Each cell In Target\r\n"
    "        If cell.Locked Then\r\n"
    "            Cancel = True\r\n"
    "            Exit For\r\n"
    "        End If\r\n"
    "    Next cell\r\n"
    "End Sub"
)

_VBA_MODULO_BLOQUEIO = (
    "Sub BloqCopiar()\r\n"
    "    Application.CutCopyMode = False\r\n"
    "    Application.StatusBar = \"Cópia não permitida nesta planilha.\"\r\n"
    "End Sub\r\n"
    "\r\n"
    "Sub BloqColar()\r\n"
    "    Application.StatusBar = \"Colar bloqueado nesta planilha.\"\r\n"
    "End Sub"
)

def _aplicar_protecao_excel(path: _Path) -> None:
    wb = load_workbook(path)
    ws = wb.active
    max_row = ws.max_row

    header = {ws.cell(row=1, column=c).value: c for c in range(1, ws.max_column + 1)}
    
    colunas_filipe = [
        "Data_Tentativa_1", "Status_Contato_1",
        "Data_Tentativa_2", "Status_Contato_2", "Observacao"
    ]
    colunas_editaveis = set(colunas_filipe)

    # Styles
    fill_orange = PatternFill(start_color="FFFFC000", end_color="FFFFC000", fill_type="solid")
    border_dotted = Border(
        left=Side(style="dotted", color="808080"),
        right=Side(style="dotted", color="808080"),
        top=Side(style="dotted", color="808080"),
        bottom=Side(style="dotted", color="808080")
    )
    unlocked = Protection(locked=False)

    # Apply AutoFilter
    ws.auto_filter.ref = ws.dimensions

    # Auto-width adjustment
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        col_name = ws.cell(row=1, column=col[0].column).value
        if col_name == "Equipamentos":
            ws.column_dimensions[col_letter].width = 45
        else:
            max_len = max((len(str(cell.value or "")) for cell in col), default=0)
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 60)

    # Unlock, Fill Orange and apply Dotted Border to feedback fields
    for col_name in colunas_editaveis:
        if col_name not in header:
            continue
        col_idx = header[col_name]
        for row in ws.iter_rows(min_row=2, max_row=max_row, min_col=col_idx, max_col=col_idx):
            row[0].protection = unlocked
            row[0].fill = fill_orange
            row[0].border = border_dotted

    # Format percentage for SOW
    if "SOW" in header:
        sow_col = header["SOW"]
        for row in ws.iter_rows(min_row=2, max_row=max_row, min_col=sow_col, max_col=sow_col):
            row[0].number_format = "0.0%"

    # Add Dropdowns for Status_Contato_1 & 2
    opcoes = '"Pendente,Venda,Não Venda"'
    for col_name in ["Status_Contato_1", "Status_Contato_2"]:
        if col_name not in header:
            continue
        col_letter = ws.cell(row=1, column=header[col_name]).column_letter
        dv = DataValidation(type="list", formula1=opcoes, allow_blank=True)
        dv.add(f"{col_letter}2:{col_letter}{max_row}")
        ws.add_data_validation(dv)

    # Add Date Validation (hoje - 30 days, hoje + 30 days)
    hoje = date.today()
    min_date = hoje - timedelta(days=30)
    max_date = hoje + timedelta(days=30)
    serial_min = (min_date - date(1899, 12, 30)).days
    serial_max = (max_date - date(1899, 12, 30)).days
    msg_erro = (
        f"Informe uma data entre {min_date.strftime('%d/%m/%Y')} "
        f"e {max_date.strftime('%d/%m/%Y')}."
    )
    for col_name in ["Data_Tentativa_1", "Data_Tentativa_2"]:
        if col_name not in header:
            continue
        col_idx = header[col_name]
        col_letter = ws.cell(row=1, column=col_idx).column_letter
        for row in ws.iter_rows(min_row=2, max_row=max_row, min_col=col_idx, max_col=col_idx):
            row[0].number_format = "DD/MM/YYYY"
        
        dv_data = DataValidation(
            type="date",
            operator="between",
            formula1=str(serial_min),
            formula2=str(serial_max),
            allow_blank=True,
            showErrorMessage=True,
            errorTitle="Data inválida",
            error=msg_erro,
        )
        dv_data.add(f"{col_letter}2:{col_letter}{max_row}")
        ws.add_data_validation(dv_data)

    # Apply protection password, allowing autoFilter and sort
    ws.protection.sheet = True
    ws.protection.password = SENHA_PROTECAO
    ws.protection.autoFilter = False  # False = Allow filtering
    ws.protection.sort = False        # False = Allow sorting
    ws.protection.enable()

    wb.save(path)

def _corrigir_formato_datas_tentativa(xlsm_path: _Path) -> None:
    wb = load_workbook(xlsm_path, keep_vba=True)
    ws = wb.active
    header = {ws.cell(row=1, column=c).value: c for c in range(1, ws.max_column + 1)}
    for col_name in ["Data_Tentativa_1", "Data_Tentativa_2"]:
        if col_name not in header:
            continue
        col_idx = header[col_name]
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=col_idx, max_col=col_idx):
            row[0].number_format = "DD/MM/YYYY"
    wb.save(xlsm_path)

def _converter_para_xlsm(xlsx_path: _Path, xlsm_path: _Path) -> bool:
    try:
        import win32com.client as win32

        excel = win32.Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False

        try:
            wb = excel.Workbooks.Open(str(xlsx_path.resolve()))
            wb.SaveAs(str(xlsm_path.resolve()), FileFormat=52)
            wb.Close(SaveChanges=False)

            wb = excel.Workbooks.Open(str(xlsm_path.resolve()))
            wb_module = None
            for name in ("EstaPastaDeTrabalho", "ThisWorkbook"):
                try:
                    wb_module = wb.VBProject.VBComponents(name).CodeModule
                    break
                except Exception:
                    continue
            if wb_module is None:
                for i in range(wb.VBProject.VBComponents.Count, 0, -1):
                    comp = wb.VBProject.VBComponents.Item(i)
                    if comp.Type == 100:
                        wb_module = comp.CodeModule
                        break
            if wb_module is not None:
                wb_module.AddFromString(_VBA_THISWORKBOOK)
            else:
                print("AVISO: Módulo workbook não encontrado no VBA.")

            mod_std = wb.VBProject.VBComponents.Add(1)
            mod_std.Name = "ModCEVAP"
            mod_std.CodeModule.AddFromString(_VBA_MODULO_BLOQUEIO)

            wb.Save()
            wb.Close(SaveChanges=False)
            return wb_module is not None
        except Exception as exc:
            print(f"AVISO: Falha ao injetar VBA COM: {exc}")
            return False
        finally:
            excel.Quit()
    except ImportError:
        print("AVISO: pywin32/win32com não disponível — fallback sem VBA.")
        return False
```

**Step 2: Run test to verify it passes**

Run: `python -m pytest tests/test_bup_security_locks.py -v`
Expected: PASS

---

### Task 3: Update `run_consolidation` Export Logic in `consolidate_bup.py`

**Files:**
- Modify: `scripts/consolidate_bup.py:819-899`

**Step 1: Write the implementation**

Replace the current Excel output block (lines 819-845) in `scripts/consolidate_bup.py` with:

```python
    # 9. EXPORTAÇÃO E PROTEÇÃO
    xlsx_intermediario = DATA_DIR / f"{OUTPUT_NAME}_{timestamp}_tmp.xlsx"
    output_filename = f"{OUTPUT_NAME}_{timestamp}.xlsm"
    output_path = os.path.join(DIR_OUTPUT, output_filename)
    output_fixo = DATA_DIR / f"{OUTPUT_NAME}.xlsm"
    
    # Formatar datas estruturais (apenas visual string)
    cols_data_leitura = ["Data_Ultima_Compra", "Data_Ultimo_Orcamento"]
    for col in cols_data_leitura:
        if col in df_final.columns:
            df_final[col] = pd.to_datetime(df_final[col], errors="coerce").dt.strftime("%d/%m/%Y").fillna("")

    # Garantir que as datas de tentativas sejam passadas como strings limpas
    # Sem remover ou apagar datas legadas que violam a janela
    for col in ["Data_Tentativa_1", "Data_Tentativa_2"]:
        if col in df_final.columns:
            df_final[col] = df_final[col].fillna("").astype(str).str.strip()

    # Saneamento prévio das observações do histórico
    if "Observacao" in df_final.columns:
        df_final["Observacao"] = df_final["Observacao"].fillna("").astype(str).str.strip()

    # Gravar arquivo intermediário local
    df_final.to_excel(xlsx_intermediario, index=False)

    # Aplicar segurança, formatação e validações via openpyxl
    _aplicar_protecao_excel(xlsx_intermediario)
    print("INFO: Segurança e validações aplicadas no arquivo Excel.")

    # Injetar VBA e converter para .xlsm
    xlsm_target = _Path(output_path)
    vba_ok = _converter_para_xlsm(xlsx_intermediario, xlsm_target)
    
    if vba_ok:
        xlsx_intermediario.unlink(missing_ok=True)
        _corrigir_formato_datas_tentativa(xlsm_target)
        # Atualizar arquivos fixos locais
        shutil.copy2(output_path, output_fixo)
        print(f"INFO: Arquivo final protegido com VBA gerado: {xlsm_target.name}")
    else:
        # Fallback: Renomear .xlsx para .xlsm/xlsx fixos sem VBA
        output_filename = f"{OUTPUT_NAME}_{timestamp}.xlsx"
        output_path = os.path.join(DIR_OUTPUT, output_filename)
        output_fixo = DATA_DIR / f"{OUTPUT_NAME}.xlsx"
        xlsx_intermediario.rename(output_path)
        shutil.copy2(output_path, output_fixo)
        print(f"AVISO: Executado fallback sem VBA: {output_filename}")

    # Cópia para OneDrive (Tentativa única sem loop de concorrência)
    onedrive_docs = os.path.expandvars(
        r"%USERPROFILE%\OneDrive - INOVA EQUIPAMENTOS LTDA\Documentos"
    )
    # Definir extensão com base no formato real gerado
    ext = ".xlsm" if vba_ok else ".xlsx"
    onedrive_destino = os.path.join(onedrive_docs, f"{OUTPUT_NAME}{ext}")
    onedrive_status = "OK"
    
    if os.path.exists(onedrive_docs):
        try:
            # Remover destino anterior se for de extensão diferente (evitar arquivos duplicados)
            outro_ext = ".xlsx" if ext == ".xlsm" else ".xlsm"
            outro_destino = os.path.join(onedrive_docs, f"{OUTPUT_NAME}{outro_ext}")
            if os.path.exists(outro_destino):
                try: os.remove(outro_destino)
                except: pass
                
            shutil.copy2(output_path, onedrive_destino)
            print(f"INFO: Planilha protegida entregue no OneDrive: {onedrive_destino}")
        except PermissionError as perm_err:
            onedrive_status = f"CONFLITO/BLOQUEADO (Arquivo em uso: {str(perm_err)})"
            print(f"\n================================================================================")
            print(f"ATENÇÃO: A planilha de entrega no OneDrive está aberta por outro usuário.")
            print(f"A atualização foi pulada para não quebrar o link de compartilhamento.")
            print(f"Os novos dados foram salvos localmente em: {output_fixo}")
            print(f"================================================================================\n")
        except Exception as exc:
            onedrive_status = f"FALHA: {str(exc)}"
            print(f"AVISO: Falha ao copiar para OneDrive: {exc}")
    else:
        onedrive_status = "AVISO: Pasta do OneDrive indisponível"
```

**Step 2: Run all test suites to verify integration**

Run:
```bash
python -m pytest tests/ -v
```
Expected: All tests pass (including new security locks test and existing invariants/integration).

---

### Task 4: Run Final Consolidation QA Check

**Files:**
- Test output validation

**Step 1: Execute local consolidation**

Run: `python scripts/consolidate_bup.py`
Expected: Consolidates BUP with warnings/info on security layout generation, opens log file, shows SUCCESS.
