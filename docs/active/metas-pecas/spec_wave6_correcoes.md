# Especificação Técnica: Motor M6 (Wave 6 - Correções e Refinamentos)

## 1. Diagnóstico dos Problemas Relatados

### 1.1 Metas Zeradas na Aba GESTAO_PERFORMANCE
**Causa Raiz:** O campo `FILIAL` no arquivo `metas_2026_processadas.csv` possui o formato numérico/float (ex: `201.0`). Ao tentar converter para string e preencher com zeros (zfill), o resultado foi `'201.0'`, que não encontrou correspondência no dicionário `map_nomes_filiais` (esperava `'0201'`). Isso resultou em filiais `NaN` nas metas, que foram removidas no groupby.

### 1.2 Ausência da Filial "GRUPO"
**Causa Raiz:** Na base de metas, os valores corporativos possuem o campo `FILIAL` nulo (`NaN`). Esses valores estavam sendo ignorados.

### 1.3 Valor Funil sem Nenhum Cliente (NOME_DO_CLIENTE vazio)
**Causa Raiz:** A base `funil_saneado_2025_2026.csv` contém `CODIGO_CLIENTE` e `LOJA_CLIENTE`, mas não o NOME_DO_CLIENTE.
**Análise sobre o M0:** O dataset de identidade M0 possui a coluna `ID_CLIENTE` (que é a concatenação de CÓDIGO e LOJA). Porém, ao cruzar o M0 com o Funil, **apenas 71 clientes do Funil foram encontrados no M0** (num universo de 3.903 clientes no funil). O M0 foca apenas nas "Big Accounts" e Quadrantes mapeados, e deixaria 98% do funil sem nome.

### 1.4 Valor Funil 100% Alocado em Peças e Acessórios
**Causa Raiz:** O script anterior aplicou um *hardcode* (`'Peças e Acessórios'`) pois a Wave 2 não estava importando o Centro de Custo. 
**Análise na VS1:** Investigamos a tabela `VS1` e descobrimos que **ela possui sim a coluna `VS1_CENCUS`**. Portanto, podemos mapear o Segmento de forma idêntica ao faturamento, bastando adicionar a coluna na query da Wave 2.

### 1.5 Remoção do Depósito Fechado
**Causa Raiz:** A filial `0205` (Depósito Fechado) está sendo extraída ativamente na query original do Fabric na Wave 1.

### 1.6 Mapeamento de Segmentos
**Causa Raiz:** O mapa de segmentos não estava aderente aos 10 nomes exatos passados.

---

## 2. Decisões Arquiteturais e Impactos
*   **Identificação do Cliente no Funil:** Dado que o M0 cobre apenas uma fração do funil, a alternativa viável para ter 100% dos nomes é criar uma *query* auxiliar na Wave 4 (ou na Wave 2) para consultar a tabela de Clientes (`SA1`) no Fabric, trazendo o `A1_NOME` e unificando via `CODIGO_CLIENTE` e `LOJA_CLIENTE`.
*   **Segmentação do Funil:** Será resolvido extraindo `VS1_CENCUS` e usando a mesma função `classificar_segmento()`.
