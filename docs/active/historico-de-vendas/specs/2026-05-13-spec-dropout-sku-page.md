# Especificação Técnica: Implementação da Página 2 - Dropout por SKU

**Data:** 2026-05-13  
**Status:** Validado  
**Projeto:** historico-de-vendas  

---

## 1. Objetivo
Expandir o relatório para incluir uma página dedicada à análise de declínio de vendas no nível de SKU (Peça), permitindo uma visão tática complementar à visão estratégica de Subgrupos.

## 2. Requisitos Funcionais
- **RF01 - Agregação por SKU:** Consolidar as vendas históricas (12, 24, 36 meses) agrupando por `ITEM` e `DESCRIÇÃO`.
- **RF02 - Ranking de Queda:** Identificar os 5 SKUs com maior perda nominal de faturamento (Impacto Financeiro = Valor Passado - Valor Presente).
- **RF03 - Filtro de Relevância:** Manter o critério de `Vendas Passadas >= 10 unidades` para garantir significância estatística.
- **RF04 - Novo Padrão Visual:** Aplicar branding John Deere Construction (Cores, Fontes, Escala Logarítmica e Eixo Horizontal).

## 3. Estrutura da Página 2
- **Cabeçalho:** Fundo Amarelo JD com título "DIAGNÓSTICO DE PERFORMANCE POR SKU (PEÇAS)".
- **KPIs de Topo:** Inventário Total do Ranking, Impacto Financeiro Total do Ranking.
- **Gráfico Principal:** Horizontal agrupado com 3 janelas temporais.
- **Legenda:** 
    - `23/24` (Cinza Claro)
    - `24/25` (Cinza Escuro)
    - `25/26 (Hoje)` (Amarelo JD)

## 4. Plano de Validação
- [ ] Gerar PDF v6 e verificar se possui 3 páginas.
- [ ] Validar se os SKUs exibidos são peças individuais (ex: "AT12345 - FILTRO") e não subgrupos.
- [ ] Confirmar se a legenda segue o padrão cronológico solicitado.

---
**Próximo Passo:** Gerar o Plano de Implementação (Strategy).
