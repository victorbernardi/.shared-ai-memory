# Spec: Patch de Versão Forçada no NotebookLM MCP

**Data:** 2026-04-28
**Status:** Pesquisa Concluída

## 1. Objetivo
Forçar o servidor MCP a utilizar o ChromeDriver compatível com a versão estável atual do usuário (147), ignorando a versão 148 (Beta/Early Stable).

## 2. Análise Técnica
O arquivo `client.py` do pacote `notebooklm_mcp` instancia o browser sem especificar a versão principal. Isso causa o download automático da versão 148, que falha ao conectar no Chrome 147.

## 3. Requisitos
- Modificar a linha 62 do arquivo `client.py` no diretório de site-packages do Anaconda.
- Garantir que a alteração seja atômica e não quebre a sintaxe Python.

## 4. Alteração Proposta
Substituir:
`self.driver = uc.Chrome(options=options, version_main=None)`
Por:
`self.driver = uc.Chrome(options=options, version_main=147)`

## 5. Plano de Validação
- Reiniciar o servidor e observar se ele para de reclamar da versão 148.
- Verificar se o browser abre corretamente.
