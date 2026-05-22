# Plano de Implementação: Melhoria Visual e Correção de Dados - PDF v2 (Horizontal)

**Goal:** Reformular a Página 1 do relatório usando gráficos horizontais e escala logarítmica para garantir a exibição de todos os itens do Top 5.

**Architecture:** Transição para `barh` (barras horizontais). Uso de `np.arange(len(df))` para o eixo Y para forçar a separação de categorias com nomes duplicados. Implementação de `ax.set_xscale('log')` no gráfico de grupos.

**Tech Stack:** Python, Pandas, Matplotlib.

---

### Task 1: Refatoração do Gráfico 1 (Maiores Quedas)
**Files:**
- Modify: `c:/Projetos/Inova/projects/Historico-de-Vendas/src/generate_pdf_report_v2.py`

**Step 1: Implementar Gráfico Horizontal (`barh`)**
Inverter eixos e usar índices numéricos.
```python
y_pos = np.arange(len(top_sku))
ax1.barh(y_pos, top_sku['QUEDA_ABS'], color=color_queda)
ax1.set_yticks(y_pos)
ax1.set_yticklabels(labels)
ax1.invert_yaxis() # Top 1 no topo
```

**Step 2: Ajustar limites e labels**
Remover rotação de ticks e garantir que o texto não corte.

---

### Task 2: Refatoração do Gráfico 2 (Mortalidade)
**Files:**
- Modify: `c:/Projetos/Inova/projects/Historico-de-Vendas/src/generate_pdf_report_v2.py`

**Step 1: Implementar Escala Logarítmica e Barras Horizontais**
```python
ax2.barh(df_morte.index, df_morte.values, color=color_accent)
ax2.set_xscale('log')
ax2.invert_yaxis()
```

---

### Task 3: Redistribuição Espacial com GridSpec
**Files:**
- Modify: `c:/Projetos/Inova/projects/Historico-de-Vendas/src/generate_pdf_report_v2.py`

**Step 1: Configurar Grid 10x1**
Dedicar 2 linhas para Header, 4 para o primeiro gráfico e 4 para o segundo.

---

### Task 4: Verificação Final
**Step 1: Gerar PDF e Validar Layout**
Comando: `python src/generate_pdf_report_v2.py`
**Step 2: Promoção Stout**
Comando: `python scripts/stout_promote.py`

---
**Aguardando aprovação para iniciar a implementação (/build).**
