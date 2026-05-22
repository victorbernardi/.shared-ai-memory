# Especificação Técnica: Redirecionamento de Fonte M2 (Faturamento)

## 1. Problema Identificado
O faturamento reportado nos motores (27M) está distante do real (190M) devido a problemas na `vw_vendas` do banco de dados (Microsoft Fabric). O cache atual é parcial.

## 2. Objetivo
Alterar o **Motor M2 (Faturamento)** para utilizar um arquivo de cache específico como fonte de dados temporária, ignorando qualquer outra tentativa de ingestão via banco ou cache genérico.

## 3. Requisitos de Implementação
- **Arquivo Fonte:** `C:\Projetos\Inova\Potencial Clientes\cache\cache_v1_vendas_dfb67fab7c.parquet`
- **Script Alvo:** `C:\Projetos\Inova\Potencial Clientes\02_Faturamento\motor_de_faturamento_v1.py`
- **Ação:** Forçar o carregamento deste arquivo na variável `df_vendas`, pulando a lógica de `get_safe_cache` para esta tabela.
- **Manutenção de Regras:** O motor M5 deve continuar considerando apenas valores de 2025.

## 4. Critérios de Aceite
- Ao rodar o Motor M2, ele deve processar exatamente os dados contidos no arquivo `dfb67fab7c`.
- O log do M2 deve registrar o uso desta fonte temporária.
