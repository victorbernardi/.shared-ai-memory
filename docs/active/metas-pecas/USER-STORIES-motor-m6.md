# User Stories - Motor M6 Inova

## US01: Unificação da Visão Temporal de Vendas
**Como** Analista de Insight,
**Eu quero** que o faturamento recente e o histórico (pré-2025) estejam consolidados,
**Para que** eu possa realizar comparativos de performance ano contra ano (YoY) sem lacunas de dados.

### Critérios de Aceitação
- **Dado que** existem as fontes `vw_VENDAS` e `f_vendas_hist31102025`.
- **Quando** o motor for executado.
- **Então** o dataframe final deve conter registros contínuos desde 2017 até a data atual, com colunas de data e valor padronizadas.

---

## US02: Limpeza Inteligente do Funil (Aging)
**Como** Gestor Comercial,
**Eu quero** que orçamentos parados há mais de 60 dias sejam marcados como expirados,
**Para que** meu pipeline de vendas reflita apenas oportunidades reais de conversão.

### Critérios de Aceitação
- **Dado que** um orçamento possui `VS1_STATUS = '0'` (Aberto).
- **Quando** a diferença entre a data atual e `VS1_DATORC` for superior a 60 dias.
- **Então** o motor deve alterar o status para "Expirado (Zumbi)" no relatório final.

---

## US03: Alinhamento Dinâmico de Metas
**Como** Diretor da Inova,
**Eu quero** comparar o faturamento real com as metas de 2026 por segmento e filial,
**Para que** eu identifique rapidamente onde estão os maiores gaps de performance.

### Critérios de Aceitação
- **Dado que** a planilha de metas possui nomes de filiais e segmentos.
- **Quando** o motor processar os dados do ERP (via Centro de Custo).
- **Então** o sistema deve utilizar o mapeamento `mapa_centro_custo_pecas.csv` para garantir que o faturamento caia na "caixa" correta da meta.

---

## US04: Segmentação Estratégica (Integração M5)
**Como** Estrategista de Vendas,
**Eu quero** visualizar a performance por categoria da Pirâmide (M5),
**Para que** eu direcione esforços para os clientes de maior potencial (A1, B2).

### Critérios de Aceitação
- **Dado que** existe a base de segmentação do Motor M5.
- **Quando** o motor realizar o join via CNPJ.
- **Então** cada linha de orçamento/venda deve conter a respectiva classificação da pirâmide (Ex: Cliente A1).
