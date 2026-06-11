# Plano de Implementação: Fix NotebookLM Unicode Error

Este plano detalha a correção do erro de codificação Unicode no servidor NotebookLM MCP através da modificação do script de proxy.

## 1. Alterações Propostas

### Componente: Scripts de Proxy

#### [MODIFY] [notebooklm_proxy.cmd](file:///C:/Users/victor.bernardi/.gemini/antigravity/scripts/notebooklm_proxy.cmd)
Injetar a variável de ambiente `PYTHONIOENCODING=utf-8` antes da execução do binário do NotebookLM.

**Diferença:**
```diff
 @echo off
+set PYTHONIOENCODING=utf-8
 C:\Users\victor.bernardi\AppData\Local\anaconda3\Scripts\notebooklm-mcp.exe server %*
```

## 2. Passo a Passo da Execução

1.  **Backup de Segurança:** Criar uma cópia temporária do script atual.
2.  **Aplicação do Patch:** Atualizar o arquivo `.cmd` com a nova instrução.
3.  **Verificação de Sintaxe:** Garantir que o comando `set` não quebre a passagem de argumentos `%*`.

## 3. Plano de Verificação

### Verificação Manual
- Executar `C:\Users\victor.bernardi\.gemini\antigravity\scripts\notebooklm_proxy.cmd` via terminal local.
- Observar se o erro `UnicodeEncodeError` desaparece.
- Confirmar se o servidor inicia o loop de escuta (STDIN/STDOUT).

### Verificação de Sistema
- Reiniciar o serviço MCP (ou o agente Antigravity).
- Validar se as ferramentas do NotebookLM aparecem como ativas.

## 4. Rollback
Em caso de falha inesperada, restaurar o backup do arquivo `.cmd`.

---
**Aguardando aprovação do Victor para prosseguir para a Fase 3: Execução.**
