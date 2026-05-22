# Spec: Wave 9 — Automação de Deployment (OnePage Dashboard)

- **Status:** Draft
- **Data:** 2026-04-30
- **Autor:** Antigravity (Stout Edition)
- **Versão:** 1.0

## 1. Objetivo
Automatizar a atualização do Dashboard OnePage (`index.html`) garantindo que a publicação dos dados só ocorra após a validação bem-sucedida da **Wave 8 (Auditoria)**.

## 2. Requisitos

### 2.1 Funcionais
- **Orquestração:** Executar sequencialmente a Wave 4 (Processamento) e a Wave 8 (Auditoria).
- **Extração de Dados:** Converter as abas `GESTAO_PERFORMANCE` e `GESTAO_STATUS_FUNIL` do Excel `Motor_Gestao_M6_v4_3.xlsx` para o formato `data.json`.
- **Validação de Paridade:** Aplicar a regra de "Tolerância Flexível" (Diferença < R$ 1,00) e "Tolerância Zero" para duplicatas.
- **Shadow Deploy:** Gerar um arquivo temporário antes de substituir o arquivo de produção.

### 2.2 Não-Funcionais
- **Atomicidade:** A atualização dos snapshots JSON deve ser feita de forma que o Dashboard nunca fique em um estado "quebrado" (ex: snapshots atualizados mas `data.json` antigo).
- **Logging:** Registrar cada etapa do processo em `log_deployment_YYYYMMDD.json`.

## 3. Arquitetura Proposta

### Fluxo de Trabalho (Pipeline)
1. **Wave 4:** Gera o `Motor_Gestao_M6_v4_3.xlsx`.
2. **Wave 8 (Refatorada):** 
   - Lê o Excel e os CSVs originais.
   - Retorna `True` se:
     - Diferença de Faturamento < 1.00
     - Diferença de Funil < 1.00
     - Duplicatas == 0
3. **Conversor (Novo Módulo):**
   - Transforma as tabelas do Excel no esquema JSON esperado pelo `aggregator.py`.
   - Salva como `data_staging.json`.
4. **Pre-Flight Validation:**
   - Compara a soma total de `data_staging.json` com os resultados aprovados na Wave 8.
5. **Atomic Swap:**
   - `mv data_staging.json data.json`
   - Executa `aggregator.py` para atualizar os snapshots de produção.

## 4. Plano de Testes (Validação)

| Teste | Critério de Sucesso |
|-------|--------------------|
| Paridade Financeira | Totais no `data.json` batem com o Relatório de Auditoria. |
| Integridade Estrutural | O schema do `data.json` mantém as chaves `metadata`, `performance` e `pipeline`. |
| Proteção de Produção | Se a Wave 8 falhar, o `data.json` original NÃO deve ser tocado. |

## 5. Decision Log
- **Decisão:** Extrair dados do Excel e não do DataFrame.
- **Motivo:** Garantir que o Dashboard reflita exatamente o documento que foi auditado e aprovado pelo usuário (Soberania de Dados).
- **Decisão:** Uso de Shadow Deploy (`data_staging.json`).
- **Motivo:** Prevenir corrupção do dashboard em caso de erro durante a escrita do JSON.
