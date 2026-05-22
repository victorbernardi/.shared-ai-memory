# Task List - Motor M6 Inova

## 🌊 Wave 1: Data Unification (Camada Lakehouse)
*Objetivo: Garantir a base histórica de faturamento sem lacunas temporais.*
- [ ] Conectar ao Microsoft Fabric (LH_Consumo).
- [ ] Extrair `vw_VENDAS` (Dados pós-nov/2025).
- [ ] Extrair `f_vendas_hist31102025` (Histórico 2017-out/2025).
- [ ] Padronizar a coluna `DATA_EMISSAO_NF` (conversão de string para datetime).
- [ ] Realizar o `UNION ALL` consolidando a série temporal.
- [ ] Aplicar filtros base (Filial `02%`, TES válidas do M2).

## 🌊 Wave 2: Saneamento do Funil (Camada Proteus)
*Objetivo: Extrair orçamentos e limpar dados fantasmas.*
- [ ] Criar o script `extrator_funil_proteus.py`.
- [ ] Consultar a tabela `VS1010` (Orçamentos).
- [ ] Aplicar lógica de Status (`0`, `F`, `I`, `X`, `C`).
- [ ] Implementar a regra de Aging: Reclassificar status `0` > 60 dias para `X`.
- [ ] Realizar de-para de Centros de Custo (`mapa_centro_custo_pecas.csv`).
- [ ] Validar integridade dos códigos de vendedor (`SA3010`).

## 🌊 Wave 3: Processamento de Metas (Camada Excel)
*Objetivo: Transformar a planilha de metas em um formato tabular relacional.*
- [ ] Criar o script `processador_metas_excel.py`.
- [ ] Implementar normalização de Filiais (ffill na coluna `Unnamed: 0`).
- [ ] Realizar o Melt das colunas de meses (Jan a Dez) para formato de linha temporal.
- [ ] Padronizar nomes de segmentos para match com Centros de Custo.

## 🌊 Wave 4: Orquestração e Integração M5 (Camada Core)
*Objetivo: O cérebro do M6 que une todas as fontes e aplica regras de negócio finais.*
- [ ] Criar o script `motor_relatorio_hierarquico.py`.
- [ ] Executar o Join: Faturamento Unificado (Wave 1) + Funil (Wave 2).
- [ ] Executar o Join com as Metas Processadas (Wave 3).
- [ ] Integrar base da Pirâmide M5 (Classificação CNPJ A1, B2, etc.).
- [ ] Implementar regra do "Resgate Branco" (Criar linha sintética para vendas sem orçamento).
- [ ] Formatar o Dataframe no layout Flat/Tabela Fato (Colunas paralelas de Valores).
- [ ] Exportar artefato final: `Performance_Hierarquica_M6.xlsx`.
## 🌊 Wave 5: QA e Reconciliação Financeira
*Objetivo: Provar matematicamente que o motor está correto.*
- [ ] Executar script de comparação de Soma M6 vs M2 (Erro admissível = R$ 0,00).
- [ ] Validar se orçamentos "zumbis" desapareceram da visão de abertos.
- [ ] Conferir o "Encaixe" das safras (ex: Venda em Janeiro de orçamento de Outubro).
