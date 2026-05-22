# GCC Learnings - Multi-Output Report

## O que funcionou e por quê
- **Refatoração Multi-Output:** Mudar a função de renderização (`macro_overview.py`) para iterar sobre uma lista de objetos `PdfPages` foi extremamente eficaz e evitou a violação do DRY (Don't Repeat Yourself), permitindo que a mesma figura fosse salva em múltiplos relatórios e num preview de PNG simultaneamente.
- **TDD:** O uso de mocks em `pytest` ajudou a identificar rapidamente um erro de namespace (passar módulo vs passar objeto Mock) e evitou que rodássemos relatórios pesados durante a fase de testes.

## Decisões técnicas validadas
- **Adaptação Visual:** A redução do `width` das barras (0.2) e da fonte do eixo Y (6-7pt) se mostrou o limite ideal para caber 20 subgrupos na Página 1 sem quebrar a proporção do PDF, que já tem um layout engessado (A4 Landscape).

## Padrões descobertos
- **Argparse vs Pytest:** Scripts executáveis (`__main__`) que usam `argparse` falham quando o pytest injeta argumentos caso o guard-block não seja respeitado. Isso validou a importância estrutural do boilerplate padrão do Python para testabilidade.
