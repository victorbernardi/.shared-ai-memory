# Learnings: enrichment-plano-a

## O que funcionou
- Implementação do layout `GridSpec` no Matplotlib para o PDF v3, resolvendo o problema de densidade de informação.
- Cálculo de rentabilidade (LUCRO e MARGEM_PERC) unificando Fabric e SB1010.
- Uso de escala logarítmica para visualização YoY de subgrupos, permitindo ver quedas em itens de baixo volume.

## Decisões Técnicas Validadas
- A unificação de bases via ITEM (SKU) é robusta o suficiente para o MVP.
- O campo `SUBGRUPO_FULL` é a melhor chave para relatórios executivos.

## Padrões Descobertos
- Labels de itens idênticos causam sobreposição em gráficos de barras; a solução foi sufixar com o SKU (*1234).
