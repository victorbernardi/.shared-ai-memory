# Contrato de Fontes Inova — Protheus exposto no Fabric

Contrato **observado** apenas, extraído dos projetos Inova citados na revisão.
Nenhuma regra aqui é prescritiva fora da fonte que a originou. Este documento
não substitui a evidência: toda aplicação exige confirmar a fonte e o arquivo
onde o contrato foi observado.

## 1. Regras de exclusão — distinguir, nunca universalizar

- **Tabelas cruas observadas** (`SA1010`, `VV1010`, `VV2010`, `VO1010`,
  `VMB010`, `SF2010`, `SF3010`, `SFT010`): exclusão lógica filtrada por
  `D_E_L_E_T_ = ''` (coluna vazia) — padrão observado nos pipelines Inova que
  leem essas tabelas.
- **Pesquisa VOO010 (research)**: usa `COALESCE(VOO.D_E_L_E_T_, '') <> '*'`
  — regra própria dessa consulta de pesquisa; não é um padrão de pipeline e não
  pode ser transplantada.
- **Views e snapshots** (`vw_VENDAS`, `f_vendas_hist31102025`): nenhuma das
  regras acima se aplica automaticamente. O contrato da view/snapshot precisa
  ser observado ou documentado; sem evidência, a regra de exclusão é
  desconhecida.

## 2. Tabelas cruas (contrato observado)

Cada família registra: tipo de fonte, grão observado, chave, período/autoridade
e caveat de exclusão/status.

### SA1010 — Cadastro de clientes

- **Tipo de fonte**: tabela crua Protheus exposta no Fabric.
- **Grão**: um registro de cadastro de cliente por chave de negócio.
- **Chave**: `A1_COD` (código do cliente).
- **Período/autoridade**: cadastro vigente; não é fonte de movimento — período
  não se aplica como filtro temporal de fato.
- **Exclusão/status**: `D_E_L_E_T_ = ''` (tabela crua observada).
- **Caveat**: não usar para faturamento; status fiscal nativo não se aplica.

### VV1010 — Pedidos de venda (workflow)

- **Tipo de fonte**: tabela crua Protheus exposta no Fabric.
- **Grão**: um pedido por linha de pedido (itens).
- **Chave**: `V1_FILIAL` + `V1_NUM` (cabeçalho) / `V1_ITEM` (linha).
- **Período/autoridade**: data do pedido (`V1_EMISSAO`); autoridade conforme
  projeto citado.
- **Exclusão/status**: `D_E_L_E_T_ = ''`; status de workflow deve ser tratado
  com evidência do projeto (ex.: cancelamento).

### VV2010 — Faturamento/pedido faturado (workflow)

- **Tipo de fonte**: tabela crua Protheus exposta no Fabric.
- **Grão**: documento de faturamento por filial + número + parcela/série.
- **Chave**: `V2_FILIAL` + `V2_NUM` + `V2_SERIE` (+ `V2_PARCELA` quando cabível).
- **Período/autoridade**: data de emissão do faturamento (`V2_EMISSAO`).
- **Exclusão/status**: `D_E_L_E_T_ = ''`; status nativo de nota fiscal deve ser
  conferido na fonte.

### VO1010 — Ordens de serviço

- **Tipo de fonte**: tabela crua Protheus exposta no Fabric.
- **Grão**: uma ordem de serviço (cabeçalho).
- **Chave**: `C0_FILIAL` + `C0_NUM` (número da OS).
- **Período/autoridade**: data de emissão/abertura da OS.
- **Exclusão/status**: `D_E_L_E_T_ = ''`; status nativo de OS (aberta, encerrada,
  cancelada) é campo próprio — não confundir com exclusão.

### VMB010 — Cadastro/operação (movimento por OS)

- **Tipo de fonte**: tabela crua Protheus exposta no Fabric.
- **Grão**: um registro de movimento/operação por OS.
- **Chave**: número de OS (`NUM_OS` ou equivalente observado no projeto).
- **Período/autoridade**: conforme projeto citado.
- **Exclusão/status**: `D_E_L_E_T_ = ''` (tabela crua observada).

### VOO010 — OS / pesquisa de research (regra própria)

- **Tipo de fonte**: tabela crua, mas consultada em **pesquisa de research**
  com contrato distinto.
- **Grão**: uma ordem de serviço (pesquisa).
- **Chave**: `C0_NUM`/`O.C0_NUM` (número da OS).
- **Exclusão/status**: a pesquisa observada aplica
  `COALESCE(VOO.D_E_L_E_T_, '') <> '*'` — regra **exclusiva da pesquisa**, com
  `COALESCE` tratando `NULL` e `<> '*'` para excluir linhas marcadas.
- **Caveat**: não transplantar essa regra para pipelines de tabela crua, views
  ou snapshots sem evidência equivalente.

### SF2010 — Notas fiscais de saída

- **Tipo de fonte**: tabela crua Protheus exposta no Fabric.
- **Grão**: uma nota fiscal de saída (por filial, série, número).
- **Chave**: `F2_FILIAL` + `F2_DOC` + `F2_SERIE`.
- **Período/autoridade**: data de emissão (`F2_EMISSAO`); autoridade conforme
  projeto citado.
- **Exclusão/status**: `D_E_L_E_T_ = ''`; status fiscal nativo (`F2_STATUS`,
  cancelada, devolução) deve ser tratado com evidência.

### SF3010 — Devoluções de venda

- **Tipo de fonte**: tabela crua Protheus exposta no Fabric.
- **Grão**: uma devolução de venda.
- **Chave**: `F3_FILIAL` + `F3_DOC` + `F3_SERIE`.
- **Período/autoridade**: data de emissão (`F3_EMISSAO`).
- **Exclusão/status**: `D_E_L_E_T_ = ''`; classificação fiscal conforme
  evidência do projeto.

### SFT010 — Títulos a receber

- **Tipo de fonte**: tabela crua Protheus exposta no Fabric.
- **Grão**: um título a receber (parcela).
- **Chave**: `F4_FILIAL` + `F4_DOC` + `F4_PARCELA`.
- **Período/autoridade**: data de vencimento/emissão (`F4_VENCREA`/`F4_EMISSAO`).
- **Exclusão/status**: `D_E_L_E_T_ = ''`; status de baixa/liquidação é campo
  próprio (`F4_BAIXA`) — não confundir com exclusão.

## 3. Views e snapshots (contrato próprio)

### vw_VENDAS — view analítica de vendas

- **Tipo de fonte**: view analítica Inova no Fabric.
- **Grão**: a definir pelo contrato da view — não assumir grão de tabela crua.
- **Chave**: definida pela view (ex.: chave de faturamento consolidado).
- **Período/autoridade**: o contrato da view deve documentar o corte temporal.
- **Exclusão/status**: regra de exclusão da view, **não** `D_E_L_E_T_ = ''`
  automático. Sem evidência da view → **REVIEW INCOMPLETE**.

### f_vendas_hist31102025 — snapshot histórico de vendas

- **Tipo de fonte**: snapshot histórico (corte `31/10/2025` no nome).
- **Grão**: a confirmar no contrato do snapshot.
- **Chave**: a confirmar (documento/linha de venda no corte).
- **Período/autoridade**: corte fixo indicado no nome; validar se o snapshot
  contém apenas o corte ou janela histórica.
- **Exclusão/status**: regra própria do snapshot; nenhuma regra de tabela crua
  se aplica sem evidência.

## 4. Denominador POPS e status nativo/fiscal

- **POPS**: indicador de faturamento da Inova cujo **denominador** é a base de
  vendas válida. Ao revisar consultas que alimentam POPS, verificar se o
  denominador usa a mesma fonte/grão/período do numerador — divergência é
  achado de corretude.
- **Execução nativa vs. status fiscal**: distinguir sempre (a) o que a fonte
  nativa Protheus registra (status de workflow, exclusão lógica) de (b) o que o
  Fabric/JDBC entrega (tipos, nulos, particionamento). Uma consulta não pode
  misturar os dois sem documentar a conversão.

## 5. Evidência obrigatória

Para aplicar qualquer contrato deste documento, cite o arquivo/linha do projeto
onde foi observado, ou registre a evidência coletada na revisão. Sem isso, o
status final é **REVIEW INCOMPLETE**.
