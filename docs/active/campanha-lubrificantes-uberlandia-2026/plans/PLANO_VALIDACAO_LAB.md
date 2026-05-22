# 🧪 PLANO DE VALIDAÇÃO LABORATORIAL: Uberlândia 2026

Este documento descreve as etapas de validação técnico-científica antes da implementação do motor oficial. Cada etapa deve ser executada em `src/lab/` e aprovada pelo usuário.

---

## 阶段 1: TAXONOMIA E FILTROS (A Linha Amarela)

**Objetivo:** Identificar com precisão o que é Lubrificante de "Linha Amarela" em Uberlândia.

* **Ações:**
    1. Listar todos os Grupos/Subgrupos que tiveram vendas para os Top 10 Clientes de Construção.
    2. Validar se o filtro `DESCRICAO_CC` (Motor M2) se aplica à base de Uberlândia.
    3. Isolar o impacto financeiro do "Autoconsumo" (Roberto pediu para manter, mas precisamos saber quanto ele representa na meta de 400k).
* **Critério de Saída:** Lista de filtros (SQL/Pandas) aprovada.

## 阶段 2: ESTIMATIVA DE POTENCIAL E GAP (Onde está o dinheiro?)

**Objetivo:** Comparar o consumo histórico com a meta de 400k.

* **Ações:**
    1. Mapear "Clientes Órfãos": Compram peças de Linha Amarela mas nunca compraram óleo.
    2. Calcular a "Recorrência Média": De quanto em quanto tempo os grandes clientes de Uberlândia trocam o óleo?
    3. Validar a Regra 50/20 (Campanha Anterior) na filial 04.
* **Critério de Saída:** Lista de "Top Attack" com potencial individualizado.

## 阶段 3: ENGENHARIA DE ATRIBUTOS (Higiene e Tipagem)

**Objetivo:** Garantir que os cálculos não tenham "lixo" (Totais, Devoluções).

* **Ações:**
    1. Validar a álgebra de Devoluções (Venda - Estorno) por Nota Fiscal.
    2. Consolidar o Master Data (Clientes unificados por CNPJ Raiz).
* **Critério de Saída:** Script de ETL testado com zero discrepância de centavos.

---

## 🚀 EXECUÇÃO INICIAL (Fase 1)

Começaremos pelo laboratório: `src/lab/valida_filtros_taxonomia.py`.
