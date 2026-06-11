# ESPECIFICAÇÃO: Ajuste de Colunas (Motor CEVAP v2)

## 1. Problema Identificado
A planilha atual (`CEVAP_ATIVACAO_20260506_1100.xlsx`) não está aderente ao dicionário de dados oficial (`DICIONARIO_DADOS_CEVAP.md`).
- **Nomes divergentes:** Ex: `Nome_Cliente` (script) vs `Cliente` (Dicionário).
- **Colunas ausentes:** `Cidade`, `Segmento`, `SOW`.

## 2. Escopo de Ajuste
- **Mapeamento:** 
    - `CNPJ_Cliente` -> `CNPJ_Cliente`
    - `Nome_Cliente` -> `Cliente`
    - `A1_MUN` (do SA1010) -> `Cidade`
    - `Status_Fidelidade` (do M5) -> `Segmento`
    - `SOW_Total_Auditado` (do M5) -> `SOW`
- **Reorganização:** Seguir exatamente a ordem do Dicionário de Dados.
