# Plano de Estratégia v1 — Wave 0 (Dry Run) do NotebookLM

## 1. Objetivo
Executar a primeira rodada de testes (Wave 0) para validar a captura de conteúdo e a geração de PDFs, sem realizar uploads para a API.

## 2. Base de Informações (Arquivos Atuais)
- **Script:** `exported-assets (6)\build_notebooklm_llm_kb_research_300_regenerated.py` (já ajustado para usar `fpdf`).
- **Dados:** `exported-assets (6)\notebooklm_llm_manifest_research_300.json`.
- **Regras:** `README_agentic_notebooklm_runbook_ptbr.md`.

## 3. Abordagem Técnica
Devido às restrições do ambiente Windows para o `weasyprint`, utilizaremos o `fpdf` para gerar PDFs simples e rápidos, priorizando a extração correta do conteúdo pela biblioteca `trafilatura`.

## 4. Etapas de Execução (Modo Build)

### Etapa 4.1: Preparação do Ambiente
- Já instalado: `trafilatura`, `fpdf`, `requests`, `markdown`.
- Garantir que o manifesto está no local esperado (concluído).

### Etapa 4.2: Execução do Dry Run
Rodar o script com as seguintes variáveis de controle:
- `NOTEBOOKLM_SKIP_UPLOAD=true` (Garante que não haverá chamadas de API).
- `NOTEBOOKLM_MAX_ITEMS=10` (Lote reduzido para validação rápida).

### Etapa 4.3: Validação (Checklist)
Após a execução, verificaremos:
1. Existência da pasta `generated_pdfs_research_300`.
2. Integridade de pelo menos 3 PDFs (abertura e leitura básica).
3. Logs de erro na pasta `logs_research_300`.

## 5. Trava de Segurança
Este plano deve ser aprovado pelo usuário antes de qualquer nova tentativa de execução do script.

---
**Aguardando aprovação para iniciar a Etapa 4.2.**
