# Especificação Técnica: Refatoração Visual INOVA v5.0 (Stout Edition)

**Data:** 2026-04-29
**Status:** Brainstorming
**Autor:** Antigravity AI

## 1. Objetivo
Restaurar a excelência visual e a precisão analítica do Dashboard INOVA, eliminando ruídos visuais e garantindo que cada pixel comunique valor estratégico.

## 2. Requisitos Funcionais (RF)
- **RF01: Filtro de Meses Inteligente**: 
    - Se `Ano Selecionado < Ano Atual`: Exibir todos os meses.
    - Se `Ano Selecionado == Ano Atual`: Exibir meses <= Mês Atual.
- **RF02: Formatação Monetária Estrita**: Todo valor numérico deve usar o helper `formatInt` (`000.000.000`), sem decimais, inclusive em tooltips de gráficos.
- **RF03: Indicadores de Status e GAP**: Restaurar triângulo de meta (acima/abaixo) no card de Faturamento e aumentar destaque visual do indicador de GAP.
- **RF04: Limpeza de UI**: Remover "Insights Executivos", Filtro "Pirâmide" e o mês da tooltip do gráfico de Evolução Mensal (já presente no eixo).

## 3. Requisitos de Design (RD) - Antigravity Style
- **RD01: Glassmorphism e Cores**: Re-aplicar efeito Glass em todos os cards (KPIs e Filiais). Reduzir a saturação do amarelo nos gráficos das filiais para um tom mais sóbrio/premium.
- **RD02: Contexto em Gráficos**: 
    - **Filiais**: Adicionar meses ao eixo X ou tooltip para que a evolução seja compreensível.
    - **Pipeline**: Tooltips devem conter Título do Tier e Valor Formatado.
- **RD03: Grid Dinâmico**: Corrigir alinhamento dos cards superiores.


## 4. Plano de Validação
- Inspeção via Browser para verificar formatação numérica.
- Teste de filtro de data para validar bloqueio de meses futuros.
- Validação visual dos triângulos de status em diferentes cenários (Meta batida vs. Meta não batida).
