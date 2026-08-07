---
name: inova-protheus-fabric-sql-review
description: Use when reviewing Python or SQL read queries against Protheus data in Microsoft Fabric, JDBC-backed access, Inova analytical views, or historical snapshots.
---

# Inova Protheus Fabric SQL Review

## Visão geral e princípio central

Esta skill revisa consultas Python/SQL de leitura executadas contra dados Protheus expostos no Microsoft Fabric (via JDBC ou ConexaoFabric) e contra views e snapshots analíticos da Inova. O princípio central: **nenhum achado sem evidência e nenhum contrato sem fonte**. Toda afirmação sobre grão, chave, período ou semântica de exclusão deve apontar a fonte observada (tabela crua, pesquisa, view ou snapshot) — regras de um tipo de fonte nunca são transplantadas para outro. Afirmações de grão/chave exigem evidência observada no arquivo ou na consulta; sem isso, o status final é **REVIEW INCOMPLETE**.

## Portão de escopo

**Aplica-se** quando a consulta é de leitura e:
- usa Python (pandas, Spark, pyodbc/JDBC) ou SQL contra dados Protheus no Fabric;
- lê views analíticas (ex.: `vw_VENDAS`) ou snapshots (ex.: `f_vendas_hist31102025`);
- usa `ConexaoFabric`, JDBC ou `load_query`/`query_loader`.

**Fora de escopo** (não aplicar esta skill):
- escrita de dados ou alterações de schema;
- código AdvPL/TLPP, DBAccess ou banco nativo (ver `references/totvs-to-inova-map.md`);
- consultas cujo destino não seja demonstravelmente Protheus no Fabric ou views/snapshots da Inova.

Se o escopo não puder ser confirmado ou faltar evidência da fonte, o status final deve ser **REVIEW INCOMPLETE** — nunca supor.

## Classificação de fontes

Classifique cada fonte citada na consulta antes de revisar:

1. **Tabela crua observada** — ex.: `SA1010`, `VV1010`, `VV2010`, `VO1010`, `VMB010`, `SF2010`. Regra de exclusão observada em um pipeline: `D_E_L_E_T_ = ''`.
2. **Pesquisa (query de research)** — ex.: consulta `VOO010` com `COALESCE(VOO.D_E_L_E_T_, '') <> '*'`. Regra própria, não universalizável.
3. **View** — ex.: `vw_VENDAS`. O contrato é o da view; não aplicar regras de tabela crua.
4. **Snapshot** — ex.: `f_vendas_hist31102025`. O contrato é o do snapshot; validar período de corte.

Detalhes observados por fonte em `references/inova-source-contract.md`. `D_E_L_E_T_ = ''` e `D_E_L_E_T_ <> '*'` são ambos observados em ativos diferentes; nenhum é regra universal Protheus.

## Extração de contrato

Para cada fonte citada, extraia e declare no relatório:

- **Fonte e autoridade**: nome exato da fonte e a **autoridade da fonte** (arquivo/linha do projeto onde o contrato foi observado; contrato registrado; ou evidência coletada na revisão).
- **Grão**: o que uma linha representa — apenas com evidência observada; sem evidência, declarar desconhecido.
- **Chave e cardinalidade**: chave de negócio e cardinalidade esperada nos joins — apenas como candidata quando observada; sem validação de duplicidade/cardinalidade, nunca provada.
- **Período**: filtro temporal aplicado e autoridade do corte (especialmente em snapshots).
- **Semântica de exclusão/status**: regra de `D_E_L_E_T_`/status aplicável àquele tipo de fonte, com evidência.
- **Status nativo vs. fiscal** e **denominador POPS** quando a fonte participa de indicador de faturamento.

Se a fonte não estiver no contrato e não houver evidência na consulta, marque a extração como pendente → **REVIEW INCOMPLETE**.

## Verificações semânticas de SQL

- Filtros por chave de negócio presentes e aplicados no SQL (pushdown), não em memória.
- Joins por chave correta; cardinalidade conhecida ou declarada como candidata; atenção a fan-out (joins 1:N duplicam o grão).
- Período explícito e com tipos compatíveis (datas vs. strings); comparações sem cast implícito.
- Semântica de exclusão/status correta para o tipo de fonte:
  - tabela crua observada: `D_E_L_E_T_ = ''` é aceitável com evidência;
  - view/snapshot: nenhuma regra de exclusão de tabela crua é aplicável sem evidência própria;
  - regra `COALESCE(..., '') <> '*'` da pesquisa VOO010 é exclusiva daquela consulta.
- Resultado final sem duplicatas não justificadas pelo grão declarado.

## Verificações Fabric/JDBC e Python

- **Conexão**: `ConexaoFabric`/JDBC correta e documentada; credenciais nunca em código.
- **Pushdown**: filtros, projeções e joins empurrados ao Fabric; `SELECT *` sem projeção é achado.
- **Python**: uso correto de `load_query`/`query_loader` e tipos de leitura; conversões de data/datetime seguras; sem loops que convertem leitura em N+1.
- **Scan duplicado**: múltiplas leituras da mesma fonte no mesmo pipeline devem ser justificadas.
- **SQL embarcado**: SQL em arquivos `.sql` ou literais em Python revisado da mesma forma; nunca concatenar inputs.

## Verificações de performance/cache

- **Cache**: chave e proveniência do cache explicitadas; nunca assumir que existe cache sem evidência.
- **Custo de scan**: tamanho estimado (linhas/partições) frente ao filtro aplicado.
- **Pushdown e filtragem precoce**: filtrar antes de joins/agregações quando possível.
- **Fan-out e agregações**: conferir se o grão final confere com o grão declarado.
- Todo achado de performance exige **Evidência** (medida, plano, contagem) e **Risco**.

## Formato exigido do relatório

O relatório de revisão deve conter, nesta ordem, todos os campos:

1. **Fonte e autoridade**
2. **Grão**
3. **Chave e cardinalidade**
4. **Período**
5. **Semântica de exclusão/status**
6. **Achados** — cada um com severidade (ALTA/MÉDIA/BAIXA), caminho e linha exatos (arquivo:linha)
7. **Evidência** — citação ou referência concreta
8. **Risco** — impacto em corretude, custo ou segurança
9. **Recomendação** — ação concreta
10. **Validação requerida** — como provar a correção (ex.: conferir contagem, rodar consulta com pushdown)
11. **Status final**

## Regras de status

- **APPROVED**: contrato conferido, achados com evidência, validação requerida definida.
- **NEEDS WORK**: achados com severidade ALTA/MÉDIA que precisam de correção antes do merge.
- **REVIEW INCOMPLETE**: falta evidência (fonte não identificada, contrato não verificado), escopo incerto, ou regra de exclusão/status sem autoridade. Nunca emitir APPROVED sem evidência.

## Exemplo completo

Consulta (pipeline Python, JDBC no Fabric, leitura):

```python
# pipelines/faturamento/leitura_faturamento.py:10
from pathlib import Path
from shared.query_loader import load_query

query = load_query(Path("queries/sa1010.sql"))
df = pd.read_sql(query, conexao_fabric)
df = df[df["D_E_L_E_T_"] == " "]
```

Revisão (formato exigido):

- **Fonte e autoridade**: `SA1010` — tabela crua observada (contrato em `references/inova-source-contract.md`; autoridade: `pipelines/potencial-clientes/01_DNA/extract.py` observa `A1_COD`/`A1_LOJA`/`A1_CGC`/`A1_NOME`).
- **Grão**: cadastro de cliente (dado de cadastro); candidato a chave `A1_COD`+`A1_LOJA` — exige validação de duplicidade/cardinalidade antes de ser provado.
- **Chave e cardinalidade**: candidata, não provada sem validação.
- **Período**: nenhum filtro temporal — leitura completa da tabela.
- **Semântica de exclusão/status**: `D_E_L_E_T_ = ''` em memória sobre tabela crua observada — regra compatível, mas aplicada fora do pushdown.
- **Achados**:
  - `[MÉDIA] pipelines/faturamento/leitura_faturamento.py:10` — `SELECT *` sem projeção; leitura de colunas não usadas.
  - `[MÉDIA] pipelines/faturamento/leitura_faturamento.py:12` — filtro de exclusão aplicado em memória; deveria estar no SQL para pushdown.
- **Evidência**: consulta sem filtro lê a tabela inteira; contrato SA1010 registra grão por cadastro.
- **Risco**: custo de scan alto no Fabric e filtragem tardia.
- **Recomendação**: projetar colunas necessárias e filtrar `D_E_L_E_T_ = ''` e chave no SQL.
- **Validação requerida**: rodar com pushdown ativo e comparar contagem de linhas com a leitura atual.
- **Status final**: NEEDS WORK.

## Erros comuns e red flags

- Universalizar `D_E_L_E_T_ = ''` para views/snapshots sem evidência; `D_E_L_E_T_ = ''` e `D_E_L_E_T_ <> '*'` são ambos observados em ativos diferentes — nenhum é universal.
- Usar a regra `COALESCE(VOO.D_E_L_E_T_, '') <> '*'` fora da pesquisa VOO010.
- Afirmar grão/chave de fonte sem evidência observada no arquivo ou na consulta — sem evidência é **REVIEW INCOMPLETE**.
- Aplicar conceitos AdvPL/DBAccess (`ChangeQuery`, `RetSqlName`, `FWxFilial`, `FWExecStatement`, Workarea, `NOLOCK`) em Python/Fabric — não aplicáveis sem evidência.
- Substituir `ConexaoFabric`/`load_query` por `query-builder` TOTVS em pipelines Python/Fabric.
- Omitir grão, chave, cardinalidade ou período no relatório.
- Recomendação sem evidência ou sem **Validação requerida**.
- Emitir status sem autoridade de fonte — isso é **REVIEW INCOMPLETE**, nunca APPROVED.
