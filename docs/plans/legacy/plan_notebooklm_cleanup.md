# Plano de Implementação: Limpeza e Unificação do NotebookLM MCP

## Objective
Limpar instalações redundantes do NotebookLM MCP no ambiente e unificar as configurações para utilizar exclusivamente a versão instalada globalmente via `uv`.

## Key Files & Context
- `C:\Users\victor.bernardi\AppData\Local\anaconda3\` (Ambiente Python a ser limpo)
- `C:\Motores-LLM\gemini-cli\settings.json` (Configuração do ecossistema)
- `C:\Motores-LLM\gemini-cli\antigravity\mcp_config.json` (Configuração do Antigravity)
- `C:\Users\victor.bernardi\.local\bin\notebooklm-mcp.exe` (Binário alvo)

## Implementation Steps
1. **Desinstalação (Anaconda):**
   - Executar `C:\Users\victor.bernardi\AppData\Local\anaconda3\python.exe -m pip uninstall -y notebooklm-mcp notebooklm-mcp-server`.
2. **Limpeza de Órfãos:**
   - Remover quaisquer arquivos `notebooklm*.exe` residuais na pasta `C:\Users\victor.bernardi\AppData\Local\anaconda3\Scripts\`.
3. **Atualização (uv):**
   - Executar `uv tool upgrade notebooklm-mcp-cli` para garantir que o wrapper `nlm` e o servidor MCP estejam na versão mais recente.
4. **Configuração (settings.json):**
   - Substituir o valor de `"command"` na chave `"notebooklm"` para apontar para `"C:\\Users\\victor.bernardi\\.local\\bin\\notebooklm-mcp.exe"`.
5. **Configuração (mcp_config.json):**
   - Substituir o valor de `"command"` na chave `"notebooklm"` para apontar para `"C:\\Users\\victor.bernardi\\.local\\bin\\notebooklm-mcp.exe"`. (Remover quaisquer `args` legados caso estivessem apontando para python scripts não padrão).

## Verification & Testing
- Executar `nlm doctor` para validar se a instalação unificada é detectada como íntegra.
- Validar se o comando de listagem de notebooks via MCP e Antigravity carrega corretamente (sem travamentos de porta stdio).