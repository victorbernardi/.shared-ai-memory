# Spec v1.2 — Inova M6 Automated Deployment (Lean Edition)

## 1. Visão Geral
Remoção total da granularidade transacional no output do Motor M6 para otimizar o consumo por ferramentas de BI e reduzir o footprint de armazenamento.

## 2. Estrutura de Dados (Excel Output)
O arquivo `Motor_Gestao_M6_v4_3.xlsx` deve conter exclusivamente:
1. `GESTAO_PERFORMANCE`: Dados agregados por Filial/Segmento/Mês.
2. `GESTAO_CONSULTOR`: Dados agregados por Consultor.
3. `GESTAO_FUNIL`: Dados agregados de orçamentos por Filial.
4. `GESTAO_STATUS_FUNIL`: Pipeline por status e aging.

## 3. Gating de Auditoria (Wave 8)
A auditoria passa a ser puramente financeira:
- **Critério 1**: `Soma(VALOR_DO_PRODUTO)` do CSV de Vendas == `Soma(VALOR_REALIZADO)` da aba `GESTAO_PERFORMANCE`.
- **Critério 2**: `Soma(VALOR_ORCAMENTO)` do CSV de Funil == `Soma(VALOR_FUNIL)` da aba `GESTAO_PERFORMANCE`.
- **Tolerância**: R$ 1,00.
- **Duplicidade**: Não auditada no output (confiança delegada ao processamento da Wave 4).

## 4. Pipeline de Orquestração (Wave 9)
O fluxo permanece atômico:
1. **Wave 4**: Processamento -> Geração de Excel (4 abas).
2. **Wave 8**: Auditoria de Paridade Financeira.
3. **Shadow Deploy**: Extrator gera `data_staging.json`.
4. **Atomic Swap**: Promoção para `data.json`.
5. **Aggregator**: Geração de snapshots para o OnePage.
