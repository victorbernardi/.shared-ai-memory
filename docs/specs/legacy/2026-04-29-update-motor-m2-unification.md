# Especificação Técnica: Motor M2 (Unificação de Faturamento)

**Objetivo:** Consolidar faturamento histórico (2025) e transacional atual do Motor M2, garantindo precisão financeira para cálculo de SOW (Share of Wallet).

## Escopo (In/Out)
**In Scope:**
* Modificação da query SQL principal do `motor_de_faturamento_v1.py` para usar `UNION ALL` entre `vw_VENDAS` e `f_vendas_hist31102025`.
* Remoção de travas estáticas de leitura de cache.
* Configuração do ciclo de vida de persistência de cache local no formato Parquet.

**Out of Scope:**
* Alteração da lógica financeira de cálculo de potencial no Motor M3.
* Modificação nos filtros da "whitelist" de Centro de Custo.

## Requisitos Funcionais (FR)

| ID | Descrição | Implementa |
|---|---|---|
| **FR-001** | O motor deve ingerir dados simultaneamente da view `[dbo].[vw_VENDAS]` e tabela `[dbo].[f_vendas_hist31102025]` usando `UNION ALL`. | AC-1 |
| **FR-002** | O script deve aplicar `CAST` e `TRY_CONVERT(DATE)` explicitamente em todas as colunas extraídas para compatibilizar os schemas. | AC-1 |
| **FR-003** | O filtro temporal da query SQL deve restringir o tráfego para `>= '2025-01-01'`. | AC-1 |
| **FR-004** | O motor deve excluir transações da filial `0205` nativamente na query SQL (padrão M6). | AC-1 |
| **FR-005** | O motor não deve utilizar paths hardcoded (`pd.read_parquet(...)`) para ingestão primária, mas sim o wrapper `get_safe_cache`. | AC-2 |

## Requisitos Não Funcionais (NFR)

| ID | Alvo | Justificativa |
|---|---|---|
| **NFR-001** | Tempo de carga via cache deve ser inferior a 5 segundos após a primeira ingestão. | Garantir a fluidez na execução da cadeia orquestrada (Wave 4). |
| **NFR-002** | Integridade dos Zeros à esquerda (Typesafety) do CNPJ. | Evitar quebra no cruzamento M0 vs M2. |

## Cenários de Teste (T)

| ID | Cenário | Cobre | Resultado Observável |
|---|---|---|---|
| **T-001** | Download inicial (Banco de Dados) | FR-001, FR-005 | A execução com `USE_CACHE=False` deve conectar ao Microsoft Fabric sem falhar no `UNION ALL`. |
| **T-002** | Consistência do Faturamento 2025 | FR-001, FR-003 | O Console Output deve exibir Faturamento Total (Peças) de R$ 193,4M (Aferição Mestra). |
| **T-003** | Consumo Rápido (Cache) | NFR-001 | A segunda execução com `USE_CACHE=True` deve logar "Cache V1 atingido" e rodar instantaneamente. |

## Matriz de Rastreabilidade

| AC (Negócio) | FR (Funcional) | Teste (QA) |
|---|---|---|
| AC-1 (Unificação M2=M6) | FR-001, FR-002, FR-003, FR-004 | T-001, T-002 |
| AC-2 (Dinamicidade) | FR-005 | T-001, T-003 |
