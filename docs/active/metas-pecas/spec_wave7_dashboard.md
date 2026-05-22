# Spec: Wave 7 - Inteligência de Conversão e Dashboard Executivo

## 1. Objetivo
Resolver as inconsistências remanescentes da Wave 6 e elevar o Motor M6 ao nível de **Prescriptive Analytics**, entregando uma visão de "One-Page" que conecte Funil, Faturamento e Metas.

## 2. Diagnóstico de Falhas (Wave 6)
- **Concentração em "Peças e acessórios":** O script `Wave2` estava extraindo apenas o código do Centro de Custo (`VS1_CENCUS`). A função de classificação buscava strings (ex: 'CRC') que não existem no código numérico.
- **Faturamento em Branco no Funil:** Na estrutura "Wide", os registros de Funil e Vendas são linhas independentes. Quando um orçamento é faturado, ele gera uma linha no Funil (Status F) e outra nas Vendas. O usuário deseja ver o faturamento "linkado" ou pelo menos consolidado na mesma visão de gestão.
- **Ausência de Funil na Gestão:** A aba `GESTAO_PERFORMANCE` foca apenas em Meta vs Realizado. Precisamos incluir a "Pipeline" (Funil em Aberto) para prever o fechamento do mês.

## 3. Proposta de Solução

### A. Saneamento de Segmentos (Wave 2)
- Alterar a query do Funil para realizar um `LEFT JOIN` com a tabela `CTT010` (Centro de Custo).
- Trazer a coluna `CTT_DESC01` (Descrição do CC).
- Atualizar o Orquestrador para classificar o segmento com base na **descrição** e não no código.

### B. Reconciliação Funil -> Vendas (Wave 4)
- Na aba `TABELA_FATO_WIDE`, manter a granularidade de eventos.
- Criar uma lógica de **Consolidação por Chave de Dimensão** (Filial + Segmento + Mês).
- Para itens com `ESTAGIO_FUNIL = 'FATURADO'`, garantir que o valor do Funil não seja somado ao Realizado de Vendas em visões agregadas para evitar double-counting (ou rotular claramente como "Conversão").

### C. Aba "EXECUTIVE_ONE_PAGE"
Criar uma nova aba no Excel (ou dashboard HTML) com:
1. **KPI Cards:** Total Meta, Total Faturado, % Atingimento, Funil Quente (Em Aberto).
2. **Visão de Tendência:** Projeção de fechamento (Faturado + Funil Probabilístico).
3. **Top 5 Segmentos:** Performance por categoria nominal.

## 4. Plano de Testes (Validação)
- **Teste de Segmentos:** Verificar se 'Peças CRC' e 'Peças Contratos' possuem valores no Funil.
- **Teste de Metas:** Validar se a coluna 'VALOR_FUNIL' na aba `GESTAO_PERFORMANCE` está populada.
- **Teste de Dash:** Verificar se os cálculos de atingimento (%) estão corretos.

---
**Status:** Aguardando Aprovação do Brainstorming para iniciar o Implementation Plan.
