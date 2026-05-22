# PLANO: Integração Final (CEVAP v4)

## 1. Execução
- **Etapa Máquinas:** 
    - Carregar `dataset_ouro_maquinas_v1.parquet`.
    - Normalizar `CNPJ Dono Oficial` para 14 dígitos.
    - Agrupar por `CNPJ Dono Oficial` e listar modelos únicos.
    - Merge no `df_cevap` usando `CNPJ_Cliente`.
- **Etapa Orçamentos:**
    - Carregar `tabela_orçamentos_abertos.xlsx` e `tabela_orçamentos_cancelados.xlsx`.
    - Unificar ambas as tabelas para obter o histórico completo.
    - Agrupar por Raiz (8 dígitos) para contar o total de orçamentos por grupo econômico no período.
    - Renomear contagem para `N_Orcamento_12m` e mergear no `df_cevap`.
- **Validação (TDD):**
    - Adicionar ao `tests/test_columns.py` check de valores não nulos para as novas colunas.
