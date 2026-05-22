# Plano de Implantação: Segmentação & Overlay Analytics (Wave 8)

Este plano detalha a implementação do sistema de segmentação granular com visão sobreposta (Total vs Segmento) e indicadores em Verde John Deere.

## 1. Preparação de Dados & Lógica
- [ ] **Extração de Segmentos:** Modificar o script de inicialização para carregar dinamicamente os valores únicos do campo `SEGMENTO`.
- [ ] **Bifurcação de Datasets:** Adaptar `updateDashboard` para calcular simultaneamente o `Total da Unidade` e o `Valor do Segmento`.
- [ ] **Cálculo de Share:** Implementar a lógica de participação percentual em tempo real.

## 2. Refatoração da Interface (UI)
- [ ] **Filtro de Segmento:** Adicionar o seletor no Header com estilo Glassmorphism.
- [ ] **KPI Hero Overlay:** Injetar o painel secundário (Verde JD) nos cards principais.
- [ ] **Bento Grid Bicolor:** 
    - Criar o CSS para barras de progresso com múltiplas camadas.
    - Adicionar label de "Share %" nos cards de filial.

## 3. Gráficos & Evolução
- [ ] **Trend Multi-Line:** Atualizar ApexCharts para exibir o Realizado Total (Amarelo) e o Realizado/Meta do Segmento (Verde).
- [ ] **Tooltips:** Customizar tooltips para mostrar a composição de faturamento.

## 4. Auditoria & Qualidade
- [ ] **OnePage Scanner:** Validar a paridade matemática após a implementação da segmentação.
- [ ] **UX Check:** Garantir que o dashboard continue fluido mesmo com o aumento de densidade de dados.
