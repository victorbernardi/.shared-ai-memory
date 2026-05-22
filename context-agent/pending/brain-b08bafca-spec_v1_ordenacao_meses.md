# Problema: Ordenação Incorreta de Meses nos Gráficos de Filiais

## Descrição do Problema
No dashboard **Inova OnePage** (`Dashboard_Executivo_M6.html`), os gráficos de desempenho por filial não seguem a ordem cronológica dos meses (Janeiro a Dezembro). Atualmente, os meses aparecem de forma aleatória ou seguindo a ordem de inserção dos dados (ex: Abril, Agosto, Dezembro, Fevereiro, Janeiro...).

## Impacto
* Dificulta a análise de tendência temporal para os gestores.
* Passa uma impressão de falta de refinamento no dashboard.
* Inconsistência com o gráfico de "Evolução Mensal" (que já possui lógica de ordenação).

## Diagnóstico Técnico
1. **Agregação (Backend/Python):** O script `aggregator.py` utiliza `defaultdict` para agrupar os dados. Ao converter esse dicionário em uma lista para o JSON (`snapshot_filiais.json`), a ordem dos itens é a ordem de descoberta no arquivo original `data.json`.
2. **Renderização (Frontend/JS):** A função `renderBranches` em `index.html` (e no dashboard final) filtra os dados da filial, mas não realiza o `sort` cronológico antes de alimentar o `ApexCharts`.

## Comportamento Esperado
* O eixo X de todos os gráficos deve sempre começar em Janeiro (ou no primeiro mês disponível no ano) e seguir sequencialmente até Dezembro (ou o mês atual).

## Plano de Correção
1. **Aggregator.py:**
   - Implementar uma função de ordenação baseada na constante `MONTH_ORDER`.
   - Garantir que `snapshot_evolution.json` e `snapshot_filiais.json` sejam salvos com os dados ordenados por `ANO` e `MES_NOME`.
2. **Dashboard JS:**
   - Refatorar a função `renderBranches` para garantir que `fData` seja ordenado usando `monthOrder.indexOf(d.MES_NOME)` antes de gerar o gráfico.

## Critérios de Aceite
- [ ] O gráfico de "Performance por Filial" deve mostrar os meses em ordem: Jan, Fev, Mar, Abr, Mai, Jun, Jul, Ago, Set, Out, Nov, Dez.
- [ ] A ordenação deve funcionar corretamente mesmo que falte dados de algum mês no meio do ano (ex: Jan, Mar, Abr).
- [ ] O script de agregação deve ser resiliente a meses não previstos (embora improvável).
