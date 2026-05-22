# Spec: Análise com Lupa - Diagnóstico Profundo de Vendas e Estoque

**Data:** 2026-05-13
**Status:** Brainstorming
**Versão:** v1.0

## 1. Objetivo
Aprofundar a análise do histórico de vendas e saúde do estoque para identificar insights acionáveis que não são visíveis no relatório macro. O foco é "colocar uma lupa" nos SKUs e Subgrupos que representam o maior risco financeiro (Capital Imobilizado) e a maior perda de mercado (Dropout).

## 2. Requisitos Analíticos (A Lupa)

Baseado nas transcrições e na análise exploratória, a "Lupa" deve focar em:

### A. Matriz de Risco Financeiro (Dead Capital)
- **O que é:** Cruzamento de `VALOR DE INV EXCEDENTE` com o `DROP` (Perda de Venda).
- **Insight:** Identificar itens que pararam de vender (Dropout) mas ainda possuem alto valor de estoque excedente.
- **Ação:** Prioridade Máxima para liquidação ou devolução ao fornecedor.

### B. Decaimento de Popularidade (Dying Stars)
- **O que é:** Itens que tinham alta `POPULARIDADE` (vendas em muitos meses) nos anos anteriores (ANO 3/ANO 2) e caíram para zero ou quase zero no ANO 1.
- **Insight:** Detectar perda de tração de itens que eram "âncoras" do portfólio.
- **Ação:** Investigar se houve substituição por SKU concorrente ou perda de cliente específico.

### C. Vitalidade por Subgrupo (Concentração de Queda)
- **O que é:** Drill-down nos Subgrupos (ex: Filtros, Rodante).
- **Insight:** Verificar se a queda de um subgrupo é sistêmica (todos os SKUs caíram) ou se é causada por 1 ou 2 SKUs de alto valor.
- **Ação:** Ajuste de estratégia de compra por categoria.

### D. Análise Regional de Abandono (Geografia do Dropout)
- **O que é:** Agrupamento por `CIDADE` e `ESTADO`.
- **Insight:** Verificar se o Dropout está concentrado em regiões específicas (ex: Uberlândia vs Serra).
- **Ação:** Campanhas de recuperação regional.

## 3. Arquitetura de Dados
- **Fontes:** 
    - `data/base_estoque_enriquecida.parquet` (Estoque, Popularidade, Excedente).
    - `data/Analise Histórico de Vendas Últimos 3 anos.xlsx` (Vendas anuais discretas).
    - `data/map_subgrupos.parquet` (Mapeamento técnico).
- **Processamento:** Utilizar Pandas para calcular métricas de intersecção (Ex: % de Estoque Excedente que está em Dropout).

## 4. Validação (Definição de Pronto)
A análise será considerada concluída quando:
1.  Identificarmos o Top 10 SKUs de "Risco Crítico" (Alto Excedente + Alto Dropout).
2.  Gerarmos uma visualização de "Pareto de Perda" por Cidade.
3.  Calcularmos o índice de "Vitalidade de Categoria" (Queda de itens ativos por Subgrupo).
4.  Apresentarmos o impacto financeiro consolidado do "Estoque Morto".

---
*Documento gerado automaticamente via skill brainstorming.*
