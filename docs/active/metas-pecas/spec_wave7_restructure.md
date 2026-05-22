# Spec: Reestruturação de Dados Motor M6 (Wave 7.1)

## 1. Objetivo
Evoluir a arquitetura de dados do Motor M6 para suportar visões de metas sem poluir o detalhamento de clientes, além de corrigir distorções na segmentação de CRC e filtrar dados irrelevantes.

## 2. Requisitos Funcionais

### 2.1 Separação de Camadas (Soberania de Grão)
O Motor deve gerar duas entidades distintas no Excel e no Dashboard:
1.  **Performance_Gestao (Agregada):**
    *   **Grão:** [Filial, Segmento, Mês].
    *   **Métricas:** Meta, Realizado (Faturamento), Pipeline (Funil em Aberto).
    *   **Objetivo:** Comparação direta de metas vs realidade sem linhas vazias de clientes.
2.  **Detalhamento_Transacional (Granular):**
    *   **Grão:** [Filial, Segmento, Mês, Cliente].
    *   **Métricas:** Realizado, Pipeline.
    *   **Objetivo:** Identificar quais clientes estão compondo o faturamento ou o funil.

### 2.2 Governança de Segmentos e Filiais
- **CRC (0211):** A filial `0211` deve ser mapeada para o Nome de Filial **CONTAGEM**, mas todas as suas transações devem ser forçadas para o segmento **Peças CRC**.
- **Depósito Fechado (0205):** Deve ser filtrado e removido de todas as bases (Metas, Vendas e Funil).

### 2.3 Regras de Negócio de Segmentação
Manter o mapeamento nominal via `DESCRICAO_CC` (Centro de Custo), garantindo que:
- Se CC contém "CRC" -> `Peças CRC`
- Se CC contém "CONTRATO" -> `Peças Contratos`
- ... (demais regras da Wave 7.0)

## 3. Arquitetura Proposta

### 3.1 Fluxo de Dados
1.  `Wave3`: Processa Metas (ignora Depósito Fechado).
2.  `Wave4`:
    *   Lê Vendas, Funil e Metas.
    *   Aplica remapeamento `0211 -> CONTAGEM`.
    *   Filtra `0205`.
    *   Gera `df_performance` (groupby sum).
    *   Gera `df_transactional` (concat sem metas).
3.  `Wave7`: Atualiza o Dashboard HTML para ler as duas fontes.

## 4. Plano de Validação
- **Teste 1:** Verificar se a filial "CRC" sumiu da lista de filiais, mas o segmento "Peças CRC" aumentou o valor em "CONTAGEM".
- **Teste 2:** Garantir que não existam metas na tabela de Detalhamento de Clientes.
- **Teste 3:** Validar se o total geral de metas no Excel bate com o total do arquivo original.
