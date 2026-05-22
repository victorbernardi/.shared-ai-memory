# Spec de Pesquisa: Resolução de Kernel Anaconda (v1.1)

## Escopo
Investigação da falha de resolução do interpretador Python/Anaconda no ambiente Antigravity.

## Critérios de Aceitação (SOW)

| ID | Critério de Aceitação | Sinal Observável (Sucesso) |
| --- | --- | --- |
| AC-1 | Acesso ao Kernel Anaconda | O seletor de kernels do VS Code deve listar e conectar ao ambiente `base`. |
| AC-2 | Resolução de Caminho | O erro "Could not resolve interpreter path" não deve ser exibido após a configuração. |
| AC-3 | Execução de Código | Células de código e janelas interativas devem executar scripts Python sem falhas de inicialização de kernel. |

## Investigação Sistemática (Phase 1)
- **Caminho Validado:** `C:\Users\victor.bernardi\AppData\Local\anaconda3\python.exe` (Físico: OK)
- **Conda Validado:** `C:\Users\victor.bernardi\AppData\Local\anaconda3\Scripts\conda.exe` (Físico: OK)
- **Configuração Atual:** O workspace `.vscode/settings.json` está presente mas não aponta caminhos explícitos.
