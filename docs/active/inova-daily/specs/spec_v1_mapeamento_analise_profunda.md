# 📝 Spec: Mapeamento de Ativos e Análise Profunda

> **Versão:** 1.0
> **Fase:** Research
> **Projeto:** Inova Daily

## 1. OBJETIVO
Catalogar todos os ativos de dados (datasets) disponíveis no ecossistema Inova/Stout para identificar oportunidades de cruzamento e extração de insights estratégicos que alimentarão o **Motor de Orquestração (Daily)**.

## 2. INVENTÁRIO DE DATASETS (Mapeamento Inicial)

| Dataset | Formato | Fonte | Descrição | Potencial de Insight |
|---------|---------|-------|-----------|----------------------|
| `dataset_ouro_identidade` | Parquet | Shared | Cadastro unificado de clientes | Base para visão 360 do cliente |
| `dataset_ouro_faturamento` | Parquet | Shared | Histórico de vendas consolidado | Análise de tendência e sazonalidade |
| `dataset_ouro_maquinas` | Parquet | Shared | Parque instalado de máquinas | Cruzamento de Market Share/Potencial |
| `dataset_ouro_pecas_grupo` | Parquet | Shared | Classificação de peças | Análise de Mix e Intensidade |
| `dataset_ouro_potencial` | Parquet | Shared | Potencial calculado por cliente | Cálculo de GAP e SOW |
| `cache_vendas_rfm` | Parquet | Shared | Segmentação RFM | Identificação de Churn e Fidelidade |
| `orçamentos_abertos` | Excel | Shared | Pipeline de vendas atual | Forecast e perda de oportunidade |
| `CEVAP_ATIVACAO` | Excel | Motor-CEVAP | Leads de ativação | Eficácia de conversão de leads |

## 3. PLANO DE ANÁLISE PROFUNDA (Scanners)

Para extrair insights sem criar complexidade desnecessária, utilizaremos a abordagem de **Engrenagens de Scanner**:

### A. Scanner de Erosão de Base
- **Input:** `rfm` + `faturamento` + `identidade`.
- **Lógica:** Identificar clientes "Ouro" que tiveram queda de >30% no faturamento nos últimos 90 dias vs histórico anual.

### B. Scanner de Oportunidade por Chassi
- **Input:** `maquinas` + `potencial` + `pecas_grupo`.
- **Lógica:** Cruzar o tipo de máquina do cliente com o mix de peças que ele compra. Identificar "GAPs Silenciosos" (máquina de alto consumo comprando apenas itens básicos).

### C. Scanner de Pipeline (Vazamento)
- **Input:** `orçamentos_abertos` + `orçamentos_cancelados` + `gap`.
- **Lógica:** Priorizar orçamentos abertos que cobrem os maiores GAPs estratégicos.

## 4. PRÓXIMAS ETAPAS (Cronograma de Research)

1. **Profiling Técnico:** Executar script de inspeção em todos os datasets `dataset_ouro_*` para confirmar schema e nulos.
2. **Entrevista com Dados:** Validar com o usuário se existem campos de "Safra" ou "Contrato" ocultos nestes datasets.
3. **Prototipagem de Insight:** Criar o primeiro "Scanner" experimental.

---
