# Especificação Técnica: Extração de Orçamentos Cancelados via Fabric

## 1. Escopo e Objetivos
O objetivo desta especificação é definir a implementação da extração de **Orçamentos Cancelados** diretamente da base de dados do Microsoft Fabric, desconsiderando a raspagem via browser (Power BI Embedded), uma vez que a validação confirmou que o Fabric possui 100% dos dados e colunas necessários.

---

## 2. Validação dos Dados no Microsoft Fabric
A comparação provou que a tabela do Power BI compartilha exatas 7 colunas em comum com a extração do Fabric. O Fabric possui adicionalmente o campo de código do motivo de cancelamento (`codigo_motivo`), permitindo maior rastreabilidade.

### Estrutura dos Dados no Fabric:
* **Tabela de Cabeçalho do Orçamento:** `dbo.VS1010` (Campos `VS1_FILIAL`, `VS1_NUMORC`, `VS1_DATORC`, `VS1_CLIFAT`, `VS1_LOJA`, `D_E_L_E_T_`).
* **Tabela de Itens do Orçamento (Foco principal):** `dbo.VS3010` (Coluna `VS3_MOTPED` que armazena o código do motivo de cancelamento, `VS3_VALTOT` com o valor do item, `VS3_CODITE` com o código da peça, `D_E_L_E_T_`).
* **Mapeamento de Filiais no Código:**
  * `"0201"` -> `"0201 - Contagem"`
  * `"0202"` -> `"0202 - Tanguá"`
  * `"0203"` -> `"0203 - Serra"`
  * `"0204"` -> `"0204 - Uberlândia"`
  * `"0210"` -> `"0210 - Pouso Alegre"`
  * `"0301"` -> `"0301 - Contagem"`
  * `"0302"` -> `"0302 - Pompéu"`
  * `"0303"` -> `"0303 - Serra"`
* **Dicionário de Motivos (`VS3_MOTPED`):**
  * `"000000"`: `"APENAS CONSULTA DE PRECO"`
  * `"000001"`: `"INDISPONIBILIDADE DE PECA"`
  * `"000002"`: `"CLIENTE NEGA JUSTIFICATIVA"`
  * `"000003"`: `"ORCAMENTO DUPLICADO"`
  * `"000004"`: `"PRECO MENOR NO CONCORRENTE"`
  * `"000005"`: `"VENDA PARA FORA DA REGIAO"`
  * `"000006"`: `"CLIENTE SEM CREDITO"`
  * `"000007"`: `"FALTA DE FOLLOW UP DO VENDEDOR"`

---

## 3. Estratégia de Extração (SQL no Fabric)
A extração ocorrerá através de conexão JDBC mapeada no módulo `shared/fabric_db.py`.

### Filtro de Datas:
A consulta aceitará parâmetros opcionais de data de início e de fim. No Protheus, as datas são armazenadas em formato string `AAAAMMDD` (ex: `'20250101'`).
* Filtro padrão de data de início: `'20250101'`.

---

## 4. Requisitos de Código (Python)
* Gravação e leitura de arquivos texto obrigatoriamente usando `encoding='utf-8'`.
* Integração com a classe `ConexaoFabric` da pasta centralizada `shared`.
