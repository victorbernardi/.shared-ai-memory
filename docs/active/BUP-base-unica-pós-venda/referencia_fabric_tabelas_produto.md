# Referência: Tabelas de Produto no Fabric (Stout — Cross-sell / Up-sell)

Descobertas durante exploração do Fabric. Insumo para os casos de uso 4 e 5 do Plano Stout
(cross-sell/up-sell inteligente e promoções orientadas por dados).

## Tabelas relevantes

### SB1010 — Cadastro de Produtos

Contém grupos e famílias de produto.

```sql
SELECT DISTINCT B1_GRUPO, B1_FAMILIA
FROM SB1010
WHERE D_E_L_E_T_ = ''
  AND (B1_GRUPO LIKE 'C%' OR B1_GRUPO LIKE 'W%'
       OR B1_FAMILIA LIKE 'C%' OR B1_FAMILIA LIKE 'W%')
```

Campos úteis: `B1_GRUPO`, `B1_FAMILIA`, `B1_COD`, `B1_DESC`.

---

### vw_VENDAS — View de Vendas (já agrega NF + produto)

Contém `CODIGO_FAMILIA`, `DESCRICAO_FAMILIA`, `DESCRICAO_SUBGRUPO`, `DESCRICAO_CC`.
Filtro padrão de filial: `FILIAL LIKE '02%' OR FILIAL LIKE '03%'`.

```sql
-- Famílias de produto ativas em 2026
SELECT DISTINCT CODIGO_FAMILIA, DESCRICAO_FAMILIA
FROM vw_VENDAS
WHERE (FILIAL LIKE '02%' OR FILIAL LIKE '03%')
  AND DATA_EMISSAO_NF >= '2026-01-01'

-- Volume por subgrupo e filial (base para cross-sell)
SELECT
    COD_VENDEDOR, NOME_VENDEDOR, FILIAL,
    DESCRICAO_CC, DESCRICAO_SUBGRUPO,
    SUM(VALOR_DO_PRODUTO) AS Total
FROM vw_VENDAS
WHERE (FILIAL LIKE '02%' OR FILIAL LIKE '03%')
  AND DATA_EMISSAO_NF >= '2026-01-01'
GROUP BY COD_VENDEDOR, NOME_VENDEDOR, FILIAL, DESCRICAO_CC, DESCRICAO_SUBGRUPO
ORDER BY Total DESC
```

---

## Aplicação no Stout

| Caso de uso Stout | Como usar |
|---|---|
| Cross-sell / up-sell | Associar `CODIGO_FAMILIA` comprado por cliente → identificar famílias ausentes no histórico |
| Promoções por segmento | Filtrar subgrupos com baixo giro por filial → campanhas direcionadas |
| Score de propensão | Usar `DESCRICAO_SUBGRUPO` como feature categórica no modelo |
| Previsão de demanda | Agregar `VALOR_DO_PRODUTO` por família + mês para série temporal |
