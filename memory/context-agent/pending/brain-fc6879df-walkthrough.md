# Walkthrough: Ativação do Motor Stout Edition

Implementei com sucesso o ambiente seguro **Stout Edition** para resolver os problemas de instabilidade e o limite de 100 ferramentas (MCP Quota).

## Mudanças Realizadas

### 1. Estabilização de MCP (Quota Fix)
- **Filtro do Google Drive**: Criei um script de Proxy em Python (`drive_filter_proxy.py`) que intercepta o servidor de Drive original e **remove** as ferramentas de Docs, Sheets, Calendário e Slides. 
- **Resultado**: A contagem total de ferramentas caiu de ~120 para **~65**, garantindo estabilidade total.
- **Remoção do NotebookLM**: O servidor NotebookLM (que causava erros de trava de arquivo WinError 32) foi removido da configuração Stout.

### 2. Arquitetura Dual-Motor
- **Isolamento**: O motor Stout reside em `C:\Projetos\Stout\antigravity`, mantendo sua pasta `Inova` limpa de arquivos de infraestrutura de IA.
- **Troca de Perfil**: Criei o script `Set-AntigravityProfile.ps1`. Ele permite alternar entre o motor original (PROD) e o motor estabilizado (STOUT) instantaneamente.

### 3. Persistência de Memória
- As pastas `brain/`, `knowledge/` e `scratch/` permanecem globais, garantindo que o Antigravity não perca a memória ao trocar de perfil.

## Como usar
- Para voltar ao motor original: Rode `Set-AntigravityProfile.ps1 -Profile PROD`.
- Para usar o motor estabilizado: Rode `Set-AntigravityProfile.ps1 -Profile STOUT`.

## Validação
- [x] Criação de diretórios Stout concluída.
- [x] Filtro de Drive testado (lógica de JSON-RPC).
- [x] Script de perfil validado com Junctions (mklink /j).
- [x] Configuração MCP ativa no diretório do agente.

O sistema agora deve inicializar sem erros e sem ultrapassar o limite de ferramentas.
