# Backlog de Produto - Dashboard Inova M6

Este documento refina o [BRD](file:///c:/Projetos/Inova/Metas%20Pe%C3%A7as/01_Documentacao/BRD-20260429-motor-m6-inova.md) em histórias de usuário prontas para implementação.

## [US01] Visualização Imersiva de Faturamento (Mês Foco)
**Como** Gestor Comercial,
**Eu quero** visualizar o faturamento do mês atual em destaque absoluto,
**Para que** eu possa tomar decisões rápidas sobre o atingimento da meta mensal sem distrações de dados anuais secundários.

### Critérios de Aceitação:
- O card de faturamento deve ser o maior elemento do Bento Grid (Hero).
- Deve exibir o valor em formato "k/M" (ex: R$ 1.2M).
- Deve incluir uma barra de progresso visual em relação à meta do mês.

## [US02] Morphing Estratégico do Pipeline
**Como** Diretor de Estratégia,
**Eu quero** que o gráfico de funil se transforme no gráfico de evolução de vendas via scroll,
**Para que** eu entenda visualmente a conversão do esforço (pipeline) em resultado (vendas).

### Critérios de Aceitação:
- O efeito deve ser realizado via GSAP ScrollTrigger (scrub).
- O estado inicial é a Composição do Funil; o estado final é o Gráfico de Linhas (Realizado vs Meta).
- A transição deve ser fluida e baseada em partículas Canvas.

## [US03] Feedback Tátil com Lottie State Machines
**Como** Usuário do Dashboard,
**Eu quero** que os ícones e botões reajam de forma fluida ao meu toque/hover,
**Para que** a interface pareça um organismo vivo e forneça confirmação tátil das ações.

### Critérios de Aceitação:
- Ícones de KPI devem usar Lottie State Machines (Idle -> Hover -> Click).
- A animação não deve introduzir latência na navegação.

## [US04] Filtragem Instantânea via "Floating Island"
**Como** Analista de Dados,
**Eu quero** alterar o ano, mês e filial através de um menu flutuante minimalista,
**Para que** o dashboard se atualize instantaneamente sem recarregar a página.

### Critérios de Aceitação:
- O menu deve usar o efeito Liquid Glass.
- A atualização dos dados deve ocorrer em < 100ms (Snapshots em memória).
