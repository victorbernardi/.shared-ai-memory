# Plano de Ação: Resolução de Duplicidade no Motor M6

Investigamos o alerta do `ydata-profiling` que apontou 14,7% de linhas duplicadas. Identificamos que a duplicidade é **semântica**, causada pela falta de colunas de identificação da transação (NF, Orçamento, Produto) na camada `DETALHE_TRANSACIONAL`.

## Objetivos
1. Eliminar duplicados e aumentar a transparência do relatório transacional adicionando chaves de auditoria.
2. Corrigir a identificação das filiais eliminando decimais (`201.0`) e tratando valores nulos (`nan`).
3. Estabelecer um Registro de Qualidade de Dados para evitar regressões.

## Proposta de Alteração

### [Componente] Motor de Dados (Wave 4)

#### [MODIFY] [Wave4_Orquestrador_M6.py](file:///C:/Projetos/Inova/Metas%20Peças/03_Scripts_Rascunhos/Wave4_Orquestrador_M6.py)
*   **Tratamento de Filiais:** Implementar conversão robusta para remover casas decimais e tratar `NaN` antes do `zfill(4)`.
*   **Ajustar Seleção de Colunas:** Adicionar `NUMERO_DA_NF`, `CODIGO_DO_PRODUTO` e `NUMERO_ORCAMENTO`.
*   **Criar Coluna Unificada:** Criar `ID_TRANSACAO` e `ITEM_PRODUTO`.

### [Componente] Documentação e Governança

#### [NEW] [DATA_QUALITY_REGISTRY.md](file:///C:/Projetos/Inova/Metas%20Peças/01_Documentacao/DATA_QUALITY_REGISTRY.md)
*   Documentar o erro de "Floating Point Filial" e a solução implementada.
*   Documentar o erro de "Semantic Duplicates" e a solução de chaves de auditoria.
*   Este arquivo servirá como memória técnica para futuros desenvolvedores/agentes.


## Verificação
1.  Rodar `Wave4_Orquestrador_M6.py`.
2.  Rodar `Wave7_YData_Profiling.py`.
3.  Validar se o alerta de duplicados caiu para próximo de 0%.

## Riscos
*   **Tamanho do Arquivo:** A adição de colunas aumentará levemente o tamanho do Excel (estimado +5MB).
