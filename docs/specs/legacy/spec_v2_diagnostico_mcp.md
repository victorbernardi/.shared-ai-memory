# Spec: Diagnóstico e Correção de Falhas Sistêmicas de MCP (v2)

## Objetivo
Resolver os erros de inicialização dos servidores MCP e a falha de execução no Antigravity, garantindo que o sistema opere abaixo do limite rígido de 100 ferramentas e que o NotebookLM funcione sem erros de trava de arquivo ou encoding.

## Problemas Identificados
1.  **Excesso de Ferramentas (Quota Exceeded):**
    - O limite do cliente é de 100 ferramentas.
    - Contagem estimada atual: Google Drive (patched ~60) + GitHub (~34) + Notion (22) + Tavily (5) + Outros (~10) = **~131 ferramentas**.
    - Isso impede o carregamento do Notion e Tavily, e causa instabilidade global.
2.  **NotebookLM - Erro de Trava de Arquivo (WinError 32):**
    - O `undetected-chromedriver` falha ao tentar patchear o `chromedriver.exe` porque o arquivo (ou seu destino) está em uso.
3.  **NotebookLM - Erro de Encoding ('â'):**
    - O handshake `initialize` falha porque o servidor envia caracteres não-JSON (como emojis ou mensagens de texto com encoding ANSI/UTF-8 misto) para o stdout.

## Requisitos
- **Funcionais:**
    - Reduzir o total de ferramentas para < 100 (Meta: ~80 para ter margem).
    - Garantir que o NotebookLM consiga iniciar o browser sem conflitos de arquivo.
    - Corrigir o parsing de JSON na inicialização dos servidores Python.
- **Não-Funcionais:**
    - Manter as ferramentas core: Google Drive (apenas Drive/Docs) e GitHub.
    - Toda a documentação e logs em **PT-BR**.
