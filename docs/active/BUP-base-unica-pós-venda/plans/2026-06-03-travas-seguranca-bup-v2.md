# BUP Security Locks and Formatting - Implementation Plan (V2)

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.
> **Important:** This plan resolves the issues regarding strict status validation, copy/paste bypassing via cell selection restrictions, and sheet sorting capabilities.

**Goal:** Modify the Excel protection scheme in BUP. Apply strict list enforcement on dropdowns, block selection of locked cells via openpyxl and win32com, and configure an `AllowEditRange` named "DadosBUP" protecting the whole table with `PecasInova2026` to allow sorting while blocking unauthorized data alterations.

**Tech Stack:** Python, Pandas, openpyxl, pywin32 (win32com), Pytest

---

### Task 1: Update Security and Layout Unit Tests

**Files:**
- Modify: `tests/test_bup_security_locks.py`

**Step 1: Write the updated test assertions**
Update the unit test to verify that:
1. `selectLockedCells` is set to `False` on the sheet protection.
2. `selectUnlockedCells` is set to `True` on the sheet protection.
3. Dropdowns for `Status_Contato_1` and `Status_Contato_2` have `showErrorMessage = True` and correct error messaging/style.

```python
def test_sheet_protection_and_validations():
    # (Arrange section remains similar to V1...)
    # Assert section:
    # 1. Sheet must be protected with password
    assert ws_result.protection.sheet is True
    # 2. autoFilter and sort must be False (unblocked in openpyxl)
    assert ws_result.protection.autoFilter is False
    assert ws_result.protection.sort is False
    # 3. Locked cell selection must be disabled
    assert ws_result.protection.selectLockedCells is False
    assert ws_result.protection.selectUnlockedCells is True
    
    # 4. Data validation dropdowns must have error messages
    dvs = ws_result.data_validations.dataValidation
    status_dvs = [dv for dv in dvs if dv.type == "list"]
    assert len(status_dvs) >= 2
    for dv in status_dvs:
        assert dv.showErrorMessage is True
        assert dv.errorStyle == "stop"
        assert dv.errorTitle == "Valor inválido"
```

---

### Task 2: Implement Updates in `scripts/consolidate_bup.py`

**Files:**
- Modify: `scripts/consolidate_bup.py`

**Step 1: Modify `_aplicar_protecao_excel`**
1. Add strict data validation constraints for "Status_Contato_1" and "Status_Contato_2".
2. Turn off selection of locked cells:
   ```python
   ws.protection.selectLockedCells = False
   ws.protection.selectUnlockedCells = True
   ```

**Step 2: Modify `_converter_para_xlsm`**
Incorporate `AllowEditRanges` and protect worksheet via win32com COM automation:
1. Call `ws.Unprotect("PecasInova2026")`.
2. Clear any existing `AllowEditRange` titled "DadosBUP".
3. Calculate range boundaries up to dynamic `max_row` and `max_col`.
4. Add the `AllowEditRange` to the range with title "DadosBUP" and password "PecasInova2026".
5. Disable locked cell selection using COM property `ws.EnableSelection = 1` (which is `xlUnlockedCells`).
6. Apply COM sheet protect `ws.Protect(Password="PecasInova2026", AllowSorting=True, AllowFiltering=True)`.

---

### Task 3: Execution and Verification

**Step 1: Run local tests to ensure no regressions**
Run: `pytest tests/` (once python path or environment is verified, or using a wrapper script)

**Step 2: Run pipeline and inspect the output**
Run: `python scripts/consolidate_bup.py`
Verify logs and check generated spreadsheet `.xlsm` and `.xlsx` sizes.
