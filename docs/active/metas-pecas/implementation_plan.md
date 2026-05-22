# Implementation Plan - Motor de Relatórios M6 (Inova)

## Goal Description
Implementar o motor de relatórios hierárquicos para Inova Equipamentos, integrando o Funil de Vendas (VS1010), o Faturamento Unificado, as Metas 2026 e a Segmentação de Clientes (Pirâmide M5), com foco em governança de dados e visão de safra.

## 📊 Dicionário de Dados Técnico

### Funil de Vendas (Tabela: VS1010)
| Campo | Descrição | Regra de Negócio |
| :--- | :--- | :--- |
| `VS1_NUMORC` | Chave Primária | Identificador único da proposta/orçamento. |
| `VS1_STATUS` | Estado do Funil | `0`=Aberto, `F/I`=Efetivado, `X`=Expirado, `C`=Cancelado. |
| `VS1_DATORC` | Data de Emissão | Base para a análise de Safra (Cohort). |
| `VS1_VTOTNF` | Valor Total | Valor líquido do orçamento para conversão. |
| `VS1_CODVEN` | Cód. Vendedor | Chave para Hierarquia na tabela `SA3010`. |


### Faturamento (Fontes: vw_VENDAS + f_vendas_hist31102025)
| Campo | Descrição | Importância |
| :--- | :--- | :--- |
| `DATA_EMISSAO_NF` | Data da Venda | Define o período de realização financeira. |
| `VALOR_DO_PRODUTO` | Valor Líquido | Base de reconciliação com o Motor M2. |
| `NUMERO_DA_NF` | Nota Fiscal | Identificador da venda realizada. |
| `CODIGO_DO_PRODUTO`| Cód. Produto | Filtro essencial para separar Peças de Máquinas. |
| `DESCRICAO_CC` | Nome CC | Chave de agrupamento para a visão de Metas. |
| `NOME_DO_CLIENTE` | Nome Cliente | Identificação do faturamento. |

### Metas 2026 (Arquivo: metas_2026_processadas.csv)
| Campo | Descrição | Regra de Negócio |
| :--- | :--- | :--- |
| `FILIAL` | Código Filial | Chave de ligação (201, 202, etc.). |
| `SEGMENTO_CC` | Centro de Custo | Agrupador de metas por departamento. |
| `MES_REFERENCIA`| Data da Meta | Primeiro dia do mês da meta. |
| `VALOR_META` | Valor Planejado | Montante em R$ a ser atingido. |
| `NOME_FILIAL_EXCEL`| Nome Original | Referência para auditoria com a planilha. |



## ⚖️ Regras de Governança e Negócio

## Regras de Saneamento e Filtros (DNA Motor M2)

Para garantir a reconciliação 100% com o faturamento financeiro, o Motor M6 aplicará os mesmos filtros do M2:

### 1. Filtros Transacionais (Wave 1)
- **Filial**: `FILIAL LIKE '02%'` (Foco exclusivo em Peças/Aftermarket).
- **Temporalidade**: Restrito aos anos de **2025 e 2026**.
- **TES de Venda (Positivo)**: `501, 504, 505, 506, 522, 541, 542, 543, 593, 600`.
- **TES de Devolução (Negativo)**: `200, 208, 235`.
- **Entidades Internas**: Exclusão de faturamento entre JD e Inova (Roots: `09441113`, `24630514`, `10777176`).

### 2. Filtros de Segmentação (Wave 4)
- **Whitelist de Centros de Custo**: Apenas CCs como 'PECAS CSN', 'PECAS CRC', 'PECAS SERVICOS', etc.
- **Whitelist de Grupos (Resgate)**: Grupos como 'JDPC', 'BAT', 'LUB', 'GRXA' (mesmo em CCs genéricos, desde que não contenham 'MAQUINA' ou 'VEICULO').

---

### Matriz de Decisão de Status
| Status Real | Código Proteus | Ação do Motor M6 |
| :--- | :---: | :--- |
| **Aberto** | `0` | Mantém se emissão < 60 dias. |
| **Efetivado** | `F` ou `I` | Conta como conversão (Independente da data da NF). |
| **Cancelado** | `C` | Exclui da visão de performance. |
| **Expirado** | `X` | Considerado perda (Zumbi). |
| **Zumbi (Auto)** | `0` (Aging > 60) | Reclassifica `0` para `X` automaticamente. |

### Lógica de Resgate e Integração
- **Resgate Branco:** Vendas sem orçamento vinculado geram linha sintética "Venda Direta".
- **Pirâmide M5:** Cada venda/orçamento recebe o "selo" de segmentação (A1, B2, C3) conforme o CNPJ.

## 🛠️ Arquitetura Proposta

### Fluxo de Processamento (Pipeline)
1. **Módulo 0 (Unificação):** `UNION ALL` das bases `vw_VENDAS` e `f_vendas_hist` (Normalizando Tipos e Leading Zeros).
2. **Módulo 1 (Funil):** Saneamento da `VS1010` com aplicação da Regra de Aging.
3. **Módulo 2 (Metas):** Normalização e Melt da planilha `Metas de peças John Deere 2026 - Revisão março.xlsx`.
4. **Módulo 3 (Consolidador):** Join final e exportação para `Performance_Hierarquica_M6.xlsx`.


## 📑 Estrutura do Relatório Final (.xlsx)

Para atender fielmente ao diagrama de arquitetura e permitir Tabelas Dinâmicas (Pivot Tables) nativas, o Excel gerado adotará uma arquitetura **Flat/Tabela Fato** com as seguintes colunas em paralelo:

### Bloco Temporal
- `Data_Base`: Data de referência formatada.
- `Ano` / `Mes_Nome` / `Semana_Ano`: Atributos para comparativos YoY, MoM e WoW.

### Bloco de Gestão de Performance (Hierarquia)
- `Filial`: Nível 1 (N1_Gestão).
- `Centro_de_Custo`: Nível 2 (Quebras de Negócio: Oficina, CRC, Contratos, etc.).
- `Consultor`: Nível 3 (SA3010).

### Bloco de Origem e Status
- `Origem`: 'Balcão' ou 'Oficina'.
- `Status_Funil`: 'EM ABERTO', 'FATURADO', 'CANCELADO', 'EXPIRADO'.

### Bloco de Métricas Financeiras
- `Valor_Orcamento_Aberto`: (R$) do funil ativo.
- `Valor_Realizado_Atual`: (R$) do faturamento da NF.
- `Valor_Meta_2026`: (R$) meta distribuída.
- `Valor_Ano_Anterior`: (R$) faturado no mesmo período em 2025.

## ✅ Plano de Verificação

### Checklist de QA
| Teste | Método | Critério de Sucesso |
| :--- | :--- | :--- |
| **Reconciliação** | Soma M6 vs M2 | Diferença = R$ 0,00 no faturamento. |
| **Vínculo Vendedor** | Join VS1010 + SA3010 | 100% de match nos códigos de vendedor. |
| **Visão de Safra** | Teste de Cohort | Orçamento de Out/25 faturado em Jan/26 deve estar na safra de Out/25. |
| **Aging** | Verificação Zumbi | Propostas > 60 dias não devem aparecer como "Abertas". |
