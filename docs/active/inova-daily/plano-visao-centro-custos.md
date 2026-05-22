# Plano — Visão por Centro de Custos (Carteiras) no Inova Daily

## Objetivo

Adicionar ao relatório diário uma visão gerencial por **Centro de Custo** (`DESCRICAO_CC`), preenchendo o buraco entre a lente de **filial** (geográfica) e a de **cliente** (CNPJ individual). É uma visão **pioneira** — nenhum bloco do daily agrega por CC hoje.

**Fonte: M2 (`cache_vendas_rfm.parquet`), via `faturamento.py`** — a mesma fonte do total do cabeçalho. O M2 já contém `DESCRICAO_CC` e `CENTRO_CUSTO`. Isso garante reconciliação ao centavo com o faturamento exibido (não usar vw_VENDAS, que tem base diferente).

## Descobertas que fundamentam o design

- `DESCRICAO_CC` é um campo achatado com **dois eixos**: **Operação** (Peças / Serviço-MO / Contratos) + **Carteira** (CSN, CRC, WIRTGEN, ATVOS, TERRABEL, FERRO+...). ~25 valores distintos.
- **Concentração:** `PECAS CSN` ≈ 43% da receita do mês. Risco nº1 de uma revenda.
- **1 carteira = N clientes:** CSN = grupo econômico (3 CNPJs), WIRTGEN = marca (~50+ clientes). Lente distinta de cliente.
- **Encoding:** 2 de 25 CCs vêm corrompidos (`PE�AS - TERRABEL`, `PE�AS SERVI�OS`) — exigem normalização para não duplicar buckets.
- **Reconciliação / qualidade de dado (CRÍTICO):** ~26% da receita (R$ 26M YTD 2026) está com `D2_CCUSTO` **em branco direto no Protheus** — confirmado na tabela `SD2010` (fonte). Não é bug de pipeline nem join faltando: o campo não é obrigatório no ERP e o operador emite a NF sem preencher. Por isso o bloco **sempre** inclui uma linha **"Sem Centro de Custo"** — sem ela a soma das carteiras não bate com o faturamento e a confiança no número se perde. Com ela, reconcilia ao centavo. A linha também serve como indicador de governança operacional (pressão visível para tornar o campo obrigatório no Protheus). Sonda periódica de % sem CC por filial: adiada, fora do escopo atual.
- `current_history.py` já puxa `DESCRICAO_CC` mas é um script standalone, **não integrado** ao `generator.py`.

## Design do bloco (2 partes)

**Sem emojis** — segue o padrão textual (markdown puro). O bloco entra logo **após o ranking de filiais** na seção FOTO DE ONTEM.

```
## CENTROS DE CUSTO — {{ data_ontem }}

**Composição Peças x Serviços** (ontem | mês):
- Peças:      R$ 95K (78%)  |  mês: R$ 2.8M (77%)
- Serviço/MO: R$ 22K (18%)  |  mês: R$ 660K (18%)
- Contratos:  R$ 5K  (4%)   |  mês: R$ 180K (5%)

**Carteiras** (receita de ontem · share · vs. média do mês):
1. CSN:     R$ 52K · 43% · +8%
2. WIRTGEN: R$ 18K · 15% · -12%
3. CRC:     R$ 11K · 9%  · +2%
...
- SEM CLASSIFICAÇÃO: R$ 30K · 25%   (receita sem CC no ERP)
> Concentração CSN: 43% da receita do dia (alerta se >50%)
```

A soma de **todas** as linhas (carteiras + SEM CLASSIFICAÇÃO) reconcilia 100% com o faturamento do cabeçalho. A linha SEM CLASSIFICAÇÃO é obrigatória e nunca omitida.

**Convenção de estilo:** o e-mail do Inova Daily NÃO usa emojis. Markdown textual apenas (`##`, `**bold:**`, listas `-`, `>` para alertas).

- **Parte 1 — Composição Peças × Serviços:** saúde do modelo de negócio (core de peças vs. serviço/MO). Receita + % do dia e do mês acumulado.
- **Parte 2 — Ranking de carteiras:** receita do dia, share %, desvio vs. média diária do mês, alerta de concentração quando a maior carteira > 50% do dia.

## Arquitetura (segue padrão do projeto)

- Novo módulo `src/centro_custos.py` (camada de domínio puro): recebe DataFrames do M2, classifica CC em Operação + Carteira, normaliza encoding, trata nulo como "SEM CLASSIFICAÇÃO", agrega. Funções puras, sem I/O.
- **Fonte de dados:** `faturamento.py` ganha `receita_por_cc(df)` ao lado de `receita_por_filial(df)`, lendo do M2 (mesma base do total). **Não** mexer na query da vw_VENDAS para isso.
- `snapshot_diario.py` passa os DataFrames M2 do dia e do mês (`df_dia_m2`, `df_mes`) ao módulo de CC e expõe os resultados no dict de retorno.
- `generator.py` chama o módulo e preenche novos placeholders no `email_template_v3.md`.
- Sem meta por CC (confirmado) → bloco não exibe % de atingimento.
- Os percentuais usam o **total do M2** como denominador (inclui SEM CLASSIFICAÇÃO) → fecham em 100%.

## Fora de escopo (decisões registradas)

- Mini-ranking de clientes do dia — adiado (usuário optou por manter só 2 partes).
- Margem por CC e churn por CC — ficam como sonda avulsa futura (`sonda_batch`), não no daily.
- Meta por CC — não existe.

## Convenção de classificação Operação

- Prefixo normalizado começa com `PECAS` → **Peças**
- Contém `MECANICA` / `ELETRICA` / `SERVICOS` → **Serviço/MO**
- Igual a `CONTRATOS` → **Contratos**
- Normalizar encoding (`PE�AS`→`PECAS`, `SERVI�OS`→`SERVICOS`) antes de classificar.
