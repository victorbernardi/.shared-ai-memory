# Plano de Implementação: Integração de Faturamento e Subgrupos (v3)

**Goal:** Enriquecer o relatório de histórico de vendas com a dimensão taxonômica (Subgrupos) e a tendência de faturamento dos últimos 3 anos (2023-2025), permitindo identificar quedas críticas por categoria.

**Architecture:**
1. **Extração:** Utilizar `src/extract_faturamento.py` ajustado para buscar o histórico de 3 anos (2023+) e a rentabilidade por item.
2. **Transformação (Join):** Criar um novo script `src/enrich_inventory_data.py` que realiza o merge do Excel de Estoque com os dados do banco (Fabric).
3. **Análise de Tendência:** Calcular a inclinação da curva de vendas por Subgrupo.

---

## Task 1: Ajuste no Motor de Faturamento
- [ ] Modificar `src/extract_faturamento.py` para garantir a extração de dados desde `2023-01-01`.
- [ ] Validar se o JOIN com `SB1010` está trazendo todos os Subgrupos necessários.
- [ ] Implementar a captura do campo `COD_PRODUTO` de forma explícita para o Join.

## Task 2: Script de Enriquecimento (Join Híbrido)
- [ ] Criar `src/enrich_inventory_data.py`.
- [ ] Carregar o Excel de Estoque e o Parquet de Faturamento.
- [ ] Realizar o `merge` pela chave `ITEM`.
- [ ] Atribuir o `SUBGRUPO` às peças que estavam órfãs de categoria no Excel.

## Task 3: Evolução do Relatório PDF (Página de Subgrupos)
- [ ] Adicionar um novo gráfico na Página 1: **"Variação de Vendas por Subgrupo (Last 3 Years)"**.
- [ ] Adicionar o campo `SUBGRUPO` na tabela de detalhamento da Página 2.
- [ ] Implementar o filtro de "Estoque 01" conforme solicitado na análise de transcrição.

---

## Verificação e Validação
- [ ] Validar a integridade do Join (porcentagem de itens enriquecidos).
- [ ] Comparar os totais de faturamento extraídos com os indicadores oficiais de BI.
- [ ] Testar a geração do PDF com a nova volumetria de dados.

---
**Aguardando aprovação para iniciar a pesquisa detalhada no banco de dados e implementação.**
