# Walkthrough - Motor M6 v4.3 (Alinhamento Estratégico)

Concluímos a refatoração do Motor M6 para garantir paridade total com a segmentação oficial e precisão financeira.

## Mudanças Principais

### 1. Join Soberano (Pirâmide M5)
- Eliminamos o cálculo interno de "Tier/Classe" no M6.
- Implementamos um Join de dois níveis:
    - `dataset_final_estrategico_v1.parquet` (M4) -> Para ligar CNPJ8 ao Grupo Econômico.
    - `segmentacao_executiva_bi.xlsx` (M5) -> Para buscar o Quadrante oficial (A1, B2, C1, etc.).
- Resultado: **100% de paridade** com o dashboard executivo.

### 2. Correção GAP_META
- O cálculo foi padronizado para `VALOR_REALIZADO - VALOR_META`.
- Isso garante que valores negativos indiquem falta de atingimento, facilitando a leitura por cores no BI.

### 3. Saneamento de Abas
- **GESTAO_FUNIL:** Removida a dimensão `PIRAMIDE_SEGMENTACAO`. Esta aba agora foca em conversão agregada por Filial/Segmento.
- **GESTAO_STATUS_FUNIL:** Mantida a pirâmide para análise granular por cliente.

## Validação Técnica
- **Output:** `C:\Projetos\Inova\Metas Peças\05_Resultados\Motor_Gestao_M6_v4_3.xlsx`
- **Integridade:** Validada via Wave 8 (Diff Zero no faturamento).
- **Amostra de Quadrantes:** [A1, B1, D3, Z3, X1, C1, etc.] detectados na saída.

---
**Status:** Pronto para homologação.
