# Especificação: Ambiente de Transcrição e Análise (Stout Edition)

**Data:** 2026-05-04  
**Versão:** v2  
**Status:** Execução (Auditado)  
**Referência:** [ADR-0001](file:///C:/Projetos/Transcricoes/docs/decisions/0001-adopt-fast-whisper-and-pandoc.md)

## 1. Objetivo
Estabelecer um ecossistema de transcrição de alta fidelidade e análise executiva, otimizado para alimentação do NotebookLM (Dashboard) e consumo humano estratégico.

## 2. Requisitos Funcionais
- **Processamento de Áudio:** Extração bruta via `faster-whisper` (Etapa 1).
- **Conversão de Mídia:** Geração obrigatória de arquivo **PDF** para a Transcrição FULL via motor `pandoc`.
- **Ata Executiva:** Sumarização inteligente via skill `meeting-assistant` (Etapa 2), focada em decisões e itens de ação.
- **Integração:** Upload automatizado (ou manual via guia) para o NotebookLM (ID: `65e6b083-0d9d-48ff-acd1-37711e1c62a5`).

## 3. Requisitos de Governança (Lei de Ferro)
- **Nomenclatura Padrão:** `YYYY-MM-DD_[Projeto-Assunto]_[TIPO].[ext]`
  - FULL: `..._FULL.md` e `..._FULL.pdf`
  - ATA: `..._ATA.md`
- **Audit Gate:** Toda transcrição deve ser registrada no `canary-log.md` após conclusão.

## 4. Mapeamento de Skills
1. `audio-transcriber`: Extração e Transcrição 1:1.
2. `meeting-assistant`: Refinamento e Ata Executiva.
3. `doc-workflow-orchestrator`: Governança e Ciclo de Vida.
4. `adr`: Registro de decisões técnicas.

## 5. Arquitetura do Pipeline
- **Entrada:** `/audio_input/`
- **Saída Bruta (FULL):** `/transcriptions/full/` (MD + PDF)
- **Saída Executiva (ATA):** `/transcriptions/summaries/` (MD)

## 6. Plano de Validação
- **Audit de Nomenclatura:** Verificar se os arquivos seguem o padrão ISO 8601.
- **Integridade do PDF:** Garantir que o PDF gerado pelo Pandoc preserve a estrutura de timestamps.
- **Sincronia:** Validar se a Ata reflete os pontos-chave da Transcrição Full sem alucinações.

---
*Status: Operacional | Auditor: Antigravity*
