# Plano de Implementação: Correção de Sobreposição do Eixo X

> **Para o Antigravity:** SUB-SKILL REQUERIDA: Use `executing-plans` para implementar este plano tarefa por tarefa.

**Objetivo:** Afastar o rótulo "Impacto Financeiro Estimado" das barras do gráfico.

**Arquitetura:** Ajuste de parâmetro `labelpad` no Matplotlib.

**Tech Stack:** Python, Matplotlib.

---

### Tarefa 1: Ajuste de Layout e Espaçamento

**Arquivos:**
- Modificar: `src/generate_pdf_report_v2.py:147`

**Passo 1: Alterar o labelpad**
Mudar de `labelpad=-2` para `labelpad=15` na linha 147.

**Passo 2: Verificação Visual**
Executar: `python src/generate_pdf_report_v2.py --preview`
Validar: Se o texto desceu o suficiente sem bater na nota de rodapé.

**Passo 3: Commit**
Usar a skill `commit`.
Mensagem: `style(report): fix x-label overlap by increasing labelpad`
