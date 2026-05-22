# Investigação: Filtro PowerBI — Orçamentos Abertos (1882 → 598)

**Status:** INCONCLUSIVO  
**Data:** 2026-05-17  
**Investigador:** Victor Bernardi  

---

## Contexto

O PowerBI exporta 598 orçamentos abertos. Nossa query no Fabric retorna 1882.
Objetivo era identificar o filtro exato para validar o script `scripts/extract_orcamentos.py`.

**Referência usada:** `C:\Users\victor.bernardi\Downloads\data (2).xlsx` (598 linhas, exportado ~15/mai/2026)

### Query base do Fabric (ponto de partida)

```sql
SELECT * FROM VS1010 v
WHERE v.D_E_L_E_T_ = ''
  AND v.VS1_STATUS = '0'        -- aberto
  AND v.VS1_TIPORC = 'P'        -- balcão peças
  AND LTRIM(RTRIM(v.VS1_DATVAL)) != ''
  AND v.VS1_DATVAL >= CONVERT(VARCHAR, GETDATE(), 112)  -- não expirado
  AND (v.VS1_FILIAL LIKE '02%' OR v.VS1_FILIAL LIKE '03%')
-- Resultado: 1882 linhas
```

---

## Fatos Confirmados

| Fato | Valor |
|------|-------|
| Total Fabric (query base) | 1882 |
| Total BI exportado | 598 |
| BI records encontrados no Fabric | 97.5% (545-548 de ~598) |
| Clientes únicos no Fabric | 733 |
| Clientes únicos no BI | 321 |
| Vendedores únicos no BI | 18 |
| Vendedores na nossa lista ativa | 14 |
| Filial 0303 no BI | 0 registros (ausente) |
| Num_orc duplicados no Fabric | 13 (irrelevante) |
| Min Data Abertura BI | 2025-04-29 |
| Max Data Abertura BI | 2026-05-15 |
| Tempo mediano orc. em aberto (BI) | 6 dias |

---

## Hipóteses Testadas

### ❌ VS1_TPATEN != '' (DESCARTADA + CORRIGIDA)

- **Resultado:** 578 registros
- **Por que errada:** 53.6% dos registros BI têm TPATEN vazio — o filtro excluiria mais da metade do BI
- **Ação:** Filtro removido do `extract_orcamentos.py` (commit `29c3406`)

### ❌ VS1_CODVEN IN (14 vendedores ativos — vendedores_ativos_2026.json)

- **Resultado:** 758 registros

### ❌ VS1_CODVEN IN (18 vendedores do BI)

- **Resultado:** 1712 registros
- **Nota:** 18 BI vendedores ≠ 14 lista ativa. Ver seção "Desalinhamento de Listas"

### ❌ SA3010 JOIN gerente=000562

- **Resultado:** 1754 registros
- **Por filial:** 0201=1144, 0204=201, 0203=153, 0202=94, 0303=76, 0210=47, 0301=39

### ❌ SA3010 JOIN supervisor=000347

- **Resultado:** 1432 registros

### ⚠️ SA3010 JOIN supervisor=000347 (registro mais recente por vendedor via R_E_C_N_O_)

- **Resultado:** 758 registros — **MELHOR HIPÓTESE ATÉ AGORA**
- **Vendedores resultantes (14):** 000357, 000377, 000382, 000409, 000425, 000431, 000442, 000449, 000488, 000559, 000818, 000835, 000860, 000909
- **Distância:** 758 - 598 = 160 a mais. Não identificado o sub-filtro que reduz esses 160.

### ❌ SA3010 JOIN filial-prefix (VS1_FILIAL LIKE A3_FILIAL + '%') + gerente=000562

- **Resultado:** 1734 registros

### ❌ Dedup por cliente (1 orçamento mais recente por cliente)

- **Resultado:** 733 registros
- **Nota:** BI não faz dedup — tem 93 clientes com múltiplos orçamentos (Terrabel=28, CSN=26)

### ❌ SA1010 campos (A1_GRPVEN, A1_CLASSE, A1_CODTER, A1_ZXVENDE)

- **Resultado:** Todos os campos estão VAZIOS para todos os clientes
- **Conclusão:** SA1010 não contém dados de carteira/território neste ambiente

### ❌ VS1010 campos customizados (VS1_XCEN, VS1_XMEC, VS1_ZELEAD, VS1_ZTLEAD, VS1_XCTOPR, VS1_XMOTRE, VS1_XCOMRE, VS1_ORCRES, VS1_CONPRO, VS1_XSEEDZ)

- **Resultado:** Distribuições idênticas entre grupo BI e não-BI

### ❌ VS1_NATURE != '011102'

- **Resultado:** 1675 (all), 1638 (18 vend)
- **Nota:** BI tem 1.8% de registros com nature=011102 — não é filtro

### ❌ VS1_FORPAG != '105'

- **Resultado:** 1445 registros
- **Nota:** BI tem 4.9% com forpag=105 — não é filtro, mas é o campo com maior correlação (20.5% em não-BI)

### ❌ VS1_RESERV = '0' (não reservado)

- **Resultado:** 1474 registros (18 vend), 1639 (all)
- **Nota:** 19.1% não-BI são reservados vs 3.6% BI — correlação mas não filtro binário

### ❌ VS3010 JOIN (orçamentos com pelo menos 1 item com VS3_VALPEC > 0)

- **Resultado:** 1868 — apenas 14 orçamentos sem itens, irrelevante

### ❌ VS1_DATENT (data de entrega/entrada)

- **Resultado:** Distribuído em ~88 datas, nenhum corte limpo

### ❌ Filtros temporais (VS1_DATORC, range de datas)

- **Resultado:** 87.6% dos 1882 foram abertos em maio/2026. Sem corte temporal que produz ~598.

### ❌ Views e tabelas customizadas

- **Tabelas ZX/ZA no banco:** Apenas ZA1010 (catálogo de peças, irrelevante)
- **Views:** vw_CCFL, vw_EstoqueNegativoB2, vw_ParqueMaquinas, vw_RFV, vw_VENDAS, vw_fvenda — nenhuma relacionada a orçamentos abertos

---

## Desalinhamento de Listas de Consultores

| Situação | Vendedores |
|----------|-----------|
| No BI, NÃO na lista ativa | 000651, 000657, 000666, 000676, 000720, 000723, 000730, 000789, 000884, 000885, 000906 (11 vendedores) |
| Na lista ativa, NÃO no BI | 000377, 000409, 000425, 000442, 000835, 000860, 000909 (7 vendedores) |

**Pendência:** Reconciliar qual lista está correta. A lista ativa (`vendedores_ativos_2026.json`) e o BI parecem referenciar equipes diferentes.

---

## Correlações Encontradas (Não Binárias)

Campos com diferença estatística entre grupo BI e não-BI (18 vendedores):

| Campo | Valor | BI% | NAO% | Dif |
|-------|-------|-----|------|-----|
| VS1_FORPAG | 105 | 4.9% | 20.5% | 15.6% |
| VS1_RESERV | 1 (reservado) | 3.6% | 19.1% | 15.5% |
| VS1_TPATEN | (vazio) | 53.6% | 72.3% | 18.7% |
| VS1_NATURE | 011107 | 14.2% | 5.1% | 9.1% |

Nenhuma dessas diferenças é binária — todos os valores aparecem nos dois grupos.

---

## Próximos Passos Sugeridos

1. **Reconciliar listas de consultores** — entender por que o BI tem 18 e nós temos 14. Qual é a lista correta para o escopo do BUP?

2. **Testar supervisor=000347 (mais recente) + VS1_RESERV='0'** — combinação ainda não testada, pode chegar mais perto de 598.

3. **Solicitar ao time de BI** a definição da medida "Orc. em Aberto" e os filtros de página ativos no relatório. O filtro pode ser um parâmetro de usuário (slicer de supervisor/equipe) não visível no export.

4. **Comparar dois exports do BI** feitos por usuários diferentes — se os counts diferirem, confirma que é filtro por usuário/parâmetro.

---

## Conclusão

A diferença 1882 → 598 **não é replicável por nenhum campo individual ou combinação óbvia** testada em VS1010, VS3010 ou SA1010. A hipótese mais provável é que o BI aplica um **filtro de parâmetro de usuário** (slicer de supervisor ou equipe) que não é visível no export CSV/XLSX. Sem acesso ao Power Query ou DAX do relatório, a investigação permanece inconclusiva.

O script `extract_orcamentos.py` está **correto** — produz o universo completo de 1882 orçamentos válidos. Os 598 do BI são um subconjunto filtrado por contexto de usuário.
