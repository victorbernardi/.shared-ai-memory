# Plano de Implementação: Unificação Conceitual (Performance v5)

> **Para o Antigravity:** SUB-SKILL REQUERIDA: Use `executing-plans` para implementar este plano tarefa por tarefa.

**Objetivo:** Alinhar KPIs e Tabela com o tema de Performance de Vendas.

**Arquitetura:** Refatoração de cálculos globais e lógica de tabela no script.

**Tech Stack:** Python, Pandas, Matplotlib.

---

### Tarefa 1: Refatoração dos KPIs de Topo

**Arquivos:**
- Modificar: `src/generate_pdf_report_v2.py`

**Passo 1: Novos Cálculos Globais**
Implementar cálculo de `total_giro_12m`, `total_gap_dropout` e `vitalidade_perc` usando `df_full`.

**Passo 2: Atualizar Header nas Páginas 1 e 2**
Substituir "Inventário Total" e "Capital Excedente" pelos novos KPIs de Performance.

---

### Tarefa 2: Reformulação da Tabela de Ações (Página 3)

**Passo 1: Alterar Ordenação e Título**
Ordenar a tabela por `IMPACTO_FINANCEIRO` (descendente).
Atualizar o título para "MATRIZ DE RECUPERAÇÃO: PRIORIDADES DE RETOMADA".

**Passo 2: Nova Lógica de Ação Sugerida**
Basear a coluna "Ação Sugerida" no cruzamento de Queda vs. Estoque Disponível.

---

### Tarefa 3: Finalização e Verificação

**Passo 1: Geração de PDF e Verificação Visual**
Executar: `python src/generate_pdf_report_v2.py`
Validar se a narrativa está 100% coerente em todas as 3 páginas.

**Passo 2: Commit**
Usar a skill `commit`.
Mensagem: `feat(report): unify report theme around sales performance and recovery`
