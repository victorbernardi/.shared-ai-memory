# Especificação v1 — Setup Inicial e Diagnóstico de Ambiente

## 1. Objetivo
Estabelecer a estrutura de governança Stout e diagnosticar o estado atual do projeto NotebookLM para iniciar a Wave 0 (Dry Run).

## 2. Contexto Atual
O projeto possui documentação operacional (Runbook, Checklist, Prompts) exportada de uma sessão anterior, mas os ativos de execução (script e manifesto) e o ambiente Python não estão sincronizados.

## 3. Descobertas da Pesquisa
- **Documentação:** Presente em `exported-assets (1-4)`.
- **Dados:** O arquivo `exported-assets (4)/notebooklm_llm_upload_priority_300.json` contém a lista de 300 fontes com URLs e metadados.
- **Lacunas de Ativos:**
    - `build_notebooklm_llm_kb_research_300.py`: MISSING.
    - `notebooklm_llm_manifest_research_300.json`: MISSING (pode ser reconstruído a partir do priority JSON).
- **Lacunas de Ambiente:**
    - `trafilatura`: NOT INSTALLED.
    - `weasyprint`: NOT INSTALLED.
    - `notebooklm-mcp`: INSTALLED (v2.0.11).

## 4. Requisitos de Implementação
Para atingir o estado operacional, é necessário:
1. Reconstruir o script `build_notebooklm_llm_kb_research_300.py` com as seguintes capacidades:
    - Leitura do JSON de prioridade.
    - Captura de conteúdo via `trafilatura` (ou alternativa disponível).
    - Geração de PDF via `fpdf` (disponível) ou instalar `weasyprint`.
    - Upload via NotebookLM API.
2. Configurar o ambiente com as dependências faltantes.

## 5. Critérios de Aceite
- Estrutura Stout (GEMINI.md, docs/) criada.
- Diagnóstico validado pelo usuário.
- Plano para reconstrução do script aprovado.
