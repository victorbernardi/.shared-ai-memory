# Walkthrough: Whitelist Fix & SQL Optimization

## 🎯 Objective
Resolve the "ID Overlap" issue in Protheus where sales from Roberto's team were being attributed to noise consultants (Julio Cesar, etc.), and fix a SQL syntax error in the "Last Sale" query.

## 🛠️ Changes Made

### 1. Noise Purge (Governance)
*   **File**: `data/config/segment_rules.json`
*   Added identified noise names (`JULIO CESAR DA CRUZ BARBOSA`, `VITORIA EDUARDA NOGUEIRA CARDOSO`, etc.) to the `vendedores_bloqueados_nomes` list.

### 2. Priority Mapping (Engine)
*   **File**: `scripts/consolidate_bup.py`
*   Refactored the name mapping logic to give **Absolute Priority** to the `vendedores_ativos_2026.json` configuration.
*   Applied the name blacklist during the `SA3010` load to prevent polluted IDs from entering the mapping dictionary.

### 3. SQL Error Fix
*   **File**: `scripts/consolidate_bup.py`
*   Fixed an `Invalid column name 'F2_TES'` error in `query_last_sale_active` by using direct filial and date filters for the header table, ensuring the "Last Sale" consultant is correctly identified.

### 4. Configuration Refresh
*   Executed `scripts/generate_active_sellers_config.py` to regenerate the clean whitelist JSON.

## ✅ Verification Results

### Terminal Output (Success)
```text
INFO: Mapa de vendedores sincronizado com a configuração oficial (14 nomes).
OK: 691 linhas retornadas (Last Sale Query)
OK: 1,896 linhas retornadas (Orcamento Query)
--- SUCESSO ---
Arquivo gerado: BUP_POS_VENDA_20260513_1955.xlsx
```

## 🚀 Next Steps
*   Deliver the generated Excel to the Pós-Venda team for validation.
*   Monitor for any new ID overlaps as the team expands.
