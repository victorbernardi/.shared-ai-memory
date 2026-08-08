# Contrato de Fontes Inova — Protheus exposto no Fabric

Contrato **observado** apenas, extraído dos projetos Inova citados na revisão.
Nenhuma regra aqui é prescritiva fora da fonte que a originou, e nenhum campo
não observado é declarado. Este documento não substitui a evidência: toda
aplicação exige confirmar a fonte e o arquivo onde o contrato foi observado.
Sem evidência, grão/chave/período/status são desconhecidos e o status final é
**REVIEW INCOMPLETE**.

## 1. Regras de exclusão — distinguir, nunca universalizar

- **`D_E_L_E_T_ = ''`** (coluna vazia) é observado em `src/seo_dna_ingest_fabric.py`
  para leitura de dados do pipeline.
- **`D_E_L_E_T_ <> '*'`** é observado na pesquisa VOO010 (research) e no
  `sandbox/investiga_protheus.py` (SF2010 agrupado por `F2_FILIAL`/count).
- **`COALESCE(VOO.D_E_L_E_T_, '') <> '*'`** é a regra própria da pesquisa VOO010;
  não é um padrão de pipeline e não pode ser transplantada.
- **Views e snapshots** (`vw_VENDAS`, `f_vendas_hist31102025`): nenhuma das
  regras acima se aplica automaticamente — o contrato da view/snapshot não
  herda filtros de exclusão de tabelas cruas; sem evidência própria, a regra é
  desconhecida.
- As duas formas observadas (`= ''` e `<> '*'`) convivem em ativos diferentes;
  **nenhuma é regra universal Protheus**.

## 2. Fontes observadas (contrato registrado)

Cada família registra: tipo de fonte, o que foi observado, autoridade do
arquivo e caveat de grão/chave/exclusão.

### SA1010 — dados de cliente (cadastro)

- **Tipo de fonte**: tabela crua Protheus exposta no Fabric.
- **Observado**: campos `A1_COD`, `A1_LOJA`, `A1_CGC`, `A1_NOME`.
- **Autoridade**: `pipelines/potencial-clientes/01_DNA/extract.py`;
  exclusão `D_E_L_E_T_ = ''` observada em `src/seo_dna_ingest_fabric.py`.
- **Grão**: dado de cadastro de cliente.
- **Chave**: `A1_COD`+`A1_LOJA` é **candidata** — exige validação de
  duplicidade/cardinalidade antes de ser provada.
- **Caveat**: cadastro não é fonte de movimento; não usar para faturamento.

### VV1010 — dados de veículo

- **Tipo de fonte**: tabela crua Protheus exposta no Fabric.
- **Observado**: campos `VV1_CHASSI`, `VV1_MODVEI`, `VV1_FABMOD`, `VV1_DOCIND`.
- **Autoridade**: `pipelines/potencial-clientes/01_DNA/extract.py`.
- **Grão**: dado de veículo por chassi.
- **Chave**: chassi é **candidata** — exige validação de duplicidade/
  cardinalidade antes de ser provada.
- **Caveat**: sem evidência, não afirmar período ou chave composta adicional.

### VV2010 — dados de referência de modelo

- **Tipo de fonte**: tabela crua Protheus exposta no Fabric.
- **Observado**: campos `VV2_MODVEI`, `VV2_DESMOD`, `VV2_GRUMOD`, `VV2_ESPVEI`.
- **Autoridade**: `pipelines/potencial-clientes/01_DNA/extract.py`.
- **Grão**: referência de modelo.
- **Chave**: modelo é **candidata** — exige validação de duplicidade/
  cardinalidade antes de ser provada.
- **Caveat**: combinação modelo-código não é chave provada sem validação.

### VO1010 — evidência de oficina/OS

- **Tipo de fonte**: pesquisa (research) sobre tabela crua Protheus.
- **Observado**: campos `VO1_FILIAL`, `VO1_NUMOSV`, `VO1_CHASSI`, `VO1_DATABE`,
  `VO1_DATSAI`, `VO1_STATUS` (status e flags nativos preservados).
- **Autoridade**: `projects/Relatórios/recuperação-POPs/docs/research/queries/fabric_vmb_vo1_operational_profile.sql`.
- **Grão**: evidência de oficina/OS por OS (não afirmado como único).
- **Chave**: filial+OS é **candidata de join**, nunca chave única provada.
- **Caveat**: status nativo da OS não é status fiscal.

### VMB010 — evidência de garantia/DTAC

- **Tipo de fonte**: pesquisa (research) sobre tabela crua Protheus.
- **Observado**: campos `VMB_FILIAL`, `VMB_CODGAR`, `VMB_NUMOSV`, `VMB_CHASSI`,
  `VMB_DTACCS`, `VMB_DTACSL`, `VMB_STATUS` (status e flags nativos preservados).
- **Autoridade**: `projects/Relatórios/recuperação-POPs/docs/research/queries/fabric_vmb_dtac_basic.sql`.
- **Grão**: evidência de garantia/DTAC por OS (não afirmado como único).
- **Chave**: filial+OS é **candidata de join**, nunca chave única provada.
- **Caveat**: execução nativa (garantia/DTAC) não é status fiscal.

### VOO010 — detalhe por natureza (research, regra própria)

- **Tipo de fonte**: pesquisa (research) sobre tabela crua Protheus.
- **Observado**: campos `VOO_FILIAL`, `VOO_NUMOSV`, `VOO_NATPEC`, `VOO_NATSRV`,
  `VOO_FATPAR`, `VOO_TOTPEC`, `VOO_TOTSRV` e `R_E_C_N_O_`.
- **Autoridade**: `projects/Relatórios/recuperação-POPs/docs/research/queries/fabric_voo010_intervention_detail.sql`
  e `fabric_voo010_nature_profile.sql`.
- **Grão**: detalhe por natureza — **não é uma linha por OS**; agregação por
  natureza muda o grão.
- **Predicado de exclusão**: `COALESCE(VOO.D_E_L_E_T_, '') <> '*'` — exato da
  pesquisa; não transplantar para pipelines, views ou snapshots.

### SF2010 — notas fiscais de saída (contagem apenas)

- **Tipo de fonte**: tabela crua Protheus exposta no Fabric.
- **Observado**: apenas que a tabela foi agrupada por `F2_FILIAL` com count e
  `D_E_L_E_T_ <> '*'`.
- **Autoridade**: `pipelines/potencial-clientes/02_Faturamento/sandbox/investiga_protheus.py`.
- **Caveat**: **não** afirmar chave única, período ou schema completo — a fonte
  só estabelece o agrupamento observado.

## 3. Fontes sem suporte — REVIEW INCOMPLETE

### SF3010

- Nenhuma query ou projeção de suporte para `SF3010` foi encontrada nos caminhos
  do projeto fornecidos.
- Tipo de fonte, grão, chave, período e status: **desconhecidos**.
- Resultado: **REVIEW INCOMPLETE** — não inventar campos.

### SFT010

- Nenhuma query ou projeção de suporte para `SFT010` foi encontrada nos caminhos
  do projeto fornecidos.
- Tipo de fonte, grão, chave, período e status: **desconhecidos**.
- Resultado: **REVIEW INCOMPLETE** — não inventar campos.

## 4. Views e snapshots (contrato próprio)

### vw_VENDAS — view corrente (Nov/2025 em diante)

- **Tipo de fonte**: view analítica Inova no Fabric.
- **Período**: Nov/2025 em diante — view corrente.
- **Autoridade**: `02_Faturamento/queries/vendas_pecas_construcao.sql` e seu
  `CONTEXT.md`.
- **Caveat**: contrato da view não herda filtros de exclusão de tabelas cruas;
  grão/chave conforme contrato da view — sem evidência, **REVIEW INCOMPLETE**.

### f_vendas_hist31102025 — snapshot histórico (Jan–Out/2025)

- **Tipo de fonte**: snapshot histórico Inova no Fabric.
- **Período**: Jan–Out/2025 (corte no nome).
- **Autoridade**: `02_Faturamento/queries/vendas_pecas_construcao.sql` e seu
  `CONTEXT.md`.
- **Caveat**: snapshot e view corrente são **períodos distintos**; o contrato do
  snapshot não herda filtros de exclusão de tabelas cruas.

## 5. Denominador POPS e status nativo/fiscal

- **POPS**: `Product_details_full.parquet` é o **denominador** da base POPS.
- **Autoridade**: `recuperação-POPs/CONTEXT.md` e `src/recuperacao_pops/extract.py`
  (precedência de fontes).
- **Execução nativa vs. fiscal**: distinguir sempre (a) o que a fonte nativa
  Protheus registra (execução/status de oficina, garantia/DTAC, exclusão lógica)
  de (b) status fiscal. Uma consulta não pode misturar os dois sem documentar a
  conversão.

## 6. Evidência obrigatória

Para aplicar qualquer contrato deste documento, cite o arquivo/linha do projeto
onde foi observado, ou registre a evidência coletada na revisão. Sem isso, o
status final é **REVIEW INCOMPLETE**.
