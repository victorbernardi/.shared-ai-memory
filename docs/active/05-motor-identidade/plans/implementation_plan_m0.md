# Motor Identidade M0 - Maestro de Unificação

Este plano detalha a criação da Dimensão Global de Clientes (**M0**) na localização oficial, abrangendo 100% da base Protheus e implementando as colunas chaves solicitadas para integração com os motores de DNA e Estratégia.

## User Review Required

> [!IMPORTANT]
> **Escopo Total:** O motor passará a ler TODOS os clientes do SA1010 (não apenas os ativos/faturados), criando a "Tabela Verdade" para o ecossistema Inova.
> **ID_GRUPO:** O `ID_GRUPO_MAESTRO` será composto pelos **8 primeiros dígitos do CNPJ da Matriz** (Raiz do representante do grupo).

## Proposed Changes

### [Projeto e Estrutura]

#### [NEW] [motor_identidade_m0.py](file:///C:/Projetos/Inova/Potencial%20Clientes/05_Motor_Identidade/02_Scripts/motor_identidade_m0.py)
Criação do script oficial na pasta de destino, unindo a lógica de unificação societária com a exportação de colunas ricas.

1.  **Ingestão:** Carregamento completo da tabela `SA1010`.
2.  **Unificação Camada 1 (CNPJ_RAIZ):** Agrupamento padrão pelos 8 primeiros dígitos.
3.  **Unificação Camada 2 (GARANTIA):** Vínculo forçado onde `Data_OS - Data_Venda <= 365 dias`.
4.  **Enriquecimento (Colunas Chave):**
    - `ID_CLIENTE`: Código Protheus (A1_COD + A1_LOJA).
    - `CNPJ_ORIGINAL`: Formato original.
    - `CNPJ_DNA`: 8 dígitos limpos.
    - `NOME_ORIGINAL`: Nome Protheus (A1_NOME).
    - `NOME_DNA`: Nome tratado (sem LTDA, ME, etc).
    - `NOME_GRUPO_ORIGINAL`: Nome do representante do grupo.
    - `NOME_DNA_GRUPO`: Nome tratado do representante do grupo.
    - `CNPJ_GRUPO_RAIZ`: Raiz 8 do grupo unificado.
    - `ID_GRUPO_MAESTRO`: ID gerado (M0-XXXX).

### [Análise e Comparação]

> [!NOTE]
> Farei uma comparação técnica entre o motor legado (`04_Grupo_Economico\motor_grupo_economico.py`) e o novo **M0** para garantir que não perdemos precisão nas unificações de nome (Fuzzy Match). O M0 terá um threshold mais conservador para evitar falsos positivos automáticos.

### [Outputs - C:\Projetos\Inova\Potencial Clientes\05_Motor_Identidade\03_Resultados]

- **Identidade_Master_M0.xlsx:** Tabela Dimensão Completa.
- **Audit_Identidade_IA_M0.xlsx:** Lista de similaridade para revisão, incluindo as colunas de "Match Key" (tokens comuns).

## Open Questions

- **Status:** Todas as questões de negócio foram alinhadas.

## Verification Plan

1.  **Execução:** Rodar o script e verificar se os ~23k clientes estão presentes.
2.  **Validação de Colunas:** Confirmar se as colunas `NOME_DNA` e `NOME_DNA_GRUPO` estão corretamente limpas.
3.  **Sanity Check:** Verificar por que as garantias não apareceram na rodada anterior (provavelmente volume de cache de workshop).
