# Specification: Fix MCP Server Initialization Errors

## 1. Resumo do Objetivo
Corrigir os erros de inicialização dos servidores MCP (Model Context Protocol) relatados pelo Victor. Os erros incluem pacotes não encontrados (404), módulos Python ausentes e artefatos de build faltando.

## 2. Diagnóstico dos Erros
- **context7:** Tentativa de instalar `context7-mcp` via npm (404). Deve-se usar `@upstash/context7-mcp`.
- **google-developer-knowledge:** Tentativa de instalar `@google/developerknowledge-mcp-server` (404). Deve-se usar `mcp-remote` com a URL da Google.
- **google-drive:** Módulo `@modelcontextprotocol/server-google-drive` instalado mas sem o diretório `dist/`. Reinstalar ou usar `@piotr-agier/google-drive-mcp`.
- **notebooklm:** Módulo Python `notebooklm_mcp` ausente no ambiente Anaconda.

## 3. Requisitos de Solução
1. Atualizar o arquivo `C:\Users\victor.bernardi\AppData\Roaming\Claude\claude_desktop_config.json` com os comandos e pacotes corretos.
2. Instalar as dependências Python necessárias no ambiente `anaconda3`.
3. Limpar cache do npm e reinstalar pacotes problemáticos.

## 4. Plano de Execução Sugerido
1. Validar e corrigir `claude_desktop_config.json`.
2. Executar `pip install notebooklm-mcp` no ambiente Anaconda.
3. Executar `npm install -g @piotr-agier/google-drive-mcp` ou similar para garantir a presença dos arquivos.
4. Testar a inicialização dos servidores.

---
*Status: Criado para atender à solicitação de correção de erros MCP.*
