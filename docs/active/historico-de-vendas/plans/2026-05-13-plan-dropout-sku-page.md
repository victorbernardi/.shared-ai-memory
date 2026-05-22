# Plano de Implementação: Adição da Página 2 (SKU Dropout)

> **Para o Antigravity:** SUB-SKILL REQUERIDA: Use `executing-plans` para implementar este plano tarefa por tarefa.

**Objetivo:** Inserir uma nova página de análise de SKUs no relatório PDF.

**Arquitetura:** Adição de um novo bloco de criação de `figure` no loop do `PdfPages`.

**Tech Stack:** Python, Matplotlib, Pandas.

---

### Tarefa 1: Implementação da Página 2 - Diagnóstico por SKU

**Arquivos:**
- Modificar: `src/generate_pdf_report_v2.py`

**Passo 1: Lógica de Agregação por SKU**
Criar um dataframe `df_sku` agrupando por `ITEM` e `DESCRIÇÃO` a partir do `df_full`.
Cálculo de impacto financeiro idêntico ao de subgrupos, mas com `head(5)` por peça.

**Passo 2: Construção do Gráfico Horizontal de SKUs**
Implementar o bloco de código para a nova página (Header + KPIs + Chart).
Título: "Onde as vendas de peças perderam fôlego? (Maiores quedas brutas 3Y)"
Legenda: `23/24`, `24/25`, `25/26 (Hoje)`.

**Passo 3: Reorganização das Páginas**
Garantir que a Tabela de Ações (anteriormente Página 2) agora seja a Página 3.

**Passo 4: Verificação Visual**
Executar: `python src/generate_pdf_report_v2.py`
Validar as 3 páginas no PDF gerado.

**Passo 5: Commit**
Usar a skill `commit`.
Mensagem: `feat(report): add Page 2 for SKU-level dropout analysis`
