# Spec: Reconciliação Sistêmica Antigravity (Stout v3)

## Objetivo
Unificar a "Fonte da Verdade" do ecossistema Antigravity, resolvendo a triplicidade de skills, estabilizando permanentemente os servidores MCP (Notion, Tavily e Drive) e eliminando erros de encoding/travas no NotebookLM.

## Problemas Identificados e Diagnóstico
1.  **Divergência de Configuração MCP:**
    - O `canary-log.md` registra a reativação do Notion e Tavily (28/04), mas o `mcp_config.json` atual não os contém.
    - A meta de < 100 ferramentas foi atingida via `drive_filter_proxy.py`, mas a configuração está incompleta.
2.  **Triplicidade de Skills:**
    - Conflito entre `./skills` (root), `./.gemini/skills` e caminhos globais. 
    - O `canary-log.md` define `./.gemini/skills` como fonte da verdade, mas o sistema ainda lê da raiz em alguns contextos.
3.  **Instabilidade do NotebookLM:**
    - Apesar do uso de `chcp 65001`, o handshake MCP ainda é sensível a outputs não-JSON no stdout (emojis, frames de tabelas do FastMCP).
    - Erros de `WinError 32` persistem se processos órfãos não forem limpos sistematicamente.
4.  **Caminhos Órfãos no Plano de Implementação:**
    - O arquivo `brain/implementation_plan.md` referencia pastas inexistentes (`antigravity-awesome-skills-main`), impedindo a automação da restauração.

## Requisitos de Reconciliação
- **Configuração MCP:**
    - Restaurar `notion` e `tavily-search` no `mcp_config.json`.
    - Validar o `drive_filter_proxy.py` para garantir que a soma total de ferramentas seja ~85.
- **Ecossistema de Skills:**
    - Consolidar todas as skills em `./.gemini/skills`.
    - Remover a pasta `./skills` da raiz após backup/verificação para evitar "shadowing".
- **Blindagem do NotebookLM:**
    - Ajustar o proxy para filtrar estritamente o stdout, permitindo apenas JSON válido para o Antigravity.
    - Implementar rotina de "Kill & Clean" antes de cada inicialização.

## Arquitetura de Solução Proposta
1.  **Unificação de Config:** Usar o `mcp_config.json` da raiz como base, adicionando os servidores faltantes com os parâmetros de proxy validados.
2.  **Limpeza de Skills:** Script de sincronização que move skills customizadas da raiz para `.gemini/skills` e deleta a origem.
3.  **Refatoração do Proxy NotebookLM:** Migrar de um `.cmd` simples para um wrapper Python que capture o stdout do servidor real e faça o parsing de JSON, descartando lixo de log.

## Plano de Validação
1.  **Auditoria de Ferramentas:** Comando `list_tools` via Antigravity deve retornar < 100 itens.
2.  **Teste de Skills:** O comando `activate_skill` deve carregar as instruções da pasta `.gemini/skills` corretamente.
3.  **Handshake Clean:** O log do NotebookLM não deve conter caracteres 'â' ou similares no fluxo JSON.

---
*Status: Pesquisa Concluída | Fase: Brainstorm*
