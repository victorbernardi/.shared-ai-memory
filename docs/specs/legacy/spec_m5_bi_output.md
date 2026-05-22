# Especificação Técnica: Novo Output M5 para BI

## 1. Objetivo
Adicionar um arquivo de saída simplificado ao Motor M5 (Segmentação) para facilitar a ingestão de dados em ferramentas de BI (Power BI/Tableau).

## 2. Requisitos do Arquivo
- **Nome:** `segmentacao_executiva_bi.xlsx`
- **Diretório:** `C:\Projetos\Inova\Potencial Clientes\06_Segmentacao\03_Resultados\`
- **Colunas Obrigatórias:**
    1. `Grupo_Economico`
    2. `Potencial_Total`
    3. `CAL2025_PECAS`
    4. `Quadrante`

## 3. Lógica de Implementação
- O exportador deve ser inserido no final do script `motor_segmentacao_v1.py`, logo após a geração do arquivo executivo principal.
- Deve-se utilizar o DataFrame final consolidado (`df_master_m4` ou similar) já com as classificações de quadrantes aplicadas.
- Caso o arquivo esteja aberto, o script deve gerar um aviso e salvar com um sufixo (timestamp).

## 4. Critérios de Aceite
- O arquivo deve conter exatamente as 4 colunas solicitadas.
- O valor total da coluna `CAL2025_PECAS` deve somar os ~R$ 187M validados anteriormente.
