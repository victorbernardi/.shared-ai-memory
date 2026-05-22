# ADR 0001: Padrões de Qualidade de Dados para o Motor M6

* Status: accepted
* Date: 2026-04-29
* Decision-makers: victor.bernardi, antigravity-agent

## Context and Problem Statement

Identificamos dois problemas críticos na integridade dos dados do Motor M6:
1. **Corrupção de IDs de Filial:** A conversão automática de tipos (float para string) estava transformando códigos como `0201` em `201.0`, impedindo o mapeamento correto dos nomes das filiais.
2. **Duplicidade Semântica:** O relatório transacional apresentava 14,7% de linhas duplicadas porque transações distintas (mesmo cliente/data/valor) eram colapsadas ao omitir o número da NF ou do Orçamento.

## Decision Outcome

Decidimos implementar os seguintes padrões de tratamento de dados:

1. **Higienização de Filiais:** Utilizar a cadeia de conversão `pd.to_numeric(..., errors='coerce').fillna(0).astype(int).astype(str).str.zfill(4)` para garantir que códigos de filial sejam sempre strings de 4 dígitos sem decimais.
2. **Unicidade Transacional:** Incluir obrigatoriamente as colunas `ID_TRANSACAO` (NF ou Número do Orçamento) e `CODIGO_DO_PRODUTO` na camada transacional para garantir a granularidade correta e permitir auditoria.

### Consequences

* **Good:** Mapeamento de filiais 100% acurado, mesmo com dados de entrada sujos.
* **Good:** Eliminação completa de falsos alertas de duplicidade no profiling.
* **Neutral:** Pequeno aumento no tamanho dos arquivos de saída (Excel) devido à maior granularidade.

## Confirmation

A conformidade será verificada através do script `Wave7_YData_Profiling.py`, que deve retornar 0% de duplicados e nenhuma filial com nome "FILIAL 0XXX.0".
