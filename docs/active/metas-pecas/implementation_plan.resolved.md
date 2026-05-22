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
| `VS1_CENCUS` | Centro de Custo | Cruzamento via `mapa_centro_custo_pecas.csv`. |
| `VS1_CODVEN` | Cód. Vendedor | Chave para Hierarquia na tabela `SA3010`. |
| `VS1_VLRPRO` | Valor Bruto | Valor nominal do orçamento para conversão. |

### Faturamento (Fontes: vw_VENDAS + f_vendas_hist31102025)
| Campo | Descrição | Importância |
| :--- | :--- | :--- |
| `DATA_EMISSAO_NF` | Data da Venda | Define o período de realização financeira. |
| `VALOR_DO_PRODUTO` | Valor Líquido | Base de reconciliação com o Motor M2. |
| `COD_GRUPO` | Grupo Produto | Filtro essencial para separar Peças de Máquinas. |
| `DESCRICAO_CC` | Nome CC | Chave de agrupamento para a visão de Metas. |

## ⚖️ Regras de Governança e Negócio

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
1. **Módulo 0 (Unificação):** `UNION ALL` das bases `vw_VENDAS` e `f_vendas_hist`.
2. **Módulo 1 (Funil):** Saneamento da `VS1010` com aplicação da Regra de Aging.
3. **Módulo 2 (Metas):** Normalização e Melt da planilha Excel de 2026.
4. **Módulo 3 (Consolidador):** Join final e exportação para `Performance_Hierarquica_M6.xlsx`.

## ✅ Plano de Verificação

### Checklist de QA
| Teste | Método | Critério de Sucesso |
| :--- | :--- | :--- |
| **Reconciliação** | Soma M6 vs M2 | Diferença = R$ 0,00 no faturamento. |
| **Vínculo Vendedor** | Join VS1010 + SA3010 | 100% de match nos códigos de vendedor. |
| **Visão de Safra** | Teste de Cohort | Orçamento de Out/25 faturado em Jan/26 deve estar na safra de Out/25. |
| **Aging** | Verificação Zumbi | Propostas > 60 dias não devem aparecer como "Abertas". |
