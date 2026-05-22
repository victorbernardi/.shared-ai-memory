# Adopt Discrete Yearly Sales Logic for Performance Reporting

* Status: accepted
* Date: 2026-05-13
* Decision-makers: Antigravity, User

## Context and Problem Statement

The sales performance report was initially implementing a cumulative-to-discrete subtraction logic (e.g., `Year2 = Last24m - Last12m`). However, inspection of the source data (Excel and Parquet) revealed that the input columns `VENDAS ÚLT. 12`, `24`, and `36` already represent discrete yearly billing safra (Safra 25/26, 24/25, 23/24). 

Using subtraction on discrete values caused mathematical distortions:
1. Intermediate years (24/25) were erroneously zeroed when Year 2 < Year 1.
2. Past years (23/24) were underestimated.
3. Financial "Dropout" (Gap) calculations lacked auditing integrity.

## Decision Outcome

Chosen option: **Adopt Discrete Logic**, because it aligns with the data source's native structure and provides high-fidelity trend analysis.

### Consequences

* **Good:** Accurate visualization of sales trends across the 3-year window.
* **Good:** Correct calculation of the "Gap de Performance" based on real billing safras.
* **Bad:** Previous versions of the report (v6.2 and below) are now considered mathematically invalid for trend analysis.

### Confirmation

* Generate PDF v6.4 and verify that items with discrete values in Excel (e.g., `AT338612`) show the correct matching values in the report bars without any subtraction logic.
