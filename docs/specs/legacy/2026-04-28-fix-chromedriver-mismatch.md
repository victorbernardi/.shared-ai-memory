# Spec: Resolução de Conflito de Versão ChromeDriver (NotebookLM)

**Data:** 2026-04-28
**Status:** Pesquisa Concluída

## 1. Objetivo
Sincronizar a versão do ChromeDriver com a versão estável do Chrome (147.x) instalada no sistema, eliminando o erro `session not created`.

## 2. Análise
O log de erro confirmou que o driver atual exige o Chrome 148, enquanto o sistema possui o 147. O `undetected_chromedriver` armazena o binário em `%APPDATA%\undetected_chromedriver\undetected_chromedriver.exe`.

## 3. Requisitos
- Remover o binário incompatível.
- Forçar o redownload automático pelo servidor MCP.
- Validar se a versão baixada corresponde à 147.

## 4. Plano de Ação
1. Encerrar processos órfãos do Chrome ou ChromeDriver.
2. Deletar `C:\Users\victor.bernardi\AppData\Roaming\undetected_chromedriver\undetected_chromedriver.exe`.
3. Reiniciar o servidor NotebookLM via script de proxy.

## 5. Plano de Validação
- O servidor deve atingir o estado "Ready" e listar as ferramentas disponíveis sem tracebacks de driver.
