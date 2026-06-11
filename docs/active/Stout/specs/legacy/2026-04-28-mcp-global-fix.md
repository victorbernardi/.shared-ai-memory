# Especificação: Correção e Estabilização MCP Global

## 1. Objetivo
Resolver a instabilidade sistêmica e erros de execução associados aos servidores MCP `google-drive` e `notebooklm` no ecossistema Antigravity, utilizando exclusivamente as configurações globais (`mcp_config.json`) e redirecionadores (proxies).

## 2. Problema Atual
- **google-drive**: Erro `context deadline exceeded` (Timeout na inicialização) ao rodar diretamente via `npx`.
- **notebooklm**: Erro `No module named notebooklm_mcp.__main__; 'notebooklm_mcp' is a package and cannot be directly executed`.
- Alterações anteriores poluiram o `claude_desktop_config.json`, que não deve ser usado para a CLI do Antigravity.

## 3. Arquitetura Proposta
- Manter o `claude_desktop_config.json` intocado (de escopo apenas do aplicativo Desktop).
- Centralizar o roteamento dos servidores MCP no arquivo global do CLI: `C:\Users\victor.bernardi\.gemini\antigravity\mcp_config.json`.
- Manter o proxy Python existente para o `google-drive`.
- Criar um proxy nativo `.cmd` para o `notebooklm` na pasta global de scripts (`C:\Users\victor.bernardi\.gemini\antigravity\scripts\`) para contornar o erro de Python sem causar gargalos de I/O de JSON-RPC.

## 4. Plano de Validação (Critérios de Sucesso)
1. O CLI do Antigravity/Claude Code deve iniciar com sucesso sem erros de "context deadline exceeded".
2. As ferramentas de ambos os MCPs devem ser corretamente injetadas no contexto do LLM.
3. Não deve haver alterações residuais ou referências hardcoded entre o Desktop e a CLI.
