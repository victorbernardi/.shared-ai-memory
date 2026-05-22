# Spec: Análise de Dropout por Subgrupo (Laboratório)

**Data:** 2026-05-12
**Status:** Draft
**Autor:** Antigravity (Gemini CLI)

## 1. Objetivo
Identificar e visualizar os 5 subgrupos com maior queda de performance ("Dropout") nos últimos 3 anos, utilizando o Excel de Histórico como fonte primária e o Scanner (Fabric) para validação mensal detalhada.

## 2. Requisitos Funcionais
- **RF01:** Ler dados do Excel `Analise Histórico de Vendas Últimos 3 anos.xlsx`.
- **RF02:** Enriquecer os dados do Excel cruzando a coluna `ITEM` com o arquivo `data/map_subgrupos.parquet` para obter o `COD_SUBGRUPO` e `DESC_SUBGRUPO`.
- **RF03:** Agrupar vendas por **Subgrupo** (granularidade inferior ao Grupo).
- **RF04:** Tratar os dados como 3 janelas isoladas de 12 meses (Bucket 12, Bucket 24, Bucket 36).
- **RF05:** Calcular o Índice de Queda (Dropout) comparando o Ano 3 (25-36m) com o Ano 1 (0-12m).
- **RF06:** Gerar gráfico de barras horizontais agrupadas para os Top 5 subgrupos em queda.
- **RF07:** Validar os subgrupos identificados consultando a tendência mensal no Microsoft Fabric via `MotorExtracaoGenerico`.

## 3. Requisitos Não-Funcionais
- **RNF01 (Visual):** O gráfico deve ser limpo, utilizando Matplotlib ou Seaborn, com as barras identificadas pelas legendas "12", "24" e "36". Os rótulos do eixo Y devem ser a **Descrição do Subgrupo** (para facilitar a interpretação).
- **RNF02 (Performance):** A análise do Excel deve ser otimizada via Pandas.
- **RNF03 (Isolamento):** Todo o código deve residir na pasta `scripts/` como um laboratório experimental.

## 4. Arquitetura de Dados
- **Input:** 
    - `data/Analise Histórico de Vendas Últimos 3 anos.xlsx` (Vendas por Item).
    - `data/map_subgrupos.parquet` (Chave: ITEM -> SUBGRUPO).
- **Processamento:**
    - Join entre Excel e Mapeamento de Subgrupos.
    - Identificação de subgrupos com queda absoluta e proporcional relevante.
- **Output:**
    - Gráfico PNG: `data/lab_dropout_subgroups.png`.
    - Log de validação no terminal comparando Excel vs Fabric.

## 5. Plano de Validação
1. Comparar o total de vendas do subgrupo `FLGD` no Excel vs a soma das vendas mensais no Fabric para o mesmo período.
2. Garantir que as legendas do gráfico correspondam exatamente aos nomes das colunas solicitadas.
