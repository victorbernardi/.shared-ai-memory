# Auditoria de Qualidade: Match de CNPJ e Pirâmide (M6 v4.2)

**Data:** 2026-04-29  
**Objeto:** Validação de cruzamento entre bases transacionais e base estratégica M5.

## 📈 Resultados da Auditoria

| Métrica | Resultado |
| :--- | :--- |
| **Cobertura de Valor (Faturamento)** | **91.11%** |
| **Match de Clientes (Faturamento)** | **89.63%** |
| **Match de Clientes (Funil)** | **71.40%** |

## 🔍 Detalhamento
- **Faturamento:** Dos R$ 309,196,972.83 processados, R$ 281,720,416.45 possuem correspondência direta na Pirâmide de Segmentação.
- **Funil:** A taxa menor no funil (71%) é justificada pela presença de orçamentos para novos prospects e CPFs que ainda não foram classificados na base de frotas estratégica (M5).

## 🛠️ Ação Corretiva
- Clientes sem match serão rotulados como `TIER 4 - NÃO MAPEADO` para evitar distorções nos agrupamentos de pirâmide.
