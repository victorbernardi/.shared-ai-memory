# GCC Learnings - Dashboard Click Filter

## O que funcionou e por quê
- **Chart.js onClick Integration:** A integração do evento `onClick` do Chart.js permitiu transformar o gráfico de uma visualização passiva em um controle de navegação ativo. O uso de `elements[0].index` para mapear a barra clicada ao nome do subgrupo foi robusto.
- **Payload Scaling:** Aumentar o payload para 500 SKUs não comprometeu a performance de carregamento e melhorou significativamente a utilidade dos filtros por subgrupo, especialmente para subgrupos de cauda longa que não apareciam no Top 50 global.

## Decisões técnicas validadas
- **Vanilla JS Filter Logic:** Manter a lógica de filtragem puramente em JavaScript (sem chamadas ao Python após o carregamento) garante uma experiência de usuário instantânea e sem "lags" de rede/processamento.
- **UI Reset Pattern:** O uso de um badge de filtro com botão de reset (✕) é um padrão de UI intuitivo que evita confusão sobre o estado atual dos dados exibidos.

## Padrões descobertos
- **Interactive Drill-down:** O padrão `Bar Chart (Category) -> Table (Details)` é extremamente eficaz para análise de causa raiz em KPIs de vendas, permitindo que o gestor saia do macro (subgrupo) para o micro (SKU) com um único clique.
