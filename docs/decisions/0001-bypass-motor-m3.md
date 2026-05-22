# ADR 0001: Bypass do Motor M3 para Recuperação de Datas de Faturamento

*   **Status:** Aceito
*   **Data:** 2026-05-06
*   **Decisores:** Arquiteto de Design Agêntico, Victor Bernardi
*   **Consultados:** Engenheiro de Dados

## Contexto e Problema
O arquivo oficial de saída do Motor M3 (`cache_vendas_rfm.parquet`) apresentou uma degradação de dados crítica, com aproximadamente **67% de valores NaT** na coluna `DATA_EMISSAO_NF`. Isso resultava em cálculos incorretos de inatividade, marcando clientes ativos (ex: FERRO, VRENTAL) como inativos de longa data (999 dias).

A entrega do Motor CEVAP era urgente e não havia tempo hábil para debugar e reprocessar todo o motor M3 original no momento da detecção.

## Opções Consideradas
1.  **Aguardar correção do M3:** Inviável devido ao prazo de entrega (amanhã).
2.  **Bypass via Base Bruta:** Ler diretamente da `cache_v1_vendas_unified_*.parquet`, que está íntegra, para extrair a `DATA_EMISSAO_NF`.
3.  **Manual Overwrite:** Inviável devido ao volume de dados (162k+ linhas).

## Decisão
Optamos pela **Opção 2 (Bypass via Base Bruta)**. O script `scripts/consolidate_cevap.py` foi alterado para consumir a base unificada de vendas, garantindo a integridade da data da última compra.

## Consequências
*   **Positivas:** 100% de match rate nas datas (Zero NaTs); Recuperação de frotistas importantes; Garantia da entrega no prazo.
*   **Negativas:** Aumento temporário do tempo de processamento (leitura de base maior); Débito técnico (necessidade de reverter o bypass após correção do M3).

## Confirmação
A integridade foi confirmada via script `scripts/qa_latest_output.py`, que atestou **Zero NaTs** na coluna `DT_Ultima_Compra` da planilha final.

---
*Este registro deve ser consultado antes de qualquer tentativa de simplificação do motor de consolidação.*
