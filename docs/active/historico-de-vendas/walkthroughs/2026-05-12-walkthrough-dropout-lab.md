# Walkthrough: Análise de Dropout de Subgrupos

Implementamos uma ferramenta de laboratório para identificar subgrupos com queda crítica de vendas nos últimos 3 anos, comparando dados do Excel histórico com o Microsoft Fabric.

## 📈 Gráfico de Dropout (Top 5 Piores)

O gráfico abaixo mostra o volume de vendas em janelas isoladas de 12, 24 e 36 meses.
A barra **36 (Escura)** representa o passado distante, enquanto a **12 (Vermelha)** representa o desempenho atual.

![Gráfico de Dropout](/c:/Projetos/Inova/projects/Historico-de-Vendas/data/lab_dropout_subgroups.png)

## 🔍 Achados Principais

1.  **Caso Crítico - FLGD (Bactericida):**
    -   Confirmado em ambas as fontes (Excel e Fabric).
    -   Volume caiu de **1.954** unidades para **320** em 3 anos.
    -   **Insight:** Ação imediata necessária para entender a perda de mercado desta linha.

2.  **Divergências de Escopo:**
    -   Para subgrupos grandes como `LUB`, o Fabric apresenta um volume ~150% maior que o Excel.
    -   **Ressalva:** O Excel de análise foca em itens críticos/estoque, enquanto o Fabric reflete a venda bruta total.

## 🛠️ Detalhes Técnicos
- **Script:** `scripts/lab_dropout_analysis.py`
- **Validação:** Realizada via `MotorExtracaoGenerico` (Fabric).
- **Testes:** Lógica de cálculo coberta por `tests/test_dropout_logic.py`.

## 🚀 Próximos Passos
- Levar a lógica de identificação de Dropout para o motor oficial de PDF.
- Investigar os SKUs específicos dentro do subgrupo `FLGD` que causaram o maior impacto.
