# Spec: Refinamento Motor M6 (v4.2) - Inteligência Comercial Completa

**Data:** 2026-04-29  
**Responsável:** Antigravity (Phase: Strategy)
**Status:** APROVADA

## 1. Objetivo
Unificar a visão de performance comercial (M6) com a inteligência de segmentação (Pirâmide), eliminando visões transacionais e focando em dashboards de gestão agregada por Consultor, Cliente e Status.

## 2. Requisitos Funcionais

### 2.1 Saneamento de Consultores (Master Map)
- **Fallback Manual**: Aplicar dicionário de mapeamento para os 13 IDs identificados historicamente (ex: `000306` -> `PEDRO ELIAS MOTA GOMES`).
- **IDs Não Mapeados**: Utilizar o rótulo `ID_ORFAO_[ID]`.
- **Vendas sem Vendedor**: Rótulo `VENDA_SEM_VENDEDOR_[ID]` para IDs de venda sem nome no ERP.

### 2.2 Integração da Pirâmide (Enriquecimento)
- **Cruzamento**: Cruzar a base de vendas/funil com o `dataset_final_estrategico_v1.parquet` via CNPJ Raiz (8 dígitos).
- **Match Rate Alvo**: >90% de cobertura de valor (Auditado em 91.11%).
- **Nova Coluna**: `PIRAMIDE_SEGMENTACAO` (Ex: "Tier 1 - Classe A").
- **Fallback Pirâmide**: Clientes sem match = `TIER 4 - NÃO MAPEADO`.

### 2.3 Regras de Status e Aging
- **Status "EM ABERTO"**: Agrupar os códigos de sistema `0, 2, 3` sob a nomenclatura unificada **"EM ABERTO"**.
- **Status "FATURADO"**: Códigos `F, I`.
- **Status "CANCELADO"**: Código `X`, `C` ou Flag M6 `EXPIRADO`.
- **Aging**: Manter flag `AGING_60_DIAS` para destacar orçamentos antigos no funil.

### 2.4 Estrutura de Saída (Abas Excel)
1. `GESTAO_PERFORMANCE`: Meta x Realizado por Filial/Segmento.
2. `GESTAO_CONSULTOR`: Performance e Ranking por Consultor e Cliente.
3. `GESTAO_FUNIL`: Conversão por Segmento, Origem e Pirâmide.
4. `GESTAO_STATUS_FUNIL`: Visão exclusiva de pipeline (Consultor, Cliente, Pirâmide, Segmento, Status, Aging).
    - **Métrica Adicional**: `TICKET_MEDIO` (`VALOR_FUNIL / QTDE_ORC`).

## 3. Plano de Validação
- **Auditoria de Faturamento**: O total deve ser idêntico à v3 (R$ 309M no faturamento 25/26).
- **Match de Consultores**: Validar via script de debug que os IDs de fallback estão sendo nomeados corretamente.
