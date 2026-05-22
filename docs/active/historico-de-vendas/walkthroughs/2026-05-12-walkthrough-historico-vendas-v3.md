# Walkthrough: Integração de Rentabilidade e Popularidade - PDF v3

**Data:** 2026-05-12  
**Status:** Concluído (Fase de Construção v3)  
**Projeto:** historico-de-vendas  

## 🚀 O que mudou?

Nesta iteração, evoluímos o relatório de uma visão puramente volumétrica para uma análise de **valor e recorrência**, integrando dados do Microsoft Fabric com a base local de estoque.

### 1. Inteligência de Rentabilidade (Profitability)
- **Implementação:** Novo motor de extração em `src/extract_faturamento.py`.
- **Lógica:** Cruzamento de vendas históricas (2023+) com custos (SB1010) para calcular lucro e margem percentual por SKU.
- **Resultado:** O relatório agora exibe a **Margem Média** da operação e permite priorizar a desova de itens com baixa rentabilidade.

### 2. Indicador de Popularidade (Recorrência)
- **Implementação:** Script `src/extract_popularity.py`.
- **Lógica:** Contagem de meses distintos com vendas nos últimos 6 meses.
- **Categorias:** 
  - `HIGH`: Vendeu em 4-6 meses.
  - `MEDIUM`: Vendeu em 2-3 meses.
  - `LOW`: Vendeu em 0-1 mês (Itens "moribundos").

### 3. Redesign de Visualização e Ação Sugerida
- **Dashboard v3:** Página 1 agora inclui a tendência anualizada por **Subgrupo** em escala logarítmica, facilitando a identificação de quedas estruturais em categorias específicas.
- **Matriz de Decisão:** A tabela da Página 2 foi enriquecida com uma coluna de **"Ação Sugerida"**, baseada em heurísticas que cruzam popularidade e valor excedente:
  - Ex: `Popularidade LOW` + `Excesso > R$ 5k` -> **Sugestão: Devolução / Queima**.

## 📊 Arquivos Gerados
- **Dataset Final:** `data/base_estoque_enriquecida.parquet` (Consolidado com todas as métricas).
- **Relatório PDF:** `docs/business/Relatorio_Executivo_Vendas_v3_20260512_174749.pdf`.

## ✅ Verificação Técnica
- [x] Extração de faturamento validada (10.454 itens processados).
- [x] Extração de popularidade validada (19.200 itens processados).
- [x] Merge híbrido realizado sem perda de registros (40.104 linhas finais).
- [x] PDF gerado com `matplotlib.gridspec` e `PdfPages` sem erros de escala.

---
*Assinado: Antigravity (Phase: Build & Document)*
