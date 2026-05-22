# GCC Learnings - Refine Dashboard Spacing

## O que funcionou e por quê
- **Ajuste de categoryPercentage:** Reduzir o `categoryPercentage` para `0.7` no Chart.js criou o espaço de respiro necessário entre os subgrupos, tornando a distinção entre as categorias imediata e agradável aos olhos.
- **Min-Height Dinâmico:** Aumentar a altura mínima do container para `900px` permitiu que cada subgrupo ganhasse mais "pixel-budget" vertical, resolvendo o problema de compressão visual sem precisar sacrificar o tamanho das fontes.

## Decisões técnicas validadas
- **Escala Logarítmica:** Confirmado que a escala logarítmica é a única forma viável de manter a paridade visual entre subgrupos de ordens de magnitude tão distantes (John Deere vs John Deere Collection).

## Padrões descobertos
- **Design Review Feedback Loop:** A rápida iteração entre o screenshot do browser e o ajuste fino no CSS/JS validou o workflow de desenvolvimento de dashboards interativos no ecossistema Antigravity.
