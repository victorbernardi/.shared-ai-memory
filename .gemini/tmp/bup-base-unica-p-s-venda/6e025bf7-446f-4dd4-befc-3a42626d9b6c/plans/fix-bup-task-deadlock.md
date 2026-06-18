# Spec: BUP Temporal Invariant Fix

## 1. Context & Motivation
- **Failure:** `run_bup_task.bat` aborts. `test_dias_inativo_consistente_com_data_ultima_compra` fails.
- **Root Cause:** Pre-flight QA reads the previous day's `.xlsx` but calculates `Dias_Esperado` using `pd.Timestamp.now()`. Date mismatch causes artificial invariant failures.

## 2. Architecture & Constraints
Make temporal tests deterministic based on the target artifact's creation date.

**Anti-Rationalization (Strict Rules):**
- **DO NOT** change the execution order in `run_bup_task.bat`. The pre-flight QA must remain before consolidation.
- **DO NOT** bypass or disable the invariant tests.
- **DO NOT** use `pd.Timestamp.now()` or `date.today()` inside `test_dias_inativo_consistente_com_data_ultima_compra`.

## 3. Implementation Steps

1. **Refactor Test Fixture:**
   - In `tests/test_bup_output_invariants.py`, update the `df` fixture to yield a tuple `(df, file_path)` or create a new fixture `target_file_path`.
   
2. **Refactor Invariant Test:**
   - Update `test_dias_inativo_consistente_com_data_ultima_compra` to parse the reference date directly from the filename (e.g., `BUP_POS_VENDA_YYYYMMDD_HHMM.xlsx`).
   - Calculate `Dias_Esperado` using this extracted reference date instead of `pd.Timestamp.now()`.

3. **Validation:**
   - Run `python -m pytest tests/test_bup_output_invariants.py -v`. Must pass against the older `11/06/2026` file.
   - Run `run_bup_task.bat` to confirm successful pipeline execution.

## 4. Traceability
- **Skill:** `systematic-debugging`
- **Post-Action:** Run `python src/tools/stout_promote.py` after verification.