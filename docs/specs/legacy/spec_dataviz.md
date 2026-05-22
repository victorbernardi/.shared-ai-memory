# Especificação: Ecossistema de Data Visualization no Antigravity

## 1. Objetivo
Identificar e catalogar as habilidades (skills) disponíveis no ambiente Antigravity voltadas para a criação de visualizações de dados, dashboards e narrativas analíticas.

## 2. Pesquisa de Skills Atuais
Após auditoria via `skillfish list` e busca nos repositórios oficiais (`johnefemer/skillfish`, `arendon1/agent-skills`), identificamos as seguintes capacidades instaladas:

### 2.1. Criação Técnica
- **`data-create-viz`**: Focada em geração de gráficos de alta qualidade usando Python (Matplotlib, Seaborn, Plotly). Ideal para relatórios estáticos e exploração de dados.
- **`data-build-dashboard`**: Focada em dashboards interativos em HTML utilizando Chart.js. Ideal para apresentações executivas e monitoramento dinâmico.

### 2.2. Fundamentos e Design
- **`data-data-visualization`**: Guia de melhores práticas de design, teoria das cores e acessibilidade. Garante que os gráficos sejam profissionais e legíveis.
- **`data-storytelling`**: Estruturas narrativas para transformar dados em insights acionáveis (Problem-Solution, Trend, Comparison).

### 2.3. Skills Complementares Identificadas (Repositórios Externos)
- **`scientific-schematics`** (`arendon1/agent-skills`): Para diagramas técnicos e esquemáticos.
- **`tech-debt-tracker`** (`johnefemer/skillfish`): Exemplo de implementação de dashboard para métricas específicas.

## 3. Conclusão da Pesquisa
O conjunto de skills atual (`data-create-viz` + `data-build-dashboard`) é o mais robusto disponível no ecossistema para uso generalista e profissional. Não foram encontradas novas skills "dataviz" que superem as atuais em termos de abrangência técnica dentro do padrão Antigravity/Stout.

## 4. Próximos Passos Sugeridos
1. **Consolidação:** Utilizar as skills existentes para qualquer demanda de visualização.
2. **Customização:** Caso as atuais não atendam uma necessidade específica, utilizar `writing-skills` para criar uma nova sub-habilidade especializada (ex: `data-viz-geospatial`).
