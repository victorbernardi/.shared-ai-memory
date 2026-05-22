# Plano de Implementação: Ajuste de Título do Relatório PDF

> **Para o Antigravity:** SUB-SKILL REQUERIDA: Use `executing-plans` para implementar este plano tarefa por tarefa.

**Objetivo:** Atualizar o título do gráfico de Dropout para "Onde as vendas perderam fôlego?".

**Arquitetura:** Alteração de string literal no motor de geração de PDF (`matplotlib`).

**Tech Stack:** Python, Matplotlib.

---

### Tarefa 1: Atualização do Título no Gerador de PDF

**Arquivos:**
- Modificar: `src/generate_pdf_report_v2.py:139`

**Passo 1: Aplicar a alteração do título**
Substituir a string na linha 139 conforme a Spec.

```python
# De:
ax1.set_title("O que paramos de vender? (Top 6 Subgrupos por Perda de Capital)", 
# Para:
ax1.set_title("Onde as vendas perderam fôlego? (Top 6 Subgrupos por Perda de Capital)", 
```

**Passo 2: Verificação Visual (Preview)**
Executar o comando de preview para validar o layout e o novo título.
Comando: `python src/generate_pdf_report_v2.py --preview`
Esperado: Arquivo `data/assets/relatorio_v4_preview_p1.png` gerado com o novo título.

**Passo 3: Commit**
Usar a skill `commit` para registrar a alteração.
Mensagem: `feat: update dropout chart title to executive tone`
