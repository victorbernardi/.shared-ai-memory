# Walkthrough: Estabilização do Sistema MCP

Concluí a implementação das correções críticas para resolver a instabilidade do Antigravity, focando no limite de 100 ferramentas e nos erros de inicialização do NotebookLM.

## Mudanças Realizadas

### 1. Limpeza de Ambiente (Task 1)
- Implementei e executei o script [cleanup_mcp.ps1](file:///C:/Users/victor.bernardi/.gemini/antigravity/scratch/cleanup_mcp.ps1).
- Encerrei com segurança processos órfãos de `python.exe` e `chromedriver.exe` que estavam bloqueando o `chromedriver.exe` (WinError 32).
- Removi o cache corrompido em `%APPDATA%\undetected_chromedriver`.

### 2. Correção de Encoding do NotebookLM (Task 2)
- Criei um wrapper script [run_notebooklm.bat](file:///C:/Users/victor.bernardi/.gemini/antigravity/scratch/run_notebooklm.bat) que força a página de código UTF-8 (`chcp 65001`) antes de iniciar o servidor Python.
- Isso resolve o erro de parsing onde o caractere 'â' (sequência UTF-8 inválida no console ANSI) quebrava o handshake JSON.

### 3. Otimização do Limite de Ferramentas (Task 3)
- Modifiquei o [mcp_config.json](file:///c:/Users/victor.bernardi/.gemini/antigravity/mcp_config.json) para:
    - Apontar o `notebooklm` para o novo wrapper `.bat`.
    - Remover os servidores `notion` e `tavily-search`, reduzindo a contagem total de ferramentas em aproximadamente 27 slots.
- Mantive o patch no `google-drive-mcp` que limita as ferramentas apenas a Drive e Docs.

## Validação

- Os comandos de limpeza foram executados com sucesso (Exit Code 0).
- O arquivo de configuração foi validado e salvo.
- A contagem total estimada de ferramentas agora é de aproximadamente **95**, ficando abaixo do limite rígido de 100 do Antigravity.

## Próximos Passos
1. **Reinicie o Antigravity:** Por favor, feche e abra o Antigravity para carregar as novas configurações.
2. **Verifique os Logs:** O NotebookLM agora deve iniciar o browser sem erros de trava de arquivo e sem falhas de encoding.
