# Plano Estratégico: MVP Relatório de Saúde do Estoque (PDF)

## 1. Visão Geral do MVP
O objetivo deste relatório em PDF é sanar a "cegueira" visual dos analistas apontada na transcrição do áudio. O relatório não terá filtros interativos (por ser um PDF), logo, precisará consolidar as informações de forma top-down (do macro para o micro), focando onde o dinheiro está parado e onde há risco de ruptura.

## 2. Estrutura Visual do Relatório (Páginas)

### Página 1: Resumo Executivo (Painel Macro)
Foco em valores financeiros gerais e saúde global do inventário.
- **KPI 1:** Valor Total do Inventário Contábil (R$).
- **KPI 2:** Valor Total de Inventário Excedente (R$) - *O dinheiro "parado"*.
- **KPI 3:** Valor Total de Inventário Saudável (R$) - *O que está girando bem*.
- **Gráfico de Rosca (Donut Chart):** Proporção Saudável vs. Excedente.
- **Gráfico de Barras (Top 5):** Os 5 depósitos (CC) com maior volume financeiro em excesso.

### Página 2: Análise de Inatividade (Peças com Zero Vendas)
Foco em identificar o que parou de girar.
- **KPI 1:** Quantidade de SKUs com 0 vendas nos últimos 12 meses (`POPS ÚLT. 12` = 0).
- **KPI 2:** Valor financeiro imobilizado nestes SKUs inativos.
- **Gráfico de Barras Horizontais:** Top 10 SKUs (Itens + Descrição) com maior valor financeiro na categoria "ZERO VENDAS 12 MESES".

### Página 3: Análise de Sorte/Sortimento e Categorização
Foco na taxonomia da matriz.
- **Gráfico de Pizza:** Distribuição do estoque por `CLASSIFICAÇÃO DE MERCADO` (Cativo, Competitivo, Neutro).
- **Tabela Resumo (Top 15 Críticos):** Uma tabela estilizada listando os 15 SKUs com maior "VALOR DE INV EXCEDENTE" do projeto, contendo:
  - SKU (Item)
  - Descrição
  - Classificação Detalhada (ex: Excesso 36 meses)
  - Qtd em Estoque (`ESTOQUE CONTÁBIL`)
  - Valor Parado (R$)

## 3. Arquitetura de Dados (Pandas)
Para gerar as páginas acima, o script fará as seguintes agregações:
1. **Limpeza:** Descarte de itens com `ESTOQUE CONTÁBIL` igual a zero ou nulo (se existirem e não agregarem valor).
2. **Cálculos Macro:** `sum()` na coluna `VALOR DE INV EXCEDENTE` e `VALOR DE INV SAUDÁVEL`.
3. **Agrupamentos:** `groupby('CC')` para encontrar os depósitos mais críticos.
4. **Filtros:** `df[df['POPS ÚLT. 12'] == 0]` para a Página 2.

## 4. Arquitetura Tecnológica
Para evitar dependências complexas (como WeasyPrint que requer GTK/Pango instalado no Windows), optaremos por um fluxo Python nativo e robusto:
- **Camada de Dados:** `pandas`
- **Camada de Visualização (Gráficos):** `matplotlib` e `seaborn`.
- **Camada de Documento (PDF):** `FPDF2` ou `matplotlib.backends.backend_pdf`. 
  - *Decisão técnica:* Usar `matplotlib` para desenhar tanto os gráficos quanto as tabelas em *Figures* e exportar todas juntas para um único PDF via `PdfPages` é a via mais rápida e estável para um MVP sem HTML intermediário.

## 5. Próximos Passos
1. Validar essa estrutura com o usuário.
2. Implementar o script `src/generate_pdf_report.py`.
3. Executar sobre a base local e gerar o MVP.