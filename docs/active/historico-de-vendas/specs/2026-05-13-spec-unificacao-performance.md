# Especificação Técnica: Unificação Conceitual (Sales Performance)

**Data:** 2026-05-13  
**Status:** Validado  
**Projeto:** historico-de-vendas  

---

## 1. Objetivo
Reformular a "moldura" do relatório (Indicadores de Topo e Tabela Final) para que todo o documento fale a mesma língua: **Performance de Vendas e Recuperação de Portfólio**, eliminando a herança visual de "Gestão de Estoque Parado".

## 2. Requisitos de Negócio
- **Alinhamento Estratégico:** Focar no faturamento nominal perdido (Dropout) e no giro atual.
- **Soberania de Dados:** Utilizar exclusivamente a Planilha Excel (Volume * Custo Médio) para os cálculos financeiros de topo e ranking.
- **Ação Sugerida:** Transformar a tabela final em um guia de retomada comercial.

## 3. Mudanças Propostas

### 3.1. Novos KPIs Globais (Header)
- **KPI 1 (Giro de Capital 12m):** Soma das vendas do último ano valorizadas ao custo médio.
- **KPI 2 (Gap de Performance 3Y):** Soma do Impacto Financeiro (Queda) de todos os itens em declínio.
- **KPI 3 (Vitalidade do Portfólio):** Percentual de itens com vendas ativas (>0) no último ano.

### 3.2. Nova Tabela de Prioridades (Página 3)
- **Título:** "MATRIZ DE RECUPERAÇÃO: PRIORIDADES DE RETOMADA".
- **Critério de Ranking:** Maior Queda Bruta em R$ (Dropout).
- **Lógica de Ação:**
    - Se Queda Alta e Estoque > 0: **"REVISÃO DE GIRO / PROMOÇÃO"**.
    - Se Queda Alta e Estoque == 0: **"FALTA DE PEÇA - REPOR"**.

## 4. Plano de Validação
- [ ] Validar se os cards de topo batem com a soma dos dados da planilha.
- [ ] Confirmar se a Tabela da Pág 3 está ordenada pelo impacto financeiro da queda.
- [ ] Verificar se os títulos das páginas refletem o tema "Performance".

---
**Próximo Passo:** Gerar o Plano de Implementação (Strategy).
