# Especificação: Correção de Conflito MCP NotebookLM

## 1. Problema
O servidor MCP do NotebookLM apresentava um `ImportError: cannot import name 'NotebookLMFastMCP' from 'notebooklm_mcp.server'`.

## 2. Causa Raiz
Colisão de pacotes no ambiente Anaconda. Dois pacotes distintos tentavam ocupar o mesmo namespace `notebooklm_mcp`:
- `notebooklm-mcp` (v2.0.11 - Desejado)
- `notebooklm-mcp-server` (v0.1.15 - Legado/Conflitante)

O pacote legado sobrescreveu os arquivos vitais do pacote novo, impedindo a inicialização do CLI.

## 3. Impacto
- Interrupção total do acesso ao NotebookLM via Antigravity e Gemini CLI.
- Falha na inicialização do servidor MCP via stdio.

## 4. Requisitos de Correção
- Limpeza total do namespace `notebooklm_mcp`.
- Instalação exclusiva da versão v2.
- Validação automatizada da integridade do namespace.
