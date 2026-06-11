# Spec: Correção Definitiva de Encoding e Handshake no NotebookLM MCP

## Problema
O servidor `notebooklm-mcp` falha ao iniciar no Windows devido a um `UnicodeEncodeError` disparado pela biblioteca `rich` ao tentar renderizar um emoji de foguete (🚀) no `stdout`. Como o transporte MCP é `stdio`, o traceback resultante corrompe o fluxo JSON, causando falhas de inicialização no Antigravity.

## Causa Raiz
1. **Conflito de Encoding:** O `rich` detecta o pipe de saída como um console legado e tenta usar `cp1252`, falhando em caracteres Unicode.
2. **Poluição de Stdout:** Mensagens de log e decorativas são enviadas para o mesmo canal de comunicação do protocolo MCP.

## Solução Proposta
1. **Isolamento de Fluxos:** Modificar o arquivo `cli.py` do pacote `notebooklm_mcp` para que o console do `rich` utilize exclusivamente o `stderr`.
2. **Remoção de Caracteres de Risco:** Remover emojis de títulos em painéis informativos para garantir compatibilidade máxima em consoles legado.
3. **Estabilização de Ambiente:** Reforçar o script de proxy com `chcp 65001` para alinhar o codepage do console com o Python.

## Plano de Implementação
### Fase 1: Patch de Código
- Localizar `C:\Users\victor.bernardi\AppData\Local\anaconda3\Lib\site-packages\notebooklm_mcp\cli.py`.
- Alterar `console = Console()` para `console = Console(stderr=True)`.
- Remover `🚀` da linha 261.

### Fase 2: Ajuste de Proxy
- Atualizar `notebooklm_proxy.cmd` com `chcp 65001`.

## Validação
1. Executar o servidor MCP via proxy e verificar se os logs aparecem no `stderr` (visíveis no terminal, mas não afetando o JSON).
2. Confirmar que o Antigravity consegue inicializar o servidor e listar as ferramentas.
