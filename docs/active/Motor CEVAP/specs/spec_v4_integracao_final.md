# SPEC: Consolidação Gold v5.1 (Motor CEVAP)

## 1. Contexto e Evolução
Esta especificação atualiza o Motor CEVAP para o estado "Gold", consolidando regras de saneamento de dados, filtros financeiros e novas alavancas comerciais identificadas nos ciclos v4 e v5.

## 2. Escopo Técnico (Modelo Híbrido)

### 2.1 Saneamento de Identidade (IDs)
- **Filtro de IDs Zerados:** Todo registro com `CNPJ_Cliente` ou `CNPJ_Grupo` igual a "0", "00000000000000" ou nulo deve ser descartado no início do processamento para evitar a mistura de grupos econômicos distintos.
- **Normalização:** Todos os CNPJs devem ser tratados como string, removendo caracteres não numéricos e aplicando `zfill(14)` para filiais e `zfill(8)` para raízes.

### 2.2 Janela Financeira e Temporal
- **Recência (Gatilho):** Inatividade >= 90 dias consolidada por **GRUPO (Raiz 8)**.
- **Faturamento (Valor_12m):** Soma do faturamento bruto limitada estritamente aos **últimos 12 meses** (Data Base: 06/05/2026 -> Início: 06/05/2025).
- **Preservação de Potencial:** Clientes classificados como **A1 ou A2** devem ser mantidos na lista mesmo que o faturamento nos últimos 12 meses seja zero (devido a compras realizadas antes de Jan/2025, limite atual da base M3).

### 2.3 Colunas Adicionais e Grão
- **Potencial_Grupo (Novo):** Extraído da base M5 (Segmentação), reflete o potencial total de compra do Grupo Econômico, servindo como KPI de priorização.
- **Nível GRUPO (Raiz 8):**
    - `Classificacao/Segmento`, `Pontos Seedz`, `InovaPay_Limite_Dis`, `Potencial_Grupo`.
    - `Equipamentos`: Fallback (Filial -> Grupo).
- **Nível FILIAL (14 dígitos):**
    - `Contatos`, `N_Orcamento_12m`, `Cidade`.

## 3. Critérios de Aceite (QA Gold)
1. **Match Rate:** 100% de preenchimento na coluna `DT_Ultima_Compra` (Bypass M3 ativado).
2. **Conformidade de ID:** Zero duplicatas de CNPJ e zero IDs zerados.
3. **Filtro de Orçamentos:** Exclusão obrigatória de clientes com orçamentos abertos nos últimos 90 dias.
4. **Layout:** Coluna `Potencial_Grupo` posicionada na Coluna J.

---
*Referência: ADR 0001 (Bypass M3) e Dicionário de Dados v1.1*
