# Spec: Correção de UnicodeEncodeError no NotebookLM MCP

**Data:** 2026-04-28
**Status:** Pesquisa Concluída
**Responsável:** Antigravity (Stout Edition)

## 1. Objetivo
Resolver a falha crítica de inicialização do servidor `notebooklm-mcp` causada pela incapacidade do console Windows (CP1252) de processar caracteres Unicode (especificamente o emoji 🚀).

## 2. Análise do Problema
O erro `UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f680'` ocorre quando o script `cli.py` do NotebookLM tenta imprimir um painel visual utilizando a biblioteca `rich`.

### Localização do Erro
- **Arquivo:** `C:\Users\victor.bernardi\AppData\Local\anaconda3\Lib\site-packages\notebooklm_mcp\cli.py`
- **Linha:** 250 (função `server`)
- **Gatilho:** `console.print(Panel.fit(...))`

## 3. Requisitos
- **Funcional:** O servidor deve iniciar sem crashar ao tentar imprimir logs formatados.
- **Não-Funcional:** A solução deve ser aplicada via proxy (`.cmd`) para não depender de alterações globais no sistema ou no executável compilado.

## 4. Arquitetura da Solução
A solução consiste em modificar o script `C:\Users\victor.bernardi\.gemini\antigravity\scripts\notebooklm_proxy.cmd` para definir o ambiente Python antes da execução.

### Alteração Proposta:
```batch
@echo off
set PYTHONIOENCODING=utf-8
C:\Users\victor.bernardi\AppData\Local\anaconda3\Scripts\notebooklm-mcp.exe server %*
```

## 5. Plano de Validação
1. **Teste de Inicialização:** Executar o script de proxy manualmente para verificar se o erro persiste.
2. **Logs do MCP:** Verificar via logs do agente (ou console de depuração) se o servidor registra "Running" com sucesso.
3. **Teste de Caractere:** Verificar se o emoji 🚀 é renderizado (ou substituído por um fallback seguro) sem interromper a execução.

---
**Decision Log:**
- **Decisão:** Usar `PYTHONIOENCODING=utf-8` em vez de alterar o código-fonte do pacote.
- **Motivo:** Facilidade de manutenção e preservação da integridade do ambiente Anaconda do usuário.
- **Alternativa Considerada:** Alterar o `mcp_config.json` para incluir a seção `env`.
- **Ressalva:** Como o servidor é chamado via `cmd.exe /c`, o uso do script de proxy é mais robusto para gerenciar variáveis de ambiente em lote.
