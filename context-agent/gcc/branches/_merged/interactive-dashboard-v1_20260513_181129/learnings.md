# GCC Learnings - Interactive Dashboard HTML

## O que funcionou e por quê
- **Desacoplamento de Dados:** Criar um payload JSON independente (`data/dashboard_payload.json`) foi fundamental para separar a lógica de análise de dados em Python da lógica de apresentação em JS. Isso permitiu iterar no design do HTML sem reprocessar as bases de dados.
- **Chart.js Log Scaling:** O uso de escala logarítmica no Chart.js resolveu o problema visual onde os subgrupos dominantes (John Deere) "esmagavam" as barras dos subgrupos menores, tornando o gráfico legível para todos os 20 itens.

## Decisões técnicas validadas
- **Self-contained HTML:** Consolidar tudo (CSS, JS logic, Data) em um único arquivo HTML (usando CDNs para bibliotecas) atende ao requisito de portabilidade para apresentações executivas.
- **Tailwind CSS:** O uso de Tailwind permitiu criar uma interface de alta fidelidade (*Glassmorphism*) em minutos, mantendo o padrão estético Stout.

## Padrões descobertos
- **Data Injection Pattern:** O fluxo `Python Data Extract -> HTML Template -> Final HTML Inject` é um padrão extremamente eficiente para gerar relatórios dinâmicos offline no ecossistema Antigravity.
