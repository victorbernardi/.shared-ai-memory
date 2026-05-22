# Plano de Implementação:# Migração de Fonte de Dados: Orçamentos M6 (PowerBI + Banco)

Este plano detalha a migração da extração de orçamentos (Pipeline) do Motor M6 para um modelo híbrido que prioriza dados tratados do PowerBI (Excel), mantendo o faturamento e nomes de consultores via Banco Fabric (Protheus).

## User Review Required

> [!IMPORTANT]
> **Conflitos Identificados**: O laboratório detectou **1.296 orçamentos** que constam como "Cancelados" no Excel, mas estão **Faturados** no Banco.
> *   **Ação**: O status do Banco (Faturado) sempre terá precedência absoluta.

> [!NOTE]
> **Status "EXPIRADO"**: Orçamentos que constarem como "Abertos" no Excel, mas que possuírem data de abertura superior a 60 dias (Aging), terão seu status alterado para **EXPIRADO** no output final.

## Proposed Changes

### 1. Novo Motor de Saneamento (`Wave2_Saneamento_BI_Hibrido.py`)

Criação de um novo script que consolida as três fontes de dados:

#### Lógica de Status e Aging:
1.  **FATURADO (Banco)**: Prioridade 1. Se estiver faturado no banco, ignora status do Excel.
2.  **CANCELADO (Excel)**: Prioridade 2. Se estiver na planilha de cancelados e não estiver faturado no banco.
3.  **EXPIRADO (Híbrido)**: Se estiver na planilha de abertos, não estiver faturado, mas a `DATA_ABERTURA` for > 60 dias atrás.
4.  **ABERTO (Excel)**: Se estiver na planilha de abertos, não estiver faturado e o Aging for <= 60 dias.

**Classificação de Origem (Balcão/Serviços/Wirtgen):**
Baseado no `CTT_DESC01` (Centro de Custo) do banco:
*   **WIRTGEN**: Se contém "WIRTGEN".
*   **SERVIÇOS**: Se contém "SERVICO" ou "MECANICA".
*   **BALCÃO**: Demais casos.

### 2. Mapeamento de Saída (Output Excel)

O output final continuará sendo o arquivo `Motor_Gestao_M6_v4_3.xlsx`, com as seguintes origens por aba:

#### Aba `GESTAO_FUNIL` (Visão Agregada)
| Coluna | Origem | Lógica |
| :--- | :--- | :--- |
| `NOME_FILIAL` | Banco/Excel | Nome da Filial padronizado |
| `SEGMENTO` | Fixo | "Peças" |
| `ORIGEM` | Banco (CTT) | Balcão, Serviços ou Wirtgen |
| `VALOR_REALIZADO`| Banco | Soma de `VS1_VTOTNF` (Status F/I) |
| `VALOR_FUNIL` | Excel | Soma de `VALOR` (Status Aberto/Expirado/Cancelado) |
| `QTDE_ORC` | Híbrido | Contagem de números de orçamento únicos |

#### Aba `GESTAO_STATUS_FUNIL` (Visão Detalhada)
| Coluna | Origem | Lógica |
| :--- | :--- | :--- |
| `CONSULTOR` | Banco (SA3) | Nome do Vendedor via `VS1_CODVEN` |
| `CLIENTE` | Banco/Excel | Nome do Cliente |
| `STATUS_ORC` | Híbrido | FATURADO, CANCELADO, ABERTO ou EXPIRADO |
| `AGING_60_DIAS` | Híbrido | "Sim" se status for EXPIRADO, "Não" caso contrário |
| `VALOR_FUNIL` | Híbrido | Valor conforme status |

### 3. Orquestrador (`Wave4_Orquestrador_M6.py`)

#### [MODIFY] [Wave4_Orquestrador_M6.py](file:///C:/Projetos/Inova/Metas%20Pe%C3%A7as/03_Scripts_Rascunhos/Wave4_Orquestrador_M6.py)

## Perguntas e Definições de Design

- **Hierarquia de Status**: FATURADO (DB) > CANCELADO (Excel) > ABERTO (Excel).
- **Valores**: Utilizaremos `VALOR_ORCAMENTO` (DB) para faturados e as colunas de valor do Excel para os demais.
- **Nomes de Consultores**: O `Wave2` exportará a coluna `CONSULTOR` já com o nome completo.

## Verification Plan

### Automated Tests
1. Executar `Wave2_Saneamento_BI.py` e verificar se o CSV é gerado corretamente.
2. Comparar a contagem de linhas e somatórios de valores entre as planilhas Excel e o CSV final.
3. Executar o `Wave4_Orquestrador_M6.py` para garantir que a dashboard HTML final reflita os novos dados.

### Manual Verification
1. Abrir o arquivo `funil_saneado_2025_2026.csv` e verificar se as colunas de Consultor e CNPJ estão preenchidas para orçamentos que existem no banco.
