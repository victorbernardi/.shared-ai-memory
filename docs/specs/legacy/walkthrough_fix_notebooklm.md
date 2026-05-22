# Walkthrough: Correção de UnicodeEncodeError (NotebookLM)

**Status:** Concluído (Patch Aplicado)
**Data:** 2026-04-28

## O Problema
O servidor MCP do NotebookLM falhava durante a inicialização no Windows devido à incapacidade do console (codificação CP1252) de processar o caractere Unicode 🚀 (foguete) utilizado pela biblioteca `rich`.

## A Solução
Implementamos a injeção da variável de ambiente `PYTHONIOENCODING=utf-8` diretamente no script de proxy que gerencia a execução do servidor.

### Arquivos Modificados
- [notebooklm_proxy.cmd](file:///C:/Users/victor.bernardi/.gemini/antigravity/scripts/notebooklm_proxy.cmd)

## Resultados dos Testes
- **Remoção do Traceback:** O erro `UnicodeEncodeError` foi totalmente suprimido.
- **Progresso da Inicialização:** O servidor agora avança além da interface visual inicial e inicia a comunicação com o navegador.

## Observação Importante
Após a correção do Unicode, um novo erro ambiental foi identificado:
`This version of ChromeDriver only supports Chrome version 148`
`Current browser version is 147.0.7727.102`

Este é um problema de compatibilidade de versões no ambiente do usuário (ChromeDriver vs Chrome) e não está relacionado ao erro de codificação original.

## Auditoria (Canary)
A alteração foi promovida seguindo o protocolo Fast Canary e registrada em `diary/canary-log.md`.
