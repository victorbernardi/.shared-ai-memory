# Plano de Implementação: Sincronização Top 5 (Relatório PDF)

> **Para o Antigravity:** SUB-SKILL REQUERIDA: Use `executing-plans` para implementar este plano tarefa por tarefa.

**Objetivo:** Ajustar o título e a lógica do gráfico de Dropout para "Top 5".

**Arquitetura:** Alteração de parâmetro no ranking e string no título.

**Tech Stack:** Python, Matplotlib.

---

### Tarefa 1: Ajuste de Lógica e Título para Top 5

**Arquivos:**
- Modificar: `src/generate_pdf_report_v2.py:117, 139`

**Passo 1: Alterar o limite do ranking (head)**
Mudar de `head(6)` para `head(5)` na linha 117.

**Passo 2: Atualizar o título do gráfico**
Mudar de "Top 6" para "Top 5" na linha 139.

**Passo 3: Verificação Visual**
Executar: `python src/generate_pdf_report_v2.py --preview`
Validar: Título e barras sincronizados em 5 unidades.

**Passo 4: Commit**
Usar a skill `commit`.
Mensagem: `fix(report): synchronize dropout chart title and logic to Top 5`
