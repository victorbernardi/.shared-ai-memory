# Spec: Estabilização do NotebookLM MCP (Encoding & ChromeDriver)

## Contexto
O servidor MCP `notebooklm-mcp` está enfrentando falhas de inicialização recorrentes no ambiente Windows. O problema principal é um `UnicodeEncodeError` disparado pela biblioteca `rich` ao tentar renderizar emojis (especificamente 🚀) em consoles com codificação legado (CP1252). Embora uma correção anterior tenha sido aplicada via proxy, o erro persiste ou retornou.

## Objetivos
1. Eliminar permanentemente o `UnicodeEncodeError` durante a inicialização.
2. Garantir a compatibilidade do ChromeDriver com a versão estável do Chrome (147) instalada no sistema.
3. Assegurar que as configurações persistam e sejam carregadas corretamente pelo Antigravity.

## Diagnóstico Atual
- **Traceback:** `UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f680'`.
- **Causa Raiz:** A biblioteca `rich` tenta renderizar emojis (🚀, ✅, ⚠️, etc.) usando o `legacy_windows_render` do Python, que falha ao mapear caracteres Unicode para a codificação CP1252 do console Windows, mesmo com variáveis de ambiente UTF-8 ativas.
- **Efeito Cascata:** A impressão desses caracteres (e dos painéis do `rich`) ocorre no `stdout`, corrompendo as mensagens JSON do protocolo MCP e impedindo a inicialização (erro `invalid character '+'`).

## Estratégia de Resolução
1. **Limpeza de Código (Surgical Patch):** Remover todos os emojis e caracteres Unicode problemáticos do arquivo `cli.py` da biblioteca instalada (`site-packages/notebooklm_mcp/cli.py`).
2. **Estabilização de Output:** Modificar o `cli.py` para garantir que toda saída visual seja enviada para `stderr` ou desativada quando o transporte for `stdio`.
3. **Reforço de Proxy:** Manter `set PYTHONUTF8=1` e `chcp 65001` no `notebooklm_proxy.cmd` como camadas de defesa.
4. **ChromeDriver Check:** Validar e reaplicar o patch de versão do Chrome (147) no arquivo `client.py` se necessário.

## Critérios de Aceite
- O servidor NotebookLM deve iniciar sem disparar tracebacks de encoding.
- O handshake MCP deve ocorrer com sucesso, sem corrupção de JSON no `stdout`.
- O Antigravity deve registrar todas as ferramentas do NotebookLM (ex: `ask_notebook`).
- O browser (Chrome) deve abrir na versão 147 sem conflitos.
