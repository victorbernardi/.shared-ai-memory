# GCC Learnings - Fix Layout Overlap (20 Subgrupos)

## O que funcionou e por quê
- **Auto-Scaling de Fontes:** Implementar uma lógica condicional no `macro_overview.py` que reduz a fonte para `5.5pt` quando o número de subgrupos ultrapassa 10 foi a solução definitiva para a sobreposição. Isso garante que o relatório seja resiliente a variações no portfólio.
- **Gridspec 100x1:** Mudar para um grid de alta resolução (100 linhas) permitiu um ajuste fino na margem superior do gráfico, evitando que o título "atropelasse" as barras superiores.

## Decisões técnicas validadas
- **Paridade Visual:** A redução do `width` das barras para `0.25` em alta densidade criou o respiro necessário para que o olho humano consiga distinguir as três safras (23/24, 24/25, 25/26) sem confusão.

## Padrões descobertos
- **Auditoria Proativa:** A falha inicial mostrou que confiar apenas na "visão geral" da IA não substitui uma parametrização de segurança. O novo padrão é incluir margens de segurança matemáticas no código de visualização.
