# Especificação Técnica: Ajuste de Ranking para Top 5 (Dropout Analysis)

**Data:** 2026-05-13  
**Status:** Validado  
**Projeto:** historico-de-vendas  

---

## 1. Objetivo
Sincronizar a comunicação visual do gráfico de Dropout com a realidade dos dados, ajustando o ranking de "Top 6" para "Top 5", mantendo o critério de relevância estatística (mínimo de 10 unidades vendidas historicamente).

## 2. Requisitos de Negócio
- **Fidelidade de Dados:** O título deve refletir exatamente o número de barras exibidas.
- **Relevância:** Manter o filtro de volume mínimo (10 unidades) para evitar ruído de itens esporádicos com baixo giro histórico.

## 3. Mudanças Propostas

### 3.1. Lógica de Ranking
- **Arquivo:** `src/generate_pdf_report_v2.py`
- **Linha:** ~117
- **Ação:** Alterar `head(6)` para `head(5)`.

### 3.2. Título do Gráfico
- **Arquivo:** `src/generate_pdf_report_v2.py`
- **Linha:** ~139
- **Ação:** Alterar `"Top 6 Subgrupos"` para `"Top 5 Subgrupos"`.

## 4. Plano de Validação
- [ ] Gerar PDF e verificar se o título agora diz "Top 5".
- [ ] Confirmar que 5 barras são exibidas e que o layout permanece equilibrado.
- [ ] Validar que o filtro de volume (>= 10) continua ativo.

---
**Próximo Passo:** Gerar o Plano de Implementação (Strategy).
